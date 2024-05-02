from gemini import llm
from pathlib import Path
from simulation import Simulation
import threading

def main():
    src_path = Path(__file__).parent

    simulation = Simulation(f"{src_path}/map", f"{src_path}/population", 18272,
                            f"{src_path}/data", {}, 600, ["playa"])

    t = threading.Thread(target=llm.chat, args=(simulation, ["Iniciar simulación", "Detener simulación"]))
    t.start()

if __name__ == '__main__':
    main()
