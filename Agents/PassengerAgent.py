from Agents.Agent import Agent

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

        if not environment["waiting"] and not environment["at_vehicle"] and not environment["walking"]:
            target_stop = self.explore_nearby_nodes(environment["city_map"], 1000)
            self.route = self.get_route_to_stop(target_stop)
            return "walk to stop"
        
        elif environment["waiting"]:
            if self.decide_boarding_vehicle(environment["current_location"]):
                self.waiting_time = 0
                return "board vehicle"
            else:
                if self.waiting_time < self.profile["max_waiting_time"]:
                    self.waiting_time += 1
                    return "wait at stop"
                else:
                    return "search alternative transport"
            
        elif environment["walking"]:
            if environment["current_location"] == self.route[-1]:
                return "arrive to stop" 
            elif environment["current_location"] == self.travel_goal:
                return "arrive to destination"
            else:
                return "walk"
            
        elif environment["on_vehicle"]:
            if environment["current_location"] == self.route[-1]:
                return "exit vehicle"
            else:
                return "continue journey"
            

    def explore_nearby_nodes(self, map, radius):

        nearby_nodes = map.get_nodes_by_radius(self.current_location, radius)
        
        max_score = float('-inf')
        best_node = None
        for node in nearby_nodes:
            score = self.calculate_node_score(node) 
            if score > max_score:
                max_score = score
                best_node = node

        return best_node

    def calculate_node_score(self, block):
        score = 0 

        distance_to_passenger = self.current_location.length_to(block.location)
        max_score = 3
        target_distance = 500  
        slope = 1 / target_distance  

        score = max(0, slope * distance_to_passenger + max_score)

        valid_routes = self.get_valid_routes(block)

        for route in valid_routes:

            if route.mode == "gazelle":
                if self.profile.money >= 5:
                    score += 1  
                if route.outbound_route[0] == block:
                    score += 1  
            else:
                if route.outbound_route[0] == block:
                    score += 1 
                score += 2 
        
        return score
