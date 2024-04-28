import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl

class FuzzySystemMoney:
    
    def __init__(self):
        """
        Initializes the Fuzzy Logic System instance with the fuzzy logic system components.
        """
        self.age = ctrl.Antecedent(np.arange(15, 101, 1), 'age')
        self.location = ctrl.Antecedent(np.arange(0, 101, 1), 'location')
        self.money = ctrl.Consequent(np.arange(0, 1001, 1), 'money')

        self.age['15-19'] = fuzz.trapmf(self.age.universe, [15, 15, 19, 20])
        self.age['20-24'] = fuzz.trapmf(self.age.universe, [20, 20, 24, 25])
        self.age['25-39'] = fuzz.trapmf(self.age.universe, [25, 25, 39, 40])
        self.age['40-54'] = fuzz.trapmf(self.age.universe, [40, 40, 54, 55])
        self.age['55-64'] = fuzz.trapmf(self.age.universe, [55, 55, 64, 65])
        self.age['65+'] = fuzz.trapmf(self.age.universe, [65, 65, 101, 101])

        self.location['Playa'] = fuzz.trimf(self.location.universe, [70, 100, 100])
        self.location['Plaza'] = fuzz.trimf(self.location.universe, [70, 100, 100])
        self.location['Centro Habana'] = fuzz.trimf(self.location.universe, [40, 70, 100])
        self.location['Habana Vieja'] = fuzz.trimf(self.location.universe, [40, 70, 100])
        self.location['Regla'] = fuzz.trimf(self.location.universe, [25, 50, 75])
        self.location['Habana del Este'] = fuzz.trimf(self.location.universe, [25, 50, 75])
        self.location['Guanabacoa'] = fuzz.trimf(self.location.universe, [25, 50, 75])
        self.location['San Miguel del Padron'] = fuzz.trimf(self.location.universe, [25, 50, 75])
        self.location['Diez de Octubre'] = fuzz.trimf(self.location.universe, [25, 50, 75])
        self.location['Cerro'] = fuzz.trimf(self.location.universe, [10, 35, 60])
        self.location['Marianao'] = fuzz.trimf(self.location.universe, [10, 35, 60])
        self.location['La Lisa'] = fuzz.trimf(self.location.universe, [10, 35, 60])
        self.location['Boyeros'] = fuzz.trimf(self.location.universe, [0, 20, 40])
        self.location['Arroyo Naranjo'] = fuzz.trimf(self.location.universe, [0, 20, 40])
        self.location['Cotorro'] = fuzz.trimf(self.location.universe, [0, 20, 40])

        self.money['low'] = fuzz.trimf(self.money.universe, [0, 0, 500])
        self.money['medium'] = fuzz.trimf(self.money.universe, [250, 500, 750])
        self.money['high'] = fuzz.trimf(self.money.universe, [500, 1000, 1000])

        self.rules = [
            ctrl.Rule(self.age['15-19'] | self.age['65+'], self.money['low']),
            ctrl.Rule(self.location['Playa'] | self.location['Plaza'] | self.location['Centro Habana'] | self.location['Habana Vieja'], self.money['high']),
            ctrl.Rule(self.location['Cerro'] | self.location['Marianao'] | self.location['La Lisa'], self.money['medium']),
            ctrl.Rule(self.location['Regla'] | self.location['Habana del Este'] | self.location['Guanabacoa'] | self.location['San Miguel del Padron'] | self.location['Diez de Octubre'] | self.location['Boyeros'] | self.location['Arroyo Naranjo'] | self.location['Cotorro'], self.money['low']),
            ctrl.Rule(self.age['20-24'] | self.age['25-39'] | self.age['40-54'] | self.age['55-64'], self.money['medium'])
        ]

        self.control_system = ctrl.ControlSystem(self.rules)
        self.control_system_simulation = ctrl.ControlSystemSimulation(self.control_system)

    def infer_money(self, age_range_str, location_str):
        """
        Infers the money level based on the specified age range and location.
        Args:
            age_range_str (str): The age range string (e.g., '15-19').
            location_str (str): The location string (e.g., 'Playa').
        Returns:
            int: The inferred money level.
        """
        age_value = map_age_range(age_range_str)
        location_value = map_location(location_str)

        self.control_system_simulation.input['age'] = age_value
        self.control_system_simulation.input['location'] = location_value

        self.control_system_simulation.compute()

        inferred_money = self.control_system_simulation.output['money']

        if inferred_money <= 250:
            return np.random.randint(1, 101) 
        elif inferred_money <= 500:
            return np.random.randint(101, 301)
        else:
            return np.random.randint(301, 1000)
        
    
class FuzzySystemWaitingTime:

    def __init__(self):
        """
        Initializes the Fuzzy Logic System instance with the fuzzy logic system components.
        """
        self.age = ctrl.Antecedent(np.arange(15, 101, 1), 'age')
        self.money = ctrl.Antecedent(np.arange(0, 1001, 1), 'money')
        self.employment_status = ctrl.Antecedent(np.arange(0, 101, 1), 'employment_status')
        self.max_waiting_time = ctrl.Consequent(np.arange(0, 101, 1), 'max_waiting_time')

        self.age['15-19'] = fuzz.trapmf(self.age.universe, [15, 15, 19, 20])
        self.age['20-24'] = fuzz.trapmf(self.age.universe, [20, 20, 24, 25])
        self.age['25-39'] = fuzz.trapmf(self.age.universe, [25, 25, 39, 40])
        self.age['40-54'] = fuzz.trapmf(self.age.universe, [40, 40, 54, 55])
        self.age['55-64'] = fuzz.trapmf(self.age.universe, [55, 55, 64, 65])
        self.age['65+'] = fuzz.trapmf(self.age.universe, [65, 65, 101, 101])

        self.employment_status['occupied'] = fuzz.trimf(self.employment_status.universe, [0, 50, 100])  
        self.employment_status['unoccupied'] = fuzz.trimf(self.employment_status.universe, [0, 0, 50])   
        self.employment_status['student'] = fuzz.trimf(self.employment_status.universe, [0, 50, 100])    
        self.employment_status['other'] = fuzz.trimf(self.employment_status.universe, [0, 0, 100])       

        self.max_waiting_time['low'] = fuzz.trimf(self.max_waiting_time.universe, [0, 0, 50])
        self.max_waiting_time['medium'] = fuzz.trimf(self.max_waiting_time.universe, [25, 50, 75])
        self.max_waiting_time['high'] = fuzz.trimf(self.max_waiting_time.universe, [50, 100, 100])

        self.money['low'] = fuzz.trimf(self.money.universe, [0, 0, 500])
        self.money['medium'] = fuzz.trimf(self.money.universe, [250, 500, 750])
        self.money['high'] = fuzz.trimf(self.money.universe, [500, 1000, 1000])

        self.rules = [            
            ctrl.Rule(self.employment_status['occupied'] | self.employment_status['student'], self.max_waiting_time['low']),
            ctrl.Rule(self.employment_status['unoccupied'], self.max_waiting_time['high']), 
            ctrl.Rule(self.employment_status['other'], self.max_waiting_time['medium']),  
            ctrl.Rule(self.money['low'], self.max_waiting_time['high']),  
            ctrl.Rule(self.money['high'], self.max_waiting_time['low']), 
            ctrl.Rule(self.money['medium'], self.max_waiting_time['medium']),
            ctrl.Rule(self.age['15-19'] | self.age['20-24'], self.max_waiting_time['low']),  
            ctrl.Rule(self.age['65+'], self.max_waiting_time['high']),
            ctrl.Rule(self.age['25-39'] | self.age['40-54'] | self.age['55-64'], self.max_waiting_time['medium'])
        ]

        self.control_system = ctrl.ControlSystem(self.rules)
        self.control_system_simulation = ctrl.ControlSystemSimulation(self.control_system)

    def infer_max_waiting_time(self, age_range_str, money_level_str, employment_status_str):  
        """
        Infers the maximum waiting time based on the specified inputs.
        Args:
            age_range_str (str): The age range string (e.g., '15-19').
            money_level_str (str): The money level string (e.g., 'low', 'medium', 'high').
            employment_status_str (str): The employment status string (e.g., 'occupied', 'unoccupied', 'student', 'other').
        Returns:
            int: The inferred maximum waiting time.
        """
        age_value = map_age_range(age_range_str)
        money_value = int(money_level_str)
        employment_status_value = map_employment_status(employment_status_str)

        self.control_system_simulation.input['age'] = age_value
        self.control_system_simulation.input['money'] = money_value
        self.control_system_simulation.input['employment_status'] = employment_status_value 

        self.control_system_simulation.compute()

        max_waiting_time = self.control_system_simulation.output['max_waiting_time']

        if max_waiting_time <= 45:
            return np.random.randint(30, 60) 
        elif max_waiting_time <= 75:
            return np.random.randint(60, 90) 
        else:
            return np.random.randint(90, 200) 


def map_age_range(age_range_str):
    """
    Maps age range string to its corresponding numerical value.
    Args:
    age_range_str (str): The age range string.
    Returns:
    int: The numerical value corresponding to the age range.
    """
    age_range_map = {
        '15-19': 17,
        '20-24': 22,
        '25-39': 32,
        '40-54': 47,
        '55-64': 59,
        '65+': 75
    }
    return age_range_map.get(age_range_str, 0)

def map_location(location_str):
    """
    Maps location string to its corresponding numerical value.
    Args:
    location_str (str): The location string.
    Returns:
    int: The numerical value corresponding to the location.
    """
    location_map = {
        'Playa': 100,
        'Plaza': 100,
        'Centro Habana': 100,
        'Habana Vieja': 100,
        'Regla': 66,
        'Habana del Este': 66,
        'Guanabacoa': 66,
        'San Miguel del Padron': 66,
        'Diez de Octubre': 66,
        'Cerro': 66,
        'Marianao': 66,
        'La Lisa': 66,
        'Boyeros': 50,
        'Arroyo Naranjo': 50,
        'Cotorro': 50
    }
    return location_map.get(location_str, 0)

def map_employment_status(employment_status_str):
    """
    Maps employment status string to its corresponding numerical value.
    Args:
        employment_status_str (str): The employment status string.
    Returns:
        int: The numerical value corresponding to the employment status.
    """
    employment_status_map = {
        'occupied': 20,   
        'student': 40,
        'unoccupied': 60,
        'other': 80     
    }
    return employment_status_map.get(employment_status_str, 0)