import find_best_strategy as strat
from threading import Thread
import time
        
# ---------------------- THREAD GAME MANAGER ----------------------

class GameManager(Thread):
    def __init__(self,i2c_service):
        super().__init__()
        self.actions = []
        self.action_running = True
        self.i2c_service = i2c_service
    
    def run(self):
        print("game manager ... ", "ready to operate")
        while (self.action_running) :
            self.define_action_state()
            time.sleep(0.1)
        print("oui")
        go = strat.find_best_strategy()
        print(go)
            
    def define_action_state(self):
        self.action_running = self.i2c_service.ask_action_state()
        
    def sent_action(self):
        pass
        
        
