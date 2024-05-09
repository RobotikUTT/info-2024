from threading import Thread

from smbus import SMBus

from useful_class import Devices


class I2CCommunication:
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
            
    def wait_start():
        while True:
            time.sleep(1)
            if self.bus.read_i2c_block_data(10, 0, 4)[0] == 1:
                return
                
    def action_done(self):
        return self.bus.read_i2c_block_data(10, 0, 4)[1] == 1
    
            


if __name__ == "__main__":
    i2c = I2CCommunication()
    i2c.send(Devices.ARDUINO, [0])
