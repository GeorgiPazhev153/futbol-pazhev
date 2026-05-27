import re
from src.database.db import execute_query, fetch_all

VALID_POSITIONS = {'GK', 'DF', 'MF', 'FW'}


def find_player_by_name(name):
    rows = fetch_all("SELECT * FROM players WHERE full_name = ?", (name.strip(),))
    if not rows:
        raise ValueError(f"Играч '{name}' не е намерен.")
    return dict(rows[0])


def _find_club_id(club_name):
    rows = fetch_all("SELECT id FROM clubs WHERE name = ?", (club_name.strip(),))
    if not rows:
        raise ValueError(f"Клуб '{club_name}' не е намерен.")
    return rows[0]['id']


def _find_player(identifier):
    if identifier.isdigit():
        rows = fetch_all("SELECT * FROM players WHERE id = ?", (int(identifier),))
    else:
        rows = fetch_all("SELECT * FROM players WHERE full_name = ?", (identifier.strip(),))
    if not rows:
        raise ValueError(f"Играч '{identifier}' не е намерен.")
    return rows[0]


def add_player(full_name, club_name, position, number, birth_date=None, nationality=None):
    if not full_name or not full_name.strip():
        raise ValueError("Името на играча не може да бъде празно.")
    full_name = full_name.strip()
    pos = position.upper().strip()
    if pos not in VALID_POSITIONS:
        raise ValueError(f"Невалидна позиция '{position}'. Позволени: {', '.join(sorted(VALID_POSITIONS))}")
    try:
        num = int(number)
    except (ValueError, TypeError):
        raise ValueError(f"Невалиден номер '{number}'. Трябва да е число между 1 и 99.")
    if num < 1 or num > 99:
        raise ValueError(f"Номерът трябва да е между 1 и 99, получен: {num}.")
    if birth_date:
        if not re.match(r'^\d{4}-\d{2}-\d{2}$', birth_date.strip()):
            raise ValueError("Невалиден формат на дата. Използвайте YYYY-MM-DD.")
    club_id = _find_club_id(club_name)
    execute_query(
        "INSERT INTO players (full_name, birth_date, nationality, position, number, club_id) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        (full_name, birth_date.strip() if birth_date else None,
         nationality.strip() if nationality else 'Неизвестна', pos, num, club_id)
    )
    return f"Играч '{full_name}' е добавен в клуб '{club_name}' с номер {num}."


def get_players_by_club(club_name):
    club_id = _find_club_id(club_name)
    rows = fetch_all(
        "SELECT p.id, p.full_name, p.birth_date, p.nationality, p.position, p.number, p.status, c.name as club_name "
        "FROM players p JOIN clubs c ON p.club_id = c.id WHERE p.club_id = ? ORDER BY p.number",
        (club_id,)
    )
    if not rows:
        return f"Няма играчи в клуб '{club_name}'."
    result = [f"Играчи на {club_name}:"]
    for r in rows:
        line = f"  {r['number']:2d}. {r['full_name']} ({r['position']}) — {r['status']}"
        if r['birth_date']:
            line += f", р. {r['birth_date']}"
        result.append(line)
    return "\n".join(result)


def get_all_players():
    rows = fetch_all(
        "SELECT p.id, p.full_name, p.birth_date, p.nationality, p.position, p.number, p.status, "
        "COALESCE(c.name, 'Без клуб') as club_name "
        "FROM players p LEFT JOIN clubs c ON p.club_id = c.id ORDER BY c.name, p.number"
    )
    if not rows:
        return "Няма добавени играчи."
    result = []
    for r in rows:
        result.append(
            f"{r['id']}. {r['full_name']} | {r['club_name']} | №{r['number']} | {r['position']} | {r['status']}"
        )
    return "\n".join(result)


def update_player_number(identifier, new_number):
    try:
        new_num = int(new_number)
    except (ValueError, TypeError):
        raise ValueError(f"Невалиден номер '{new_number}'.")
    if new_num < 1 or new_num > 99:
        raise ValueError(f"Номерът трябва да е между 1 и 99.")
    player = _find_player(identifier)
    execute_query("UPDATE players SET number = ? WHERE id = ?", (new_num, player['id']))
    return f"Номерът на '{player['full_name']}' е сменен на {new_num}."


def update_player_status(identifier, new_status):
    if not new_status or not new_status.strip():
        raise ValueError("Статусът не може да бъде празен.")
    player = _find_player(identifier)
    execute_query("UPDATE players SET status = ? WHERE id = ?", (new_status.strip(), player['id']))
    return f"Статусът на '{player['full_name']}' е сменен на '{new_status.strip()}'."


def update_player_position(identifier, new_position):
    pos = new_position.upper().strip()
    if pos not in VALID_POSITIONS:
        raise ValueError(f"Невалидна позиция '{new_position}'. Позволени: {', '.join(sorted(VALID_POSITIONS))}")
    player = _find_player(identifier)
    execute_query("UPDATE players SET position = ? WHERE id = ?", (pos, player['id']))
    return f"Позицията на '{player['full_name']}' е сменена на '{pos}'."


def delete_player(identifier):
    player = _find_player(identifier)
    execute_query("DELETE FROM players WHERE id = ?", (player['id'],))
    return f"Играч '{player['full_name']}' е изтрит."
