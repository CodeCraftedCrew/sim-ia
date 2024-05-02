from enum import Enum, auto


class EventType(Enum):

    GET_OFF_VEHICLE = auto()
    BOARD_VEHICLE = auto()
    BUS_STOP = auto()
    DEPARTURE = auto()
    DETOUR = auto()
    ARRIVAL = auto()
    CONTINUE = auto()
    CHANGE_POSITION = auto()
    FUEL_SPENT = auto()
    AT_STOP = auto()
    AT_GOAL = auto()
    ROUTE_ENDED = auto()
    ROUTE_ENDED_ABRUPTLY = auto()
    IMPOSSIBLE_PLAN = auto()


class Event:
    def __init__(self, time, event_type, agent):
        self.time = time
        self.event_type = event_type
        self.agent = agent

    def __lt__(self, other):
        return self.time < other.time or (self.time == other.time and self.event_type.value <= other.event_type.value)
