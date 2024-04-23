class Graph:

    def __init__(self):
        self.nodes = {}
        self.edges = {}
        self.map = {}
        self.count = 0

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
