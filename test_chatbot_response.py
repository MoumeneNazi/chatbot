import sys
import os
import logging

# Add the Backend directory to the path so we can import from it
sys.path.append(os.path.join(os.path.dirname(__file__), "Backend"))

from chatbot import MentalHealthChatbot

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Neo4j connection details (these won't be used as we'll mock the connection)
NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "mimo2021"

def test_creator_response():
    """Test that the chatbot responds correctly to 'who made you' questions"""
    try:
        # Initialize the chatbot
        chatbot = MentalHealthChatbot(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD)
        
        # Test various creator-related questions
        test_questions = [
            "Who made you?",
            "Who created you?",
            "Tell me who developed you",
            "I'm curious about your developers",
            "Who are your creators?",
            "Who designed you?",
            "What are you?",  # This should trigger the other response
            "I'm feeling anxious"  # This should trigger mental health response
        ]
        
        print("\n===== CHATBOT RESPONSE TESTS =====\n")
        
        for question in test_questions:
            print(f"Q: {question}")
            response = chatbot.chat(question)
            print(f"A: {response}\n")
            
        print("===== TEST COMPLETE =====")
        
    except Exception as e:
        logger.error(f"Test error: {e}")
        print(f"Error running test: {e}")

if __name__ == "__main__":
    test_creator_response() 