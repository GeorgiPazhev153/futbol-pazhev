import re
import json
from src.clubs_service import add_club, get_all_clubs, delete_club, update_club
from src.players_service import (
    add_player, get_players_by_club, get_all_players,
    update_player_number, update_player_status, delete_player
)

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

    # --- Player handlers ---

    def handle_add_player(self, name=None, club_name=None, position=None, number=None):
        if not all([name, club_name, position, number]):
            return "Моля, използвайте: добави играч <име> в <клуб> позиция <GK|DF|MF|FW> номер <число>"
        try:
            return add_player(name, club_name, position, number)
        except (ValueError, RuntimeError) as e:
            return str(e)

    def handle_list_players(self, club_name=None):
        if not club_name:
            return "Моля, укажете клуб. Пример: покажи играчи на Левски"
        try:
            return get_players_by_club(club_name.strip())
        except (ValueError, RuntimeError) as e:
            return str(e)

    def handle_update_player_number(self, identifier=None, new_number=None):
        if not identifier or not new_number:
            return "Моля, използвайте: смени номер на <играч> на <число>"
        try:
            return update_player_number(identifier.strip(), new_number.strip())
        except (ValueError, RuntimeError) as e:
            return str(e)

    def handle_update_player_status(self, identifier=None, new_status=None):
        if not identifier or not new_status:
            return "Моля, използвайте: смени статус на <играч> на <статус>"
        try:
            return update_player_status(identifier.strip(), new_status.strip())
        except (ValueError, RuntimeError) as e:
            return str(e)

    def handle_delete_player(self, identifier=None):
        if not identifier:
            return "Моля, укажете име на играч. Пример: изтрий играч Иван Иванов"
        try:
            return delete_player(identifier.strip())
        except (ValueError, RuntimeError) as e:
            return str(e)
