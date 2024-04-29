import heapq
import math
import random
from enum import Enum, auto

from Agents.Agent import Agent
from events.event import Event, EventType
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
        self.time = time
        self.goal = goal
        self.plan_type = plan_type

    def __lt__(self, other):
        return self.plan_type.value > other.plan_type.value


class PassengerState(Enum):
    IDLE = auto()
    WALKING = auto()
    WAITING = auto()
    ON_VEHICLE = auto()
    WALK_TO_STOP = auto()
    BOARD_VEHICLE = auto()
    ARRIVAL_AT_STOP = auto()
    ARRIVAL_AT_DESTINATION = auto()
    SEARCH_ALTERNATIVE = auto()

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
        self.route = None

        self.can_walk = 0.5  # distance in km

    @staticmethod
    def get_schedule(profile, now):
        if profile["employment_status"] == "occupied":
            return profile["work_schedule"]
        elif profile["employment_status"] == "student":
            return profile["school_schedule"]
        else:
            start_hour = random.randint(math.ceil(now / 60), 22)
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

            if len(routes) == 0:
                return -1

            route_times = [(route, self.calculate_route_time(*route)) for route in routes]

            min_route, min_time = min(route_times, key=lambda x: x[1])

            return max(now, next_plan.time - min_time)

        return next_plan.time

    def think(self, environment_info):

        if self.state == PassengerState.IDLE:
            return PassengerState.WALK_TO_STOP
        
        if self.state == PassengerState.WAITING:
            if self.decide_boarding_vehicle(self.current_block, environment_info):
                return PassengerState.BOARD_VEHICLE
            else:
                if self.waiting_time < self.profile["max_waiting_time"]:
                    return PassengerState.WAITING
                else:
                    return PassengerState.SEARCH_ALTERNATIVE

        if self.state == PassengerState.WALKING or self.state == PassengerState.ON_VEHICLE:
            if self.current_block == self.route[-1]:
                return PassengerState.ARRIVAL_AT_STOP
            
            if self.current_block == self.plans[0].goal:
                return PassengerState.ARRIVAL_AT_DESTINATION
               
        return self.state
    
    def take_action(self, state, environment_info):

        if state == PassengerState.WALK_TO_STOP:
            return self.walk_to_stop(environment_info)
        
        if state == PassengerState.BOARD_VEHICLE:
            return self.board_vehicle(environment_info)
        
        if state == PassengerState.SEARCH_ALTERNATIVE:
            return self.search_alternative(environment_info)
        
        if state == PassengerState.WAITING:
            return [Event(environment_info["time"], EventType.AT_STOP, self)]
        
        if state == PassengerState.WALKING:
            return self.walk(environment_info)
            
    # def decide_action(self, environment):
    #     """
    #     Decides the action to take based on the current environment.

    #     Args:
    #         environment (dict): The current environment.

    #     Returns:
    #         str: The action to take.
    #     """

    #     if self.state not in [PassengerState.WAITING, PassengerState.WALKING, PassengerState.ON_VEHICLE]:
    #         self.route = self.explore_routes(environment["city_map"], 1000, self.plans[0].goal)
    #         self.state = PassengerState.WALKING
    #         return "walk to stop"

    #     elif self.state == PassengerState.WAITING:
    #         if self.decide_boarding_vehicle(self.current_block):
    #             self.update_expected_waiting_time(self.waiting_time)
    #             self.waiting_time = 0
    #             return "board vehicle"
    #         else:
    #             if self.waiting_time < self.profile["max_waiting_time"]:
    #                 self.waiting_time += 1
    #                 return "wait at stop"
    #             else:
    #                 return "search alternative transport"

    #     elif self.state == PassengerState.WALKING:
    #         if self.current_block == self.route[-1]:
    #             return "arrive to stop"

    #         elif self.current_block == self.plans[0].goal:
    #             return "arrive to destination"
    #         else:
    #             return "walk"

    #     elif self.state == PassengerState.ON_VEHICLE:
    #         if self.current_block == self.route[-1]:
    #             return "exit vehicle"
    #         else:
    #             return "continue journey"

    def explore_routes(self, graph, radio, goal):

        possible_routes = routing.get_routes(graph, self.current_block, goal, radio)

        if len(possible_routes) == 0:
            return []

        max_score = float('-inf')
        best_route = None

        for route in possible_routes:
            score = self.calculate_route_time(map, route)
            if score > max_score:
                max_score = score
                best_route = route

        return best_route

    def calculate_route_time(self, estimated_time, route):
        time = estimated_time

        previous_action = {"walk"}
        for blocks, action in route:
            intersection = previous_action.intersection(action)
            if previous_action and action != intersection and intersection != {"walk"}:
                time += self.expected_waiting_time
            elif previous_action == "walk" and action != "walk":
                time += self.expected_waiting_time
            previous_action = action

        return time

    def decide_boarding_vehicle(self, current_location):
        pass
