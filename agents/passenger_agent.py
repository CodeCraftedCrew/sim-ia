import heapq
import math
import random
import uuid
from enum import Enum, auto

from agents.agent import Agent
from environment.environment import PassengerEnvironment
from events.event import Event, EventType
from routing import routing
from routing.routing import get_routes, path_search


def time_to_minutes(time_str):
    hours, minutes = map(int, time_str.split(":"))
    total_minutes = (hours * 60) + minutes
    return total_minutes


class PlanType(Enum):
    GO_TO_WORK = 1
    RANDOM_TRAVEL = 2
    RETURN_HOME = 3


class Plan:
    def __init__(self, time, goal, plan_type):
        self.time = time
        self.goal = goal
        self.plan_type = plan_type

    def __lt__(self, other):
        return self.plan_type.value < other.plan_type.value


class PassengerStatus(Enum):
    IDLE = auto()
    WALKING = auto()
    WAITING = auto()
    ON_VEHICLE = auto()
    OFF_VEHICLE = auto()
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

        self.id = str(uuid.uuid4())

        self.arrival_at_stop = 0
        self.profile = profile

        self.plans = []

        for plan in plans:
            heapq.heappush(self.plans, plan)

        self.home_block = home_block
        self.workplace_blocks = workplace_blocks
        self.current_block = current_block

        self.status = PassengerStatus.IDLE
        self.expected_waiting_time = 15
        self.route = None

        self.can_walk = 0.5  # distance in km
        self.speed = profile["walk_speed"]
        self.time_to_get_off = 0.3
        self.time_to_onboard = 0.3

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

    def think(self, event, environment_info: PassengerEnvironment):

        if event.event_type == EventType.DEPARTURE:
            return PassengerStatus.WALK_TO_STOP

        if event.event_type in [EventType.AT_GOAL, EventType.IMPOSSIBLE_PLAN]:
            return PassengerStatus.IDLE

        if event.event_type == EventType.BUS_STOP:
            if self.status == PassengerStatus.WAITING:
                waiting_time = environment_info.time - self.arrival_at_stop
                if self.decide_boarding_vehicle(environment_info):
                    return PassengerStatus.BOARD_VEHICLE
                else:
                    if waiting_time < self.profile["max_waiting_time"]:
                        return PassengerStatus.WAITING
                    else:
                        return PassengerStatus.SEARCH_ALTERNATIVE
            if self.status == PassengerStatus.ON_VEHICLE:
                if self.decide_leave_vehicle(environment_info):
                    return PassengerStatus.ARRIVAL_AT_STOP
                return PassengerStatus.ON_VEHICLE

            else:
                return PassengerStatus.WAITING

        if event.event_type == EventType.ROUTE_ENDED_ABRUPTLY:
            return PassengerStatus.SEARCH_ALTERNATIVE

        if event.event_type == EventType.GET_OFF_VEHICLE:
            return PassengerStatus.OFF_VEHICLE

        return self.status

    def take_action(self, status, environment_info: PassengerEnvironment):

        self.status = status

        if status == PassengerStatus.WALK_TO_STOP:
            return self.walk_to_stop(environment_info)

        if status == PassengerStatus.BOARD_VEHICLE:
            environment_info.current_bus_route = environment_info.bus_at_stop
            return Event(environment_info.time + self.time_to_onboard, EventType.BOARD_VEHICLE, self)

        if status == PassengerStatus.OFF_VEHICLE:
            environment_info.current_bus_route = ""
            environment_info.current_driver = ""
            self.status = PassengerStatus.WAITING
            return []

        if status == PassengerStatus.ARRIVAL_AT_STOP:
            return self.arrive_at_stop(environment_info)

        if status == PassengerStatus.SEARCH_ALTERNATIVE:
            return self.search_alternative(environment_info)

        if status == PassengerStatus.IDLE:
            return self.start_plan(environment_info)

        return []

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

    def decide_boarding_vehicle(self, environment_info: PassengerEnvironment):
        return environment_info.bus_at_stop in self.route[environment_info.current_position]

    def decide_leave_vehicle(self, environment_info):
        return (environment_info.current_position == len(self.route) - 1
                or environment_info.bus_at_stop not in self.route[environment_info.current_position + 1])

    def walk_to_stop(self, environment_info: PassengerEnvironment, explore=True):

        if explore:
            self.route = self.explore_routes(environment_info.map, self.can_walk, self.plans[0].goal)
            environment_info.current_position = 0

        if not self.route:
            heapq.heappop(self.plans)
            return Event(environment_info.time, EventType.IMPOSSIBLE_PLAN, self)

        time_spent = 0

        walk = True
        while walk:

            if environment_info.current_position >= len(self.route):
                break

            block, actions = self.route[environment_info.current_position]
            block = environment_info.map.nodes[block]

            if actions == {"walk"}:
                time_spent += (block.length / self.speed) * 60
            else:
                break

            environment_info.current_position += 1

        if environment_info.current_position >= len(self.route):
            last_position = self.route[environment_info.current_position - 1][0]
            if last_position == self.plans[0].goal.id:
                last_plan = heapq.heappop(self.plans)
                self.current_block = last_plan.goal
                return Event(environment_info.time + time_spent, EventType.AT_GOAL, self)
            else:
                path = path_search(environment_info.map, last_position,
                                   [self.plans[0].goal.id], [], 1, True,
                                   True)[1]

                if not path:
                    heapq.heappop(self.plans)
                    return Event(environment_info.time, EventType.IMPOSSIBLE_PLAN, self)

                self.route = [(node, {"walk"}) for node in path]

                environment_info.time += time_spent
                environment_info.current_position = 0
                return self.walk_to_stop(environment_info, False)

        self.current_block = environment_info.map.nodes[self.route[environment_info.current_position][0]]
        return self.arrive_at_stop(environment_info)

    def explore_routes(self, graph, radio, goal):

        possible_routes = routing.get_routes(graph, self.current_block, goal, radio)

        if len(possible_routes) == 0:
            return []

        max_score = float('-inf')
        best_route = None

        for estimated_time, route in possible_routes:
            score = self.calculate_route_time(estimated_time, route)
            if score > max_score:
                max_score = score
                best_route = route

        return best_route

    def arrive_at_stop(self, environment_info):
        self.arrival_at_stop = environment_info.time
        self.status = PassengerStatus.WAITING

        if environment_info.current_bus_route:
            return Event(environment_info.time + self.time_to_get_off, EventType.GET_OFF_VEHICLE, self)
        else:
            return Event(environment_info.time, EventType.AT_STOP, self)

    def search_alternative(self, environment_info):
        self.current_block = self.route[environment_info.current_position]
        return self.walk_to_stop(environment_info)

    def start_plan(self, environment_info):

        while self.plans:

            time = self.decide_departure_time(environment_info.map, environment_info.time)

            if time == - 1:
                heapq.heappop(self.plans)
                continue

            return Event(time=max(environment_info.time, self.plans[0].time - time), event_type=EventType.DEPARTURE,
                         agent=self)

        return []
