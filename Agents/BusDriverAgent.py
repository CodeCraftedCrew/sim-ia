class BusDriverAgent:
    def __init__(self, route):
        self.route = route

    def decide_action(self, environment):
        if self.waiting_for_passengers and not self.time_waiting == 2:
            self.time_waiting += 1
            return None
        elif self.is_bus_stop_nearby(environment.current_location, self.route) and not environment.at_bus_stop:
            self.waiting_for_passengers = True
            self.time_waiting = 0
            return "stop at bus stop"
        elif environment.at_bus_stop and self.time_waiting == 2:
            self.waiting_for_passengers = False
            return "drive"
        elif self.is_fuel_low(environment.fuel) and not environment.at_gas_station:
            start = self.current_location
            goal = self.find_nearest_gas_station()
            path = self.search(start, goal, environment.city_map)
            self.original_route = self.route
            self.route = self.reconstruct_path(path, start, goal)
            return "follow new route"
        elif environment.at_gas_station and self.is_fuel_low(environment.fuel):
            return "refuel"
        elif environment.at_gas_station and not self.is_fuel_low(environment.fuel):
            self.route = self.original_route
            return "rejoin route"
        elif environment.detour_ahead or environment.accident_ahead:
            start = self.current_location
            goal = self.route[-1]
            path = self.search(start, goal, environment.city_map)
            self.route = self.reconstruct_path(path, start, goal)
            return "take detour"
        elif environment.traffic_signal == "stop":
            return "stop"
        else:
            return "drive"
        
    def is_bus_stop_nearby(current_location, route):
        pass

    def is_bus_full(bus_max_capacity, bus_current_capacity):
        return bus_current_capacity >= bus_max_capacity
    
    def is_fuel_low(fuel):
        return fuel < 10
    
    def find_nearest_gas_station():
        pass

    def search(start, goal, city_map):
        pass

    def reconstruct_path(path, start, goal):
        pass

# class Environment:
#     bus_max_capacity = 40
#     bus_current_capacity = 0
#     at_bus_stop = False
#     at_gas_station = False
#     detour_ahead = False
#     accident_ahead = False
#     fuel = 0
#     current_location = 0
#     traffic_signal = None
#     city_map = None
