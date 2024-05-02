import json
from gemini import llm
from pathlib import Path
from simulation import Simulation
import threading


def chat(simulation: Simulation, actions: list):
    """
        Simulates a chat interaction with the user, taking actions based on user input.

        Args:
            simulation (Simulation): The simulation object to run or stop based on user input.
            actions (list): A list of possible actions that the user can choose from.
        """

    print(
        "Bienvenido a la simulación. ¿Qué te gustaría que hiciera primero? Cuando lo escribas, presiona Enter para continuar.")
    while True:
        entry = input()

        response = llm.chat(entry, actions)

        if response == "Iniciar simulación":
            print("La simulación ha empezado. Por favor, espera unos minutos.")
            threading.Thread(target=simulation.run).start()
        elif response == "Detener simulación":
            print("La simulación se detuvo.")
            simulation.stop()
        elif response == "Planes imposibles":
            llm.answer_chat(entry, None)
        elif response == "Caminando":
            llm.answer_chat(entry, None)
        elif response == "Máximo tiempo de espera":
            llm.answer_chat(entry, None)
        elif response == "Mínimo tiempo de espera":
            llm.answer_chat(entry, None)
        elif response == "Tiempo promedio de espera":
            llm.answer_chat(entry, None)
        elif response == "Pasajeros en una ruta":
            llm.answer_chat(entry, None)
        else:
            print("Acción no reconocida.")
            


def main():
    src_path = Path(__file__).parent

    with open(f"{src_path}/data/routes.json", 'r') as file:
        data = json.load(file)["routes"]

    distributions = {ref: 1 for ref in data}

    simulation = Simulation(f"{src_path}/map", f"{src_path}/population", 1827,
                            f"{src_path}/data", distributions, 600, ["playa"])

    t = threading.Thread(target=chat, args=(simulation, ["Iniciar simulación", "Detener simulación", "Planes imposibles", "Caminando", "Máximo tiempo de espera", "Mínimo tiempo de espera", "Tiempo promedio de espera", "Pasajeros en una ruta"]))
    t.start()


if __name__ == '__main__':
    main()
