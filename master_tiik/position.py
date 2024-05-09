from threading import Thread
import time
from math import pi



class PositionService:
    def __init__(self):
        super().__init__()
        self.x = 0
        self.y = 0
        self.angle = 0
        self.radius = 500
        
    def set_position(self,x,y,angle):
        self.x = x
        self.y = y
        self.angle = angle%(2*pi)

    def get_angle(self):
        return self.angle

    def get_position(self):
        return (self.x,self.y)
    
    def get_radius(self):
        return self.radius

