from Agents.Agent import Agent
from Agents.agent_tools import distance_between

class PassengerAgent(Agent):
    """
    Represents a passenger agent.
    
    """

    def __init__(self, profile, travel_goal):
        self.profile = profile
        self.travel_goal = travel_goal
        self.route = None
        self.waiting_time = 0
        self.nearest_bus_stop = None
        self.suitable_stops = None

    def decide_action(self, environment):
        """
        Decides the action to take based on the current environment.

        Args:
            environment (dict): The current environment.

        Returns:
            str: The action to take.
        """
        current_location = environment['current_location']
        bus_stops = environment['bus_stops']
        buses = environment['buses']
        gazelles = environment['gazelles']
        city_map = environment['city_map']
        
        if self.decide_boarding_vehicle(environment["buses_at_stop"], environment["gazelles_at_stop"], buses, gazelles):
                self.waiting_time = 0
                return "board vehicle"
            
        elif self.waiting_time < self.profile['max_waiting_time']:
            self.waiting_time += 1
            return "wait at stop"
        
        elif environment["at_bus_stop"] and self.waiting_time >= self.profile['max_waiting_time']:
            return "search alternative transport"
        
        elif environment["on_bus"]:
            if environment["current_location"] == self.travel_goal:
                return "arrive destination"
            else:
                self.monitor_environment(environment)
                return "continue journey"
            
        elif not environment["waiting_at_stop"] and not environment["walking"]:
            self.decide_destination_stop(current_location, environment['bus_stops'], buses)
            return f"walk to {self.nearest_bus_stop}"

    def decide_boarding_vehicle(self, buses_at_stop, gazelles_at_stop):
        
        if not buses_at_stop and not gazelles_at_stop:
            return False

        suitable_vehicles = []

        for bus in buses_at_stop:
            if bus.current_capacity < bus.max_capacity and self.is_vehicle_convenient(bus):
                suitable_vehicles.append(bus)

        if self.profile.get("willing_to_take_gazelle", False):
            for gazelle in gazelles_at_stop:
                if gazelle.current_capacity < gazelle.max_capacity and self.is_vehicle_convenient(gazelle):
                    suitable_vehicles.append(gazelle)

        if not suitable_vehicles:
            return False

        best_vehicle = self.select_best_vehicle(suitable_vehicles)

        if best_vehicle:
            return True
        else:
            return False
    
    def find_nearest_bus_stop(self, current_location, bus_stops):
        min_distance = float('inf')
        nearest_stop = None

        for stop_id, stop_location in bus_stops.items():
            distance = distance_between(current_location, stop_location)
            if distance < min_distance:
                min_distance = distance
                nearest_stop = stop_id

        return nearest_stop

    def search_alternative_transport(self):
        #buscar alternativas de transporte?
        pass

    def decide_destination_stop(self, buses, current_location):

        self.suitable_stops = self.find_suitable_stops(self.travel_goal, buses)
        self.nearest_bus_stop = self.find_nearest_bus_stop(current_location, self.suitable_stops)
   

    def select_best_vehicle(self, vehicles):
        
        if not vehicles:
            return None
        
        best_vehicle = None
        min_distance = float('inf')
        
        for vehicle in vehicles:
        
            for stop_node in vehicle.route:
                distance_to_destination = distance_between(stop_node, self.travel_goal)

                if distance_to_destination < min_distance_to_destination:
                    min_distance_to_destination = distance_to_destination
                    best_vehicle = vehicle
        
        return best_vehicle
    
    def find_suitable_stops(self, travel_goal, buses):

        suitable_stops = set()

        for bus in buses:
            if self.is_vehicle_convenient(bus) and travel_goal in bus.route:
                suitable_stops.update(bus.route)

        return list(suitable_stops)
