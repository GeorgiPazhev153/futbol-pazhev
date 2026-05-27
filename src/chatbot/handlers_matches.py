from src.services.matches_service import (
    show_round, select_match, record_score, record_score_by_clubs,
    add_goal, add_card, show_events
)
from src.services.leagues_service import get_all_leagues


def handle_select_league(league_name, season):
    from src.repositories import leagues_repo
    league = leagues_repo.get_league(league_name.strip(), season.strip())
    if not league:
        raise ValueError(f"Лига '{league_name}' за сезон '{season}' не е намерена. "
                         f"Първо я създайте с 'създай лига {league_name} {season}'.")
    return f"Избрана лига: {league_name} (сезон {season})"


def handle_show_round(league_name, season, round_no):
    return show_round(league_name, season, round_no)


def handle_select_match(match_id):
    match = select_match(match_id)
    score = f"{match['home_goals'] or '?'}:{match['away_goals'] or '?'}"
    return (f"Избран мач #{match_id}: {match['home_name']} vs {match['away_name']} ({score}) "
            f"— кръг {match['round_no']}, {match.get('status', 'scheduled')}")


def handle_record_score(home_goals, away_goals, current_match_id):
    if current_match_id is None:
        return "Няма избран мач. Първо използвайте 'Избери мач <ID>'."
    return record_score(current_match_id, home_goals, away_goals)


def handle_record_score_by_clubs(home_club, away_club, home_goals, away_goals,
                                 current_league_name, current_season):
    if not current_league_name or not current_season:
        return ("Няма избрана лига. Първо използвайте 'Избери лига <име> <сезон>' "
                "или задайте кръг/лига в командата.")
    return record_score_by_clubs(current_league_name, current_season,
                                 home_club, away_club, home_goals, away_goals)


def handle_add_goal(player_name, club_name, minute, current_match_id):
    if current_match_id is None:
        return "Няма избран мач. Първо използвайте 'Избери мач <ID>'."
    return add_goal(current_match_id, player_name, club_name, minute)


def handle_add_card(player_name, club_name, card_type, minute, current_match_id):
    if current_match_id is None:
        return "Няма избран мач. Първо използвайте 'Избери мач <ID>'."
    return add_card(current_match_id, player_name, club_name, card_type, minute)


def handle_show_events(match_id, current_match_id):
    mid = match_id or current_match_id
    if mid is None:
        return "Няма избран мач. Използвайте 'Избери мач <ID>' или 'Покажи събития <ID>'."
    return show_events(mid)
