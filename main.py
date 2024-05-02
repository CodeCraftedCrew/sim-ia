import json
from gemini import llm
from pathlib import Path
from simulation import Simulation
import threading

def main():
    src_path = Path(__file__).parent

    with open(f"{src_path}/data/routes.json", 'r') as file:
        data = json.load(file)["routes"]

    distributions = {ref: 1 for ref in data}

    simulation = Simulation(f"{src_path}/map", f"{src_path}/population", 1827,
                            f"{src_path}/data", distributions, 600, ["playa"])

    t = threading.Thread(target=llm.chat, args=(simulation, ["Iniciar simulación", "Detener simulación"]))
    t.start()

if __name__ == '__main__':
    main()
