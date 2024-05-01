import random
import uuid
from enum import Enum, auto

from agents.agent import Agent
from environment.environment import DriverEnvironment
from events.event import Event, EventType
from map.map_elements import ElementType, Block, Route
from routing.routing import path_search


class DriverStatus(Enum):
    IDLE = auto()
    WAITING_AT_STOP = auto()
    DRIVING = auto()
    SEARCH_FOR_FUEL = auto()
    DRIVING_FOR_FUEL = auto()
    START_DRIVING = auto()
    REFUEL = auto()
    DETOUR = auto()


class BusDriverAgent(Agent):
    """
    Represents a bus driver agent.

    Attributes:
        route: The route that the bus driver follows.
    """

    def __init__(self, route, wait_time):
        self.id = str(uuid.uuid4())

        self.trip = 0
        self.route: Route = route
        self.current_route: list[Block] = route.outbound_route
        self.wait_time = wait_time
        self.status = DriverStatus.IDLE
        self.ability = random.uniform(0.5, 1)

        self.time_ranges = {
            ElementType.STOP: (2, 5),
            ElementType.GIVE_WAY: (0, 3),
            ElementType.TRAFFIC_LIGHT: (1, 3),
            ElementType.CROSSING: (0, 7),
            ElementType.TRAIN_RAIL: (0, 7)
        }

    def think(self, event, environment_info: DriverEnvironment):
        """
        Decides the action to take based on the current environment_info.

        Args:
            environment_info (DriverEnvironment): The current environment info.
            event (Event): The current event.

        Returns:
            str: The action to take.
        """

        if event.event_type == EventType.BUS_STOP and environment_info.onboarding:
            return DriverStatus.WAITING_AT_STOP

        elif event.event_type == EventType.ROUTE_ENDED and environment_info.current_bus.is_fuel_low():
            return DriverStatus.SEARCH_FOR_FUEL

        elif event.event_type == EventType.CONTINUE:
            if (self.status == DriverStatus.DRIVING_FOR_FUEL
                    and environment_info.current_position in environment_info.gas_stations):
                return DriverStatus.REFUEL
            if self.status == DriverStatus.DRIVING or environment_info.obstacle_ahead:
                return DriverStatus.DETOUR

        elif event.event_type == EventType.ROUTE_ENDED_ABRUPTLY:
            return DriverStatus.IDLE

        return DriverStatus.DRIVING

    def take_action(self, status, environment_info: DriverEnvironment):

        self.status = status

        if status == DriverStatus.WAITING_AT_STOP:
            return [Event(environment_info.time + self.wait_time, EventType.BUS_STOP, self)]

        if status == DriverStatus.DRIVING or status == DriverStatus.DRIVING_FOR_FUEL:
            return self.drive(environment_info)

        if status == DriverStatus.SEARCH_FOR_FUEL:
            return self.search_gas_station(environment_info)

        if status == DriverStatus.DETOUR:
            return self.take_detour(environment_info)

        if status == DriverStatus.REFUEL:
            return self.refuel(environment_info)

        if status == DriverStatus.IDLE:
            return self.restart(environment_info)

    def drive(self, environment_info: DriverEnvironment):
        """
        Performs the 'drive' action for the given agent.
        """

        elements = self.current_route[environment_info.current_position].elements[
                   environment_info.last_element_index + 1:] \
            if environment_info.last_element_index < len(
            self.current_route[environment_info.current_position].elements) - 1 else []

        if len(elements) == 0:
            if environment_info.current_position == len(self.current_route) - 1:
                return [Event(environment_info.time, EventType.ROUTE_ENDED, self)]

            environment_info.current_position += 1
            elements = self.current_route[environment_info.current_position].elements

        events = []

        bus_speed = self.current_route[environment_info.current_position].max_speed
        time = environment_info.time

        last_position = 0

        for element in elements:

            time += (element.position - last_position) / (bus_speed / 60)

            if element.type == ElementType.BUS_STOP and self.status != DriverStatus.DRIVING_FOR_FUEL:
                events.append(Event(time, EventType.BUS_STOP, self))

            if element.is_traffic_sign:
                events.append(self.obey_traffic_signal(time, element.type))

            last_position = element.position

        events.append(Event(environment_info.time, EventType.CONTINUE, self))
        events.append(Event(time, EventType.FUEL_SPENT, self))
        return events

    def search_gas_station(self, environment_info: DriverEnvironment):
        """
        Performs the 'refuel' action for the given agent.
        """
        detour = path_search(environment_info.map, self.current_route[environment_info.current_position].id,
                             list(map(lambda x: x.id, environment_info.gas_stations)), [], self.ability,
                             False)

        self.current_route = detour
        return Event(environment_info.time, EventType.DEPARTURE, self)

    def refuel(self, environment_info):
        environment_info.current_bus.fuel = environment_info.current_bus.max_fuel

        detour = path_search(environment_info.map, self.current_route[environment_info.current_position].id,
                             [self.current_route[len(self.current_route) - 1].id], [], self.ability,
                             False)

        self.current_route = detour
        return Event(environment_info.time, EventType.DEPARTURE, self)

    def take_detour(self, environment_info):
        """
        Performs the 'take_detour' action for the given agent.
        """

        detour = []
        last_index = environment_info.current_position + 1

        while not detour:

            if last_index >= len(self.current_route):
                return Event(environment_info.time, EventType.ROUTE_ENDED_ABRUPTLY, self)

            detour = path_search(environment_info.map, self.current_route[environment_info.current_position].id,
                                 [self.current_route[last_index].id], environment_info.obstacles_blocks, self.ability,
                                 False)

        self.current_route[environment_info.current_position + 1: last_index + 1] = detour
        return Event(environment_info.time, EventType.CONTINUE, self)

    def obey_traffic_signal(self, time, signal_type):
        """
        Perform the appropriate action based on the given traffic signal.

        This method takes a parameter `signal_type` which indicates the type of traffic signal.

        :param time: Time when the agent will arrive at the traffic signal.
        :param signal_type: Type of traffic signal.
        """
        time_spent = random.uniform(*self.time_ranges[signal_type])
        return [Event(time + time_spent, EventType.CONTINUE, self)]

    def restart(self, environment_info):

        if environment_info.current_position == len(self.current_route) - 1:
            if self.trip == 0:
                self.current_route = self.route.return_route
                self.trip = 1
            else:
                self.current_route = self.route.outbound_route
                self.trip = 0

            environment_info.current_position = 0
            environment_info.last_element_index = - 1

            return Event(environment_info.time, EventType.DEPARTURE, self)

        detour = path_search(environment_info.map, self.current_route[environment_info.current_position].id,
                             [self.current_route[0].id], [], self.ability,
                             False)

        self.current_route = detour
        return Event(environment_info.time, EventType.DEPARTURE, self)
