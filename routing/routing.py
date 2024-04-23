import heapq

from map.graph import Graph

OBSTACLE_PENALTY_FACTOR = 1
MAX_SPEED = 50


class Node:
    def __init__(self, idx, g_score=float('inf'), f_score=float('inf'), parent=None):
        self.idx = idx
        self.g_score = g_score
        self.f_score = f_score
        self.parent = parent

    def __lt__(self, other):
        return self.f_score < other.f_score


def heuristic(src_node, goal_node):
    return src_node.length_to(goal_node) / MAX_SPEED


def cost(graph, src_idx):
    block = graph.nodes[src_idx]
    estimated_time = block.length / block.max_speed
    penalty = len(block.obstacles) * OBSTACLE_PENALTY_FACTOR

    return estimated_time + penalty


def a_star(graph: Graph, start_idx: str, goal_idx: str):
    open_set = []
    heapq.heappush(open_set, Node(start_idx, g_score=0,
                                  f_score=heuristic(graph.nodes[start_idx], graph.nodes[goal_idx])))

    g_scores = {start_idx: 0}

    came_from = {}

    while open_set:
        current_node = heapq.heappop(open_set)

        if current_node.idx == goal_idx:
            return reconstruct_path(came_from, current_node.idx)

        if current_node.idx in graph.edges:
            for neighbor_idx in graph.edges[current_node.idx]:
                tentative_g_score = g_scores[current_node.idx] + cost(graph, current_node.idx)

                if neighbor_idx not in g_scores or tentative_g_score < g_scores[neighbor_idx]:
                    came_from[neighbor_idx] = current_node.idx
                    g_scores[neighbor_idx] = tentative_g_score
                    f_score = tentative_g_score + heuristic(graph.nodes[neighbor_idx], graph.nodes[goal_idx])
                    heapq.heappush(open_set, Node(neighbor_idx, g_score=tentative_g_score, f_score=f_score))

    return None


def reconstruct_path(came_from, current_idx):
    path = [current_idx]
    while current_idx in came_from:
        current_idx = came_from[current_idx]
        path.append(current_idx)
    return path[::-1]
