from src.repositories import matches_repo as repo
from src.repositories import leagues_repo
from src.services.players_service import find_player_by_name
from src.services.clubs_service import find_club_by_name


def show_round(league_name, season, round_no):
    league = leagues_repo.get_league(league_name.strip(), season.strip())
    if not league:
        raise ValueError(f"Лига '{league_name}' за сезон '{season}' не е намерена.")
    try:
        rn = int(round_no)
    except (ValueError, TypeError):
        raise ValueError(f"Невалиден номер на кръг: '{round_no}'.")
    if rn < 1:
        raise ValueError(f"Номерът на кръг трябва да е положително число.")
    matches = repo.get_round_matches(league['id'], rn)
    if not matches:
        return f"Няма мачове за кръг {rn} в '{league_name}' ({season})."
    result = [f"Кръг {rn} — {league_name} (сезон {season}):"]
    for m in matches:
        status = m['status'] or 'scheduled'
        score = f"{m['home_goals'] or '?'}:{m['away_goals'] or '?'}"
        result.append(f"  [ID {m['id']}] {m['home_name']} vs {m['away_name']} ({score}) — {status}")
    return "\n".join(result)


def get_league_rounds(league_name, season):
    league = leagues_repo.get_league(league_name.strip(), season.strip())
    if not league:
        raise ValueError(f"Лига '{league_name}' за сезон '{season}' не е намерена.")
    return league


def select_match(match_id):
    try:
        mid = int(match_id)
    except (ValueError, TypeError):
        raise ValueError(f"Невалидно ID на мач: '{match_id}'.")
    match = repo.get_match(mid)
    if not match:
        raise ValueError(f"Мач с ID '{match_id}' не е намерен.")
    return match


def record_score(match_id, home_goals, away_goals):
    match = select_match(match_id)
    try:
        hg = int(home_goals)
        ag = int(away_goals)
    except (ValueError, TypeError):
        raise ValueError(f"Резултатът трябва да са цели числа >= 0.")
    if hg < 0 or ag < 0:
        raise ValueError(f"Резултатът не може да бъде отрицателен.")
    if match.get('status') == 'played':
        raise ValueError(
            f"Мач #{match_id} ({match['home_name']} vs {match['away_name']}) "
            f"вече е изигран с резултат {match['home_goals']}:{match['away_goals']}."
        )
    repo.update_score(match_id, hg, ag)
    return f"Записано: {match['home_name']}–{match['away_name']} {hg}:{ag} (мач #{match_id})"


def record_score_by_clubs(league_name, season, home_club, away_club, home_goals, away_goals):
    league = leagues_repo.get_league(league_name.strip(), season.strip())
    if not league:
        raise ValueError(f"Лига '{league_name}' за сезон '{season}' не е намерена.")
    match = repo.find_match_by_clubs(league['id'], home_club.strip(), away_club.strip())
    if not match:
        match = repo.find_match_by_clubs(league['id'], away_club.strip(), home_club.strip())
        if match:
            raise ValueError(
                f"Мачът между тези отбори е {match['home_name']} vs {match['away_name']}. "
                f"Използвайте правилния ред: домакин-гост."
            )
        raise ValueError(
            f"Няма мач '{home_club} vs {away_club}' в '{league_name}' ({season})."
        )
    try:
        hg = int(home_goals)
        ag = int(away_goals)
    except (ValueError, TypeError):
        raise ValueError(f"Резултатът трябва да са цели числа >= 0.")
    if hg < 0 or ag < 0:
        raise ValueError(f"Резултатът не може да бъде отрицателен.")
    if match.get('status') == 'played':
        raise ValueError(
            f"Мач #{match['id']} ({home_club} vs {away_club}) "
            f"вече е изигран с резултат {match['home_goals']}:{match['away_goals']}."
        )
    repo.update_score(match['id'], hg, ag)
    return f"Записано: {home_club}–{away_club} {hg}:{ag} (мач #{match['id']})"


def add_goal(match_id, player_name, club_name, minute):
    match = select_match(match_id)
    try:
        mn = int(minute)
    except (ValueError, TypeError):
        raise ValueError(f"Минутата трябва да е цяло число между 1 и 120.")
    if mn < 1 or mn > 120:
        raise ValueError(f"Минутата трябва да е между 1 и 120, получена: {mn}.")
    club = find_club_by_name(club_name)
    if club['id'] not in (match['home_club_id'], match['away_club_id']):
        raise ValueError(f"Отбор '{club_name}' не участва в мач #{match_id}.")
    try:
        player = find_player_by_name(player_name)
    except ValueError:
        raise ValueError(f"Играч '{player_name}' не е намерен.")
    if player['club_id'] != club['id']:
        raise ValueError(
            f"Играч '{player_name}' не играе за '{club_name}'. "
            f"Той е в клуб ID {player['club_id'] or 'без клуб'}."
        )
    repo.add_goal(match_id, player['id'], club['id'], mn)
    return f"Гол: {player_name} ({club_name}) {mn}' — мач #{match_id}"


def add_card(match_id, player_name, club_name, card_type, minute):
    match = select_match(match_id)
    ct = card_type.upper().strip()
    if ct not in ('Y', 'R'):
        raise ValueError(f"Типът картон трябва да е Y (жълт) или R (червен), получен: '{card_type}'.")
    try:
        mn = int(minute)
    except (ValueError, TypeError):
        raise ValueError(f"Минутата трябва да е цяло число между 1 и 120.")
    if mn < 1 or mn > 120:
        raise ValueError(f"Минутата трябва да е между 1 и 120, получена: {mn}.")
    club = find_club_by_name(club_name)
    if club['id'] not in (match['home_club_id'], match['away_club_id']):
        raise ValueError(f"Отбор '{club_name}' не участва в мач #{match_id}.")
    try:
        player = find_player_by_name(player_name)
    except ValueError:
        raise ValueError(f"Играч '{player_name}' не е намерен.")
    if player['club_id'] != club['id']:
        raise ValueError(
            f"Играч '{player_name}' не играе за '{club_name}'. "
            f"Той е в клуб ID {player['club_id'] or 'без клуб'}."
        )
    repo.add_card(match_id, player['id'], club['id'], mn, ct)
    ct_label = "жълт" if ct == 'Y' else "червен"
    return f"Картон: {player_name} ({club_name}) {mn}' — {ct_label} (мач #{match_id})"


def show_events(match_id):
    match = select_match(match_id)
    goals = repo.get_goals(match_id)
    cards = repo.get_cards(match_id)
    if not goals and not cards:
        return f"Няма събития за мач #{match_id}: {match['home_name']} vs {match['away_name']}."
    score = f"{match['home_goals'] or '?'}:{match['away_goals'] or '?'}"
    result = [
        f"Събития за мач #{match_id}: {match['home_name']} vs {match['away_name']} ({score})"
    ]
    if goals:
        result.append("  Голове:")
        for g in goals:
            og = " (автогол)" if g['is_own_goal'] else ""
            result.append(f"    {g['minute']}' {g['player_name']} ({g['club_name']}){og}")
    if cards:
        result.append("  Картони:")
        for c in cards:
            ct = "Y" if c['card_type'] == 'Y' else "R"
            result.append(f"    {c['minute']}' {c['player_name']} ({c['club_name']}) — {ct}")
    return "\n".join(result)
