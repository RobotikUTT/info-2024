import find_best_strategy as strat
from threading import Thread


class Turn:
    def __init__(self,angle,clockwise):
        self.angle = angle
        self.clockwise = clockwise


class MoveForward:
    def __init__(self,distance,direction_angle):
        self.distance = distance
        self.direction_angle = direction_angle

class GameManager(Thread):
    def __init__(self):
        super().__init__()
