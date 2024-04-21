import random

class Person:
    def __init__(self, attributes):
        self.attributes = attributes

class DemographicGenerator:
    def __init__(self):
        self.demographic_distributions = {
            'age': {'0-4': 0.043, '5-9': 0.052, '10-14': 0.049, '15-19': 0.049, '20-24':0.06, '25-29':0.062, '30-34':0.074, '35-39':0.067, '40-44':0.053, '45-49':0.069, '50-54':0.083, '55-59':0.096, '60-64':0.07, '65+':0.166},
            'gender': {'Male': 0.47, 'Female': 0.53},
            'location': {'Playa': 0.083, 'Plaza de la Revolución': 0.065, 'Centro Habana': 0.061, 'La Habana Vieja': 0.037, 'Regla': 0.02, 'La Habana del Este': 0.081, 'Guanabacoa': 0.06, 'San Miguel del Padrón': 0.075, 'Diez de Octubre': 0.093, 'Cerro': 0.058, 'Marianao': 0.062, 'La Lisa': 0.068, 'Boyeros': 0.095, 'Arroyo Naranjo': 0.096, 'Cotorro': 0.038},
            'money': {
                '0-4': {'low': 0.9, 'medium': 0.05, 'high': 0.05},
                '5-9': {'low': 0.6, 'medium': 0.3, 'high': 0.1},
                '10-14': {'low': 0.3, 'medium': 0.6, 'high': 0.1},
                '15-19': {'low': 0.6, 'medium': 0.3, 'high': 0.1},
                '20-24': {'low': 0.3, 'medium': 0.6, 'high': 0.1},
                '25-29': {'low': 0.1, 'medium': 0.8, 'high': 0.1},
                '30-34': {'low': 0.1, 'medium': 0.8, 'high': 0.1},
                '35-39': {'low': 0.1, 'medium': 0.8, 'high': 0.1},
                '40-44': {'low': 0.1, 'medium': 0.8, 'high': 0.1},
                '45-49': {'low': 0.1, 'medium': 0.8, 'high': 0.1},
                '50-54': {'low': 0.1, 'medium': 0.8, 'high': 0.1},
                '55-59': {'low': 0.1, 'medium': 0.8, 'high': 0.1},
                '60-64': {'low': 0.1, 'medium': 0.8, 'high': 0.1},
                '65+': {'low': 0.4, 'medium': 0.5, 'high': 0.1},
            },
            #hacer travel_goal más accurated
            'travel_goal': {'Playa': 0.1, 'Plaza de la Revolución': 0.1, 'Centro Habana': 0.1, 'La Habana Vieja': 0.1, 'Regla': 0.1, 'La Habana del Este': 0.1, 'Guanabacoa': 0.1, 'San Miguel del Padrón': 0.1, 'Diez de Octubre': 0.1, 'Cerro': 0.1, 'Marianao': 0.1, 'La Lisa': 0.1, 'Boyeros': 0.1, 'Arroyo Naranjo': 0.1, 'Cotorro': 0.1},
            'max_waiting_time': {'low': {'low': 0.9, 'medium': 0.6, 'high': 0.3},
                             'medium': {'low': 0.05, 'medium': 0.3, 'high': 0.6},
                             'high': {'low': 0.05, 'medium': 0.1, 'high': 0.1}}
        }

    def alter_distribution(self, attribute, new_distribution):

        if attribute in self.demographic_distributions:
        
            if isinstance(new_distribution, dict):
                self.demographic_distributions[attribute].update(new_distribution)
        
            else:
                raise ValueError("New distribution must be a dictionary.")
        
        else:
            raise ValueError(f"No distribution defined for attribute '{attribute}'")

    def generate_demographic_data(self, attribute, current_age=None, current_money_category=None):
        
        distribution = self.demographic_distributions.get(attribute)
        
        if not distribution:
            raise ValueError(f"No distribution defined for attribute '{attribute}'")

        if attribute in ['age', 'gender', 'location', 'travel_goal']:
            return random.choices(list(distribution.keys()), weights=list(distribution.values()))[0]
        
        elif attribute == 'money':
        
            if not current_age:
                raise ValueError("Current age must be provided for generating money category.")
        
            age_distribution = self.demographic_distributions['age']
            age_category = current_age if current_age in age_distribution else random.choices(list(age_distribution.keys()), weights=list(age_distribution.values()))[0]
            money_distribution = self.demographic_distributions['money'].get(age_category)
        
            if not money_distribution:
                raise ValueError(f"No money distribution defined for age category '{age_category}'")
        
            return random.choices(list(money_distribution.keys()), weights=list(money_distribution.values()))[0]
        
        elif attribute == 'max_waiting_time':
        
            if not current_money_category:
                raise ValueError("Current money category must be provided for generating waiting time.")
        
            max_waiting_time_distribution = self.demographic_distributions['max_waiting_time'].get(current_money_category.lower())
        
            if not max_waiting_time_distribution:
                raise ValueError(f"No waiting time distribution defined for money category '{current_money_category}'")
        
            return random.choices(['low', 'medium', 'high'], weights=list(max_waiting_time_distribution.values()))[0]
        
        else:
            raise ValueError("Attribute not supported for demographic data generation.")

    def generate_person_list(self, sample_size):
        
        person_list = []
        
        for _ in range(sample_size):
        
            attributes = {}
            current_age = None
            current_money_category = None
        
            for attribute in self.demographic_distributions.keys():
                if attribute == 'age':
                    attributes[attribute] = current_age = self.generate_demographic_data(attribute)
                elif attribute == 'money':
                    attributes[attribute] = current_money_category = self.generate_demographic_data(attribute, current_age=current_age)
                elif attribute == 'max_waiting_time':
                    attributes[attribute] = self.generate_demographic_data(attribute, current_money_category=current_money_category)
                else:
                    attributes[attribute] = self.generate_demographic_data(attribute)

            person = Person(attributes)
            person_list.append(person)

        return person_list