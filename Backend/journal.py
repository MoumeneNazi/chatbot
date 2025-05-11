import os
import json
from datetime import datetime
from textblob import TextBlob
from collections import Counter
from datetime import date

JOURNAL_FILE = "journal_entries.json"

def load_journal():
    if not os.path.exists(JOURNAL_FILE):
        return []
    with open(JOURNAL_FILE, "r") as f:
        return json.load(f)

def analyze_sentiment(text):
    polarity = TextBlob(text).sentiment.polarity
    if polarity > 0.2:
        return "positive"
    elif polarity < -0.2:
        return "negative"
    else:
        return "neutral"


def get_sentiment_summary():
    entries = load_journal()
    today = date.today()
    sentiments = [e.get("sentiment", "unknown") for e in entries if e["timestamp"].startswith(str(today))]
    count = Counter(sentiments)
    return {
        "date": str(today),
        "summary": count
    }

def save_entry(user_input: str):
    sentiment = analyze_sentiment(user_input)
    entry = {
        "timestamp": str(datetime.now()),
        "entry": user_input,
        "sentiment": sentiment
    }
    entries = load_journal()
    entries.append(entry)
    with open(JOURNAL_FILE, "w") as f:
        json.dump(entries, f, indent=4)
    return entry
def get_entries():
    return load_journal()
