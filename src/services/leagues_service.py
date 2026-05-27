import re
from src.repositories import leagues_repo as repo
from src.services.clubs_service import find_club_by_name


def _validate_season(season):
    if not re.match(r'^\d{4}/\d{4}$', season.strip()):
        raise ValueError(f"Невалиден формат на сезон '{season}'. Използвайте YYYY/YYYY (напр. 2025/2026).")
    years = season.strip().split('/')
    if int(years[1]) != int(years[0]) + 1:
        raise ValueError(f"Сезонът трябва да е две последователни години (напр. 2025/2026).")


def create_league(name, season):
    if not name or not name.strip():
        raise ValueError("Името на лигата не може да бъде празно.")
    name = name.strip()
    _validate_season(season)
    season = season.strip()

    existing = repo.get_league(name, season)
    if existing:
        raise ValueError(f"Лига '{name}' за сезон '{season}' вече съществува.")

    repo.create_league(name, season)
    return f"Лига '{name}' (сезон {season}) е създадена."


def get_all_leagues():
    rows = repo.get_all_leagues()
    if not rows:
        return "Няма добавени лиги."
    result = []
    for r in rows:
        cnt = repo.count_teams_in_league(r['id'])
        result.append(f"{r['id']}. {r['name']} — сезон {r['season']} ({cnt} отбора)")
    return "\n".join(result)


def add_team_to_league(club_name, league_name, season):
    club = find_club_by_name(club_name)
    league = repo.get_league(league_name.strip(), season.strip())
    if not league:
        raise ValueError(f"Лига '{league_name}' за сезон '{season}' не е намерена.")

    if repo.is_team_in_league(league['id'], club['id']):
        raise ValueError(f"Отбор '{club_name}' вече е добавен в лига '{league_name}' ({season}).")

    repo.add_team_to_league(league['id'], club['id'])
    return f"Отбор '{club_name}' е добавен в лига '{league_name}' ({season})."


def remove_team_from_league(club_name, league_name, season, force=False):
    club = find_club_by_name(club_name)
    league = repo.get_league(league_name.strip(), season.strip())
    if not league:
        raise ValueError(f"Лига '{league_name}' за сезон '{season}' не е намерена.")

    if not repo.is_team_in_league(league['id'], club['id']):
        raise ValueError(f"Отбор '{club_name}' не е в лига '{league_name}' ({season}).")

    if not force and repo.has_matches(league['id']):
        raise ValueError(
            f"Лига '{league_name}' има генерирана програма. "
            f"Използвайте 'прегенерирай програма {league_name} {season}' за да изтриете и създадете наново."
        )

    repo.remove_team_from_league(league['id'], club['id'])
    return f"Отбор '{club_name}' е премахнат от лига '{league_name}' ({season})."


def get_league_teams(league_name, season):
    league = repo.get_league(league_name.strip(), season.strip())
    if not league:
        raise ValueError(f"Лига '{league_name}' за сезон '{season}' не е намерена.")

    teams = repo.get_league_teams(league['id'])
    if not teams:
        return f"Няма отбори в лига '{league_name}' ({season})."

    result = [f"Отбори в {league_name} (сезон {season}):"]
    for t in teams:
        result.append(f"  {t['id']}. {t['name']}")
    return "\n".join(result)


def generate_schedule(league_name, season):
    league = repo.get_league(league_name.strip(), season.strip())
    if not league:
        raise ValueError(f"Лига '{league_name}' за сезон '{season}' не е намерена.")

    if repo.has_matches(league['id']):
        raise ValueError(
            f"Лига '{league_name}' вече има генерирана програма. "
            f"Използвайте 'прегенерирай програма {league_name} {season}'."
        )

    teams = repo.get_league_teams(league['id'])
    if len(teams) < 4:
        raise ValueError(
            f"Недостатъчно отбори за програма (има {len(teams)}, минимум 4)."
        )

    club_ids = [t['id'] for t in teams]
    n = len(club_ids)
    is_odd = n % 2 != 0

    if is_odd:
        fixed_n = n + 1
    else:
        fixed_n = n

    ids = list(club_ids)
    if is_odd:
        ids.append(None)

    rounds_count = fixed_n - 1
    matches_count = n * (n - 1) // 2

    fixed = ids[0]
    rotating = ids[1:]

    round_data = []
    for rn in range(1, rounds_count + 1):
        round_matches = []
        if rotating[0] is not None and fixed is not None:
            round_matches.append((fixed, rotating[0]))
        for i in range(1, fixed_n // 2):
            home = rotating[i]
            away = rotating[fixed_n - 1 - i]
            if home is not None and away is not None:
                round_matches.append((home, away))
        round_data.append(round_matches)
        rotating = [rotating[-1]] + rotating[:-1]

    for rn, matches in enumerate(round_data, 1):
        for home_id, away_id in matches:
            repo.insert_match(league['id'], rn, home_id, away_id)

    first_round = round_data[0] if round_data else []
    first_round_str = []
    for home_id, away_id in first_round:
        home_name = next(t['name'] for t in teams if t['id'] == home_id)
        away_name = next(t['name'] for t in teams if t['id'] == away_id)
        first_round_str.append(f"    {home_name} vs {away_name}")

    result = [
        f"Програмата е генерирана за '{league_name}' ({season}).",
        f"  Кръгове: {rounds_count}",
        f"  Мачове: {matches_count}",
        f"  Отбори: {n}" + (" (1 BYE/кръг)" if is_odd else ""),
        f"  Примерен 1-ви кръг:",
    ]
    result.extend(first_round_str)
    return "\n".join(result)


def regenerate_schedule(league_name, season):
    league = repo.get_league(league_name.strip(), season.strip())
    if not league:
        raise ValueError(f"Лига '{league_name}' за сезон '{season}' не е намерена.")

    repo.delete_matches_by_league(league['id'])
    return generate_schedule(league_name, season)


def get_league_matches(league_name, season):
    league = repo.get_league(league_name.strip(), season.strip())
    if not league:
        raise ValueError(f"Лига '{league_name}' за сезон '{season}' не е намерена.")

    matches = repo.get_matches_by_league(league['id'])
    if not matches:
        return f"Няма генерирани мачове за '{league_name}' ({season})."

    result = [f"Програма за {league_name} (сезон {season}):"]
    current_round = None
    for m in matches:
        if m['round_no'] != current_round:
            current_round = m['round_no']
            result.append(f"  Кръг {current_round}:")
        score = f"{m['home_goals'] or '?'}:{m['away_goals'] or '?'}"
        result.append(f"    {m['home_name']} vs {m['away_name']} ({score})")
    return "\n".join(result)
