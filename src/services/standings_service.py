from src.repositories import leagues_repo
from src.repositories import standings_repo


def show_standings(league_name, season):
    league = leagues_repo.get_league(league_name.strip(), season.strip())
    if not league:
        raise ValueError(f"Лига '{league_name}' за сезон '{season}' не е намерена.")

    teams = leagues_repo.get_league_teams(league['id'])
    if not teams:
        raise ValueError(f"Няма отбори в лига '{league_name}' ({season}).")

    played_matches = standings_repo.get_played_matches(league['id'])

    stats = {}
    for t in teams:
        stats[t['id']] = {
            'name': t['name'],
            'mp': 0, 'w': 0, 'd': 0, 'l': 0,
            'gf': 0, 'ga': 0, 'gd': 0, 'pts': 0
        }

    for m in played_matches:
        home_id = m['home_club_id']
        away_id = m['away_club_id']
        hg = m['home_goals']
        ag = m['away_goals']

        if home_id in stats:
            stats[home_id]['mp'] += 1
            stats[home_id]['gf'] += hg
            stats[home_id]['ga'] += ag
            if hg > ag:
                stats[home_id]['w'] += 1
                stats[home_id]['pts'] += 3
            elif hg == ag:
                stats[home_id]['d'] += 1
                stats[home_id]['pts'] += 1
            else:
                stats[home_id]['l'] += 1

        if away_id in stats:
            stats[away_id]['mp'] += 1
            stats[away_id]['gf'] += ag
            stats[away_id]['ga'] += hg
            if ag > hg:
                stats[away_id]['w'] += 1
                stats[away_id]['pts'] += 3
            elif ag == hg:
                stats[away_id]['d'] += 1
                stats[away_id]['pts'] += 1
            else:
                stats[away_id]['l'] += 1

    for s in stats.values():
        s['gd'] = s['gf'] - s['ga']

    sorted_teams = sorted(
        stats.values(),
        key=lambda x: (-x['pts'], -x['gd'], -x['gf'], x['name'])
    )

    if not played_matches:
        result = [f"Класиране: {league_name} (сезон {season})"]
        result.append("  (няма изиграни мачове)")
        header = f"{'#':>2} {'Отбор':<20} {'MP':>2} {'W':>2} {'D':>2} {'L':>2} {'GF:GA':>7} {'GD':>4} {'PTS':>3}"
        result.append("  " + header)
        for i, s in enumerate(sorted_teams, 1):
            result.append(
                f"  {i:2d}. {s['name']:<20} {s['mp']:2d} {s['w']:2d} {s['d']:2d} {s['l']:2d} "
                f"{s['gf']:2d}:{s['ga']:<2d} {s['gd']:+3d} {s['pts']:3d}"
            )
        return "\n".join(result)

    result = [f"Класиране: {league_name} (сезон {season})"]
    header = f"{'#':>2} {'Отбор':<20} {'MP':>2} {'W':>2} {'D':>2} {'L':>2} {'GF:GA':>7} {'GD':>4} {'PTS':>3}"
    result.append("  " + header)
    for i, s in enumerate(sorted_teams, 1):
        result.append(
            f"  {i:2d}. {s['name']:<20} {s['mp']:2d} {s['w']:2d} {s['d']:2d} {s['l']:2d} "
            f"{s['gf']:2d}:{s['ga']:<2d} {s['gd']:+3d} {s['pts']:3d}"
        )
    return "\n".join(result)
