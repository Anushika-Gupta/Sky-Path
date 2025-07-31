class Graph:
    def __init__(self):
        self.adjacency = {}

    def add_edge(self, origin, dest, cost):
        if origin not in self.adjacency:
            self.adjacency[origin] = []
        self.adjacency[origin].append((dest, cost))
