from dataclasses import dataclass

from map.graph import Graph
from map.map_elements import Block

MIN_FUEL = 20


@dataclass
class Bus:
    fuel: float
    max_fuel: float
    consumption_rate: float
    capacity: int
    count: int
    model: str

    def is_fuel_low(self):
        return self.fuel <= MIN_FUEL

    def space(self):
        return self.capacity - self.count


@dataclass
class DriverEnvironment:
    time: int

    current_bus: Bus
    current_position: int
    last_element_index: int

    map: Graph
    gas_stations: list[str]

    onboarding: bool
    obstacle_ahead: bool
    obstacles_blocks: list[str]


@dataclass
class PassengerEnvironment:
    time: int
    map: Graph
    current_position: int
    bus_at_stop: str
    current_bus_route: str
