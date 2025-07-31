import queue

class Flight:
    def __init__(self, name, origin, dest, arrivalT, departT):
        self.name = name
        self.origin = origin
        self.dest = dest
        self.arrivalT = arrivalT
        self.departT = departT
        self.weight = arrivalT - departT  # Correct: travel duration

    def __str__(self):
        return f"{self.name}: {self.origin} → {self.dest} | Departs at {self.departT}:00, Arrives at {self.arrivalT}:00"

    def __repr__(self):
        return self.__str__()

    def __lt__(self, other):
        return self.arrivalT < other.arrivalT  # for priority queue


class Graph:
    def __init__(self, vertices):
        self.vertices = vertices


class Schedule:
    def __init__(self, vertex, time):
        self.vertex = vertex
        self.time = time

    def __hash__(self):
        return hash(str(self.vertex) + ":" + str(self.time))

    def __lt__(self, other):
        return self.time < other.time

    def __str__(self):
        return "{" + str(self.vertex) + ":" + str(self.time) + "}"

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        if isinstance(other, Schedule):
            return (self.vertex == other.vertex) and (self.time == other.time)
        return False


class Vertex:
    def __init__(self, name, adjacentVertices):
        self.name = name
        self.adjacentVertices = adjacentVertices

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        if isinstance(other, Vertex):
            return self.name == other.name
        return False

    def __hash__(self):
        return hash(self.name)


def FlightAgency(F, G, s, d, startT):
    """
    F: List of flights
    G: Graph with vertices
    s: Source vertex
    d: Destination vertex
    startT: Start time in 24-hour format

    Returns:
        (earliest arrival time, list of flights taken as path)
    """
    T = {vertex: float('inf') for vertex in G.vertices}
    T[s] = startT

    prev_flight = {}  # Track flight used to reach each vertex

    q = queue.PriorityQueue()
    for vertex in G.vertices:
        q.put(Schedule(vertex, T[vertex]))

    while not q.empty():
        v_schedule = q.get()
        current_vertex = v_schedule.vertex

        for neighbor in current_vertex.adjacentVertices:
            # Filter flights from current to neighbor that depart after current time
            possible_flights = [
                flight for flight in F
                if flight.origin == current_vertex and flight.dest == neighbor and flight.departT >= T[current_vertex]
            ]

            if possible_flights:
                # Choose flight with earliest arrival
                best_flight = min(possible_flights, key=lambda f: f.arrivalT)
                arrival_time = best_flight.arrivalT

                if arrival_time < T[neighbor]:
                    T[neighbor] = arrival_time
                    prev_flight[neighbor] = best_flight
                    q.put(Schedule(neighbor, arrival_time))

    # Reconstruct path
    path = []
    current = d
    while current != s:
        if current in prev_flight:
            flight = prev_flight[current]
            path.append(flight)
            current = flight.origin
        else:
            # No path found
            return float('inf'), []

    path.reverse()
    return T[d], path
