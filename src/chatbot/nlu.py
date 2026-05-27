import re
from src.chatbot.intents import INTENTS


class NLU:
    def __init__(self):
        self.intents = INTENTS

    def process(self, text):
        if not text or not text.strip():
            return 'unknown', ()
        text = text.strip()
        for intent in self.intents:
            for pattern in intent['patterns']:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    return intent['tag'], match.groups()
        return 'unknown', ()
