from threading import Thread
import time

class PositionService(Thread):
	def __init__(self):
		super().__init__()
		self.x = 0
		self.y = 0
		self.angle = 0
		self.radius = 500
		
	def run(self):
		print("position service ... ", "ready to operate")
		
	def get_angle(self):
		return self.angle
		
	def get_position(self):
		return (self.x,self.y)

	
