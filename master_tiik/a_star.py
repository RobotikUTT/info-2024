import heapq
from typing import List, Tuple


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
        self.cost = cost
        self.path_length = 1
        if parent is not None:
            self.path_length = parent.path_length + 1


def a_star(start_node: Node, null_cost: Cost, stop_after=1000):
    opened_nodes: List[(int, int, Node | None)] = [(null_cost, 0, start_node)]
    heapq.heapify(opened_nodes)
    closed_nodes = set()
    nodes_data = {start_node: NodeData(start_node, null_cost, None)}
    heapq_counter = 1
    while len(opened_nodes):
        current_node: Node | None = None
        while (current_node is None or current_node in closed_nodes) and len(opened_nodes):
            current_node = heapq.heappop(opened_nodes)[2]
        if current_node is None:
            break
        current_node_data = nodes_data[current_node]
        if current_node.is_end or current_node_data.path_length >= stop_after:
            path = []
            node = current_node_data
            while node is not None:
                path.append(node.node)
                node = node.parent
            return list(reversed(path))
        closed_nodes.add(current_node)
        neighbours = current_node.get_neighbours()
        for node, cost in neighbours:
            if node in closed_nodes:
                continue
            new_cost = cost + current_node_data.cost
            if node not in opened_nodes:
                heapq.heappush(opened_nodes, (new_cost.as_number(), heapq_counter, node))
                heapq_counter += 1
                nodes_data[node] = NodeData(node, new_cost, current_node_data)
                continue
            node_data = nodes_data[node]
            if node_data.cost.as_number() > new_cost.as_number():
                # We don't need to remove the node, as the old one will be taken after, and will eventually be removed : when picked up, it will be in the closed_nodes
                node_data.cost = new_cost
                heapq.heappush(opened_nodes, (new_cost.as_number(), heapq_counter, node))
                heapq_counter += 1
    if not len(closed_nodes):
        return None
    node_to_send_back = nodes_data[closed_nodes.pop()]
    while len(closed_nodes):
        node = nodes_data[closed_nodes.pop()]
        if node.path_length >= node_to_send_back.path_length and node.cost.as_number() < node_to_send_back.cost.as_number():
            node_to_send_back = node
    path = []
    node = node_to_send_back
    while node is not None:
        path.append(node.node)
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