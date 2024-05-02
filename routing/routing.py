import heapq
import random

from map.graph import Graph
from map.map_elements import Node, Block

OBSTACLE_PENALTY_FACTOR = 1
MAX_SPEED = 50
MAX_WALK_SPEED = 5
MAX_DISTANCE_TOLERANCE = 10
ITERATIONS_FACTOR = 1000


def heuristic(src_node, goal_nodes, drivers_ability, walk):
    base_heuristic = min(src_node.length_to(goal_node) / (MAX_SPEED if not walk else MAX_WALK_SPEED) for goal_node in goal_nodes)
    error = 0 if random.uniform(0, 1) <= drivers_ability else base_heuristic + base_heuristic * (1 - drivers_ability)

    return base_heuristic + error*random.choice([-1, 1])


def cost(graph, src_id, walk):
    block = graph.nodes[src_id]
    estimated_time = block.length / (int(block.max_speed) if not walk else MAX_WALK_SPEED)
    penalty = len([element for element in block.elements if element.is_traffic_sign]) * OBSTACLE_PENALTY_FACTOR

    return estimated_time + penalty


def get_max_iterations(start, goals, avg_node_length):
    path_length = max(start.length_to(goal) for goal in goals)

    avg_nodes = path_length / avg_node_length

    return avg_nodes * ITERATIONS_FACTOR


def path_search(graph: Graph, start_id: str, goal_ids: list[str], blocked_nodes,
                drivers_ability: float = 1, walk: bool = False, only_walk: bool = False):
    if len(goal_ids) == 0:
        return None

    open_set = []
    goal_nodes = [graph.nodes[goal_id] for goal_id in goal_ids]
    start_node = graph.nodes[start_id]

    heapq.heappush(open_set, Node(start_id, g_score=0,
                                  f_score=heuristic(graph.nodes[start_id], goal_nodes, drivers_ability,
                                                    walk or only_walk),
                                  ))

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
            return current_node.g_score, reconstruct_path(came_from, current_node.id)

        if multiple:
            if iterations > max_iterations:
                return -1, None
            iterations += 1

        elif (graph.nodes[current_node.id].length_to(goal_nodes[0])
              > distance_from_start + MAX_DISTANCE_TOLERANCE):
            continue

        if current_node.id in graph.edges:
            for neighbor_id, walk_value in graph.edges[current_node.id]:
                if not walk and walk_value:
                    continue

                tentative_g_score = g_scores[current_node.id] + cost(graph, current_node.id, walk_value)

                if neighbor_id not in g_scores or tentative_g_score < g_scores[neighbor_id]:
                    came_from[neighbor_id] = current_node.id
                    g_scores[neighbor_id] = tentative_g_score
                    f_score = tentative_g_score + heuristic(graph.nodes[neighbor_id], goal_nodes, drivers_ability,
                                                            walk_value or only_walk)
                    heapq.heappush(open_set, Node(neighbor_id, g_score=tentative_g_score, f_score=f_score))

    return -1, None


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

    blocks_of_interest = {start_block} if start_block.contains_stop() else set()

    while open_set:
        current_node = heapq.heappop(open_set)

        if current_node.id in graph.edges:
            for neighbor_id, walk_value in graph.edges[current_node.id]:

                if walk_value and not walk:
                    continue

                neighbor = graph.nodes[neighbor_id]
                current_block = graph.nodes[current_node.id]
                tentative_length = length_to_start[current_node.id] + current_block.length_to(neighbor)

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
    possible_ends = set()

    if isinstance(dest, list):
        for block in dest:
            possible_ends.update(blocks_in_radio(graph, block, radio, False))
    else:
        possible_ends = blocks_in_radio(graph, dest, radio, True)

    if len(possible_starts) == 0 or len(possible_ends) == 0:
        return []

    possible_paths = []

    for start in possible_starts:

        possible_path = []

        score, path = path_search(graph, start.id, [end.id for end in possible_ends], [], 1)

        if score == -1:
            continue

        last_ways = {"walk"}
        last_node = None

        for node_id in path:
            ways_to_get_to_node = graph.nodes[node_id].ways_to_arrive(last_node)
            possible_path.append((node_id, last_ways.intersection(ways_to_get_to_node)))
            last_ways = ways_to_get_to_node
            last_node = node_id

        possible_paths.append((score, possible_path))

    return possible_paths
