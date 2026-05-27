from src.db import execute_query, fetch_all

try:
    execute_query("ALTER TABLE matches ADD COLUMN status TEXT DEFAULT 'scheduled'")
except RuntimeError:
    pass


def get_match(match_id):
    rows = fetch_all(
        "SELECT m.*, hc.name as home_name, ac.name as away_name, l.name as league_name, l.season "
        "FROM matches m "
        "JOIN clubs hc ON m.home_club_id = hc.id "
        "JOIN clubs ac ON m.away_club_id = ac.id "
        "JOIN leagues l ON m.league_id = l.id "
        "WHERE m.id = ?",
        (match_id,)
    )
    return dict(rows[0]) if rows else None


def get_round_matches(league_id, round_no):
    return fetch_all(
        "SELECT m.id, m.round_no, m.match_date, m.home_goals, m.away_goals, m.status, "
        "hc.name as home_name, ac.name as away_name "
        "FROM matches m "
        "JOIN clubs hc ON m.home_club_id = hc.id "
        "JOIN clubs ac ON m.away_club_id = ac.id "
        "WHERE m.league_id = ? AND m.round_no = ? "
        "ORDER BY m.id",
        (league_id, round_no)
    )


def find_match_by_clubs(league_id, home_club_name, away_club_name):
    rows = fetch_all(
        "SELECT m.id, m.league_id, m.round_no, m.match_date, m.home_goals, m.away_goals, m.status, "
        "hc.name as home_name, ac.name as away_name "
        "FROM matches m "
        "JOIN clubs hc ON m.home_club_id = hc.id "
        "JOIN clubs ac ON m.away_club_id = ac.id "
        "WHERE m.league_id = ? AND hc.name = ? AND ac.name = ?",
        (league_id, home_club_name, away_club_name)
    )
    return dict(rows[0]) if rows else None


def find_match_by_league_and_id(league_id, match_id):
    rows = fetch_all(
        "SELECT * FROM matches WHERE id = ? AND league_id = ?",
        (match_id, league_id)
    )
    return dict(rows[0]) if rows else None


def update_score(match_id, home_goals, away_goals):
    execute_query(
        "UPDATE matches SET home_goals = ?, away_goals = ?, status = 'played' WHERE id = ?",
        (home_goals, away_goals, match_id)
    )


def add_goal(match_id, player_id, club_id, minute):
    execute_query(
        "INSERT INTO goals (match_id, player_id, club_id, minute) VALUES (?, ?, ?, ?)",
        (match_id, player_id, club_id, minute)
    )


def add_card(match_id, player_id, club_id, minute, card_type):
    execute_query(
        "INSERT INTO cards (match_id, player_id, club_id, minute, card_type) VALUES (?, ?, ?, ?, ?)",
        (match_id, player_id, club_id, minute, card_type)
    )


def get_goals(match_id):
    return fetch_all(
        "SELECT g.id, g.match_id, g.player_id, g.club_id, g.minute, g.is_own_goal, "
        "p.full_name as player_name, c.name as club_name "
        "FROM goals g "
        "JOIN players p ON g.player_id = p.id "
        "JOIN clubs c ON g.club_id = c.id "
        "WHERE g.match_id = ? ORDER BY g.minute",
        (match_id,)
    )


def get_cards(match_id):
    return fetch_all(
        "SELECT c.id, c.match_id, c.player_id, c.club_id, c.minute, c.card_type, "
        "p.full_name as player_name, cl.name as club_name "
        "FROM cards c "
        "JOIN players p ON c.player_id = p.id "
        "JOIN clubs cl ON c.club_id = cl.id "
        "WHERE c.match_id = ? ORDER BY c.minute",
        (match_id,)
    )
