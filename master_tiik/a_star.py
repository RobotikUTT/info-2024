import heapq
import time
from typing import List, Tuple

from master_tiik.debug_utils import TimeIt


class Node:
    def __init__(self, is_end):
        self.is_end = is_end
    def to_tuple(self):
        raise NotImplementedError("to_tuple is not implemented")
    def get_neighbours(self) -> "List[Tuple[Node, Cost]]":
        raise NotImplementedError("get_neighbours is not implemented")
    def __str__(self):
        return str(self.to_tuple())
    def __hash__(self):
        return hash(self.to_tuple())
    def __eq__(self, other):
        return hash(self) == hash(other)


class Cost:
    def as_number(self):
        raise NotImplementedError("as_number is not implemented")
    def __add__(self, other):
        raise NotImplementedError("__add__ is not implemented")


class NodeData:
    def __init__(self, node: Node, cost: Cost, parent: "NodeData | None"):
        self.node = node
        self.parent = parent
        self.cost_from_parent = cost
        self.cost = cost
        self.path_length = 1
        if parent is not None:
            self.cost = parent.cost + cost
            self.path_length = parent.path_length + 1


def a_star(start_node: Node, null_cost: Cost, stop_after=1000, stop_on_path_ends=False):
    opened_nodes: List[(int, int, Node | None)] = [(null_cost, 0, start_node)]
    heapq.heapify(opened_nodes)
    heapq_counter = 1
    opened_nodes_set = {hash(start_node)}
    closed_nodes = set()
    nodes_data = {start_node: NodeData(start_node, null_cost, None)}
    while len(opened_nodes):
        current_node: Node | None = None
        while (current_node is None or current_node in closed_nodes) and len(opened_nodes):
            current_node = heapq.heappop(opened_nodes)[2]
            # For now, this is slower by removing the node from the set.
            # You can try to uncomment this and check if it's faster in the future.
            # if current_node in opened_nodes_set:
            #    opened_nodes_set.remove(hash(current_node))
        if current_node is None:
            print("no nodes left")
            break
        current_node_data = nodes_data[current_node]
        closed_nodes.add(current_node)
        if current_node.is_end or current_node_data.path_length >= stop_after:
            path = []
            node = current_node_data
            while node is not None:
                path.append((node.node, node.cost_from_parent))
                node = node.parent
            return list(reversed(path))
        neighbours = current_node.get_neighbours()
        if stop_on_path_ends and len(neighbours) == 0:
            print("end of path")
            break
        for node, cost in neighbours:
            if node in closed_nodes:
                continue
            new_node_data = NodeData(node, cost, current_node_data)
            if hash(node) not in opened_nodes_set or nodes_data[node].cost.as_number() > new_node_data.cost.as_number():
                nodes_data[node] = new_node_data
                heapq.heappush(opened_nodes, (new_node_data.cost.as_number(), heapq_counter, node))
                heapq_counter += 1
                opened_nodes_set.add(hash(node))
                continue
    if not len(closed_nodes):
        return None
    node_to_send_back = nodes_data[closed_nodes.pop()]
    while len(closed_nodes):
        node = nodes_data[closed_nodes.pop()]
        if node.path_length < node_to_send_back.path_length:
            continue
        if node.path_length > node_to_send_back.path_length:
            node_to_send_back = node
        elif node.cost.as_number() < node_to_send_back.cost.as_number():
            node_to_send_back = node
    path = []
    node = node_to_send_back
    while node is not None:
        path.append((node.node, node.cost_from_parent))
        node = node.parent
    return list(reversed(path))

if __name__ == '__main__':
    class MyNode(Node):
        def __init__(self, x, y):
            super().__init__(x == 9 and y == 9)
            self.x = x
            self.y = y
        def to_tuple(self):
            return self.x, self.y
        def get_neighbours(self):
            neighbours = []
            if self.x != 0:
                neighbours.append((MyNode(self.x-1, self.y), MyCost(1, 0)))
            if self.x != 9:
                neighbours.append((MyNode(self.x+1, self.y), MyCost(1, 0)))
            if self.y != 0:
                neighbours.append((MyNode(self.x, self.y-1), MyCost(1, 0)))
            if self.y != 9:
                neighbours.append((MyNode(self.x, self.y+1), MyCost(1, 0)))
            return neighbours
        def __str__(self):
            return f"Node({self.x}, {self.y})"
    class MyCost(Cost):
        def __init__(self, time, points):
            self.time = time
            self.points = points
        def as_number(self):
            return self.points / self.time
        def __add__(self, other):
            return MyCost(self.time + other.time, self.points + other.points)
