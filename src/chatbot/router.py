from src.chatbot.intents import INTENTS
from src.services.clubs_service import add_club, get_all_clubs, delete_club, update_club
from src.services.players_service import (
    add_player, get_players_by_club, get_all_players,
    update_player_number, update_player_status, delete_player
)
from src.services.transfers_service import (
    transfer_player, list_transfers_by_player, list_transfers_by_club
)
from src.chatbot.handlers_leagues import (
    handle_create_league, handle_list_leagues,
    handle_add_team_to_league, handle_remove_team_from_league,
    handle_show_league_teams, handle_generate_schedule,
    handle_regenerate_schedule, handle_show_schedule
)
from src.chatbot.handlers_matches import (
    handle_select_league as _handle_select_league,
    handle_show_round as _handle_show_round,
    handle_select_match as _handle_select_match,
    handle_record_score as _handle_record_score,
    handle_record_score_by_clubs as _handle_record_score_by_clubs,
    handle_add_goal as _handle_add_goal,
    handle_add_card as _handle_add_card,
    handle_show_events as _handle_show_events,
)
from src.chatbot.handlers_standings import handle_show_standings as _handle_show_standings


class Router:
    def __init__(self):
        self.current_league_name = None
        self.current_season = None
        self.current_match_id = None

    def route(self, intent, params):
        handler = getattr(self, f'handle_{intent}', None)
        if handler:
            try:
                return handler(*params)
            except (ValueError, RuntimeError) as e:
                return str(e)
        return "Не разпознах командата. Напишете 'помощ' за наличните команди."

    def handle_help(self):
        for intent in INTENTS:
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
            return "Моля, използвайте: трансфер <играч> от <клуб> в <клуб> YYYY-MM-DD [сума <число>]"
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

    # --- League handlers ---

    def handle_create_league(self, name=None, season=None):
        return handle_create_league(name, season)

    def handle_list_leagues(self):
        return handle_list_leagues()

    def handle_add_team_to_league(self, club_name=None, league_name=None, season=None):
        return handle_add_team_to_league(club_name, league_name, season)

    def handle_remove_team_from_league(self, club_name=None, league_name=None, season=None):
        return handle_remove_team_from_league(club_name, league_name, season)

    def handle_show_league_teams(self, league_name=None, season=None):
        return handle_show_league_teams(league_name, season)

    def handle_generate_schedule(self, league_name=None, season=None):
        return handle_generate_schedule(league_name, season)

    def handle_regenerate_schedule(self, league_name=None, season=None):
        return handle_regenerate_schedule(league_name, season)

    def handle_show_schedule(self, league_name=None, season=None):
        return handle_show_schedule(league_name, season)

    # --- Match handlers ---

    def handle_select_league(self, league_name=None, season=None):
        if not league_name or not season:
            return "Моля, използвайте: избери лига <име> <сезон> (напр. избери лига Първа лига 2025/2026)"
        try:
            result = _handle_select_league(league_name, season)
            self.current_league_name = league_name
            self.current_season = season
            return result
        except ValueError as e:
            return str(e)

    def handle_show_round(self, round_no=None, league_name=None, season=None):
        if not round_no:
            return "Моля, използвайте: покажи кръг <N> [<лига> <сезон>]"
        if league_name and season:
            return _handle_show_round(league_name, season, round_no)
        if self.current_league_name and self.current_season:
            return _handle_show_round(self.current_league_name, self.current_season, round_no)
        return "Няма избрана лига. Използвайте 'Избери лига <име> <сезон>' или 'Покажи кръг <N> <лига> <сезон>'"

    def handle_select_match(self, match_id=None):
        if not match_id:
            return "Моля, използвайте: избери мач <ID>"
        result = _handle_select_match(match_id)
        if "Избран мач" in result:
            self.current_match_id = int(match_id)
        return result

    def handle_record_score(self, home_goals=None, away_goals=None):
        return _handle_record_score(home_goals, away_goals, self.current_match_id)

    def handle_record_score_by_clubs(self, home_club=None, away_club=None,
                                     home_goals=None, away_goals=None):
        return _handle_record_score_by_clubs(
            home_club, away_club, home_goals, away_goals,
            self.current_league_name, self.current_season
        )

    def handle_add_goal(self, player_name=None, club_name=None, minute=None):
        return _handle_add_goal(player_name, club_name, minute, self.current_match_id)

    def handle_add_card(self, player_name=None, club_name=None, card_type=None, minute=None):
        return _handle_add_card(player_name, club_name, card_type, minute, self.current_match_id)

    def handle_show_events(self, match_id=None):
        return _handle_show_events(match_id, self.current_match_id)

    # --- Standings handler ---

    def handle_show_standings(self, league_name=None, season=None):
        return _handle_show_standings(league_name, season)
