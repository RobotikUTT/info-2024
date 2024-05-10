import time
from threading import Thread

from smbus import SMBus

from useful_class import Devices
import time


class I2CCommunication:
    def __init__(self):
        self.bus = SMBus(1)
        self.emergency_stop = False

    def send(self, command, plier):
        self.bus.write_byte(10, (command << 1) | (plier & 1))
        self.update_values()
            
    def wait_start(self):
        while True:
            time.sleep(1)
            if self.bus.read_byte(10) & 1 != 0:
                return

    def action_done(self):
        return self.request()[0] == 1

    def request(self):
        data = self.bus.read_byte(10)
        print(data)
        val = []
        for i in range(6):
            val.append((data & (1 << i)) > 0)
        return val
        
    def update_values(self):
        data = self.request()
            


if __name__ == "__main__":
    i2c = I2CCommunication()
    #i2c.start()
    actions = range(0, 8)
    for action in actions:
        i2c.send(action, 0)
        #i2c.join()
        while not i2c.action_done():
            pass
        time.sleep(1)
    
    print(i2c.request())
