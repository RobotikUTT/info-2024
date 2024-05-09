# ---------------------- DEFINE AREA CARACT ----------------------
import random
import uuid
from enum import Enum
from math import pi, sqrt, atan2, nan, isnan
from typing import List
from value_to_set import POINTS_FOR_POTTED_PLANTS,POINTS_FOR_UNPOTTED_PLANTS

from position import PositionService
from utils import Circle


class Devices(Enum):
    ARDUINO, \
    STM32, \
        = range(2)


class Plier:
    def __init__(self,id,angle):
        self.id = id
        self.angle = angle
        self.plants = [Plant(),Plant()]
        self.value = 0

    def set_grab_plant(self,received_data):
        if received_data == 1 :
            self.plants[0].exist = True
        elif received_data == 2 : 
            self.plants[1].exist = True
        elif received_data == 3 : 
            self.plants[0].exist = True
            self.plants[1].exist = True

    def set_potted_plant(self,received_data):
        if received_data == 1 :
            self.plants[0].is_potted = True
        elif received_data == 2 : 
            self.plants[1].is_potted = True
        elif received_data == 3 : 
            self.plants[0].is_potted = True
            self.plants[1].is_potted = True

    def get_pliers_value(self):
        for i in self.plants :
            self.value += i.calcul_value

class Plant : 
    def __init__(self):
        self.exist = False
        self.is_potted = False
        self.value = 0
    
    def calcul_value(self):
        if self.exist:
            if self.is_potted :
                self.value = POINTS_FOR_POTTED_PLANTS
            else:
                self.value = POINTS_FOR_UNPOTTED_PLANTS
        return self.value


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

    def get_action(self) -> "Action | None":
        return None


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
    def __init__(self, device: Devices):
        self.device = device

    def __str__(self):
        return self.__class__.__name__

    def get_data(self):
        raise NotImplementedError("get_action method is not implemented")


class MoveAction(Action):
    def __init__(self, position_service: PositionService, x=nan, y=nan, force_angle: "bool | int"=False):
        super().__init__(Devices.STM32)
        self.x = x
        self.y = y
        self.force_angle = force_angle
        self.position_service = position_service

    def get_data(self):
        if not self.force_angle:
            return [self.x, self.y, nan]
        if isnan(self.x) or isnan(self.y):
            return [nan, nan, self.force_angle]
        angle = atan2(self.y - self.position_service.y, self.x - self.position_service.x)
        return [self.x, self.y, angle]


class TakePotAction(Action):
    def __init__(self):
        super().__init__(Devices.ARDUINO)
        self.pot = random.randint(1, 5)

    def get_data(self):
        return [0]


class DepositPlantAction(Action):
    def __init__(self):
        super().__init__(Devices.ARDUINO)
        self.plant = random.randint(1, 6)

    def get_data(self):
        return [3]


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
        self.pot_areas: List[PotArea] = [
            PotArea(600, 2000 - 35, pi / 2),  # IMPORTANT PAS LES BONNES VALEURS POUR X
            PotArea(3000 - 600, 2000 - 35, pi / 2),  # IMPORTANT PAS LES BONNES VALEURS POUR X
        ]
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
