from src.db import fetch_all


def get_played_matches(league_id):
    return fetch_all(
        "SELECT m.id, m.home_club_id, m.away_club_id, m.home_goals, m.away_goals, "
        "hc.name as home_name, ac.name as away_name "
        "FROM matches m "
        "JOIN clubs hc ON m.home_club_id = hc.id "
        "JOIN clubs ac ON m.away_club_id = ac.id "
        "WHERE m.league_id = ? AND m.status = 'played'",
        (league_id,)
    )
