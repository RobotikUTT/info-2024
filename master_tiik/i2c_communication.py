from threading import Thread

from smbus import SMBus

from master_tiik.useful_class import Devices


class I2CCommunication(Thread):
    def __init__(self):
        super().__init__()
        self.bus = SMBus(1)

    def send(self, device: Devices, data):
        if device == Devices.ARDUINO:
            address = 0x04
        else:
            raise ValueError(f"Device {device} is not registered")
        self.bus.write_i2c_block_data(address, 0, data)

    def is_action_done(self):
        return self.bus.read_i2c_block_data(0x04, 1, 1) == 0
