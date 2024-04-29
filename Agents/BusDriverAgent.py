import random
import uuid
from enum import Enum, auto

from Agents.Agent import Agent
from events.event import Event, EventType
from map.map_elements import ElementType


class DriverState(Enum):
    IDLE = auto()
    WAITING_AT_STOP = auto()
    DRIVING = auto()
    DRIVING_FOR_FUEL = auto()
    STOP_ONBOARDING = auto()
    START_DRIVING = auto()
    ARRIVAL_AT_STOP = auto()
    OBEY_TRAFFIC_SIGNAL = auto()
    REFUEL = auto()
    DETOUR = auto()


class BusDriverAgent(Agent):
    """
    Represents a bus driver agent.

    Attributes:
        route: The route that the bus driver follows.
    """

    def __init__(self, route, wait_time):
        self.round_trips = 0
        self.route = route
        self.current_route = route.outbound_route
        self.wait_time = wait_time
        self.state = DriverState.IDLE

        self.time_ranges = {
            ElementType.STOP: (2, 5),
            ElementType.GIVE_WAY: (0, 3),
            ElementType.TRAFFIC_LIGHT: (1, 3),
            ElementType.CROSSING: (0, 7),
            ElementType.TRAIN_RAIL: (0, 7)
        }

    def think(self, environment_info):
        """
        Decides the action to take based on the current environment_info.

        Args:
            environment_info (dict): The current environment_info.

        Returns:
            str: The action to take.
        """

        if self.state == DriverState.WAITING_AT_STOP:
            if environment_info["onboarding"]:
                if environment_info["bus_full"]:
                    return DriverState.STOP_ONBOARDING
                return DriverState.WAITING_AT_STOP
            return DriverState.START_DRIVING

        if self.state == DriverState.DRIVING and environment_info["current_location"].type == ElementType.BUS_STOP:
            return DriverState.ARRIVAL_AT_STOP

        if self.state == DriverState.IDLE and environment_info["is_fuel_low"]:
            return DriverState.DRIVING_FOR_FUEL

        if self.state == DriverState.DRIVING_FOR_FUEL and environment_info["at_gas_station"]:
            return DriverState.REFUEL

        if self.state == DriverState.DRIVING and environment_info["traffic_sign"]:
            return DriverState.OBEY_TRAFFIC_SIGNAL

        if self.state == DriverState.DRIVING or environment_info["obstacle_ahead"]:
            return DriverState.DETOUR

        return self.state

    def take_action(self, state, environment_info):

        if state == DriverState.STOP_ONBOARDING:
            return [Event(environment_info["time"], EventType.STOP_ONBOARDING, self)]

        if state == DriverState.WAITING_AT_STOP:
            return [Event(environment_info["time"] + self.wait_time, EventType.BUS_STOP, self)]

        if state == DriverState.START_DRIVING:
            return self.drive(environment_info)

        if state == DriverState.DRIVING_FOR_FUEL:
            return self.refuel(environment_info)

        if state == DriverState.OBEY_TRAFFIC_SIGNAL:
            return self.obey_traffic_signal(environment_info)

        if state == DriverState.DETOUR:
            return self.take_detour(environment_info)

    def drive(self, environment_info):
        """
        Performs the 'drive' action for the given agent.
        """

        elements = environment_info["next_elements"]

        events = []

        bus_speed = environment_info["bus_speed"]
        time = environment_info["start_time"]

        last_position = 0

        for element in elements:

            time += (element.position - last_position) / (bus_speed / 60)

            if element.type == ElementType.BUS_STOP:
                events.append(Event(time, EventType.BUS_STOP, self))

            if element.is_traffic_sign:
                events.append(Event(time, EventType.OBEY_SIGNAL, self))

            last_position = element.position

        events.append(Event(time, EventType.FUEL_SPENT, self))
        events.append(Event(time, EventType.CHANGE_POSITION, self))

        return events

    def refuel(self, environment_info):
        """
        Performs the 'refuel' action for the given agent.
        """
        pass

    def take_detour(self, environment_info):
        """
        Performs the 'take_detour' action for the given agent.
        """
        pass

    def obey_traffic_signal(self, environment_info):
        """
        Perform the appropriate action based on the given traffic signal.

        This method takes a parameter `signal_type` which indicates the type of traffic signal.

        :param environment_info: The current environment perceived by the agent.
        """
        signal_type = environment_info["traffic_signal"]
        time_spent = random.uniform(*self.time_ranges[signal_type])
        return [Event(environment_info["time"] + time_spent, EventType.CONTINUE, self)]
