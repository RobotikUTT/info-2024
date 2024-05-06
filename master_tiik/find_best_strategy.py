import copy
import sys
import time
from typing import List, Callable, Tuple

import a_star
from master_tiik.debug_utils import TimeIt
from utils import find_path, Circle
from useful_class import Area, GameState, Action

MAX_ROBOT_PLANTS = 6
POINTS_FOR_UNPOTTED_PLANTS = 1
POINTS_FOR_POTTED_PLANTS = 2
POINTS_FOR_POT = POINTS_FOR_POTTED_PLANTS - POINTS_FOR_UNPOTTED_PLANTS


# ---------------------- DEFINE NODE ----------------------

class GameNode(a_star.Node):
    def __init__(self, game_state: GameState, is_end: bool):
        super().__init__(is_end)
        self.game_state = copy.copy(game_state)
        self.game_state.robot_unpotted_plants = game_state.robot_unpotted_plants
        self.game_state.robot_potted_plants = game_state.robot_potted_plants
        self.game_state.plant_areas = [copy.copy(area) for area in game_state.plant_areas]
        self.game_state.garden_areas = [copy.copy(area) for area in game_state.garden_areas]
        self.game_state.garden_pot_areas = [copy.copy(area) for area in game_state.garden_pot_areas]
        self.game_state.pot_areas = [copy.copy(area) for area in game_state.pot_areas]
        self.game_state.station_areas = [copy.copy(area) for area in game_state.station_areas]
        self.possible_points = 0
        self.area: Area | None = None

    def to_tuple(self):
        return self.__class__.__name__, None if self.area is None else self.area.id, *self.game_state.to_tuple()

    def get_neighbours(self):
        neighbours = []
        area_types: List[Tuple[List[Area], Callable[[GameState, int], GameNode]]] = [
            (self.game_state.plant_areas, PlantAreaNode),
            (self.game_state.garden_areas, GardenAreaNode),
            (self.game_state.station_areas, StationAreaNode),
            (self.game_state.garden_pot_areas, GardenPotAreaNode),
            (self.game_state.pot_areas, PotAreaNode),
        ]
        for areas, node_factory in area_types:
            for i in range(len(areas)):
                node = node_factory(self.game_state, i)
                if node.possible_points == 0:
                    continue
                if node.possible_points < 0:
                    print(f"{node} returned a negative points amount", file=sys.stderr)
                neighbours.append((node, self.compute_cost(node)))
        return neighbours

    def compute_cost(self, node: "GameNode"):
        circles_to_avoid = []
        for area in self.game_state.areas:
            circle = Circle(area.center_x, area.center_y, area.radius)
            if not circle.contains_point(self.area.center_x, self.area.center_y) and not circle.contains_point(node.area.center_x, node.area.center_y) and area.radius != 0:
                circles_to_avoid.append(circle)
        return Cost(node.area.time_spent, node.possible_points, find_path((self.area.center_x, self.area.center_y), (node.area.center_x, node.area.center_y), circles_to_avoid))


class PlantAreaNode(GameNode):
    def __init__(self, game_state, area_index: int):
        super().__init__(game_state, False)
        self.area = self.game_state.plant_areas[area_index]
        self.plants_taken = min(MAX_ROBOT_PLANTS - self.game_state.robot_unpotted_plants - self.game_state.robot_potted_plants, self.area.plants)
        self.game_state.robot_unpotted_plants += self.plants_taken
        self.area.plants -= self.plants_taken
        self.possible_points = self.plants_taken * POINTS_FOR_UNPOTTED_PLANTS


class StationAreaNode(GameNode):
    def __init__(self, game_state, area_index: int):
        super().__init__(game_state, False)
        self.area = self.game_state.station_areas[area_index]
        potted_plants_added = min(self.game_state.robot_potted_plants, 6 - self.area.plants)
        unpotted_plants_added = min(self.game_state.robot_unpotted_plants, 6 - self.area.plants - potted_plants_added)
        self.area.plants += potted_plants_added + unpotted_plants_added
        self.possible_points = potted_plants_added * POINTS_FOR_POTTED_PLANTS + unpotted_plants_added * POINTS_FOR_UNPOTTED_PLANTS
        self.game_state.robot_unpotted_plants = 0


class GardenAreaNode(GameNode):
    def __init__(self, game_state, area_index: int):
        super().__init__(game_state, False)
        self.area = self.game_state.garden_areas[area_index]
        potted_plants_added = min(self.game_state.robot_potted_plants, 6 - self.area.plants)
        unpotted_plants_added = min(self.game_state.robot_unpotted_plants, 6 - self.area.plants - potted_plants_added)
        self.area.plants += potted_plants_added + unpotted_plants_added
        self.possible_points = potted_plants_added * POINTS_FOR_POTTED_PLANTS + unpotted_plants_added * POINTS_FOR_UNPOTTED_PLANTS
        self.game_state.robot_unpotted_plants -= unpotted_plants_added
        self.game_state.robot_potted_plants -= potted_plants_added


class GardenPotAreaNode(GameNode):
    def __init__(self, game_state, area_index: int):
        super().__init__(game_state, False)
        self.area = self.game_state.garden_pot_areas[area_index]
        pots_taken = min(self.game_state.robot_unpotted_plants, self.area.pots)
        self.game_state.robot_unpotted_plants -= pots_taken
        self.game_state.robot_potted_plants += pots_taken
        potted_plants_added = min(self.game_state.robot_potted_plants, 6 - self.area.plants)
        pots_taken_but_not_replaced = max(0, pots_taken - potted_plants_added)
        unpotted_plants_added = min(self.game_state.robot_unpotted_plants, 6 - self.area.plants - potted_plants_added)
        self.game_state.robot_potted_plants -= potted_plants_added
        self.game_state.robot_unpotted_plants -= unpotted_plants_added
        self.area.plants += potted_plants_added + unpotted_plants_added
        self.possible_points = potted_plants_added * POINTS_FOR_POTTED_PLANTS + unpotted_plants_added * POINTS_FOR_UNPOTTED_PLANTS + pots_taken_but_not_replaced * POINTS_FOR_POT


class PotAreaNode(GameNode):
    def __init__(self, game_state, area_index: int):
        super().__init__(game_state, False)
        self.area = self.game_state.pot_areas[area_index]
        pots_taken = min(self.game_state.robot_unpotted_plants, self.area.pots)
        self.game_state.robot_unpotted_plants -= pots_taken
        self.game_state.robot_potted_plants += pots_taken
        self.area.pots -= pots_taken
        self.possible_points = pots_taken * POINTS_FOR_POT


class StartNode(GameNode):
    class StartArea(Area):
        def __init__(self, x, y):
            super().__init__(x, y, 1500, 1000)

    def __init__(self, game_state, x, y):
        super().__init__(game_state, False)
        self.area = StartNode.StartArea(x, y)


# ---------------------- DEFINE WAY TIME ----------------------

class Cost(a_star.Cost):
    def __init__(self, time_in_node, points, path = None):
        self.path = path
        self.time_in_node = time_in_node
        self.time = (0 if self.path is None else self.path.length) + self.time_in_node
        self.points = points

    def as_number(self):
        return -self.points / self.time

    def __add__(self, other):
        return Cost(self.time + other.time, self.points + other.points)


# ---------------------- FUNCTION TO USE ----------------------

def find_best_strategy(game_state):
    path = a_star.a_star(StartNode(game_state, 0, 0), Cost(0.001, 0), stop_after=10, stop_on_path_ends=True)
    areas = []
    for node, cost in path[1:]:
        areas.append((node.area, cost.path))
    return areas


if __name__ == '__main__':
    start = time.time()
    strategy = find_best_strategy(GameState())
    print(strategy)
    print("time taken :", time.time() - start)
    # print(TimeIt)
