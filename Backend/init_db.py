from neo4j import GraphDatabase
import logging
import os
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
env_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path=env_path)

# Neo4j connection details
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "mimo2021")

# Disorder to symptom mappings
disorders_symptoms = {
    "Anxiety": [
        "Excessive worry", "Restlessness", "Difficulty concentrating", 
        "Sleep problems", "Muscle tension"
    ],
    "Depression": [
        "Persistent sadness", "Loss of interest", "Changes in appetite", 
        "Sleep disturbances", "Fatigue"
    ],
    "Generalized Anxiety Disorder": [
        "Chronic worry", "Difficulty controlling worry", "Physical tension", 
        "Sleep disturbances", "Irritability"
    ],
    "Major Depressive Disorder": [
        "Severe depression", "Hopelessness", "Loss of pleasure", 
        "Weight changes", "Suicidal thoughts"
    ],
    "Panic Disorder": [
        "Panic attacks", "Fear of panic attacks", "Avoidance behavior", 
        "Heart palpitations", "Sweating"
    ],
    "Bipolar Disorder": [
        "Mood swings", "Manic episodes", "Depressive episodes", 
        "Changes in energy", "Impulsivity"
    ],
    "Post-Traumatic Stress Disorder": [
        "Flashbacks", "Nightmares", "Avoidance", 
        "Hypervigilance", "Emotional numbness"
    ],
    "Obsessive-Compulsive Disorder": [
        "Intrusive thoughts", "Compulsive behaviors", "Anxiety about rituals", 
        "Time-consuming rituals", "Distress when rituals interrupted"
    ]
}

class Neo4jInitializer:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def clear_database(self):
        with self.driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")
            logger.info("Database cleared")

    def create_disorder(self, name):
        with self.driver.session() as session:
            session.run(
                "MERGE (d:Disorder {name: $name})",
                name=name
            )
            logger.info(f"Created disorder: {name}")

    def create_symptom(self, name):
        with self.driver.session() as session:
            session.run(
                "MERGE (s:Symptom {name: $name})",
                name=name
            )
            logger.info(f"Created symptom: {name}")

    def create_relationship(self, disorder_name, symptom_name):
        with self.driver.session() as session:
            session.run(
                """
                MATCH (d:Disorder {name: $disorder_name})
                MATCH (s:Symptom {name: $symptom_name})
                MERGE (d)-[:HAS_SYMPTOM]->(s)
                """,
                disorder_name=disorder_name,
                symptom_name=symptom_name
            )
            logger.info(f"Created relationship between {disorder_name} and {symptom_name}")

    def initialize_database(self):
        try:
            # Clear the database first
            self.clear_database()
            
            # Create disorders and symptoms with relationships
            for disorder, symptoms in disorders_symptoms.items():
                self.create_disorder(disorder)
                for symptom in symptoms:
                    self.create_symptom(symptom)
                    self.create_relationship(disorder, symptom)
            
            logger.info("Database initialization completed successfully")
            return True
        except Exception as e:
            logger.error(f"Error initializing database: {str(e)}")
            return False

if __name__ == "__main__":
    try:
        logger.info("Connecting to Neo4j...")
        initializer = Neo4jInitializer(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD)
        success = initializer.initialize_database()
        initializer.close()
        
        if success:
            logger.info("Neo4j database initialized successfully.")
        else:
            logger.error("Failed to initialize Neo4j database.")
    except Exception as e:
        logger.error(f"Error: {str(e)}") 