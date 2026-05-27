import re
import json
from src.clubs_service import add_club, get_all_clubs, delete_club, update_club

INTENTS_FILE = 'src/intents.json'


def load_intents():
    with open(INTENTS_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)['intents']


class Chatbot:
    def __init__(self):
        self.intents = load_intents()

    def process(self, user_input):
        if not user_input or not user_input.strip():
            return "Моля, въведете команда."

        text = user_input.strip()

        for intent in self.intents:
            for pattern in intent['patterns']:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    groups = match.groups()
                    handler = getattr(self, f"handle_{intent['tag']}", None)
                    if handler:
                        return handler(*groups)
                    return intent['responses'][0]

        return "Не разпознах командата. Напишете 'помощ' за наличните команди."

    def handle_help(self):
        for intent in self.intents:
            if intent['tag'] == 'help':
                return intent['responses'][0]
        return "Налични команди: помощ, добави клуб, списък клубове, изтрий клуб, промени клуб, изход."

    def handle_exit(self):
        return "EXIT"

    def handle_add_club(self, name=None):
        if not name:
            return "Моля, укажете име на клуб. Пример: добави клуб Левски София"
        try:
            return add_club(name)
        except (ValueError, RuntimeError) as e:
            return str(e)

    def handle_list_clubs(self):
        try:
            return get_all_clubs()
        except RuntimeError as e:
            return str(e)

    def handle_delete_club(self, identifier=None):
        if not identifier:
            return "Моля, укажете име или ID на клуб за изтриване."
        try:
            return delete_club(identifier.strip())
        except (ValueError, RuntimeError) as e:
            return str(e)

    def handle_update_club(self, identifier=None, new_name=None):
        if not identifier or not new_name:
            return "Моля, укажете клуб и ново име. Пример: промени клуб Левски на ЦСКА"
        try:
            return update_club(identifier.strip(), new_name.strip())
        except (ValueError, RuntimeError) as e:
            return str(e)
