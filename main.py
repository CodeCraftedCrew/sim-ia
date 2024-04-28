from pathlib import Path

from map.map_loader import MapLoader


def main():
    src_path = Path(__file__).parent

    loader = MapLoader(f"{src_path}/map/havana.osm",
                       f"{src_path}/map/municipalities.poly")
    loader.load_map(f"{src_path}/map", f"{src_path}/map/GAZelles.json")


if __name__ == '__main__':
    main()
