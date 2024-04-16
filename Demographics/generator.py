import random

class Person:
    def __init__(self, attributes):
        self.attributes = attributes

class DemographicGenerator:

    def __init__(self):

        self.demographic_distributions = {
            'age': {'0-4': 0.043, '5-9': 0.052, '10-14': 0.049, '15-19': 0.049, '20-24':0.06, '25-29':0.062, '30-34':0.074, '35-39':0.067, '40-44':0.053, '45-49':0.069, '50-54':0.083, '55-59':0.096, '60-64':0.07, '65+':0.166},
            'gender': {'Male': 0.47, 'Female': 0.53},
            'location': {'Playa': 0.083, 'Plaza de la Revolución': 0.065, 'Centro Habana': 0.061, 'La Habana Vieja': 0.037, 'Regla': 0.02, 'La Habana del Este': 0.081, 'Guanabacoa': 0.06, 'San Miguel del Padrón': 0.075, 'Diez de Octubre': 0.093, 'Cerro': 0.058, 'Marianao': 0.062, 'La Lisa': 0.068, 'Boyeros': 0.095, 'Arroyo Naranjo': 0.096, 'Cotorro': 0.038}
        }

    def add_distribution(self, attribute, distribution):

        if isinstance(distribution, dict):
            self.demographic_distributions[attribute] = distribution
        
        else:
            raise ValueError("Distribution must be a dictionary.")

    def alter_distribution(self, attribute, new_distribution):
       
        if attribute in self.demographic_distributions:
            if isinstance(new_distribution, dict):
                self.demographic_distributions[attribute].update(new_distribution)
       
            else:
                raise ValueError("New distribution must be a dictionary.")
       
        else:
            raise ValueError(f"No distribution defined for attribute '{attribute}'")

    def generate_demographic_data(self, attribute):
        
        distribution = self.demographic_distributions.get(attribute)
        
        if distribution:
            categories = list(distribution.keys())
            weights = list(distribution.values())
            category = random.choices(categories, weights=weights)[0]
            return category
        
        else:
            raise ValueError(f"No distribution defined for attribute '{attribute}'")

    def generate_person_list(self, sample_size):
        
        person_list = []
        
        for _ in range(sample_size):
            attributes = {}
            for attribute in self.demographic_distributions.keys():
                attributes[attribute] = self.generate_demographic_data(attribute)
            
            person = Person(attributes)
            person_list.append(person)
        
        return person_list