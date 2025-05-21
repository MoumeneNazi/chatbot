#!/usr/bin/env python3
"""
Chat Learning Module

Analyzes chat conversations to extract disorders, symptoms, and meaningful phrases
to enhance the Neo4j knowledge base.
"""

import os
import logging
import sqlite3
import json
import re
from collections import Counter
from typing import List, Dict, Tuple, Set
from datetime import datetime
from neo4j import GraphDatabase
from dotenv import load_dotenv
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import textblob
import spacy
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Ensure NLTK data is downloaded
import nltk
try:
    nltk.data.find('corpora/stopwords')
    nltk.data.find('tokenizers/punkt')
    nltk.data.find('corpora/wordnet')
except LookupError:
    nltk.download('stopwords')
    nltk.download('punkt')
    nltk.download('wordnet')

# Load environment variables
env_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path=env_path)

# Neo4j connection details
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "mimo2021")

# Database connection
DATABASE_URI = os.getenv("DATABASE_URI", "sqlite:///./mental_health.db")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Load spaCy model
try:
    nlp = spacy.load("en_core_web_sm")
except Exception as e:
    logger.error(f"Could not load spaCy model: {e}")
    logger.info("Installing spaCy model...")
    os.system("python -m spacy download en_core_web_sm")
    try:
        nlp = spacy.load("en_core_web_sm")
    except Exception as e:
        logger.error(f"Failed to install spaCy model: {e}")
        raise

class ChatLearningSystem:
    """System to learn from chat conversations and update the knowledge base."""
    
    def __init__(self):
        self.known_disorders = set()
        self.known_symptoms = set()
        self.word_lemmatizer = WordNetLemmatizer()
        self.stopwords = set(stopwords.words('english'))
        self.threshold = 3  # Minimum occurrences to consider a potential new entity
        
        # Connect to Neo4j
        try:
            self.neo4j_driver = GraphDatabase.driver(
                NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD)
            )
            logger.info("Connected to Neo4j database")
        except Exception as e:
            logger.error(f"Failed to connect to Neo4j: {e}")
            self.neo4j_driver = None
        
        # Connect to SQL database
        try:
            self.engine = create_engine(DATABASE_URI)
            self.Session = sessionmaker(bind=self.engine)
            logger.info("Connected to SQL database")
        except Exception as e:
            logger.error(f"Failed to connect to SQL database: {e}")
            self.engine = None
            self.Session = None
            
        # Load existing knowledge
        self.load_existing_knowledge()
    
    def load_existing_knowledge(self):
        """Load existing disorders and symptoms from Neo4j."""
        if not self.neo4j_driver:
            logger.warning("No Neo4j connection. Skipping knowledge loading.")
            return
            
        with self.neo4j_driver.session() as session:
            # Load existing disorders
            result = session.run("MATCH (d:Disorder) RETURN d.name AS name")
            for record in result:
                self.known_disorders.add(record["name"].lower())
            
            # Load existing symptoms
            result = session.run("MATCH (s:Symptom) RETURN s.name AS name")
            for record in result:
                self.known_symptoms.add(record["name"].lower())
                
        logger.info(f"Loaded {len(self.known_disorders)} disorders and {len(self.known_symptoms)} symptoms")
    
    def fetch_chat_messages(self, limit=1000, days=30):
        """Fetch recent chat messages from the database."""
        if not self.engine:
            logger.warning("No database connection. Cannot fetch chat messages.")
            return []
            
        try:
            with self.engine.connect() as connection:
                query = text("""
                    SELECT content 
                    FROM chat_messages 
                    WHERE role = 'user' 
                    AND timestamp > datetime('now', :days_ago)
                    ORDER BY timestamp DESC
                    LIMIT :limit
                """)
                
                result = connection.execute(query, {"days_ago": f"-{days} days", "limit": limit})
                messages = [row[0] for row in result]
                logger.info(f"Fetched {len(messages)} chat messages")
                return messages
        except Exception as e:
            logger.error(f"Error fetching chat messages: {e}")
            return []
    
    def preprocess_text(self, text):
        """Clean and preprocess text for analysis."""
        # Convert to lowercase
        text = text.lower()
        
        # Remove special characters and digits
        text = re.sub(r'[^\w\s]', ' ', text)
        text = re.sub(r'\d+', ' ', text)
        
        # Tokenize
        tokens = word_tokenize(text)
        
        # Remove stopwords and lemmatize
        tokens = [self.word_lemmatizer.lemmatize(word) for word in tokens if word not in self.stopwords]
        
        return tokens
    
    def extract_potential_entities(self, messages):
        """Extract potential mental health entities from messages."""
        potential_disorders = Counter()
        potential_symptoms = Counter()
        
        for message in messages:
            # Use spaCy for entity recognition
            doc = nlp(message)
            
            # Extract noun phrases as potential disorders/symptoms
            for chunk in doc.noun_chunks:
                if 3 <= len(chunk.text.split()) <= 6:  # Only consider phrases of reasonable length
                    potential_disorders[chunk.text.lower()] += 1
                    
            # Extract symptoms using symptom-related patterns
            symptom_patterns = [
                "feel", "feeling", "felt", "experiencing", "experience", "suffered from", 
                "having", "have", "had", "struggling with", "battling", "fighting"
            ]
            
            for pattern in symptom_patterns:
                matches = re.finditer(f"{pattern} ([^.!?]*)", message.lower())
                for match in matches:
                    symptom_text = match.group(1).strip()
                    if 2 <= len(symptom_text.split()) <= 7:  # Only consider phrases of reasonable length
                        potential_symptoms[symptom_text] += 1
        
        # Filter by threshold
        potential_disorders = {k: v for k, v in potential_disorders.items() if v >= self.threshold}
        potential_symptoms = {k: v for k, v in potential_symptoms.items() if v >= self.threshold}
        
        # Remove known entities
        new_disorders = {k: v for k, v in potential_disorders.items() if k not in self.known_disorders}
        new_symptoms = {k: v for k, v in potential_symptoms.items() if k not in self.known_symptoms}
        
        return new_disorders, new_symptoms
    
    def add_entities_to_neo4j(self, new_disorders, new_symptoms):
        """Add new entities to Neo4j if they meet the threshold."""
        if not self.neo4j_driver:
            logger.warning("No Neo4j connection. Skipping knowledge update.")
            return
            
        added_disorders = []
        added_symptoms = []
        
        with self.neo4j_driver.session() as session:
            # Add new disorders
            for disorder, count in new_disorders.items():
                logger.info(f"Adding new disorder: {disorder} (mentioned {count} times)")
                session.run(
                    "MERGE (d:Disorder {name: $name})",
                    name=disorder.title()  # Convert to title case for better readability
                )
                added_disorders.append(disorder)
                self.known_disorders.add(disorder)
            
            # Add new symptoms
            for symptom, count in new_symptoms.items():
                logger.info(f"Adding new symptom: {symptom} (mentioned {count} times)")
                session.run(
                    "MERGE (s:Symptom {name: $name})",
                    name=symptom.title()  # Convert to title case for better readability
                )
                added_symptoms.append(symptom)
                self.known_symptoms.add(symptom)
                
        return added_disorders, added_symptoms
    
    def analyze_chats(self):
        """Main function to analyze chats and update the knowledge base."""
        # Fetch chat messages
        messages = self.fetch_chat_messages()
        if not messages:
            logger.warning("No messages to analyze")
            return
            
        # Extract potential new entities
        new_disorders, new_symptoms = self.extract_potential_entities(messages)
        
        if not new_disorders and not new_symptoms:
            logger.info("No new entities found")
            return
            
        # Add entities to Neo4j
        added_disorders, added_symptoms = self.add_entities_to_neo4j(new_disorders, new_symptoms)
        
        # Log results
        if added_disorders:
            logger.info(f"Added {len(added_disorders)} new disorders: {', '.join(added_disorders)}")
        
        if added_symptoms:
            logger.info(f"Added {len(added_symptoms)} new symptoms: {', '.join(added_symptoms)}")
            
        return {
            "added_disorders": added_disorders,
            "added_symptoms": added_symptoms
        }

def main():
    """Run the chat learning system."""
    try:
        logger.info("Starting Chat Learning System")
        system = ChatLearningSystem()
        results = system.analyze_chats()
        
        if results:
            logger.info(f"Learning completed successfully. Added {len(results.get('added_disorders', []))} disorders and {len(results.get('added_symptoms', []))} symptoms.")
        else:
            logger.info("Learning completed. No new entities added.")
            
    except Exception as e:
        logger.error(f"Error in Chat Learning System: {e}")

if __name__ == "__main__":
    main() 