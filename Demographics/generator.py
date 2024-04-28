import json
import random
from fuzzy_system import FuzzySystemMoney, FuzzySystemWaitingTime

class PopulationGenerator:

    def __init__(self, data_file):
        """
        Initializes the PopulationGenerator instance with the data from the specified file.
        Args:
            data_file (str): The path of the JSON data file.
        """
        self.data = self.load_data(data_file)
        self.cumulative_ranges = self.calculate_cumulative_ranges()
        self.fuzzy_system_money = FuzzySystemMoney()
        self.fuzzy_system_waiting_time = FuzzySystemWaitingTime()

    def load_data(self, file_path):
        """
        Loads data from a JSON file.
        Args:
            file_path (str): The path of the JSON file.
        Returns:
            dict: The data loaded from the JSON file.
        """
        with open(file_path, 'r') as file:
            data = json.load(file)
        return data

    def calculate_cumulative_ranges(self):
        """
        Calculates the cumulative probability ranges for each attribute in the data.
        Returns:
            dict: A dictionary of the cumulative probability ranges.
        """
        cumulative_ranges = {}
        
        for attribute_name, attribute_data in self.data.items():
        
            if isinstance(attribute_data, dict):
                cumulative_range = {}
        
                if all(isinstance(v, (int, float)) for v in attribute_data.values()):
                    total_probability = sum(attribute_data.values())
                    cumulative_prob = 0
        
                    for key, value in attribute_data.items():
                        cumulative_prob += value / total_probability
                        cumulative_range[key] = cumulative_prob
        
                else:
        
                    for key, value in attribute_data.items():
                        sub_cumulative_range = {}
                        total_sub_probability = sum(value.values())
                        sub_cumulative_prob = 0
        
                        for sub_key, sub_value in value.items():
                            sub_cumulative_prob += sub_value / total_sub_probability
                            sub_cumulative_range[sub_key] = sub_cumulative_prob
        
                        cumulative_range[key] = sub_cumulative_range
        
                cumulative_ranges[attribute_name] = cumulative_range
        
        return cumulative_ranges


    def generate_attribute(self, attribute_name, conditional_attribute=None):
        """
        Generates a random value for a given attribute.
        Args:
            attribute_name (str): The name of the attribute for which to generate the value.
            conditional_attribute (str): The value of the conditional attribute (if any).
        Returns:
            str: The generated value for the attribute.
        """
        cumulative_range = self.cumulative_ranges[attribute_name]
        
        if conditional_attribute:
        
            conditional_range = cumulative_range[conditional_attribute]
            rand_value = random.random()
        
            for key, value in conditional_range.items():        
                if rand_value <= value:
                    return key
        
        else:
        
            rand_value = random.random()        
            for key, value in cumulative_range.items():
                if rand_value <= value:
                    return key

    def generate_person(self):
        """
        Generates the data for a person.
        Returns:
            dict: A dictionary containing the generated data for a person.
        """
        person = {}

        person['municipality'] = self.generate_attribute('municipality')

        person['employment_status'] = self.generate_attribute('employment_status', person['municipality'])

        if person['employment_status'] == "occupied" or person['employment_status'] == "student":
            person['workplace_location'] = self.generate_attribute('workplace_location', person['municipality'])

        person['age'] = self.generate_attribute('age', person['employment_status'])

        person['money'] = self.fuzzy_system_money.infer_money(person['age'], person['municipality'])

        person['max_waiting_time'] = self.fuzzy_system_waiting_time.infer_max_waiting_time(person['age'], person['money'], person['employment_status'])

        return person

    def generate_population(self, n):
        """
        Generates a population of people.
        Args:
            n (int): The size of the population to generate.
        Returns:
            list: A list of dictionaries, where each dictionary represents the data of a person.
        """
        population = []
 
        for _ in range(n):
            population.append(self.generate_person())
        return population