from neo4j import GraphDatabase
import json
import os
import random
from datetime import datetime
from textblob import TextBlob         # pip install textblob

# Neo4j connection details
URI      = "bolt://localhost:7687"
USERNAME = "neo4j"
PASSWORD = "mimo2021"

class MentalHealthChatbot:
    def __init__(self, uri, user, password, memory_file="session_memory.json"):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        self.memory_file = memory_file
        self.session_context = self.load_session()
        self.symptom_list = self.load_symptom_list()
        self.disorder_list = self.load_disorder_list()  # Dynamically load disorders

    def load_symptom_list(self):
        """Load all symptom names from the Neo4j database."""
        with self.driver.session() as session:
            result = session.run("MATCH (s:Symptom) RETURN s.name AS name")
            return [r["name"] for r in result]

    def load_disorder_list(self):
        """Load all disorder names from the Neo4j database."""
        with self.driver.session() as session:
            result = session.run("MATCH (d:Disorder) RETURN d.name AS name")
            return [r["name"] for r in result]

    def load_session(self):
        """Load or initialize session memory."""
        if os.path.exists(self.memory_file):
            with open(self.memory_file, 'r') as f:
                return json.load(f)
        return {
            "reported_symptoms": [],
            "last_followup":    None,
            "session_history":  [],
            "journals":         []
        }

    def save_session(self):
        """Persist session memory."""
        with open(self.memory_file, 'w') as f:
            json.dump(self.session_context, f, indent=4)

    def close(self):
        """Save then close the driver."""
        self.save_session()
        self.driver.close()

    def extract_symptoms(self, user_input):
        """Return any symptom names that appear fully in the input."""
        low = user_input.lower()
        return [name for name in self.symptom_list if name.lower() in low]

    def diagnose_disorders(self, symptoms):
        """Graph-based approximate matching for disorders based on symptoms."""
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
            "date":        now,
            "entry":       entry,
            "mood_rating": mood_rating
        })
        self.save_session()

    def get_journal_entries(self):
        return self.session_context["journals"]

    def detect_sentiment(self, text):
        """Polarity: -1 (neg) to +1 (pos)."""
        return TextBlob(text).sentiment.polarity

    def ask_follow_up(self, symptom):
        """Default prompts for symptoms."""
        prompts = {
            "feeling tired":            "Have you been getting enough rest, or is your mind feeling constantly drained?",
            "hopelessness":             "Would you like to talk more about what's been weighing on you?",
            "having trouble in sleeping":"Is your sleep being interrupted by stress or worry?",
            "panic":                    "Can you tell me about what’s happening when you feel that way?",
            "anger":                    "Have there been situations lately that made you feel overwhelmed?",
            "sweating":                 "Does it come with anxiety or panic-like feelings?",
            "social media addiction":   "Do you think it’s affecting how you feel about yourself or your day?",
        }
        return prompts.get(symptom, "Would you like to talk more about what's been going on?")

    def chat(self, user_input):
        # Normalize user input to lowercase for consistent checks
        normalized_input = user_input.lower()

        # Handle specific cases
        if normalized_input in ["what is your purpose?", "why are you here?", "what do you do?"]:
            return "I am here to assist you with mental health-related questions and provide support."

        if normalized_input in ["who created you?", "who made you?"]:
            return "I was created by a team of developers to help users with mental health support."

        if normalized_input in ["how can you help me?", "what can you do?"]:
            return "I can provide mental health resources, help you track your mood, and assist with journaling."

        # Check if the user input mentions a disorder
        for disorder in self.disorder_list:
            if disorder.lower() in normalized_input:
                return f"It sounds like you're asking about **{disorder}**. Would you like to know more about it?"

        # Check if the user input mentions a symptom
        found_symptoms = self.extract_symptoms(user_input)
        if found_symptoms:
            return f"I noticed you mentioned the symptom(s): {', '.join(found_symptoms)}. Would you like to explore how these might relate to your mental health?"

        # 1) record
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.session_context["session_history"].append({
            "timestamp":  now,
            "user_input": user_input
        })

        # 2) sentiment
        polarity = self.detect_sentiment(user_input)
        if polarity < -0.2:
            sentiment = "negative"
        elif polarity > 0.2:
            sentiment = "positive"
        else:
            sentiment = "neutral"

        # 3) clarification check
        clarifiers = ["what", "mean", "explain", "define", "why", "how"]
        if any(kw in user_input for kw in clarifiers):
            return "I hear you're asking for clarification. Could you specify what you need more details about?"

        # 4) greetings
        if normalized_input in ["hello", "hi", "hey", "good morning", "good evening"]:
            return random.choice([
                "Hello! 😊 How have you been feeling lately?",
                "Hi there! What’s been on your mind today?",
                "Hey! I’m here whenever you want to share."
            ])

        # 5) farewells
        if normalized_input in ["bye", "goodbye", "quit", "exit"]:
            return random.choice([
                "Take care of yourself. 💙",
                "Goodbye! I'm here if you need me.",
                "Wishing you well. Reach out anytime."
            ])

        # 6) journal/mood prompts
        if "journal" in user_input:
            return "Would you like to write about your day and give your mood a score from 1 to 10?"
        if "mood" in user_input:
            return "How would you rate your mood today on a scale from 1 (low) to 10 (great)?"

        # 7) explicit diagnosis
        if any(kw in user_input for kw in ["diagnose", "what could this be", "what is wrong"]):
            if not self.session_context["reported_symptoms"]:
                return "We haven’t discussed many details. Would you like to share more about how you’re feeling?"
            preds = self.diagnose_disorders(self.session_context["reported_symptoms"])
            if not preds:
                return "I can’t guess based on what you’ve shared so far—but your feelings matter."
            msg = "Here’s what might relate to your experience:\n"
            for d, c in preds:
                msg += f"- {c:.1f}% match with **{d}**\n"
            msg += "This isn’t a medical diagnosis. Would you like to journal or talk more?"
            return msg

        # 8) symptom extraction & specific follow-ups
        found = self.extract_symptoms(user_input)
        new   = [s for s in found if s not in self.session_context["reported_symptoms"]]
        self.session_context["reported_symptoms"].extend(new)

        if new:
            sym = new[0]
            self.session_context["last_followup"] = sym
            self.save_session()

            # special case: sweating before sleep
            if "sweating" in sym and "sleep" in user_input:
                return random.choice([
                    "It sounds like you're having **sweating before sleep**. That must be uncomfortable. Have you noticed what triggers it?",
                    "Sweating before sleep can be distressing. Would you like to explore if it’s tied to anxiety or something else?"
                ])

            return random.choice([
                f"It sounds like you're experiencing **{sym}**. That’s not easy—how long has this been going on?",
                f"I hear you're dealing with **{sym}**. Would you like to explore what might be causing it?",
                f"Thanks for sharing about **{sym}**. Has it been affecting your daily life much?",
                f"That must be difficult. I'm here to support you—do you want to talk more about **{sym}**?"
            ])

        # 9) varied fallback
        if sentiment == "negative":
            fallbacks = [
                "I’m sorry you’re feeling this way. Would you like to share more about what’s on your mind?",
                "It sounds like you're going through a difficult time. I’m here to listen if you wish to continue.",
                "This seems hard. Want to talk more about it?"
            ]
        elif sentiment == "positive":
            fallbacks = [
                "I’m glad to hear you’re feeling okay. What’s been going well for you?",
                "You sound positive today—would you like to share what’s uplifting you?",
                "Great that things feel alright—anything specific bringing you joy?"
            ]
        else:
            fallbacks = [
                "I appreciate you opening up. Would you like to share more about what’s on your mind?",
                "That makes sense. How is this affecting your mood?",
                "Thank you for sharing. Anything in particular that triggered these feelings?",
                "I'm here for you—tell me more if you feel comfortable."
            ]

        self.save_session()
        return random.choice(fallbacks)


# Optional CLI runner
if __name__ == "__main__":
    bot = MentalHealthChatbot(URI, USERNAME, PASSWORD)
    print("🤖 Chatbot: Hello! I'm here to help. Tell me how you're feeling. (Type 'exit' to quit)\n")
    while True:
        ui = input("You: ").strip().lower()
        if ui in ["exit", "quit"]:
            print("Chatbot: Take care! 💙")
            break
        print("Chatbot:", bot.chat(ui))
    bot.close()
