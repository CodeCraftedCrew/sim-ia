from map.map_loader import MapLoader


def main():
    loader = MapLoader("D:/Work/Repositories/sim-ia/map/havana.osm",
                       "D:/Work/Repositories/sim-ia/map/municipalities.poly")
    loader.load_map("D:/Work/Repositories/sim-ia/map")


if __name__ == '__main__':
    main()
