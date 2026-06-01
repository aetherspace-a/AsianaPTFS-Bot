import enum


class PilotRank(str, enum.Enum):
    TRAINEE = "Trainee"
    FIRST_OFFICER = "First Officer"
    CAPTAIN = "Captain"
    SENIOR_CAPTAIN = "Senior Captain"
