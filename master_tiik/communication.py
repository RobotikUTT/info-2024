from useful_class import Action, Devices
from serial_service import SerialService
from i2c_service import I2CService


class CommunicationService:
    def __init__(self, serial_service: SerialService, i2c_service: I2CService):
        super().__init__()
        self.serial = serial_service
        self.i2c = i2c_service

    def send_action(self, action: Action):
        device = action.device
        if device == Devices.ARDUINO:
            self.i2c.send(action)
        elif device == Devices.STM32:
            self.serial.send(action)

    def is_action_done(self):
        return self.serial.is_moving() or self.i2c.is_action_done()
