from Agents.BusDriverAgent import BusDriverAgent
from Agents.PassengerAgent import PassengerAgent


class Simulation:
    def __init__(self, agents, map, bus_list):
        """
        Initializes a Simulation object.
        Args:
            agents (list): A list of Agent objects.
            map (Map): A Map object representing the simulation map.
        """
        self.agents = agents
        self.map = map
        self.time = 0
        self.bus_list = bus_list
        self.action_list = {
            "drive": self.action_drive,
            "stop_at_bus_stop": self.action_stop_at_bus_stop,
            "go_to_the_gas_station": self.action_go_to_the_gas_station,
            "refuel": self.action_refuel,
            "back_to_route": self.action_back_to_route,
            "take_detour": self.action_take_detour
        }

    def prepare_simulation(self):
        """
        Prepares the simulation for execution.
        """
        pass

    def next_step(self):
        """
        Executes the next step of the simulation for each agent.
        """
        self.time += 1
        for agent in self.agents:
            environment = self.get_environment_info(agent)
            action = agent.decide_action(environment)
            self.execute_action(agent, action)

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
        #     "current_location": None,
        #     "traffic_signal": None,
        #     "city_map": None
        # }
        pass

    def get_environment_info_passenger(self, agent):
        """
            Retrieves the environment information for the passenger agent.
            Returns:
                dict: A dictionary containing the environment information.
        """
        pass

    def execute_action(self, agent, action):
        """
        Executes the given action for the given agent.
        Args:
            agent (Agent): The agent for which to execute the action.
            action (str): The action to execute.
        """
        if action in self.action_list:
            self.action_list[action](agent)
        else:
            print("Invalid action")

    def action_drive(self, agent):
        """
        Performs the 'drive' action for the given agent.
        Args:
            agent (Agent): The agent performing the action.
        """
        pass

    def action_stop_at_bus_stop(self, agent):
        """
        Performs the 'stop_at_bus_stop' action for the given agent.
        Args:
            agent (Agent): The agent performing the action.
        """
        pass

    def action_go_to_the_gas_station(self, agent):
        """
        Performs the 'go_to_the_gas_station' action for the given agent.
        Args:
            agent (Agent): The agent performing the action.
        """
        pass

    def action_refuel(self, agent):
        """
        Performs the 'refuel' action for the given agent.
        Args:
            agent (Agent): The agent performing the action.
        """
        pass

    def action_back_to_route(self, agent):
        """
        Performs the 'back_to_route' action for the given agent.
        Args:
            agent (Agent): The agent performing the action.
        """
        pass

    def action_take_detour(self, agent):
        """
        Performs the 'take_detour' action for the given agent.
        Args:
            agent (Agent): The agent performing the action.
        """
        pass

    def stop(self, agent):
        """
        Stops the simulation for the given agent.
        Args:
            agent (Agent): The agent performing the action.
        """
        pass