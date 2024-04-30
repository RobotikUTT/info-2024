
# ---------------------- DEFINE AREA CARACT ----------------------

class Area:
    def __init__(self, id, centerX, centerY, radius, time_spent):
        self.id = id
        self.centerX = centerX
        self.centerY = centerY
        self.radius = radius
        self.time_spent = time_spent

# PLANT

class PlantArea(Area):
    def __init__(self, id, x, y):
        super().__init__(id, x, y, 125, 10)
        self.plants = 6

# PLAYER AREA

class PlayerArea(Area):
    def __init__(self, id, x, y, radius, time_spent):
        super().__init__(id, x, y, radius, time_spent)
        
class StationArea(PlayerArea):
    def __init__(self, id, x, y):
        super().__init__(id, x, y, 225, 5)
        
class GardenArea(PlayerArea):
    def __init__(self, id, x, y,angle):
        super().__init__(id, x, y, 0, 3)
        self.angle = angle
        
class GardenPotArea(PlayerArea):
    def __init__(self, id, x, y,angle):
        super().__init__(id, x, y, 0, 7)

# POT AREA

class PotArea(Area):
	def __init__(self, id, x, y,angle):
        super().__init__(id, x, y, 0, 10)
        self.angle = angle

        
# ---------------------- DEFINE ACTION ----------------------

class Turn:
    def __init__(self,init_angle,final_angle):
        self.init_angle = init_angle
        self.final_angle = final_angle


class MoveForward:
    def __init__(self,distance,direction_angle):
        self.distance = distance
        self.directionAngle = direction_angle


# ---------------------- DEFINE GAME CARACT  ----------------------

class GameState:
    def __init__(self):
        self.plant_areas = [
			PlantArea(0, 1500, 500),
			PlantArea(1, 1000, 700),
			PlantArea(2, 1000, 1300),
			PlantArea(3, 1500, 1500),
			PlantArea(4, 2000, 1300),
			PlantArea(5, 2000, 700)
        ]
        self.player_areas = []
        self.robot_plants = 0
        
	def init_areas(self,player_areas):
		self.player_areas = player_areas
		

    def to_tuple(self):
        return self.robot_plants, *[(area.centerX, area.centerY, area.plants) for area in self.plant_areas], *[(area.centerX, area.centerY) for area in self.player_areas]

