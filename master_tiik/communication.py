from useful_class import Action, Devices
from serial_communication import SerialService
from i2c_communication import I2CCommunication


class CommunicationService:
    def __init__(self, serial_service: SerialService, i2c_service: I2CCommunication):
        super().__init__()
        self.serial = serial_service
        self.i2c = i2c_service

    def send_action(self, action: Action):
        device = action.device
        if device == Devices.ARDUINO:
            self.i2c.send(Devices.ARDUINO, action.get_data())
        elif device == Devices.STM32:
            self.serial.send_action(action.get_data())
            
    def emergencyStop(self):
        self.serial.send_stop()

    def is_action_done(self):
        return self.serial.is_moving() or self.i2c.action_done

    def should_emergency_stop(self):
        return self.i2c.emergency_stop
