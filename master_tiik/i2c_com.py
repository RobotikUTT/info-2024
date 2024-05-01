import smbus
from threading import Thread
import time

class I2CService(Thread):
    def __init__(self):
        super().__init__()
        self.bus = smbus.SMBus(1)
        self.stm_address = 0x08
        self.arduino_address = 0x10
        self.action_running = False

    def run(self):
        print("i2c service ... ", "ready to operate")

    def ask_action_state(self):
        return self.action_running

def read_from_slave():
    return None
