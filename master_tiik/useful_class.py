# ---------------------- DEFINE AREA CARACT ----------------------
import random
import uuid
from typing import List


class Area:
    def __init__(self, center_x, center_y, radius, time_spent):
        self.id = uuid.uuid4().bytes
        self.center_x = center_x
        self.center_y = center_y
        self.radius = radius
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

class Turn:
    def __init__(self, init_angle, final_angle):
        self.init_angle = init_angle
        self.final_angle = final_angle


class MoveForward:
    def __init__(self, distance, direction_angle):
        self.distance = distance
        self.directionAngle = direction_angle


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
        self.garden_areas: List[GardenArea] = [
            GardenArea(10, 10, 0),
            GardenArea(20, 20, 0),
            GardenArea(30, 30, 0),
        ]
        self.pot_areas: List[PotArea] = []
        self.garden_pot_areas: List[GardenPotArea] = []
        self.robot_unpotted_plants = 0
        self.robot_potted_plants = 0

    def init_areas(self, areas):
        for area in areas:
            if isinstance(area, PlantArea):
                self.plant_areas.append(area)
            elif isinstance(area, GardenArea):
                self.garden_areas.append(area)
            elif isinstance(area, PotArea):
                self.pot_areas.append(area)
            elif isinstance(area, GardenPotArea):
                self.garden_pot_areas.append(area)

    def to_tuple(self):
        return (self.robot_unpotted_plants,
                *[(area.center_x, area.center_y, area.plants) for area in self.plant_areas],
                *[(area.center_x, area.center_y, area.plants) for area in self.garden_areas])

    @property
    def areas(self):
        return self.plant_areas + self.garden_areas + self.pot_areas + self.garden_pot_areas
