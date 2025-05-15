from neo4j import GraphDatabase
import json
import os
import random
from datetime import datetime
from textblob import TextBlob
from groq import Groq
from dotenv import load_dotenv

# Load environment variables for Groq API
load_dotenv()
# groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
groq_client = Groq(api_key="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")

# Neo4j connection details
URI = "bolt://localhost:7687"
USERNAME = "neo4j"
PASSWORD = "mimo2021"

def ask_groq(message):
    try:
        response = groq_client.chat.completions.create(
            model="mixtral-8x7b-32768",
            messages=[{"role": "user", "content": message}],
            max_tokens=300,
            temperature=0.7,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"[Groq API Error]: {e}")
        return None

class MentalHealthChatbot:
    def __init__(self, uri, user, password, memory_file="session_memory.json"):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        self.memory_file = memory_file
        self.session_context = self.load_session()
        self.symptom_list = self.load_symptom_list()
        self.disorder_list = self.load_disorder_list()

    def load_symptom_list(self):
        with self.driver.session() as session:
            result = session.run("MATCH (s:Symptom) RETURN s.name AS name")
            return [r["name"] for r in result]

    def load_disorder_list(self):
        with self.driver.session() as session:
            result = session.run("MATCH (d:Disorder) RETURN d.name AS name")
            return [r["name"] for r in result]

    def load_session(self):
        if os.path.exists(self.memory_file):
            with open(self.memory_file, 'r') as f:
                return json.load(f)
        return {
            "reported_symptoms": [],
            "last_followup": None,
            "session_history": [],
            "journals": []
        }

    def save_session(self):
        with open(self.memory_file, 'w') as f:
            json.dump(self.session_context, f, indent=4)

    def close(self):
        self.save_session()
        self.driver.close()

    def extract_symptoms(self, user_input):
        low = user_input.lower()
        return [name for name in self.symptom_list if name.lower() in low]

    def diagnose_disorders(self, symptoms):
        query = """
        MATCH (s:Symptom)-[:INDICATES]->(d:Disorder)
        WHERE s.name IN $symptoms
        RETURN d.name AS disorder, count(*) AS score
        ORDER BY score DESC
        """
        with self.driver.session() as session:
            result = session.run(query, symptoms=symptoms)
            preds, total = [], max(len(symptoms), 1)
            for r in result:
                preds.append((r["disorder"], min(100, (r["score"] / total) * 100)))
            return preds

    def add_journal_entry(self, entry, mood_rating):
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.session_context["journals"].append({
            "date": now,
            "entry": entry,
            "mood_rating": mood_rating
        })
        self.save_session()

    def get_journal_entries(self):
        return self.session_context["journals"]

    def detect_sentiment(self, text):
        return TextBlob(text).sentiment.polarity

    def chat(self, user_input):
        normalized_input = user_input.lower()

        # Replace rule-based replies with Groq API calls
        if normalized_input in ["what is your purpose?", "why are you here?", "what do you do?"]:
            return ask_groq("As a mental health chatbot, what is your purpose?")
        if normalized_input in ["who created you?", "who made you?"]:
            return ask_groq("Who created you as a mental health chatbot?")
        if normalized_input in ["how can you help me?", "what can you do?"]:
            return ask_groq("How can you help me as a mental health chatbot?")

        for disorder in self.disorder_list:
            if disorder.lower() in normalized_input:
                return ask_groq(f"The user mentioned '{disorder}'. Respond as a mental health chatbot offering more information.")

        found_symptoms = self.extract_symptoms(user_input)
        if found_symptoms:
            symptom_string = ", ".join(found_symptoms)
            return ask_groq(f"The user mentioned the symptom(s): {symptom_string}. Acknowledge this and offer to explore how these might relate to their mental health.")

        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.session_context["session_history"].append({
            "timestamp": now,
            "user_input": user_input
        })

        polarity = self.detect_sentiment(user_input)
        sentiment = "negative" if polarity < -0.2 else "positive" if polarity > 0.2 else "neutral"

        clarifiers = ["what", "mean", "explain", "define", "why", "how"]
        if any(kw in user_input for kw in clarifiers):
            return ask_groq("The user is asking for clarification. Prompt them to specify what they need more details about.")

        if normalized_input in ["hello", "hi", "hey", "good morning", "good evening"]:
            return ask_groq("Respond to a greeting as a friendly mental health chatbot.")

        if normalized_input in ["bye", "goodbye", "quit", "exit"]:
            return ask_groq("Respond to the user saying goodbye as a supportive mental health chatbot.")

        if "journal" in user_input:
            return ask_groq("The user mentioned 'journal'. Prompt them if they would like to write about their day and rate their mood.")
        if "mood" in user_input:
            return ask_groq("The user mentioned 'mood'. Ask them to rate their mood on a scale from 1 to 10.")

        if any(kw in user_input for kw in ["diagnose", "what could this be", "what is wrong"]):
            if not self.session_context["reported_symptoms"]:
                return ask_groq("The user is asking for a potential diagnosis but hasn't shared many details. Encourage them to share more about how they're feeling.")
            preds = self.diagnose_disorders(self.session_context["reported_symptoms"])
            if not preds:
                return ask_groq("The user is asking for a potential diagnosis based on shared symptoms, but no strong matches were found. Reassure them that their feelings matter and suggest journaling or talking more.")
            msg = "Here’s what might relate to your experience:\n"
            for d, c in preds:
                msg += f"- {c:.1f}% match with **{d}**\n"
            msg += "This isn’t a medical diagnosis. Would you like to journal or talk more?"
            return ask_groq(msg) # Consider refining this prompt

        found = self.extract_symptoms(user_input)
        new = [s for s in found if s not in self.session_context["reported_symptoms"]]
        self.session_context["reported_symptoms"].extend(new)

        if new:
            sym = new[0]
            self.session_context["last_followup"] = sym
            self.save_session()
            if "sweating" in sym and "sleep" in user_input:
                return ask_groq("The user mentioned 'sweating' and 'sleep'. Respond as a mental health chatbot acknowledging this and asking if they've noticed any triggers or if it feels tied to anxiety.")
            return ask_groq(f"The user mentioned experiencing '{sym}'. Acknowledge this and ask how long it has been going on, if they'd like to explore potential causes, or if it has significantly affected their daily life. Offer support.")

        self.save_session()

        # Default fallback - use Groq to generate a response based on the user input and context
        try:
            prompt = f"The user said: '{user_input}'. Respond as a helpful and supportive mental health chatbot."
            return ask_groq(prompt)
        except Exception as e:
            print(f"[Groq Fallback Error]: {e}")
            if sentiment == "negative":
                return random.choice([
                    "I’m sorry you’re feeling this way. Would you like to share more?",
                    "You're not alone—I'm here for you if you want to talk more.",
                    "It sounds tough. Want to tell me more about it?"
                ])
            elif sentiment == "positive":
                return random.choice([
                    "I'm happy to hear that! 😊 What made your day better?",
                    "That’s great! Want to share what's been uplifting?"
                ])
            else:
                return random.choice([
                    "Thanks for sharing. Would you like to dive deeper into this?",
                    "Got it. How do you feel about that now?",
                    "I'm listening—anything else you'd like to add?"
                ])

# Optional CLI
if __name__ == "__main__":
    # Ensure you have a .env file with your GROQ_API_KEY
    load_dotenv()
    if not os.getenv("GROQ_API_KEY"):
        print("Error: GROQ_API_KEY not found in .env file.")
    else:
        bot = MentalHealthChatbot(URI, USERNAME, PASSWORD)
        print("🤖 Hello! I'm here to support you. Type 'exit' to quit.\n")
        while True:
            user_input = input("You: ").strip()
            if user_input.lower() in ["exit", "quit"]:
                print("Chatbot: Take care! 💙")
                break
            response = bot.chat(user_input)
            if response:
                print("Chatbot:", response)
            else:
                print("Chatbot: I'm having trouble connecting right now. Please try again later.")
        bot.close()



# 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