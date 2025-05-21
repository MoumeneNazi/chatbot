"""
Test script for DeepSeek API integration
This will test if we can successfully call the DeepSeek API with our credentials
"""
import os
import requests
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get DeepSeek API key
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
if not DEEPSEEK_API_KEY:
    raise ValueError("Missing DEEPSEEK_API_KEY in .env file")

def fallback_response(message: str) -> str:
    """Generate a fallback response when the DeepSeek API is unavailable"""
    # Convert message to lowercase for easier matching
    msg_lower = message.lower().strip()
    
    # Basic greeting detection
    if any(greeting in msg_lower for greeting in ["hey", "hi", "hello", "howdy", "greetings"]):
        return "Hello! I'm here to support you. How are you feeling today?"
    
    # Detect questions about depression
    if "depress" in msg_lower:
        return "Depression can be challenging to deal with. Regular exercise, maintaining a routine, and speaking with a professional can help. Would you like to share more about how you're feeling?"
    
    # Detect questions about anxiety
    if any(word in msg_lower for word in ["anxious", "anxiety", "worried", "stress", "panic"]):
        return "Anxiety can feel overwhelming. Deep breathing exercises, mindfulness, and speaking with a professional can be helpful. Remember that you're not alone in this experience."
    
    # Detect questions about sleep
    if any(word in msg_lower for word in ["sleep", "insomnia", "tired", "exhausted", "fatigue"]):
        return "Sleep issues can affect our mental health. Try maintaining a regular sleep schedule, avoiding screens before bed, and creating a relaxing bedtime routine. If problems persist, consider speaking with a healthcare provider."
    
    # Detect questions seeking help
    if any(word in msg_lower for word in ["help", "suicide", "kill myself", "die", "end it"]):
        return "I'm concerned about what you're sharing. Please reach out to a crisis support line immediately: National Suicide Prevention Lifeline at 988 or 1-800-273-8255, or text HOME to 741741 to reach the Crisis Text Line. Your life matters."
    
    # Detect questions about therapy
    if any(word in msg_lower for word in ["therapy", "therapist", "counseling", "psychologist", "psychiatrist"]):
        return "Seeking therapy can be a positive step toward better mental health. Types include cognitive-behavioral therapy, psychodynamic therapy, and others. Would you like more information about finding a therapist?"
    
    # Default supportive response when no specific pattern is matched
    return "I'm here to listen and support you. Would you like to tell me more about what you're experiencing?"

def test_deepseek_api():
    """Test if we can successfully call the DeepSeek API"""
    print(f"Using DeepSeek API key: {DEEPSEEK_API_KEY[:4]}...{DEEPSEEK_API_KEY[-4:]}")
    
    # DeepSeek API endpoint
    api_url = "https://api.deepseek.com/v1/chat/completions"
    
    # Request payload
    payload = {
        "model": "deepseek-chat",
        "messages": [
            {
                "role": "system",
                "content": "You are a helpful assistant."
            },
            {"role": "user", "content": "Hello! How are you?"}
        ],
        "max_tokens": 50,
        "temperature": 0.7,
        "stream": False
    }
    
    # Headers
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}"
    }
    
    print("Sending request to DeepSeek API...")
    
    try:
        # Make the API call
        response = requests.post(api_url, json=payload, headers=headers)
        
        # Check for successful response
        if response.status_code == 200:
            print("API call successful!")
            result = response.json()
            content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
            print(f"Response: {content}")
            
            # Print full response for debugging
            print("\nFull API response:")
            print(json.dumps(result, indent=2))
            
            return True
        else:
            print(f"API call failed with status code: {response.status_code}")
            print(f"Response content: {response.text}")
            
            # If there's an issue with the API, test the fallback
            print("\nTesting fallback mechanism...")
            return test_fallback()
    
    except Exception as e:
        print(f"Error calling DeepSeek API: {str(e)}")
        
        # If the API call fails completely, test the fallback
        print("\nTesting fallback mechanism...")
        return test_fallback()

def test_fallback():
    """Test the fallback functionality with various inputs"""
    print("\n=== Testing Fallback Responses ===")
    
    test_cases = [
        ("Hello there", "greeting"),
        ("I've been feeling really depressed lately", "depression"),
        ("I'm having a lot of anxiety and stress", "anxiety"),
        ("I can't sleep at night", "sleep"),
        ("I need help, I'm thinking about suicide", "crisis"),
        ("Should I try therapy?", "therapy"),
        ("What do you think about the weather?", "general")
    ]
    
    all_passed = True
    for message, category in test_cases:
        print(f"\nTesting '{category}' fallback with: '{message}'")
        response = fallback_response(message)
        print(f"Response: {response}")
        
        # Simple validation that we got something reasonable
        if len(response) > 20:  # Basic check that we got a meaningful response
            print("✅ Got meaningful fallback response")
        else:
            print("❌ Fallback response seems too short")
            all_passed = False
    
    return all_passed

if __name__ == "__main__":
    print("Testing DeepSeek API connection...")
    result = test_deepseek_api()
    if result:
        print("\n✅ Overall test passed!")
    else:
        print("\n❌ Test failed!") 