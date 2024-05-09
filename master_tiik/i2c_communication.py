import time
from threading import Thread

from smbus import SMBus

from useful_class import Devices
import time


class I2CCommunication(Thread):
    def __init__(self):
        super().__init__()
        self.bus = SMBus(1)
        self.emergency_stop = False

    def send(self, data):
        for i, d in enumerate(data):
            pass #self.bus.write_byte_data(10, i, d)
            
    def wait_start(self):
        while True:
            time.sleep(1)
            #if self.request()[1] == 1:
            #    return
            return

    def action_done(self):
        #return self.request()[0] == 1
        return True
        
    def request(self):
        data = []
        for i in range(2):
            timeouted = True
            while timeouted:
                try:
                    data.append(self.bus.read_byte(10))
                    timeouted = False
                except TimeoutError:
                    pass # HEHE, NO TIMEOUT ERROR HERE !
        return data
    
            


if __name__ == "__main__":
    i2c = I2CCommunication()
    i2c.start()
    i2c.join()
    i2c.send(Devices.ARDUINO, [0])
