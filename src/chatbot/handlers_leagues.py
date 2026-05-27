from src.services.leagues_service import (
    create_league, get_all_leagues, add_team_to_league, remove_team_from_league,
    get_league_teams, generate_schedule, regenerate_schedule, get_league_matches
)


def handle_create_league(name, season):
    if not name or not season:
        return "Моля, използвайте: създай лига <име> <сезон> (напр. създай лига Първа лига 2025/2026)"
    return create_league(name, season)


def handle_list_leagues():
    return get_all_leagues()


def handle_add_team_to_league(club_name, league_name, season):
    if not all([club_name, league_name, season]):
        return "Моля, използвайте: добави отбор <клуб> в лига <име> <сезон>"
    return add_team_to_league(club_name, league_name, season)


def handle_remove_team_from_league(club_name, league_name, season):
    if not all([club_name, league_name, season]):
        return "Моля, използвайте: премахни отбор <клуб> от лига <име> <сезон>"
    try:
        return remove_team_from_league(club_name, league_name, season)
    except ValueError as e:
        return str(e)


def handle_show_league_teams(league_name, season):
    if not league_name or not season:
        return "Моля, използвайте: покажи отбори в лига <име> <сезон>"
    return get_league_teams(league_name, season)


def handle_generate_schedule(league_name, season):
    if not league_name or not season:
        return "Моля, използвайте: генерирай програма <име> <сезон>"
    return generate_schedule(league_name, season)


def handle_regenerate_schedule(league_name, season):
    if not league_name or not season:
        return "Моля, използвайте: прегенерирай програма <име> <сезон>"
    return regenerate_schedule(league_name, season)


def handle_show_schedule(league_name, season):
    if not league_name or not season:
        return "Моля, използвайте: покажи програма <име> <сезон>"
    return get_league_matches(league_name, season)
