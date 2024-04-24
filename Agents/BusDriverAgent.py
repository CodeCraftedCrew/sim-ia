from Agents.Agent import Agent


class BusDriverAgent(Agent):
    """
    Represents a bus driver agent.

    Attributes:
        route: The route that the bus driver follows.
    """

    def __init__(self, route):
        self.route = route
        self.current_route = route.outbound_route

    def decide_action(self, environment):
        """
        Decides the action to take based on the current environment.

        Args:
            environment (dict): The current environment.

        Returns:
            str: The action to take.
        """
        if self.waiting_for_passengers and not self.time_waiting == 2:
            self.time_waiting += 1
            return None
        elif self.is_bus_stop_nearby(environment["current_location"], self.current_route) and not environment["at_bus_stop"]:
            self.waiting_for_passengers = True
            self.time_waiting = 0
            return "stop at bus stop"
        elif environment["at_bus_stop"] and self.time_waiting == 2:
            self.waiting_for_passengers = False
            return "drive"
        elif self.is_fuel_low(environment["fuel"]) and not environment["at_gas_station"]:
            start = self.current_location
            goal = self.find_nearest_gas_station()
            path = self.search(start, goal, environment["city_map"])
            self.original_route = self.current_route
            self.current_route = self.reconstruct_path(path, start, goal)
            return "go to the gas station"
        elif environment["at_gas_station"] and self.is_fuel_low(environment["fuel"]):
            return "refuel"
        elif environment["at_gas_station"] and not self.is_fuel_low(environment["fuel"]):
            self.current_route = self.original_route
            return "back to route"
        elif environment["detour_ahead"] or environment["accident_ahead"]:
            start = self.current_location
            goal = self.current_route[-1]
            path = self.search(start, goal, environment["city_map"])
            self.current_route = self.reconstruct_path(path, start, goal)
            return "take detour"
        elif environment["traffic_signal"] == "stop":
            return "stop"
        else:
            return "drive"
        
    def is_bus_stop_nearby(self, current_location, current_route):
        """
        Checks if there is a bus stop nearby.

        Args:
            current_location: The current location of the bus.
            current_route: The route that the bus follows.

        Returns:
            bool: True if there is a bus stop nearby, False otherwise.
        """
        pass

    def is_bus_full(self, bus_max_capacity, bus_current_capacity):
        """
        Checks if the bus is full.

        Args:
            bus_max_capacity (int): The maximum capacity of the bus.
            bus_current_capacity (int): The current capacity of the bus.

        Returns:
            bool: True if the bus is full, False otherwise.
        """
        return bus_current_capacity >= bus_max_capacity
    
    def is_fuel_low(self, fuel):
        """
        Checks if the fuel level is low.

        Args:
            fuel (int): The current fuel level.

        Returns:
            bool: True if the fuel level is low, False otherwise.
        """
        return fuel < 10
    
    def find_nearest_gas_station(self):
        """
        Finds the nearest gas station.

        Returns:
            The location of the nearest gas station.
        """
        pass

    def search(self, start, goal, city_map):
        """
        Performs a search algorithm to find a path from the start location to the goal location.

        Args:
            start: The start location.
            goal: The goal location.
            city_map: The map of the city.

        Returns:
            The path from the start location to the goal location.
        """
        pass

    def reconstruct_path(self, path, start, goal):
        """
        Reconstructs the path from the search algorithm.

        Args:
            path: The path from the search algorithm.
            start: The start location.
            goal: The goal location.

        Returns:
            The reconstructed path.
        """
        pass
    