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
            print("Iniciando simulación...")
            threading.Thread(target=simulation.run).start()
        elif response == "Detener simulación":
            print("Deteniendo simulación...")
            simulation.stop()
        else:
            print("Acción no reconocida.")



def main():
    src_path = Path(__file__).parent

    with open(f"{src_path}/data/routes.json", 'r') as file:
        data = json.load(file)["routes"]

    distributions = {ref: 1 for ref in data}

    simulation = Simulation(f"{src_path}/map", f"{src_path}/population", 1827,
                            f"{src_path}/data", distributions, 600, ["playa"])

    t = threading.Thread(target=chat, args=(simulation, ["Iniciar simulación", "Detener simulación"]))
    t.start()


if __name__ == '__main__':
    main()
