from src.services.clubs_service import add_club, get_all_clubs, delete_club, update_club
from src.services.players_service import (
    add_player, get_players_by_club, get_all_players,
    update_player_number, update_player_status, delete_player
)
from src.services.transfers_service import (
    transfer_player, list_transfers_by_player, list_transfers_by_club
)


class Router:
    def route(self, intent, params):
        handler = getattr(self, f'handle_{intent}', None)
        if handler:
            try:
                return handler(*params)
            except (ValueError, RuntimeError) as e:
                return str(e)
        return "Не разпознах командата. Напишете 'помощ' за наличните команди."

    def handle_help(self):
        import json, os
        path = os.path.join(os.path.dirname(__file__), 'intents.json')
        with open(path, 'r', encoding='utf-8') as f:
            intents = json.load(f)['intents']
        for intent in intents:
            if intent['tag'] == 'help':
                return intent['responses'][0]
        return "Налични команди: помощ, добави клуб, списък клубове, изтрий клуб, промени клуб, изход."

    def handle_exit(self):
        return "EXIT"

    def handle_add_club(self, name=None):
        if not name:
            return "Моля, укажете име на клуб. Пример: добави клуб Левски София"
        return add_club(name)

    def handle_list_clubs(self):
        return get_all_clubs()

    def handle_delete_club(self, identifier=None):
        if not identifier:
            return "Моля, укажете име или ID на клуб за изтриване."
        return delete_club(identifier.strip())

    def handle_update_club(self, identifier=None, new_name=None):
        if not identifier or not new_name:
            return "Моля, укажете клуб и ново име. Пример: промени клуб Левски на ЦСКА"
        return update_club(identifier.strip(), new_name.strip())

    def handle_add_player(self, name=None, club_name=None, position=None, number=None):
        if not all([name, club_name, position, number]):
            return "Моля, използвайте: добави играч <име> в <клуб> позиция <GK|DF|MF|FW> номер <число>"
        return add_player(name, club_name, position, number)

    def handle_list_players(self, club_name=None):
        if not club_name:
            return "Моля, укажете клуб. Пример: покажи играчи на Левски"
        return get_players_by_club(club_name.strip())

    def handle_update_player_number(self, identifier=None, new_number=None):
        if not identifier or not new_number:
            return "Моля, използвайте: смени номер на <играч> на <число>"
        return update_player_number(identifier.strip(), new_number.strip())

    def handle_update_player_status(self, identifier=None, new_status=None):
        if not identifier or not new_status:
            return "Моля, използвайте: смени статус на <играч> на <статус>"
        return update_player_status(identifier.strip(), new_status.strip())

    def handle_delete_player(self, identifier=None):
        if not identifier:
            return "Моля, укажете име на играч. Пример: изтрий играч Иван Иванов"
        return delete_player(identifier.strip())

    def handle_transfer_player(self, player_name=None, from_club=None, to_club=None, date=None, fee=None):
        if not all([player_name, from_club, to_club, date]):
            return ("Моля, използвайте: трансфер <играч> от <клуб> в <клуб> YYYY-MM-DD [сума <число>]")
        return transfer_player(player_name, from_club, to_club, date, fee)

    def handle_show_transfers(self, name=None):
        if not name:
            return "Моля, укажете играч или клуб. Пример: покажи трансфери на Иван Петров"
        try:
            return list_transfers_by_player(name.strip())
        except ValueError:
            pass
        try:
            return list_transfers_by_club(name.strip())
        except ValueError:
            return f"Не е намерен играч или клуб с име '{name.strip()}'."
