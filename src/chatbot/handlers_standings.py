from src.services.standings_service import show_standings


def handle_show_standings(league_name, season):
    if not league_name or not season:
        return "Моля, използвайте: покажи класиране <лига> <сезон> (напр. покажи класиране Първа лига 2025/2026)"
    return show_standings(league_name, season)
