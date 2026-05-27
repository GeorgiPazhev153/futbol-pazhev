from src.db import execute_query, fetch_all


def add_club(name):
    if not name or not name.strip():
        raise ValueError("Името на клуба не може да бъде празно.")
    name = name.strip()
    existing = fetch_all("SELECT id FROM clubs WHERE name = ?", (name,))
    if existing:
        raise ValueError(f"Клуб '{name}' вече съществува.")
    execute_query("INSERT INTO clubs (name) VALUES (?)", (name,))
    return f"Клуб '{name}' е добавен успешно."


def get_all_clubs():
    rows = fetch_all("SELECT id, name, created_at FROM clubs ORDER BY id")
    if not rows:
        return "Няма добавени клубове."
    result = []
    for r in rows:
        result.append(f"{r['id']}. {r['name']} (създаден на {r['created_at']})")
    return "\n".join(result)


def delete_club(identifier):
    if not identifier:
        raise ValueError("Моля, въведете име или ID на клуб за изтриване.")

    if identifier.isdigit():
        row = fetch_all("SELECT id, name FROM clubs WHERE id = ?", (int(identifier),))
        if not row:
            raise ValueError(f"Клуб с ID '{identifier}' не е намерен.")
        execute_query("DELETE FROM clubs WHERE id = ?", (int(identifier),))
        return f"Клуб '{row[0]['name']}' (ID: {identifier}) е изтрит."
    else:
        row = fetch_all("SELECT id, name FROM clubs WHERE name = ?", (identifier.strip(),))
        if not row:
            raise ValueError(f"Клуб '{identifier}' не е намерен.")
        execute_query("DELETE FROM clubs WHERE name = ?", (identifier.strip(),))
        return f"Клуб '{identifier}' е изтрит."


def update_club(identifier, new_name):
    if not new_name or not new_name.strip():
        raise ValueError("Новото име не може да бъде празно.")
    new_name = new_name.strip()

    duplicate = fetch_all("SELECT id FROM clubs WHERE name = ?", (new_name,))
    if duplicate:
        raise ValueError(f"Клуб '{new_name}' вече съществува.")

    if identifier.isdigit():
        row = fetch_all("SELECT id, name FROM clubs WHERE id = ?", (int(identifier),))
        if not row:
            raise ValueError(f"Клуб с ID '{identifier}' не е намерен.")
        execute_query("UPDATE clubs SET name = ? WHERE id = ?", (new_name, int(identifier)))
        return f"Клуб ID {identifier} е преименуван на '{new_name}'."
    else:
        row = fetch_all("SELECT id FROM clubs WHERE name = ?", (identifier.strip(),))
        if not row:
            raise ValueError(f"Клуб '{identifier}' не е намерен.")
        execute_query("UPDATE clubs SET name = ? WHERE name = ?", (new_name, identifier.strip()))
        return f"Клуб '{identifier}' е преименуван на '{new_name}'."
