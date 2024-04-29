from enum import Enum, auto


class EventType(Enum):
    OBEY_SIGNAL = auto()
    BUS_STOP = auto()
    STOP_ONBOARDING = auto()
    DEPARTURE = auto()
    DETOUR = auto()
    ARRIVAL = auto()
    CONTINUE = auto()
    CHANGE_POSITION = auto()
    FUEL_SPENT = auto()


class Event:
    def __init__(self, time, event_type, agent):
        self.time = time
        self.event_type = event_type
        self.agent = agent

    def __lt__(self, other):
        return self.time < other.time or self.event_type.value <= other.event_type.value
