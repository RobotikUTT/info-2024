# ---------------------- DEFINE AREA CARACT ----------------------
import random
import uuid
from typing import List

from master_tiik.utils import Circle


class Area:
    def __init__(self, center_x, center_y, radius, time_spent):
        self.id = uuid.uuid4().bytes
        self.center_x = center_x
        self.center_y = center_y
        self.radius = radius
        self.circle = Circle(center_x, center_y, radius)
        self.time_spent = time_spent

    def __repr__(self):
        return str(self)

    def __str__(self):
        return f"{self.__class__.__name__}({self.center_x}, {self.center_y})"


class PlantArea(Area):
    def __init__(self, x, y):
        super().__init__(x, y, 125, 10)
        self.plants = 6


class StationArea(Area):
    def __init__(self, x, y):
        super().__init__(x, y, 225, 5)


class GardenArea(Area):
    def __init__(self, x, y, angle):
        super().__init__(x, y, 0, 3)
        self.angle = angle
        self.plants = 0


class GardenPotArea(Area):
    def __init__(self, x, y, angle):
        super().__init__(x, y, 0, 7)
        self.pots = 5
        self.plants = 0


class PotArea(Area):
    def __init__(self, x, y, angle):
        super().__init__(x, y, 0, 10)
        self.angle = angle
        self.pots = 5


# ---------------------- DEFINE ACTION ----------------------

class Action:
    def __init__(self,card,area):
        self.card = card
        self.movement = movement
        self.area = area
        
class Path:
    def __init__(self, keypoints):
        self.points = keypoints
        self.length = 0
        for i in range(1, len(keypoints)):
            self.length += sqrt((keypoints[i][0] - keypoints[i - 1][0]) ** 2 + (keypoints[i][1] - keypoints[i - 1][1]) ** 2)

    def __str__(self):
        return f"Path({str(self.points)[1:-1]})"

    def __repr__(self):
        return str(self)

# ---------------------- DEFINE GAME CARACT  ----------------------

class GameState:
    def __init__(self):
        self.plant_areas: List[PlantArea] = [
            PlantArea(1500, 500),
            PlantArea(1000, 700),
            PlantArea(1000, 1300),
            PlantArea(1500, 1500),
            PlantArea(2000, 1300),
            PlantArea(2000, 700)
        ]
        self.garden_areas: List[GardenArea] = []
        self.station_areas: List[StationArea] = []
        self.pot_areas: List[PotArea] = []
        self.garden_pot_areas: List[GardenPotArea] = []
        self.areas_to_avoid: List[Area] = []
        self.robot_unpotted_plants = 0
        self.robot_potted_plants = 0

    def init_areas(self, areas, areas_to_avoid):
        for area in areas:
            if isinstance(area, PlantArea):
                self.plant_areas.append(area)
            elif isinstance(area, GardenArea):
                self.garden_areas.append(area)
            elif isinstance(area, PotArea):
                self.pot_areas.append(area)
            elif isinstance(area, GardenPotArea):
                self.garden_pot_areas.append(area)
        self.areas_to_avoid.extend(areas_to_avoid)

    def to_tuple(self):
        return (self.robot_unpotted_plants,
                *[(area.center_x, area.center_y, area.plants) for area in self.plant_areas],
                *[(area.center_x, area.center_y, area.plants) for area in self.garden_areas],
                *[(area.center_x, area.center_y, area.pots) for area in self.pot_areas],
                *[(area.center_x, area.center_y, area.pots) for area in self.garden_pot_areas])

    @property
    def areas(self):
        return self.plant_areas + self.garden_areas + self.pot_areas + self.garden_pot_areas + self.areas_to_avoid
