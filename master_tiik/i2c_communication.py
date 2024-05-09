import time
from threading import Thread

from smbus import SMBus

from useful_class import Devices
import time


class I2CCommunication(Thread):
    def __init__(self):
        super().__init__()
        self.bus = SMBus(1)
        self.action_done = True
        self.emergency_stop = False

    def send(self, device: Devices, data):
        if device == Devices.ARDUINO:
            address = 10
        else:
            raise ValueError(f"Device {device} is not registered")
        self.bus.write_i2c_block_data(address, 0, data)

    def run(self):
        while True:
            data = self.bus.read_i2c_block_data(10, 0, 4)
            self.action_done = data[0] == 0
            self.emergency_stop = data[1] == 1
            
    def wait_start(self):
        while True:
            time.sleep(1)
            if self.bus.read_byte(10) == 1 :
                return
            
            
    def action_done(self):
        return self.bus.read_i2c_block_data(10, 0, 2)[1] == 1
            


if __name__ == "__main__":
    i2c = I2CCommunication()
    i2c.start()
    i2c.join()
    i2c.send(Devices.ARDUINO, [0])
