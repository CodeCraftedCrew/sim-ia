import google.generativeai as genai
from environment.environment import Bus
from agents.passenger_agent import PassengerAgent
import os
from dotenv import load_dotenv

load_dotenv()

api_k = os.getenv("API_KEY")

genai.configure(api_key=api_k)

model = genai.GenerativeModel('gemini-pro')

def minimumFuelLevel(bus: Bus):

    response = model.generate_content(f'Una guagua modelo {bus.model}, tiene un tanque de capacidad {bus.max_fuel} litros, a partir de qué cantidad de litros se considera que está bajo de combustible y debería ir a rellenar el tanque? Dame tu respuesta con solo una palabra, sin ningún tipo de explicación, solo un número')

    try:
        return int(response.text)
    except ValueError:
        print("La respuesta no es un número entero.")
        return None
    
def WalkSpeed(passenger: PassengerAgent):
    age = passenger.profile['age']
    
    if (passenger.profile['employment_status'] == "occupied"):
        response = model.generate_content(f'A cuántos kilómetros por hora camina una persona de {age} años que trabaja? Dame tu respuesta con solo una palabra, sin ningún tipo de explicación, solo un número')
    elif (passenger.profile['employment_status'] == "student"):
        if (passenger.profile['student_type'] == "high_school"):
            response = model.generate_content(f'A cuántos kilómetros por hora camina una persona de {age} años que estudia en la secundaria? Dame tu respuesta con solo una palabra, sin ningún tipo de explicación, solo un número')
        elif (passenger.profile['student_type'] == "technician"):
            response = model.generate_content(f'A cuántos kilómetros por hora camina una persona de {age} años que estudia en el tecnológico? Dame tu respuesta con solo una palabra, sin ningún tipo de explicación, solo un número')
        elif (passenger.profile['student_type'] == "pedagogical"):
            response = model.generate_content(f'A cuántos kilómetros por hora camina una persona de {age} años que estudia pedagogía? Dame tu respuesta con solo una palabra, sin ningún tipo de explicación, solo un número')
        elif (passenger.profile['student_type'] == "special"):
            response = model.generate_content(f'A cuántos kilómetros por hora camina una persona de {age} años que estudia en la educación especial? Dame tu respuesta con solo una palabra, sin ningún tipo de explicación, solo un número')
        elif (passenger.profile['student_type'] == "bachelor"):
            if (passenger.profile['bachelor_type'] == "medicine"):
                response = model.generate_content(f'A cuántos kilómetros por hora camina una persona de {age} años que estudia medicina? Dame tu respuesta con solo una palabra, sin ningún tipo de explicación, solo un número')
            else:
                response = model.generate_content(f'A cuántos kilómetros por hora camina una persona de {age} años que estudia en la universidad? Dame tu respuesta con solo una palabra, sin ningún tipo de explicación, solo un número')
    elif (passenger.profile['employment_status'] == "unoccupied"):
        response = model.generate_content(f'A cuántos kilómetros por hora camina una persona de {age} años que no trabaja? Dame tu respuesta con solo una palabra, sin ningún tipo de explicación, solo un número')
    else:
        response = model.generate_content(f'A cuántos kilómetros por hora camina una persona de {age} años que no estudia ni trabaja? Dame tu respuesta con solo una palabra, sin ningún tipo de explicación, solo un número')
    try:
        return int(response.text)
    except ValueError:
        print("La respuesta no es un número entero.")
        return None