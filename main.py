from pathlib import Path
from simulation import Simulation


def main():
    src_path = Path(__file__).parent

    simulation = Simulation(f"{src_path}/map", f"{src_path}/population", 18272,
                            f"{src_path}/data", {}, 600)


if __name__ == '__main__':
    main()
