import smbus
from threading import Thread
import time

class CommunicationService(Thread):
    def __init__(self):
        super().__init__()

    def run(self):
        print("communication service ... ", "ready to operate")
        while 

    def ask_action_state(self):
        return self.action_running

