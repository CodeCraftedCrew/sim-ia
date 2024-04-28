from enum import Enum
from queue import PriorityQueue
from Agents.Agent import Agent
from routing import routing

class PlanType(Enum):
    WORK = 3
    RETURN_HOME = 2
    RANDOM_TRAVEL = 1

class Plan:
    def __init__(self, goal, plan_type):
        self.goal = goal
        self.importance = plan_type.value

    def __lt__(self, other):
        return self.importance < other.importance
    
class PassengerAgent(Agent):
    """
    Represents a passenger agent.
    
    """
    def __init__(self, profile, plans, home_block, workplace_block, current_block):

        self.profile = profile

        self.plans = PriorityQueue() 
        for plan in plans:
            self.plans.put(plan)
        
        self.home_block = home_block
        self.workplace_block = workplace_block
        self.current_block = current_block

    def decide_action(self, environment):
        """
        Decides the action to take based on the current environment.

        Args:
            environment (dict): The current environment.

        Returns:
            str: The action to take.
        """

        if not environment["waiting"] and not environment["at_vehicle"] and not environment["walking"]:
            target_stop = self.explore_nearby_nodes(environment["city_map"], 1000, environment["current_location"])
            self.route = self.get_route_to_stop(target_stop, environment["city_map"])
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
            

    def explore_nearby_nodes(self, map, radio, current_location):

        blocks_of_interest = routing.blocks_in_radio(map, radio, current_location)
        
        max_score = float('-inf')
        best_block = None

        for block in blocks_of_interest:
            score = self.calculate_block_score(map, block, current_location) 
            if score > max_score:
                max_score = score
                best_block = block

        return best_block

    def calculate_block_score(self, map, block, current_location):
        score = 0 

        distance_to_passenger = current_location.length_to(block.location)
        max_score = 3
        target_distance = 500
        slope = 1 / target_distance

        score = max(0, slope * distance_to_passenger + max_score)

        valid_routes = routing.get_routes(map, block.location, self.travel_goal, 1000)

        for route in valid_routes:

            if route in map.gazelle_routes:
                if self.profile.money >= 5:
                    score += 1
                if route.outbound_route[0] == block:
                    score += 1
            else:
                if route.outbound_route[0] == block:
                    score += 1
                score += 2

        return score
    
    def get_route_to_stop(self, target_stop, map):
        pass

    def decide_boarding_vehicle(self, current_location):
        pass
