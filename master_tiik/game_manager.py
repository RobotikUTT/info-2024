import find_best_strategy as strat
from threading import Thread
import time

from communication import CommunicationService
from detection import DetectionService
from position import PositionService
from utils import Line, Point
from useful_class import StationArea, GardenArea, GardenPotArea, GameState, PotArea, Path, PlantArea, Area, Action, \
    MoveAction
from math import pi, atan, sqrt, atan2

distance_tiik_pot = 14

# ---------------------- DEFINE AREA ----------------------

blue_station_area_1 = StationArea(3000-(450/2),225)
blue_station_area_2 = StationArea(450/2,1000)
blue_station_area_3 = StationArea(3000-(450/2),2000-(450/2))
blue_garden_pot_area_1 = GardenPotArea(3000-35,450+(325/2),pi)
blue_garden_pot_area_2 = GardenPotArea(35,450+325+450+(325/2),0)
blue_garden_area_1 = GardenArea(3000-(600+(325/2)),0,3*pi/2)
bonus_blue_pot_area_1 = PotArea(35,450+(325/2),pi)
bonus_blue_pot_area_2 = PotArea(3000-35,450+325+450+(325/2),0)
blue_specific_areas = [
    blue_station_area_1,
    blue_station_area_2,
    blue_station_area_3,
    blue_garden_pot_area_1,
    blue_garden_pot_area_2,
    blue_garden_area_1,
    bonus_blue_pot_area_1,
    bonus_blue_pot_area_2,
]

yellow_station_area_1 = StationArea(225,225)
yellow_station_area_2 = StationArea(3000-(450/2),1000)
yellow_station_area_3 = StationArea(225,2000-(450/2))
yellow_garden_pot_area_1 = GardenPotArea(35,450+(325/2),pi)
yellow_garden_pot_area_2 = GardenPotArea(3000-35,450+325+450+(325/2),0)
yellow_garden_area_1 = GardenArea(600+(325/2),0,3*pi/2)
bonus_yellow_pot_area_1 = PotArea(3000-35,450+(325/2),pi)
bonus_yellow_pot_area_2 = PotArea(35,450+325+450+(325/2),0)
yellow_specific_areas = [
    yellow_station_area_1,
    yellow_station_area_2,
    yellow_station_area_3,
    yellow_garden_pot_area_1,
    yellow_garden_pot_area_2,
    yellow_garden_area_1,
    bonus_yellow_pot_area_1,
    bonus_yellow_pot_area_2,
]

# ---------------------- THREAD GAME MANAGER ----------------------

class GameManager(Thread):
    def __init__(self, com_service: CommunicationService, position_service: PositionService, detection_service: DetectionService):
        super().__init__()
        self.actions = []
        self.action_running = False
        self.com_service = com_service
        self.color = ""
        self.game_state = GameState()
        self.position_service = position_service
        self.state = 0
        self.start_time = time.time()
        self.current_action = None
        self.detection_service = detection_service
    
    def run(self):
        print("game manager ... ", "ready to operate")
        self.define_areas()
        self.com_service.wait_start()
        while time:
            for area, path in strat.find_best_strategy(self.game_state):
                self.create_actions_for_area(area, path)
            for action in self.actions:
                self.send_next_action()
                self.wait_end_action()

    def define_areas(self):
        while self.color == "":
            color = input()
            if color == "blue":
                self.game_state.init_areas(blue_specific_areas, yellow_specific_areas)
                print("Color Blue Selected")
                self.color = "blue"
                self.actions = [MoveAction(self.position_service, 1000, 700, force_angle=True), TakePotAction(), MoveAction(self.position_service, 3000-(450/2), 2000-(450/2)), DepositPlantAction()]
            elif color == "yellow":
                self.game_state.init_areas(yellow_specific_areas, blue_specific_areas)
                print("Color Yellow Selected")
                self.color = "yellow"
                self.actions = [MoveAction(self.position_service, 2000, 700, force_angle=True), TakePotAction(), MoveAction(self.position_service, 225, 2000-(450/2)), DepositPlantAction()]
            else :
                print("Still no color")

    def create_actions_for_area(self, element: Area, path: Path):
        if len(path.points) == 0:
            return
        for point in path.points[1:-1]:
            self.actions.append(MoveAction(self.position_service, x=point[0], y=point[1]))
        print(path.points)
        last_point = Point(path.points[-2][0], path.points[-2][1])
        destination = Point(path.points[-1][0], path.points[-1][1])
        distance = destination - last_point
        destination = destination + (destination - last_point) / abs(distance) * element.radius
        self.actions.append(MoveAction(self.position_service, x=destination.x, y=destination.y, force_angle=True))
        action = element.get_action()
        if action is not None:
            self.actions.append(action)

    def wait_end_action(self):
        while not self.com_service.is_action_done():
            time.sleep(0.1)
            if self.detection_service.emergency_stop:
                self.com_service.emergencyStop()
                while self.detection_service.emergency_stop:
                    pass
                self.com_service.send_action(self.current_action)

    def set_time(self):
        self.start_time = time.time()

    def send_next_action(self):
        self.current_action = self.actions.pop(0)
        print("sending action", self.current_action)
        self.com_service.send_action(self.current_action)
