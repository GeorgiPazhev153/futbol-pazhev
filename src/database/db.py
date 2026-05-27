import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'football.db')


def get_connection():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def execute_query(sql, params=None):
    try:
        conn = get_connection()
        cur = conn.cursor()
        if params:
            cur.execute(sql, params)
        else:
            cur.execute(sql)
        conn.commit()
        return cur
    except sqlite3.Error as e:
        raise RuntimeError(f"Грешка в базата данни: {e}")
    finally:
        conn.close()


def fetch_all(sql, params=None):
    try:
        conn = get_connection()
        cur = conn.cursor()
        if params:
            cur.execute(sql, params)
        else:
            cur.execute(sql)
        return cur.fetchall()
    except sqlite3.Error as e:
        raise RuntimeError(f"Грешка в базата данни: {e}")
    finally:
        conn.close()


def with_transaction(callback):
    conn = get_connection()
    try:
        conn.execute("BEGIN")
        result = callback(conn)
        conn.commit()
        return result
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db():
    schema_path = os.path.join(os.path.dirname(__file__), '..', '..', 'sql', 'schema.sql')
    with open(schema_path, 'r', encoding='utf-8') as f:
        sql = f.read()
    conn = get_connection()
    try:
        conn.executescript(sql)
        conn.commit()
    except sqlite3.Error as e:
        raise RuntimeError(f"Грешка при инициализация на БД: {e}")
    finally:
        conn.close()
