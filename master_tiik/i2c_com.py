import smbus
from threading import Thread
import time

class I2CService(Thread):
	def __init__(self):
		super().__init__()
		self.bus = smbus.SMBus(1)
		self.stm_address = 0x08
		self.arduino_address = 0x10
		self.action_running = False
		
	def run(self):
		print("i2c service ... ", "ready to operate")
#		bus = smbus.SMBus(1)
#		address = 0x0a
#		data = [0x03,0x01,0x02,0x03]
#		while True:
#			bus.write_i2c_block_data(address,0,data)
#			read_data= bus.read_i2c_block_data(address,0,4)
#			print(read_data)
#			time.sleep(3)
		
	def ask_action_state(self):
		return self.action_running
		
		
def read_from_slave():
	return None
