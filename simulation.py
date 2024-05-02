import heapq
import json
import logging
import random
from datetime import datetime
from pathlib import Path
from collections.abc import Iterable

import dill

from agents.bus_driver_agent import BusDriverAgent
from agents.passenger_agent import PassengerAgent
from environment.environment import DriverEnvironment, Bus, PassengerEnvironment
from events.event import Event, EventType
from gemini.llm import minimum_fuel_level
from population.generator import PopulationGenerator
from map.map_loader import MapLoader

TIME_BETWEEN_DEPARTURES = 30
WAIT_TIME = 5


class Simulation:
    def __init__(self, maps_path, population_path, population_size, data_path, bus_distributions, start_time,
                 analyzed_municipalities):
        """
        Initializes a Simulation object.
        Args:
            maps_path: path to where the maps and the files necessary to create them are stored.
            population_path: path to where the population1 and the files necessary to create it are stored.
            population_size: size of the population1.
            data_path: path to where the school quantity and universities entries are stored.
            bus_distributions: amount of buses per route
            start_time: time at which the simulation starts.
            analyzed_municipalities: municipalities to analyze.

        """

        self.events = []
        self.time = 0
        self.passengers_waiting = {}
        self.passengers_on_vehicle = {}
        self.environments = {}

        self.routes_graph = None
        self.complete_graph = None
        self.analyzed_municipalities = analyzed_municipalities
        self.initialize_maps(maps_path)

        self.population = None
        self.initialize_population(population_path, population_size)

        self.schools = {}
        self.initialize_schools(data_path)

        self.passengers = []
        self.initialize_passengers(data_path)

        self.drivers = []
        self.min_fuel_by_model = {}
        self.initialize_drivers(bus_distributions, start_time, data_path)

        now = datetime.now()
        formatted_date = now.strftime("%Y-%m-%d_%H-%M-%S")
        logging.basicConfig(
            filename=f'sim_{formatted_date}.log',
            level=logging.INFO
        )

    def initialize_maps(self, maps_path):

        loader = MapLoader(f"{maps_path}/havana.osm",
                           f"{maps_path}/municipalities.poly",
                           self.analyzed_municipalities)
        self.complete_graph, self.routes_graph = loader.load_maps(maps_path, f"{maps_path}/GAZelles.json")

    def initialize_population(self, population_path, population_size):

        generator = PopulationGenerator(population_path)
        self.population = generator.generate_population(population_size)

    def initialize_schools(self, schools_path):

        if Path(f"{schools_path}/schools.pkl").exists():
            self.schools = dill.load(open(f"{schools_path}/schools.pkl", "rb"))
            return

        with open(f"{schools_path}/schools.json", 'r') as file:
            data = json.load(file)

        school_blocks = [
            self.complete_graph.nodes[block]
            for (_, _, place_type), (block, _) in self.complete_graph.places_of_interest.items()
            if place_type == "school"
        ]

        for key, value in data.items():

            if key not in self.analyzed_municipalities:
                continue

            schools_in_municipality = {school for school in school_blocks if school.city == key
                                       and school.id in self.routes_graph.nodes}

            for stype, quantity in value.items():
                if len(schools_in_municipality) > quantity:
                    selected_schools = random.choices(list(schools_in_municipality), k=quantity)
                    schools_in_municipality.difference_update(selected_schools)
                else:
                    selected_schools = self.get_nodes_in_route(key, quantity)

                self.schools[(key, stype)] = selected_schools

        with open(f"{schools_path}/universities.json", 'r') as file:
            data = json.load(file)

        if Path(schools_path).exists():
            dill.dump(self.schools, open(f"{schools_path}/schools.pkl", 'wb'))

    def initialize_passengers(self, data_path):

        if (Path(f"{data_path}/passengers.pkl").exists() and Path(f"{data_path}/passenger_events.pkl").exists()
                and Path(f"{data_path}/passenger_environments.pkl").exists()):
            self.passengers = dill.load(open(f"{data_path}/passengers.pkl", "rb"))
            self.events = dill.load(open(f"{data_path}/passenger_events.pkl", "rb"))
            self.environments = dill.load(open(f"{data_path}/passenger_environments.pkl", "rb"))
            return

        for profile in self.population:

            if (profile["municipality"] not in self.analyzed_municipalities
                    or ("workplace_location" in profile
                        and profile["workplace_location"] not in self.analyzed_municipalities)):
                continue

            home_block = self.get_node_in_route(profile["municipality"])

            workplace, other_block = self.get_workplace_and_other_block(profile)

            plans = PassengerAgent.create_plans(profile, home_block, workplace, other_block, self.time)

            passenger = PassengerAgent(profile, plans, home_block, workplace, home_block)

            time = passenger.decide_departure_time(self.routes_graph, self.time)

            if time == -1:
                continue

            self.passengers.append(passenger)

            heapq.heappush(self.events, Event(time=time,
                                              event_type=EventType.DEPARTURE,
                                              agent=passenger))

            environment = PassengerEnvironment(time=time, map=self.routes_graph, current_position=0,
                                               bus_at_stop="", current_bus_route="", current_driver="")
            self.environments[f"passenger:{passenger.id}"] = environment

            if Path(data_path).exists():
                dill.dump(self.passengers, open(f"{data_path}/passengers.pkl", 'wb'))
                dill.dump(self.events, open(f"{data_path}/passenger_events.pkl", 'wb'))
                dill.dump(self.environments, open(f"{data_path}/passenger_environments.pkl", 'wb'))

    def get_workplace_and_other_block(self, profile):

        if profile["employment_status"] == "occupied":

            workplace = self.get_node_in_route(profile["workplace_location"])
            other_block = None
        elif profile["employment_status"] == "student":
            if profile["student_type"] == "bachelor":
                if profile["bachelor_type"] == "medicine":
                    workplace = self.get_node_in_route(profile["workplace_location"])
                else:
                    workplace = self.schools.get(profile["bachelor_type"], None)
            else:
                workplace = random.choice(
                    self.schools.get((profile["workplace_location"], profile["student_type"]), []))
            other_block = None
        else:
            workplace = None
            other_block = self.routes_graph.nodes[random.choice(list(self.routes_graph.nodes.keys()))]

        return workplace, other_block

    def get_node_in_route(self, municipality):

        node = None
        while node not in self.routes_graph.nodes:
            node = random.choice(self.complete_graph.nodes_by_municipality[municipality])

        return self.complete_graph.nodes[node]

    def get_nodes_in_route(self, municipality, quantity):
        result = []

        current_quantity = quantity
        while current_quantity > 0:
            choices = random.choices(
                self.complete_graph.nodes_by_municipality[municipality], k=quantity
            )

            result += [self.complete_graph.nodes[node] for node in choices if node in self.routes_graph.nodes]

            current_quantity = quantity - len(result)

        return result

    def initialize_drivers(self, bus_distributions, start_time, data_path):

        if (Path(f"{data_path}/drivers.pkl").exists() and Path(f"{data_path}/drivers_events.pkl").exists()
                and Path(f"{data_path}/drivers_environments.pkl").exists()):

            if dill.load(open(f"{data_path}/bus_distributions.pkl", "rb")) == bus_distributions:
                self.drivers = dill.load(open(f"{data_path}/drivers.pkl", "rb"))
                self.events.extend(dill.load(open(f"{data_path}/driver_events.pkl", "rb")))
                self.environments |= dill.load(open(f"{data_path}/driver_environments.pkl", "rb"))
            return

        gas_stations_blocks = [
            block
            for (_, _, place_type), (block, _) in self.complete_graph.places_of_interest.items()
            if place_type == "school"
        ]

        for ref, quantity in bus_distributions.items():

            if ref not in self.complete_graph.bus_routes:
                continue

            route = self.complete_graph.bus_routes[ref]

            for i in range(quantity):
                driver = BusDriverAgent(route, WAIT_TIME)
                self.drivers.append(driver)
                heapq.heappush(self.events, Event(time=start_time + i * TIME_BETWEEN_DEPARTURES,
                                                  event_type=EventType.DEPARTURE,
                                                  agent=driver))

                model, max_fuel, consumption_rate, capacity = ("MAZ-105", 300, 0.4, 160) if "P" in route.name else ("MAZ-103T", 160, 0.3, 80)

                if model in self.min_fuel_by_model:
                    min_fuel = self.min_fuel_by_model[model]
                else:
                    min_fuel = minimum_fuel_level(model, max_fuel)
                    self.min_fuel_by_model[model] = min_fuel

                environment = DriverEnvironment(time=start_time + i * TIME_BETWEEN_DEPARTURES,
                                                current_bus=Bus(max_fuel, max_fuel, min_fuel, consumption_rate,
                                                                capacity, 0, model),
                                                current_position=0, last_element_index=-1, map=self.routes_graph,
                                                gas_stations=gas_stations_blocks,
                                                onboarding=False,
                                                obstacle_ahead=False,
                                                obstacles_blocks=[])

                self.environments[f"driver:{driver.id}"] = environment

        if Path(data_path).exists():
            dill.dump(bus_distributions, open(f"{data_path}/bus_distributions.pkl", 'wb'))
            dill.dump(self.drivers, open(f"{data_path}/drivers.pkl", 'wb'))
            dill.dump([event for event in self.events if isinstance(event.agent, BusDriverAgent)],
                      open(f"{data_path}/driver_events.pkl", 'wb'))
            dill.dump([env for env in self.environments if isinstance(env, DriverEnvironment)],
                      open(f"{data_path}/driver_environments.pkl", 'wb'))

    def run(self):

        while self.events and self.time < 1440:
            current_event = heapq.heappop(self.events)

            self.time = current_event.time
            agent = current_event.agent

            env = self.get_environment_info(agent)
            env.time = current_event.time

            undefined = "undefined"
            logging.info(
                f"{current_event.time}:{current_event.event_type}:{current_event.agent.id}:"
                f"{env.current_driver if isinstance(env, PassengerEnvironment) else undefined}")

            if current_event.event_type == EventType.BOARD_VEHICLE:

                driver_env = self.environments[f"driver:{env.current_driver}"]

                if driver_env.current_bus.space():

                    current_block_id = agent.current_route[driver_env.current_position].id
                    waiting_passengers = self.passengers_waiting.get(current_block_id, [])

                    for passenger in waiting_passengers:
                        passenger_env = self.get_environment_info(passenger)

                        passenger_env.time = self.time
                        passenger_env.bus_at_stop = env.current_bus_route
                        passenger_env.current_driver = env.current_driver

                        action = passenger.think(current_event, passenger_env)
                        event = passenger.take_action(action, passenger_env)

                        if event.event_type == EventType.BOARD_VEHICLE:
                            driver_env.current_bus.count += 1
                            heapq.heappush(self.events, event)
                            break
                    else:
                        driver_env.onboarding = False
                else:
                    driver_env.onboarding = False

            if current_event.event_type == EventType.FUEL_SPENT:
                env.current_bus.fuel -= env.current_bus.consumption_rate * agent.current_route[env.current_position]

            if current_event.event_type == EventType.BUS_STOP and not env.onboarding:

                passengers_on_vehicle = self.passengers_on_vehicle.get(agent.id, [])

                last_leave_time = env.time

                for passenger in passengers_on_vehicle:
                    passenger_env = self.get_environment_info(passenger)

                    action = passenger.think(current_event, passenger_env)
                    event = passenger.take_action(action, passenger_env)

                    heapq.heappush(self.events, event)

                    if event.event_type == EventType.GET_OFF_VEHICLE:
                        last_leave_time = event.time

                if env.current_bus.space():

                    current_block_id = agent.current_route[env.current_position].id
                    waiting_passengers = self.passengers_waiting.get(current_block_id, [])

                    for passenger in waiting_passengers:
                        passenger_env = self.get_environment_info(passenger)

                        passenger_env.time = last_leave_time
                        passenger_env.bus_at_stop = agent.route.name
                        passenger_env.current_driver = agent.id

                        action = passenger.think(current_event, passenger_env)
                        event = passenger.take_action(action, passenger_env)

                        if event.event_type == EventType.BOARD_VEHICLE:
                            env.current_bus.count += 1
                            env.onboarding = True
                            heapq.heappush(self.events, event)
                            break

            action = agent.think(current_event, env)
            events = agent.take_action(action, env)

            if not isinstance(events, Iterable):
                events = [events]

            for event in events:
                heapq.heappush(self.events, event)

    def get_environment_info(self, agent):
        if isinstance(agent, BusDriverAgent):
            return self.get_driver_environment_info(agent)

        if isinstance(agent, PassengerAgent):
            return self.get_passenger_environment_info(agent)

        raise TypeError(f"Agent {agent} does not implement get_environment_info")

    def get_driver_environment_info(self, agent: BusDriverAgent):
        """
        Retrieves the environment information for the bus driver agent.
        Returns:
            DriverEnvironment
        """

        return self.environments[f"driver:{agent.id}"]

    def get_passenger_environment_info(self, agent: PassengerAgent):
        """
            Retrieves the environment information for the passenger agent.
            Returns:
                PassengerEnvironment: A dictionary containing the environment information.
        """
        return self.environments[f"passenger:{agent.id}"]

    def stop(self):
        pass
