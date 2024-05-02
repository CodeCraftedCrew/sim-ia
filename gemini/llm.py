from dotenv import load_dotenv
import google.generativeai as genai
import os

load_dotenv()

api_k = os.getenv("API_KEY")

genai.configure(api_key=api_k)

model = genai.GenerativeModel('gemini-pro')


def minimum_fuel_level(bus_model, max_fuel):
    """
    Determines the minimum fuel level at which the bus should go to refill the tank.

    Args:
        bus_model (str): Model of the bus.
        max_fuel (int): Maximum fuel capacity.

    Returns:
        int or None: The minimum fuel level in liters at which the bus should go to refill the tank.
                     Returns None if the response is not a valid integer.
    """
    response = model.generate_content(
        f'Una guagua modelo {bus_model}, tiene un tanque de capacidad {max_fuel} litros, a partir de qué cantidad de litros se considera que está bajo de combustible y debería ir a rellenar el tanque? Dame tu respuesta con solo una palabra, sin ningún tipo de explicación, solo un número')

    try:
        return int(response.text)
    except ValueError:
        print("La respuesta no es un número entero.")
        return None


def walk_speed(employment_status: str, student_type: str, age: int):
    """
    Calculates the walking speed of a person based on their profile information.

    Args:
        passenger (PassengerAgent): The passenger object containing the profile information.

    Returns:
        int or None: The walking speed in kilometers per hour as an integer, or None if the response is not a valid integer.
    """

    if (employment_status == "occupied"):
        response = model.generate_content(
            f'A cuántos kilómetros por hora camina una persona de {age} años que trabaja? Dame tu respuesta con solo una palabra, sin ningún tipo de explicación, solo un número')
    elif (employment_status == "student"):
        if (student_type == "high_school"):
            response = model.generate_content(
                f'A cuántos kilómetros por hora camina una persona de {age} años que estudia en la secundaria? Dame tu respuesta con solo una palabra, sin ningún tipo de explicación, solo un número')
        elif (student_type == "technician"):
            response = model.generate_content(
                f'A cuántos kilómetros por hora camina una persona de {age} años que estudia en el tecnológico? Dame tu respuesta con solo una palabra, sin ningún tipo de explicación, solo un número')
        elif (student_type == "pedagogical"):
            response = model.generate_content(
                f'A cuántos kilómetros por hora camina una persona de {age} años que estudia pedagogía? Dame tu respuesta con solo una palabra, sin ningún tipo de explicación, solo un número')
        elif (student_type == "special"):
            response = model.generate_content(
                f'A cuántos kilómetros por hora camina una persona de {age} años que estudia en la educación especial? Dame tu respuesta con solo una palabra, sin ningún tipo de explicación, solo un número')
        elif (student_type == "bachelor"):
            response = model.generate_content(
                f'A cuántos kilómetros por hora camina una persona de {age} años que estudia en la universidad? Dame tu respuesta con solo una palabra, sin ningún tipo de explicación, solo un número')
    elif (employment_status == "unoccupied"):
        response = model.generate_content(
            f'A cuántos kilómetros por hora camina una persona de {age} años que no trabaja? Dame tu respuesta con solo una palabra, sin ningún tipo de explicación, solo un número')
    else:
        response = model.generate_content(
            f'A cuántos kilómetros por hora camina una persona de {age} años que no estudia ni trabaja? Dame tu respuesta con solo una palabra, sin ningún tipo de explicación, solo un número')
    try:
        return int(response.text)
    except ValueError:
        print("La respuesta no es un número entero.")
        return None


def chat(entry, actions: list):
    response = model.generate_content(
        f'Dada la siguiente orden: {entry}, clasifica la acción como una de las siguientes: {actions}. Responde solo con la elección, no expliques nada.')

    return response.text

def answer_chat(entry, data):
    response = model.generate_content(
        f'Dada la siguiente información: {data}, responde la pregunta siguiente: {entry}.')

    return response.text
