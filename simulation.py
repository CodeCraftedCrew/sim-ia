import json
import random
from pathlib import Path

import dill

from Agents.BusDriverAgent import BusDriverAgent
from Agents.PassengerAgent import PassengerAgent
from population.generator import PopulationGenerator
from map.map_loader import MapLoader


class Simulation:
    def __init__(self, maps_path, population_path, population_size, school_path):
        """
        Initializes a Simulation object.
        Args:
            maps_path: path to where the maps and the files necessary to create them are stored.
            population_path: path to where the population1 and the files necessary to create it are stored.
            population_size: size of the population1.
            school_path: path to where the school quantity and universities entries are stored.

        """

        self.routes_graph = None
        self.complete_graph = None
        self.initialize_maps(maps_path)

        self.population = None
        self.initialize_population(population_path, population_size)

        self.schools = {}
        self.initialize_schools(school_path)

        self.passengers = []
        self.initialize_passengers()

        self.agents = []
        self.map = map
        self.time = 0
        self.bus_list = []
        self.action_list = {
            "drive": self.action_drive,
            "stop_at_bus_stop": self.action_stop_at_bus_stop,
            "refuel": self.action_refuel,
            "take_detour": self.action_take_detour,
            "stop": self.action_stop,
            "traffic_light": self.action_traffic_light,
            "give_way": self.action_give_way,
            "crossing": self.action_crossing,
            "train_rail": self.action_train_rail,
        }
        self.locations = []
        self.bus_stops = {}
        self.bus_fuel = []
        self.number_steps = 1

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
            home_block = random.choice(self.complete_graph.nodes_by_municipality[profile["municipality"]])

            workplace, other_block = self.get_workplace_and_other_block(profile)

            plans = PassengerAgent.create_plans(profile, home_block, workplace, other_block)

            passenger = PassengerAgent(profile, plans, home_block, workplace, home_block)

            self.passengers.append(passenger)

    def get_workplace_and_other_block(self, profile):

        if profile["employment_status"] == "occupied":
            workplace = [random.choice(self.complete_graph.nodes_by_municipality[profile["workplace_location"]])]
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

    def prepare_simulation(self):
        """
        Prepares the simulation for execution.
        """
        pass

    def next_step(self):
        """
        Executes the next step of the simulation for each agent.
        """
        self.time += self.number_steps
        for i in range(0, len(self.agents)):
            environment = self.get_environment_info(self.agents[i])
            action = self.agents[i].decide_action(environment)
            self.execute_action(i, action)

    def get_environment_info(self, agent):
        """
        Retrieves the environment information for the given agent.
        Args:
            agent (Agent): The agent for which to retrieve the environment information.
        Returns:
            dict: A dictionary containing the environment information.
        """
        if agent is BusDriverAgent:
            self.get_environment_info_bus_driver(agent)
        elif agent is PassengerAgent:
            self.get_environment_info_passenger(agent)

    def get_environment_info_bus_driver(self, agent):
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

    def get_environment_info_passenger(self, agent):
        """
            Retrieves the environment information for the passenger agent.
            Returns:
                dict: A dictionary containing the environment information.
        """
        pass

    def execute_action(self, agentID, action):
        """
        Executes the given action for the given agent.
        Args:
            agent (Agent): The agent for which to execute the action.
            action (str): The action to execute.
        """
        if action in self.action_list:
            self.action_list[action](agentID)
        else:
            print("Invalid action")

    def action_drive(self, agentID):
        """
        Performs the 'drive' action for the given agent.
        Args:
            agentID (int): The ID of the agent performing the action.
        """
        current_location = self.locations[agentID]
        current_route = self.agent[agentID].current_route
        bus_speed = self.environment["bus_speed"]
        distance = (bus_speed * self.number_steps / 3600) * 1000  # Convert from km to m

        if current_location[1] + distance < current_location[0].length:
            current_location[1] += distance
        else:
            current_location[0] = current_route[current_route.index(current_location[0]) + 1]
            current_location[1] = distance - (current_location[0].length - current_location[1])

        self.bus_fuel[agentID] -= distance * 0.0002
        self.locations[agentID] = current_location

    def action_stop_at_bus_stop(self, agentID):
        """
        Performs the 'stop_at_bus_stop' action for the given agent.
        Args:
            agentID (int): The ID of the agent performing the action.
        """
        current_location = self.locations[agentID]
        bus_stop_position = next(
            (element.position for element in current_location[0].elements if element.type == "BUS_STOP"), None)
        if bus_stop_position is None:
            print("There is no bus stop in the block")
            return
        distance_to_bus_stop = current_location[1] - bus_stop_position

        if distance_to_bus_stop <= 10:
            self.bus_stops[(current_location[0], bus_stop_position)] = True
            self.locations[agentID] = [current_location[0], bus_stop_position]

    def action_refuel(self, agentID):
        """
        Performs the 'refuel' action for the given agent.
        Args:
            agentID (int): The ID of the agent performing the action.
        """
        self.bus_fuel[agentID] = 100

    def action_take_detour(self, agentID):
        """
        Performs the 'take_detour' action for the given agent.
        Args:
            agentID (int): The ID of the agent performing the action.
        """
        pass

    def action_stop(self, agentID):
        """
        Performs the 'stop' action for the given agent.
        Args:
            agentID (int): The ID of the agent performing the action.
        """
        pass

    def action_traffic_light(self, agentID):
        """
        Performs the 'traffic_light' action for the given agent.
        Args:
            agentID (int): The ID of the agent performing the action.
        """
        pass

    def action_give_way(self, agentID):
        """
        Performs the 'give_way' action for the given agent.
        Args:
            agentID (int): The ID of the agent performing the action.
        """
        pass

    def action_crossing(self, agentID):
        """
        Performs the 'crossing' action for the given agent.
        Args:
            agentID (int): The ID of the agent performing the action.
        """
        pass

    def action_train_rail(self, agentID):
        """
        Performs the 'train_rail' action for the given agent.
        Args:
            agentID (int): The ID of the agent performing the action.
        """
        pass

    def stop(self, agent):
        """
        Stops the simulation for the given agent.
        Args:
            agent (Agent): The agent performing the action.
        """
        pass
