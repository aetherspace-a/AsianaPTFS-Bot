from app.core.branding import load_branding
from app.models.pilot_rank import PilotRank


def rank_definitions() -> list[dict]:
    branding = load_branding()
    raw = branding.pilot_ranks or []
    if not raw:
        return [
            {"name": "Trainee", "min_hours": 0},
            {"name": "First Officer", "min_hours": 10},
            {"name": "Captain", "min_hours": 50},
            {"name": "Senior Captain", "min_hours": 100},
        ]
    return sorted(raw, key=lambda r: r["min_hours"])


def hours_from_minutes(total_minutes: int) -> float:
    return round(total_minutes / 60, 2)


def rank_for_minutes(total_minutes: int) -> PilotRank:
    hours = total_minutes / 60
    current = PilotRank.TRAINEE
    for entry in rank_definitions():
        if hours >= entry["min_hours"]:
            current = PilotRank(entry["name"])
    return current


def next_rank(current: PilotRank) -> PilotRank | None:
    defs = rank_definitions()
    names = [PilotRank(d["name"]) for d in defs]
    try:
        idx = names.index(current)
    except ValueError:
        return None
    if idx + 1 >= len(names):
        return None
    return names[idx + 1]
