import find_best_strategy as strat
from threading import Thread
import time
<<<<<<< HEAD
from useful_class import StationArea, GardenArea, GardenPotArea, GameState, PotArea
from math import pi
=======
from useful_class import StationArea, GardenArea, GardenPotArea, GameState, PotArea, Path
from math import pi, atan, sqrt
>>>>>>> 5719a45 (WIP: added serial communication)

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
    def __init__(self,com_service,position_service):
        super().__init__()
        self.actions = []
        self.action_running = False
        self.com_service = com_service
        self.color = ""
        self.game_state = GameState()
        self.position_service = position_service
        self.state = 0
    
    def run(self):
        print("game manager ... ", "ready to operate")
        self.define_areas()
        while True :
            for area in strat.find_best_strategy(self.game_state):
                define_next_actions()
                wait_end_action()
                

    def define_areas(self):
        while self.color == "":
            color = input()
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
            

    def define_next_actions(self,next_area):
        if isinstance(element, PlantArea):
            self.actions.append(Action(1,2,[element.center_x,element.center_y,element.radius]))
            self.actions.append(Action(2,0,[])) # trouver les plantes et les prendre
        elif isinstance(element, GardenArea):
            pass
        elif isinstance(element, PotArea):
            pass
        elif isinstance(element, StationArea):
            pass
        elif isinstance(element, Area):
            pass
        elif isinstance(element, GardenPotArea):
            pass
        elif isinstance(element, GardenPotArea):
            pass
        

    def wait_end_action(self):
        while self.action_running:
            self.define_action_state()
            time.sleep(0.1)
        
    def sent_action(self):
        pass
        
        
