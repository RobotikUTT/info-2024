import find_best_strategy as strat
from threading import Thread
import time
from useful_class import Area,PlantArea,PlayerArea,StationArea,GardenArea,GardenPotArea,GameState

pi = 3.14159265
distance_tiik_pot = 14
        
# ---------------------- THREAD GAME MANAGER ----------------------

class GameManager(Thread):
    def __init__(self,i2c_service,team_color):
        super().__init__()
        self.actions = []
        self.action_running = True
        self.i2c_service = i2c_service
        self.color = False
        self.game_state = GameState()
    
    def run(self):
        self.define_areas()
        print("game manager ... ", "ready to operate")
        while (self.action_running) :
            self.define_action_state()
            time.sleep(0.1)
        go = strat.find_best_strategy()
    
    def define_areas(self):
        while (!self.color): 
            print("Define color")
            color = input()
            if color == "blue" :
                self.game_state.init_areas([
                    StationArea(0,225,225),
                    StationArea(1,3000-(450/2),1000),
                    StationArea(2,225,2000-(450/2)),
                    GardenPotArea(3,35,450+(325/2),pi), # à redéfinir pour x
                    GardenPotArea(4,3000-35,450+325+450+(325/2),0),
                    GardenArea(5,600+(325/2),0,3*pi/2)
                ])
            elif color == "yellow":
                self.game_state.init_areas([
                    StationArea(0,3000-(450/2),225),
                    StationArea(1,450/2,1000),
                    StationArea(2,3000-(450/2),2000-(450/2)),
                    GardenPotArea(3,3000-35,450+(325/2),pi), # à redéfinir pour x
                    GardenPotArea(4,35,450+325+450+(325/2),0),
                    GardenArea(5,3000-(600+(325/2)),0,3*pi/2)
                ])
            else : 

    
    def define_action_state(self):
        self.action_running = self.i2c_service.ask_action_state()
        
    def sent_action(self):
        pass
        
        
