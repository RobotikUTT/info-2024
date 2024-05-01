import find_best_strategy as strat
from threading import Thread
import time
from useful_class import StationArea, GardenArea, GardenPotArea, GameState
from math import pi

distance_tiik_pot = 14

# ---------------------- DEFINE AREA ----------------------

blue_station_area_1 = StationArea(0,3000-(450/2),225),
blue_station_area_2 = StationArea(1,450/2,1000),
blue_station_area_3 = StationArea(2,3000-(450/2),2000-(450/2)),
blue_garden_pot_area_1 = GardenPotArea(3,3000-35,450+(325/2),pi), # à redéfinir pour x
blue_garden_pot_area_2 = GardenPotArea(4,35,450+325+450+(325/2),0),
blue_garden_area_1 = GardenArea(5,3000-(600+(325/2)),0,3*pi/2)

yellow_station_area_1 = StationArea(0,225,225),
yellow_station_area_2 = StationArea(1,3000-(450/2),1000),
yellow_station_area_3 = StationArea(2,225,2000-(450/2)),
yellow_garden_pot_area_1 = GardenPotArea(3,35,450+(325/2),pi), # à redéfinir pour x
yellow_garden_pot_area_2 = GardenPotArea(4,3000-35,450+325+450+(325/2),0),
yellow_garden_area_1 = GardenArea(5,600+(325/2),0,3*pi/2)

        
# ---------------------- THREAD GAME MANAGER ----------------------

class GameManager(Thread):
    def __init__(self,i2c_service):
        super().__init__()
        self.actions = []
        self.action_running = True
        self.i2c_service = i2c_service
        self.color = False
        self.game_state = GameState()
        self.player_area = []
    
    def run(self):
        self.define_areas()
        print("game manager ... ", "ready to operate")
        while self.action_running:
            self.define_action_state()
            time.sleep(0.1)
        strategy = strat.find_best_strategy(self.game_state)
    
    def define_areas(self):
        while not self.color:
            print("Define color")
            color = input()
            if color == "blue" :
                self.game_state.init_areas([
                    StationArea(225,225),
                    StationArea(3000-(450/2),1000),
                    StationArea(225,2000-(450/2)),
                    GardenPotArea(35,450+(325/2),pi), # à redéfinir pour x
                    GardenPotArea(3000-35,450+325+450+(325/2),0),
                    GardenArea(600+(325/2),0,3*pi/2)
                ])
            elif color == "yellow":
                self.game_state.init_areas([
                    StationArea(3000-(450/2),225),
                    StationArea(450/2,1000),
                    StationArea(3000-(450/2),2000-(450/2)),
                    GardenPotArea(3000-35,450+(325/2),pi), # à redéfinir pour x
                    GardenPotArea(35,450+325+450+(325/2),0),
                    GardenArea(3000-(600+(325/2)),0,3*pi/2)
                ])
                self.color = "yellow"
    
    def define_action_state(self):
        self.action_running = self.i2c_service.ask_action_state()
        
    def sent_action(self):
        pass
        
        
