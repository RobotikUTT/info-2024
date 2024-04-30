import copy
import a_star
from useful_class import Area,PlantArea,PlayerArea,StationArea,GardenArea,GameState

MAX_ROBOT_PLANTS = 12

# ---------------------- DEFINE NODE ----------------------

class GameNode(a_star.Node):
    def __init__(self, game_state: GameState, is_end: bool):
        super().__init__(is_end)
        self.game_state = copy.deepcopy(game_state)
        self.possible_points = 0
        self.area: Area | None = None

    def to_tuple(self):
        return self.__class__.__name__, None if self.area is None else self.area.id, *self.game_state.to_tuple()

    def get_neighbours(self):
        neighbours = []
        for area in self.game_state.plant_areas:
            node = PlantAreaNode(self.game_state, area)
            neighbours.append((node, self.compute_cost(node)))
        for area in self.game_state.player_areas:
            node = PlayerAreaNode(self.game_state, area)
            neighbours.append((node, self.compute_cost(node)))
        return neighbours

    def compute_cost(self, node: "GameNode"):
        return Cost((self.area.centerX - node.area.centerX) ** 2 + (self.area.centerY - node.area.centerY) ** 2 + node.area.time_spent, node.possible_points)


class PlantAreaNode(GameNode):
    def __init__(self, game_state, area: PlantArea):
        super().__init__(game_state, False)
        self.area = copy.deepcopy(area)
        self.plants_taken = min(MAX_ROBOT_PLANTS - self.game_state.robot_plants, self.area.plants)
        self.game_state.robot_plants += self.plants_taken
        self.game_state.plant_areas[self.area.id].plants -= self.plants_taken
        self.possible_points = self.plants_taken


class PlayerAreaNode(GameNode):
    def __init__(self, game_state, area: PlayerArea):
        super().__init__(game_state, False)
        self.area = copy.deepcopy(area)
        self.game_state.robot_plants = 0
        self.possible_points = 0


class StartNode(GameNode):
    class StartArea(Area):
        def __init__(self, x, y):
            super().__init__(0, x, y, 0, 0)

    def __init__(self, game_state, x, y):
        super().__init__(game_state, False)
        self.area = StartNode.StartArea(x, y)

# ---------------------- DEFINE WAY TIME ----------------------

class Cost(a_star.Cost):
    def __init__(self, time, points):
        self.time = time
        self.points = points

    def as_number(self):
        return -self.points / self.time

    def __add__(self, other):
        return Cost(self.time + other.time, self.points + other.points)

# ---------------------- FONCTION TO USE ----------------------

def find_best_strategy(game_state):
    path = a_star.a_star(StartNode(game_state, 0, 0), Cost(0.001, 0), stop_after=10)
    areas = []
    for i in path[1:]:
        areas.append(i.area)
    return areas
