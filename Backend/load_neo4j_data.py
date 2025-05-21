#!/usr/bin/env python3
from neo4j import GraphDatabase
import os
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

# Neo4j connection details
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "mimo2021")

# Mental health disorders and symptoms data
disorders_data = [
    {
        "name": "Anxiety",
        "symptoms": ["Excessive worry", "Restlessness", "Difficulty concentrating", "Sleep problems", "Muscle tension"]
    },
    {
        "name": "Depression",
        "symptoms": ["Persistent sadness", "Loss of interest", "Changes in appetite", "Sleep disturbances", "Fatigue"]
    },
    {
        "name": "Generalized Anxiety Disorder",
        "symptoms": ["Chronic worry", "Difficulty controlling worry", "Physical tension", "Sleep disturbances", "Irritability"]
    },
    {
        "name": "Major Depressive Disorder",
        "symptoms": ["Severe depression", "Hopelessness", "Loss of pleasure", "Weight changes", "Suicidal thoughts"]
    },
    {
        "name": "Panic Disorder",
        "symptoms": ["Panic attacks", "Fear of panic attacks", "Avoidance behavior", "Heart palpitations", "Sweating"]
    },
    {
        "name": "Bipolar Disorder",
        "symptoms": ["Mood swings", "Manic episodes", "Depressive episodes", "Changes in energy", "Impulsivity"]
    },
    {
        "name": "Post-Traumatic Stress Disorder",
        "symptoms": ["Flashbacks", "Nightmares", "Avoidance", "Hypervigilance", "Emotional numbness"]
    },
    {
        "name": "Obsessive-Compulsive Disorder",
        "symptoms": ["Intrusive thoughts", "Compulsive behaviors", "Anxiety about rituals", "Time-consuming rituals", "Distress when rituals interrupted"]
    },
    {
        "name": "Schizophrenia",
        "symptoms": ["Delusions", "Hallucinations", "Disorganized thinking", "Reduced emotional expression", "Social withdrawal"]
    },
    {
        "name": "Borderline Personality Disorder",
        "symptoms": ["Emotional instability", "Fear of abandonment", "Impulsive behaviors", "Unstable relationships", "Self-harm"]
    },
    {
        "name": "ADHD",
        "symptoms": ["Inattention", "Hyperactivity", "Impulsivity", "Forgetfulness", "Fidgeting"]
    },
    {
        "name": "Autism Spectrum Disorder",
        "symptoms": ["Difficulty with communication", "Repetitive behaviors", "Sensory sensitivity", "Social challenges", "Restricted interests"]
    },
    {
        "name": "Social Anxiety Disorder",
        "symptoms": ["Fear of judgment", "Avoiding social interactions", "Blushing", "Nausea", "Sweating"]
    },
    {
        "name": "Dissociative Identity Disorder",
        "symptoms": ["Multiple identities", "Memory gaps", "Depersonalization", "Emotional detachment", "Blackouts"]
    },
    {
        "name": "Insomnia",
        "symptoms": ["Difficulty falling asleep", "Waking up frequently", "Early morning awakening", "Daytime fatigue", "Irritability"]
    },
    {
        "name": "Eating Disorder",
        "symptoms": ["Obsessive thoughts about food", "Extreme weight changes", "Distorted body image", "Purging", "Binge eating"]
    },
    {
        "name": "Anorexia Nervosa",
        "symptoms": ["Fear of gaining weight", "Restricted eating", "Low body weight", "Excessive exercise", "Body dysmorphia"]
    },
    {
        "name": "Bulimia Nervosa",
        "symptoms": ["Binge eating", "Purging", "Tooth decay", "Shame after eating", "Dehydration"]
    },
    {
        "name": "Body Dysmorphic Disorder",
        "symptoms": ["Preoccupation with appearance", "Mirror checking", "Avoiding mirrors", "Skin picking", "Comparing appearance"]
    },
    {
        "name": "Paranoia",
        "symptoms": ["Distrust of others", "Belief of being targeted", "Suspicion", "Isolation", "Hostility"]
    },
    {
        "name": "Agoraphobia",
        "symptoms": ["Fear of open spaces", "Avoiding public places", "Fear of leaving home", "Panic attacks", "Feeling trapped"]
    },
    {
        "name": "Histrionic Personality Disorder",
        "symptoms": ["Attention seeking", "Emotional overreaction", "Easily influenced", "Dramatic behavior", "Shallow emotions"]
    },
    {
        "name": "Narcissistic Personality Disorder",
        "symptoms": ["Inflated self-importance", "Lack of empathy", "Need for admiration", "Sense of entitlement", "Envy of others"]
    },
    {
        "name": "Antisocial Personality Disorder",
        "symptoms": ["Disregard for laws", "Deceitfulness", "Impulsivity", "Aggressiveness", "Lack of remorse"]
    },
    {
        "name": "Avoidant Personality Disorder",
        "symptoms": ["Social inhibition", "Feelings of inadequacy", "Hypersensitivity to criticism", "Avoiding social interaction", "Fear of rejection"]
    },
    {
        "name": "Dependent Personality Disorder",
        "symptoms": ["Excessive need to be taken care of", "Submissiveness", "Fear of separation", "Lack of confidence", "Difficulty making decisions"]
    },
    {
        "name": "Obsessive-Compulsive Personality Disorder",
        "symptoms": ["Preoccupation with orderliness", "Perfectionism", "Inflexibility", "Reluctance to delegate", "Overworking"]
    },
    {
        "name": "Somatic Symptom Disorder",
        "symptoms": ["Chronic pain", "Fatigue", "Excessive thoughts about symptoms", "Health anxiety", "Physical symptoms without medical cause"]
    },
    {
        "name": "Illness Anxiety Disorder",
        "symptoms": ["Fear of having illness", "Checking for signs of illness", "Avoiding doctors", "Health-related internet searching", "Reassurance seeking"]
    },
    {
        "name": "Psychotic Depression",
        "symptoms": ["Severe depression", "Delusions", "Hallucinations", "Paranoia", "Disorganized thinking"]
    }
]

def load_data_to_neo4j():
    try:
        # Connect to Neo4j
        driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
        logger.info("Connected to Neo4j database")
        
        # Clear existing data (optional)
        with driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")
            logger.info("Cleared existing data")
        
        # Load disorders and symptoms
        for disorder in disorders_data:
            with driver.session() as session:
                # Create disorder node
                session.run(
                    "MERGE (d:Disorder {name: $name})",
                    name=disorder["name"]
                )
                
                # Create symptom nodes and relationships
                for symptom in disorder["symptoms"]:
                    session.run(
                        """
                        MERGE (s:Symptom {name: $symptom})
                        MERGE (s)-[:INDICATES]->(d:Disorder {name: $disorder})
                        """,
                        symptom=symptom,
                        disorder=disorder["name"]
                    )
                
                logger.info(f"Added disorder: {disorder['name']} with {len(disorder['symptoms'])} symptoms")
        
        logger.info("Data loading complete")
        driver.close()
        return True
    
    except Exception as e:
        logger.error(f"Error loading data: {e}")
        return False

if __name__ == "__main__":
    logger.info("Starting Neo4j data loading process...")
    success = load_data_to_neo4j()
    if success:
        logger.info("Successfully loaded mental health data into Neo4j")
    else:
        logger.error("Failed to load data into Neo4j") 