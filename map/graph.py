class Graph:

    def __init__(self):
        self.nodes = {}
        self.edges = {}
        self.map = {}
        self.bus_routes = {}
        self.count = 0
        self.avg_length = 0

    def add_node(self, idx, node):

        if idx not in self.nodes:
            self.nodes[idx] = node
            self.count += 1
        else:
            raise Exception("Node already exists")

    def add_edge(self, src, dest):
        if src not in self.edges:
            self.edges[src] = {dest}
        else:
            self.edges[src].add(dest)

    def get_route(self, ref, block):

        route = self.bus_routes.get(ref, None)

        if route is None:
            return []

        if route.outbound_route[0].id == block.id:
            return route.outbound_route

        if route.return_route[0].id == block.id:
            return route.return_route
