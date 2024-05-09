from threading import Thread
import time
from math import pi
from useful_class import Plier



class PositionService:
    def __init__(self):
        super().__init__()
        self.x = 0
        self.y = 0
        self.angle = 0
        self.radius = 500
        self.pliers = [Plier(1,0),Plier(2,2*pi/3),Plier(3,4*pi/3)]

    def run(self):
        print("position service ... ", "ready to operate")
        
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

