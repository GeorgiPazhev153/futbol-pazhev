from src.db import execute_query, fetch_all


def create_league(name, season):
    execute_query(
        "INSERT INTO leagues (name, season) VALUES (?, ?)",
        (name, season)
    )


def get_league(name, season):
    rows = fetch_all(
        "SELECT * FROM leagues WHERE name = ? AND season = ?",
        (name, season)
    )
    return dict(rows[0]) if rows else None


def get_all_leagues():
    return fetch_all("SELECT * FROM leagues ORDER BY name")


def add_team_to_league(league_id, club_id):
    execute_query(
        "INSERT INTO league_teams (league_id, club_id) VALUES (?, ?)",
        (league_id, club_id)
    )


def remove_team_from_league(league_id, club_id):
    execute_query(
        "DELETE FROM league_teams WHERE league_id = ? AND club_id = ?",
        (league_id, club_id)
    )


def is_team_in_league(league_id, club_id):
    rows = fetch_all(
        "SELECT 1 FROM league_teams WHERE league_id = ? AND club_id = ?",
        (league_id, club_id)
    )
    return len(rows) > 0


def get_league_teams(league_id):
    return fetch_all(
        "SELECT c.id, c.name, lt.joined_at "
        "FROM league_teams lt JOIN clubs c ON lt.club_id = c.id "
        "WHERE lt.league_id = ? ORDER BY c.name",
        (league_id,)
    )


def count_teams_in_league(league_id):
    rows = fetch_all(
        "SELECT COUNT(*) as cnt FROM league_teams WHERE league_id = ?",
        (league_id,)
    )
    return rows[0]['cnt']


def has_matches(league_id):
    rows = fetch_all(
        "SELECT 1 FROM matches WHERE league_id = ? LIMIT 1",
        (league_id,)
    )
    return len(rows) > 0


def delete_matches_by_league(league_id):
    execute_query("DELETE FROM matches WHERE league_id = ?", (league_id,))


def insert_match(league_id, round_no, home_club_id, away_club_id):
    execute_query(
        "INSERT INTO matches (league_id, round_no, home_club_id, away_club_id) VALUES (?, ?, ?, ?)",
        (league_id, round_no, home_club_id, away_club_id)
    )


def get_matches_by_league(league_id):
    return fetch_all(
        "SELECT m.id, m.round_no, m.match_date, m.home_goals, m.away_goals, "
        "hc.name as home_name, ac.name as away_name "
        "FROM matches m "
        "JOIN clubs hc ON m.home_club_id = hc.id "
        "JOIN clubs ac ON m.away_club_id = ac.id "
        "WHERE m.league_id = ? ORDER BY m.round_no, m.id",
        (league_id,)
    )
