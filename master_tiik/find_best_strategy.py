import copy
import a_star

MAX_ROBOT_PLANTS = 12

# ---------------------- DEFINE AREA CARACT ----------------------

class Area:
    def __init__(self, id, centerX, centerY, radius, time_spent):
        self.id = id
        self.centerX = centerX
        self.centerY = centerY
        self.radius = radius
        self.time_spent = time_spent

class PlantArea(Area):
    def __init__(self, id, x, y):
        super().__init__(id, x, y,4,10)
        self.plants = 6

class PlayerArea(Area):
    def __init__(self, id, x, y, radius, time_spent):
        super().__init__(id, x, y, radius, time_spent)
        
class StationArea(PlayerArea):
    def __init__(self, id, x, y):
        super().__init__(id, x, y, 10, 5)
        
class GardenArea(PlayerArea):
    def __init__(self, id, x, y):
        super().__init__(id, x, y, 0, 3)
        self.angle = 3.14 / 2 # absolument changer ça

        
# ---------------------- DEFINE ACTION ----------------------

class Turn:
    def __init__(self,init_angle,final_angle):
        self.init_angle = init_angle
        self.final_angle = final_angle


class MoveForward:
    def __init__(self,distance,direction_angle):
        self.distance = distance
        self.directionAngle = direction_angle
        

# ---------------------- DEFINE GAME CARACT  ----------------------


class GameState:
    def __init__(self):
        self.plant_areas = [
            PlantArea(0, 700, 1000),
            PlantArea(1, 1300, 1000),
            PlantArea(2, 500, 1500),
            PlantArea(3, 1500, 1500),
            PlantArea(4, 700, 2000),
            PlantArea(5, 1300, 2000),
        ]
        self.player_areas = [
            StationArea(0, 2000, 2237.5),
            StationArea(1, 2000, 762.5),
            StationArea(2, 612.5, 3000),
            StationArea(3, 1387.5, 3000),
            GardenArea(4, 612.5, 0),
            GardenArea(5, 1387.5, 0),
        ]
        self.robot_plants = 0

    def to_tuple(self):
        return self.robot_plants, *[(area.centerX, area.centerY, area.plants) for area in self.plant_areas], *[(area.centerX, area.centerY) for area in self.player_areas]

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

def find_best_strategy():
    path = a_star.a_star(StartNode(GameState(), 0, 0), Cost(0.001, 0), stop_after=10)
    return path[1:]
