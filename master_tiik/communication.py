from useful_class import Action, Devices
from serial_communication import SerialService
from i2c_communication import I2CCommunication


class CommunicationService:
    def __init__(self, serial_service: SerialService, i2c_service: I2CCommunication):
        super().__init__()
        self.serial = serial_service
        self.i2c = i2c_service

    def is_action_done(self):
        return not self.serial.is_moving and self.i2c.action_done()

    # FONCTION STM32 
    
    def move(self,x,y,angle):
        self.serial.send_action(x,y,angle)

    def mvt_state(self):
        return self.serial.get_mvt_state()
        
    def get_position(self):
        return self.serial.detected_position
        
    def emergencyStop(self):
        self.serial.send_stop()
    
    # FONCTION ARDUINO
    
    def grab_plant(self,plier_id):
        self.i2c.send([0,plier_id])

    def grab_pot(self,plier_id):
        self.i2c.send([1,plier_id])

    def potting(self,plier_id):
        self.i2c.send([2,plier_id])

    def release_on_ground(self,plier_id):
        self.i2c.send([3,plier_id])

    def release_on_garden(self,plier_id):
        self.i2c.send([4,plier_id])

    def open_unfull_pliers(self,plier_id):
        self.i2c.send([5,plier_id])

    def arm_down(self,plier_id):
        self.i2c.send([6,plier_id])
            
    def should_emergency_stop(self):
        return self.i2c.emergency_stop
        
    def wait_start(self):
        self.i2c.wait_start()
