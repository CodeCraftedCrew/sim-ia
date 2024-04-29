import heapq
import math
import random
from enum import Enum
from queue import PriorityQueue
from Agents.Agent import Agent
from routing import routing
from routing.routing import get_routes


def time_to_minutes(time_str):
    hours, minutes = map(int, time_str.split(":"))
    total_minutes = (hours * 60) + minutes
    return total_minutes

class PlanType(Enum):
    GO_TO_WORK = 3
    RETURN_HOME = 2
    RANDOM_TRAVEL = 1

class Plan:
    def __init__(self, time, goal, plan_type):
        self.goal = goal
        self.importance = plan_type.value

    def __lt__(self, other):
        return self.importance < other.importance
    
class PassengerState(Enum):
    INITIAL_STATE = 1
    WALKING = 2
    WAITING = 3
    AT_VEHICLE = 4

class PassengerAgent(Agent):
    """
    Represents a passenger agent.
    
    """

    def __init__(self, profile, plans, home_block, workplace_blocks, current_block):

        self.waiting_time = 0
        self.profile = profile

        self.plans = []

        for plan in plans:
            heapq.heappush(self.plans, plan)

        self.home_block = home_block
        self.workplace_blocks = workplace_blocks
        self.current_block = current_block

        self.state = PassengerState.INITIAL_STATE
        self.expected_waiting_time = 15

        self.can_walk = 0.5  # distance in km

    @staticmethod
    def get_schedule(profile, now):
        if profile["employment_status"] == "occupied":
            return profile["work_schedule"]
        elif profile["employment_status"] == "student":
            return profile["school_schedule"]
        else:
            start_hour = random.randint(math.ceil(now/60), 22)
            start = f"{start_hour}:{random.randint(0, 59)}"
            end = f"{random.randint(start_hour + 1, 23)}:{random.randint(0, 59)}"
            return f"{start}-{end}"

    @staticmethod
    def create_plans(profile, home_block, workplace_block, other_block, now):
        schedule = PassengerAgent.get_schedule(profile, now)

        start, end = schedule.split("-")

        is_random = "employment_status" not in profile or profile["employment_status"] not in ["student", "occupied"]

        plans = [
            Plan(time_to_minutes(start), other_block if is_random else workplace_block,
                 PlanType.RANDOM_TRAVEL if is_random else PlanType.GO_TO_WORK),
            Plan(time_to_minutes(end), home_block, PlanType.RETURN_HOME)
        ]

        return plans

    def decide_departure_time(self, graph, now):

        next_plan = self.plans[0]

        if next_plan.plan_type == PlanType.GO_TO_WORK:
            routes = get_routes(graph, self.current_block, next_plan.goal, self.can_walk)

            route = max(routes, key=lambda x: self.evaluate_route(x))
            estimated_time = self.estimated_time(route)

            return max(now, next_plan.time - estimated_time)

        return next_plan.time


    def evaluate_route(self, route):
        return 1

    def estimated_time(self, route):
        pass


    def decide_action(self, environment):
        """
        Decides the action to take based on the current environment.

        Args:
            environment (dict): The current environment.

        Returns:
            str: The action to take.
        """

        if self.state not in [PassengerState.WAITING, PassengerState.WALKING, PassengerState.AT_VEHICLE]:
            route = self.explore_routes(environment["city_map"], 1000, self.plans[0].goal)
            self.state = PassengerState.WALKING
            return "walk to stop"

        elif self.state == PassengerState.WAITING:
            if self.decide_boarding_vehicle(self.current_block):
                self.update_expected_waiting_time(self.waiting_time)
                self.waiting_time = 0
                return "board vehicle"
            else:
                if self.waiting_time < self.profile["max_waiting_time"]:
                    self.waiting_time += 1
                    return "wait at stop"
                else:
                    return "search alternative transport"

        elif self.state == PassengerState.WALKING:
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

    def explore_routes(self, map, radio, goal):

        possible_routes = routing.get_routes(map, self.current_block, goal, radio)

        max_score = float('-inf')
        best_route = None

        for route in possible_routes:
            score = self.calculate_route_time(map, route)
            if score > max_score:
                max_score = score
                best_route = route

        return best_route
    
    def calculate_route_time(self, map, route):
        time = 0

        time += route.total_time

        previous_action = None
        for action, blocks in route:
            if previous_action and previous_action != action != "walk":
                time += self.expected_waiting_time
            elif previous_action == "walk" and action != "walk":
                time += self.expected_waiting_time
            previous_action = action
        
        return time


    def decide_boarding_vehicle(self, current_location):
        pass
