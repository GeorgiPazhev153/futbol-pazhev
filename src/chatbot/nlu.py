import re
import json
import os

INTENTS_PATH = os.path.join(os.path.dirname(__file__), 'intents.json')


class NLU:
    def __init__(self):
        with open(INTENTS_PATH, 'r', encoding='utf-8') as f:
            self.intents = json.load(f)['intents']

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
