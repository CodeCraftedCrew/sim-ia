import heapq
import json
import random
from pathlib import Path

import dill

from Agents.BusDriverAgent import BusDriverAgent
from Agents.PassengerAgent import PassengerAgent
from events.event import Event, EventType
from population.generator import PopulationGenerator
from map.map_loader import MapLoader

TIME_BETWEEN_DEPARTURES = 30
WAIT_TIME = 5


class Simulation:
    def __init__(self, maps_path, population_path, population_size, school_path, bus_distributions, start_time):
        """
        Initializes a Simulation object.
        Args:
            maps_path: path to where the maps and the files necessary to create them are stored.
            population_path: path to where the population1 and the files necessary to create it are stored.
            population_size: size of the population1.
            school_path: path to where the school quantity and universities entries are stored.
            bus_distributions: amount of buses per route
            start_time: time at which the simulation starts.

        """

        self.events = []
        self.time = 0

        self.routes_graph = None
        self.complete_graph = None
        self.initialize_maps(maps_path)

        self.population = None
        self.initialize_population(population_path, population_size)

        self.schools = {}
        self.initialize_schools(school_path)

        self.passengers = []
        self.initialize_passengers()

        self.drivers = []
        self.initialize_drivers(bus_distributions, start_time)

        self.run()

    def initialize_maps(self, maps_path):

        loader = MapLoader(f"{maps_path}/havana.osm",
                           f"{maps_path}/municipalities.poly")
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

            schools_in_municipality = {school for school in school_blocks if school.city == key}

            for stype, quantity in value.items():
                if len(schools_in_municipality) > quantity:
                    selected_schools = random.choices(list(schools_in_municipality), k=quantity)
                    schools_in_municipality.difference_update(selected_schools)
                else:
                    selected_schools = random.choices(
                        self.complete_graph.nodes_by_municipality[key], quantity
                    )

                self.schools[(key, stype)] = selected_schools

        with open(f"{schools_path}/universities.json", 'r') as file:
            data = json.load(file)

        for key, value in data.items():
            self.schools[key] = [self.complete_graph.nodes[key] for key in value]

        if Path(schools_path).exists():
            dill.dump(self.schools, open(f"{schools_path}/schools.pkl", 'wb'))

    def initialize_passengers(self):
        for profile in self.population:
            home_block = self.complete_graph.nodes[random.choice(self.complete_graph.nodes_by_municipality[profile["municipality"]])]

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

    def get_workplace_and_other_block(self, profile):

        if profile["employment_status"] == "occupied":
            workplace = self.complete_graph.nodes[random.choice(self.complete_graph.nodes_by_municipality[profile["workplace_location"]])]
            other_block = None
        elif profile["employment_status"] == "student":
            if profile["student_type"] == "bachelor":
                if profile["bachelor_type"] == "medicine":
                    workplace = [
                        random.choice(self.complete_graph.nodes_by_municipality[profile["workplace_location"]])]
                else:
                    workplace = self.schools.get(profile["bachelor_type"], None)
            else:
                workplace = random.choice(
                    self.schools.get((profile["workplace_location"], profile["student_type"]), []))
            other_block = None
        else:
            workplace = None
            other_block = self.complete_graph.nodes[random.choice(list(self.complete_graph.nodes.keys()))]

        return workplace, other_block

    def initialize_drivers(self, bus_distributions, start_time):

        for route, quantity in bus_distributions.items():

            for i in range(quantity):
                driver = BusDriverAgent(route, WAIT_TIME)
                self.drivers.append(driver)
                heapq.heappush(self.events, Event(time=start_time + i * TIME_BETWEEN_DEPARTURES,
                                                  event_type=EventType.DEPARTURE,
                                                  agent=driver))

    def run(self):

        while self.events:
            current_event = heapq.heappop(self.events)
            agent = current_event.agent

            action = agent.think(current_event, self.get_environment_info(agent))
            events = agent.take_action(action)

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
            dict: A dictionary containing the environment information.
        """
        # environment = {
        #     "bus_max_capacity": None,
        #     "bus_current_capacity": None,
        #     "at_bus_stop": None,
        #     "at_gas_station": None,
        #     "detour_ahead": None,
        #     "accident_ahead": None,
        #     "fuel": None,
        #     "current_location": [route[i], numero entre 0 y route[i].length)],
        #     "traffic_signal": None,
        #     "city_map": None
        #     "bus_speed": None
        # }
        pass

    def get_passenger_environment_info(self, agent: PassengerAgent):
        """
            Retrieves the environment information for the passenger agent.
            Returns:
                dict: A dictionary containing the environment information.
        """
        pass
