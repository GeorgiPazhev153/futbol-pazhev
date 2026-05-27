import re
from src.database.db import fetch_all, with_transaction
from src.services.clubs_service import find_club_by_name
from src.services.players_service import find_player_by_name


def transfer_player(player_name, from_club, to_club, date, fee=None):
    if not player_name or not from_club or not to_club or not date:
        raise ValueError("Моля, използвайте: трансфер <играч> от <клуб> в <клуб> YYYY-MM-DD [сума <число>]")

    player = find_player_by_name(player_name)

    if not re.match(r'^\d{4}-\d{2}-\d{2}$', date.strip()):
        raise ValueError("Невалиден формат на дата. Използвайте YYYY-MM-DD.")

    from_club_lower = from_club.strip().lower()
    is_free_agent = from_club_lower in ('няма', 'свободен', 'без клуб', 'none', 'free')

    if from_club.strip().lower() == to_club.strip().lower():
        raise ValueError("Клубовете 'от' и 'към' трябва да са различни.")

    to_club_data = find_club_by_name(to_club)

    from_club_id = None
    from_club_name = "свободен агент"
    if not is_free_agent:
        from_data = find_club_by_name(from_club)
        from_club_id = from_data['id']
        from_club_name = from_data['name']

        if player['club_id'] is None:
            raise ValueError(
                f"Играч '{player_name}' няма клуб (свободен агент). "
                f"Използвайте: трансфер {player_name} от свободен в {to_club} {date}"
            )
        if player['club_id'] != from_club_id:
            current_club = "без клуб" if player['club_id'] is None else \
                fetch_all("SELECT name FROM clubs WHERE id = ?", (player['club_id'],))
            current_name = current_club[0]['name'] if current_club else "без клуб"
            raise ValueError(
                f"Играч '{player_name}' не играе в '{from_club}'. Текущ клуб: {current_name}."
            )
    else:
        if player['club_id'] is not None:
            current_club = fetch_all("SELECT name FROM clubs WHERE id = ?", (player['club_id'],))
            current_name = current_club[0]['name'] if current_club else "неизвестен"
            raise ValueError(
                f"Играч '{player_name}' не е свободен агент. Текущ клуб: {current_name}. "
                f"Посочете правилния клуб."
            )

    parsed_fee = None
    if fee is not None:
        try:
            parsed_fee = float(fee)
        except (ValueError, TypeError):
            raise ValueError(f"Невалидна сума '{fee}'. Трябва да е число >= 0.")
        if parsed_fee < 0:
            raise ValueError(f"Сумата не може да бъде отрицателна.")

    def _execute(conn):
        conn.execute(
            "INSERT INTO transfers (player_id, from_club_id, to_club_id, transfer_date, fee) "
            "VALUES (?, ?, ?, ?, ?)",
            (player['id'], from_club_id, to_club_data['id'], date.strip(), parsed_fee)
        )
        conn.execute(
            "UPDATE players SET club_id = ? WHERE id = ?",
            (to_club_data['id'], player['id'])
        )

    with_transaction(_execute)

    parts = [
        f"✓ Трансфер завършен: {player['full_name']}",
        f"  От: {from_club_name}",
        f"  Към: {to_club_data['name']}",
        f"  Дата: {date.strip()}",
    ]
    if parsed_fee is not None:
        parts.append(f"  Сума: {parsed_fee:.2f}")
    return "\n".join(parts)


def list_transfers_by_player(player_name):
    player = find_player_by_name(player_name)
    rows = fetch_all(
        "SELECT t.id, t.transfer_date, t.fee, t.note, "
        "COALESCE(fc.name, 'Свободен агент') as from_name, "
        "tc.name as to_name "
        "FROM transfers t "
        "LEFT JOIN clubs fc ON t.from_club_id = fc.id "
        "JOIN clubs tc ON t.to_club_id = tc.id "
        "WHERE t.player_id = ? "
        "ORDER BY t.transfer_date DESC",
        (player['id'],)
    )
    if not rows:
        return f"Няма трансфери за '{player_name}'."
    result = [f"Трансфери на {player_name}:"]
    for r in rows:
        fee_part = f", сума {r['fee']:.2f}" if r['fee'] is not None else ""
        note_part = f" — {r['note']}" if r['note'] else ""
        result.append(f"  {r['transfer_date']}: {r['from_name']} → {r['to_name']}{fee_part}{note_part}")
    return "\n".join(result)


def list_transfers_by_club(club_name):
    club = find_club_by_name(club_name)
    rows = fetch_all(
        "SELECT t.id, t.transfer_date, t.fee, p.full_name, "
        "COALESCE(fc.name, 'Свободен агент') as from_name, "
        "tc.name as to_name "
        "FROM transfers t "
        "JOIN players p ON t.player_id = p.id "
        "LEFT JOIN clubs fc ON t.from_club_id = fc.id "
        "JOIN clubs tc ON t.to_club_id = tc.id "
        "WHERE t.from_club_id = ? OR t.to_club_id = ? "
        "ORDER BY t.transfer_date DESC",
        (club['id'], club['id'])
    )
    if not rows:
        return f"Няма трансфери свързани с '{club_name}'."
    result = [f"Трансфери с {club_name}:"]
    for r in rows:
        fee_part = f", сума {r['fee']:.2f}" if r['fee'] is not None else ""
        direction = f"{r['from_name']} → {r['to_name']}"
        result.append(f"  {r['transfer_date']}: {r['full_name']} — {direction}{fee_part}")
    return "\n".join(result)
