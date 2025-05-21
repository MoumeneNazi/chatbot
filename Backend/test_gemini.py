import requests, os
from dotenv import load_dotenv

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
headers = {"Content-Type": "application/json"}
params = {"key": GEMINI_API_KEY}
payload = {
    "contents": [
        {"parts": [{"text": "Explain how AI works in simple terms"}]}
    ]
}

response = requests.post(url, headers=headers, params=params, json=payload)
print("STATUS:", response.status_code)
print("BODY:", response.text)
