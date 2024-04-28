import heapq
import random

from map.graph import Graph
from map.map_elements import Node

OBSTACLE_PENALTY_FACTOR = 1
MAX_SPEED = 50
MAX_DISTANCE_TOLERANCE = 10
ITERATIONS_FACTOR = 100


def heuristic(src_node, goal_nodes, drivers_ability):
    base_heuristic = min(src_node.length_to(goal_node) / MAX_SPEED for goal_node in goal_nodes)
    error = 0 if random.uniform(0, 1) <= drivers_ability else base_heuristic + base_heuristic * (1 - drivers_ability)

    return base_heuristic + error*random.choice([-1, 1])


def cost(graph, src_id):
    block = graph.nodes[src_id]
    estimated_time = block.length / block.max_speed
    penalty = len(block.obstacles) * OBSTACLE_PENALTY_FACTOR

    return estimated_time + penalty


def get_max_iterations(start, goals, avg_node_length):
    path_length = max(start.length_to(goal) for goal in goals)

    avg_nodes = path_length / avg_node_length

    return avg_nodes * ITERATIONS_FACTOR


def path_search(graph: Graph, start_id: str, goal_ids: list[str], blocked_nodes,
                drivers_ability: float = 1):
    if len(goal_ids) == 0:
        return None

    open_set = []
    goal_nodes = [graph.nodes[goal_id] for goal_id in goal_ids]
    start_node = graph.nodes[start_id]

    heapq.heappush(open_set, Node(start_id, g_score=0,
                                  f_score=heuristic(graph.nodes[start_id], goal_nodes, drivers_ability), ))

    g_scores = {start_id: 0}

    came_from = {}
    distance_from_start = start_node.length_to(goal_nodes[0])
    multiple = len(goal_nodes) > 1
    max_iterations = get_max_iterations(start_node, goal_nodes, graph.avg_length)
    iterations = 0

    while open_set:
        current_node = heapq.heappop(open_set)

        if current_node in blocked_nodes:
            continue

        if current_node.id in goal_ids:
            return reconstruct_path(came_from, current_node.id)

        if multiple:
            if iterations > max_iterations:
                return None
            iterations += 1

        elif (graph.nodes[current_node.id].length_to(graph.nodes[goal_nodes[0]])
              > distance_from_start + MAX_DISTANCE_TOLERANCE):
            continue

        if current_node.id in graph.edges:
            for neighbor_id, walk in graph.edges[current_node.id]:
                if walk:
                    continue

                tentative_g_score = g_scores[current_node.id] + cost(graph, current_node.id)

                if neighbor_id not in g_scores or tentative_g_score < g_scores[neighbor_id]:
                    came_from[neighbor_id] = current_node.id
                    g_scores[neighbor_id] = tentative_g_score
                    f_score = tentative_g_score + heuristic(graph.nodes[neighbor_id], goal_nodes, drivers_ability)
                    heapq.heappush(open_set, Node(neighbor_id, g_score=tentative_g_score, f_score=f_score))

    return None


def reconstruct_path(came_from, current_id):
    path = [current_id]
    while current_id in came_from:
        current_id = came_from[current_id]
        path.append(current_id)
    return path[::-1]


def blocks_in_radio(graph, start_block, radio, walk):

    length_to_start = {start_block.id: 0}

    open_set = []

    heapq.heappush(open_set, Node(start_block.id, g_score=0, f_score=0))

    blocks_of_interest = {start_block} if any(element.is_stop for element in start_block.elements) else set()

    while open_set:
        current_node = heapq.heappop(open_set)

        if current_node.id in graph.edges:
            for neighbor_id, walk_value in graph.edges[current_node.id]:

                if walk_value and not walk:
                    continue

                neighbor = graph.nodes[neighbor_id]
                tentative_length = length_to_start[current_node.id] + current_node.lenght_to(neighbor)

                if tentative_length > radio:
                    continue

                if neighbor.contains_stop():
                    blocks_of_interest.add(neighbor)

                if neighbor_id not in length_to_start or tentative_length < length_to_start[neighbor_id]:
                    length_to_start[neighbor_id] = tentative_length
                    heapq.heappush(open_set, Node(neighbor_id, g_score=tentative_length, f_score=tentative_length))

    return blocks_of_interest


def get_routes(graph, src, dest, radio):

    if not graph.is_simplified:
        raise ValueError("Graph is not simplified")

    possible_starts = blocks_in_radio(graph, src, radio, True)
    possible_ends = blocks_in_radio(graph, dest, radio, True)

    possible_paths = []

    for start in possible_starts:

        path = path_search(graph, start.id, [end.id for end in possible_ends], [], 1)
        last_ways = {"walk"}

        for node_id in path:
            ways_to_get_to_node = graph.nodes[node_id].ways_to_arrive()
            possible_paths.append((node_id, last_ways.intersection(ways_to_get_to_node)))
            last_ways = ways_to_get_to_node

    return possible_paths
