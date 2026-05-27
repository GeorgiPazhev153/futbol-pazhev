"""
Тестови данни за Етап 4 — Трансфери.

Пуска се с: python seed_data.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.database.db import init_db, execute_query, fetch_all, with_transaction


def seed():
    init_db()

    # Clean existing data
    execute_query("DELETE FROM transfers")
    execute_query("DELETE FROM players")
    execute_query("DELETE FROM clubs")

    # --- 4 клуба ---
    clubs = ['Левски', 'ЦСКА', 'Лудогорец', 'Ботев Пловдив']
    for c in clubs:
        execute_query("INSERT INTO clubs (name) VALUES (?)", (c,))

    def club_id(name):
        return fetch_all("SELECT id FROM clubs WHERE name = ?", (name,))[0]['id']

    levski_id = club_id('Левски')
    cska_id = club_id('ЦСКА')
    ludogorec_id = club_id('Лудогорец')
    botev_id = club_id('Ботев Пловдив')

    # --- 6 играчи ---
    players_data = [
        ('Стилиян Петров', '1979-07-05', 'България', 'MF', 10, levski_id),
        ('Георги Иванов', '1976-07-02', 'България', 'FW', 9, levski_id),
        ('Христо Стоичков', '1966-02-08', 'България', 'FW', 8, cska_id),
        ('Димитър Бербатов', '1981-01-30', 'България', 'FW', 9, ludogorec_id),
        ('Ивет Горанова', '2000-03-06', 'България', 'DF', 3, None),
        ('Мартин Петров', '1979-01-15', 'България', 'MF', 17, botev_id),
    ]
    for p in players_data:
        execute_query(
            "INSERT INTO players (full_name, birth_date, nationality, position, number, club_id) "
            "VALUES (?, ?, ?, ?, ?, ?)", p
        )

    # Get player IDs
    def player_id(name):
        return fetch_all("SELECT id FROM players WHERE full_name = ?", (name,))[0]['id']

    stilqn_id = player_id('Стилиян Петров')
    georgi_id = player_id('Георги Иванов')
    hristo_id = player_id('Христо Стоичков')
    dimitar_id = player_id('Димитър Бербатов')
    martin_id = player_id('Мартин Петров')

    # --- 5 трансфера ---
    transfers_data = [
        (stilqn_id, None, levski_id, '2020-01-15', None, 'Първи клуб'),
        (georgi_id, None, levski_id, '2021-06-01', None, 'Първи клуб'),
        (hristo_id, cska_id, ludogorec_id, '2023-07-01', 500000, 'Директен трансфер'),
        (dimitar_id, ludogorec_id, cska_id, '2024-01-10', 200000, 'Зимен трансфер'),
        (martin_id, botev_id, levski_id, '2025-08-15', 150000, 'Трансфер'),
    ]
    for t in transfers_data:
        execute_query(
            "INSERT INTO transfers (player_id, from_club_id, to_club_id, transfer_date, fee, note) "
            "VALUES (?, ?, ?, ?, ?, ?)", t
        )

    # Update player clubs to match last transfer
    execute_query("UPDATE players SET club_id = ? WHERE id = ?", (ludogorec_id, hristo_id))
    execute_query("UPDATE players SET club_id = ? WHERE id = ?", (cska_id, dimitar_id))
    execute_query("UPDATE players SET club_id = ? WHERE id = ?", (levski_id, martin_id))

    sys.stdout.reconfigure(encoding='utf-8')
    print("OK - Тестовите данни са заредени успешно.")
    print(f"  Клубове: {len(clubs)}")
    print(f"  Играчи: {len(players_data)}")
    print(f"  Трансфери: {len(transfers_data)}")


if __name__ == '__main__':
    seed()
