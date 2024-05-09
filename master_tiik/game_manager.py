import find_best_strategy as strat
from threading import Thread
import time
from value_to_set import POSITION_PINCE_DU_CENTRE

from communication import CommunicationService
from detection import DetectionService
from position import PositionService
from utils import Line, Point, find_path, Circle
from useful_class import StationArea, GardenArea, GardenPotArea, GameState, PotArea, Path, PlantArea, Area, Action, \
    MoveAction
from math import pi, atan, sqrt, atan2, cos, sin

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
        self.global_point = 0
        self.start_time = time.time()
        self.current_action = None
        self.detection_service = detection_service
    
    def run(self):
        print("game manager ... ", "ready to operate")
        self.define_areas()
        self.com_service.wait_start()
        best_strategy = [1] #yellow_garden_area_1, yellow_garden_pot_area_1] #strat.find_best_strategy(self.game_state)
        while True:
            for area in best_strategy:
                self.set_up_area_action(area)
                print("finished area")
        self.set_time()

    def define_areas(self):
        while self.color == "":
            color = "blue"
            if color == "blue":
                self.game_state.init_areas(blue_specific_areas, yellow_specific_areas)
                print("Color Blue Selected")
                self.color = "blue"
            elif color == "yellow":
                self.game_state.init_areas(yellow_specific_areas, blue_specific_areas)
                print("Color Yellow Selected")
                self.color = "yellow"
            else :
                print("Still no color")

    def set_up_area_action(self,area):
        if isinstance(area, PlantArea):
            front_plier = None
            for plier in self.position_service.pliers:
                plier.get_pliers_value()
                if plier.value == 0 :
                    front_plier = plier
            if front_plier != None:
                dir_angle = atan2(area.y - self.position_service.y,area.x - self.position_service.x)
                distance = sqrt((area.y - self.position_service.y)**2 + (area.x - self.position_service.x)**2) - area.radius - POSITION_PINCE_DU_CENTRE
                x = distance * cos(dir_angle) + self.position_service.x
                y = distance * sin(dir_angle) + self.position_service.y
                angle = (dir_angle - self.position_service.angle - plier.x) # angle - angle - x ??
                self.move(x, y, angle)
                x += 50*cos(dir_angle)
                y += 50*sin(dir_angle)
                self.com_service.arm_down(0)
                self.move(x,y,angle)
                self.com_service.grab_plant(0)
                self.wait_end_action()
        if isinstance(area, GardenPotArea):
            self.move(area.center_x, area.center_y, "nan")
            self.com_service.release_on_garden(0)
            self.wait_end_action()
        if isinstance(area, GardenArea):
            self.move(area.center_x, area.center_y, "nan")
            print("ok, on a fini de se déplacer!")
            self.com_service.release_on_ground(0)
            print("sent")
            self.wait_end_action()
        if isinstance(area, PotArea):
            self.move(area.center_x, area.center_y, "nan")
            self.com_service.potting(0)
            self.wait_end_action()
        if area == 1:
            self.move(300, 0, "nan")
            self.move(300, 200, "nan")
            self.move(0, 200, "nan")

    def move(self, x, y, angle):
        circles_to_avoid = []
        for area in self.game_state.areas:
            circle = Circle(area.center_x, area.center_y, area.radius)
            if not circle.contains_point(self.position_service.x, self.position_service.y) and not circle.contains_point(x, y) and area.radius != 0:
                circles_to_avoid.append(circle)
        current_position = Point(self.position_service.x, self.position_service.y)
        destination = Point(x, y)
        while abs(current_position - destination) > 1:
            path = find_path((self.position_service.x, self.position_service.y), (x, y), circles_to_avoid)
            print("len", len(path.points))
            for x_checkpoint, y_checkpoint in path.points[1:]:
                print("moving from ", self.position_service.x, self.position_service.y, " to ", x, y)
                self.com_service.move(x, y, angle)
                premature_stop = False
                #time.sleep(0.5) # Wait a bit so the previous call has time to be sent
                print("mvt_state :", self.com_service.mvt_state())
                while self.com_service.mvt_state():
                    if self.detection_service.emergency_stop:
                        self.com_service.emergencyStop()
                        while self.detection_service.emergency_stop:
                            pass
                        premature_stop = True
                print("mvt_state :", self.com_service.mvt_state())
                pos = self.com_service.get_position()
                current_position = Point(pos[0], pos[1])
                print("prematurestop:", premature_stop)
                if premature_stop:
                    break
            print("after for")
        print("afterwhile")
        self.position_service.x = current_position.x
        self.position_service.y = current_position.y

    def wait_end_action(self):
        while not self.com_service.is_action_done():
            time.sleep(0.1)

    def set_time(self):
        self.start_time = time.time()

    def send_next_action(self):
        self.current_action = self.actions.pop(0)
        print("sending action", self.current_action)
        self.com_service.send_action(self.current_action)
