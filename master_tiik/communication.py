import smbus
from threading import Thread
import time
import pigpio

class CommunicationService(Thread):
    def __init__(self):
        super().__init__()
        self.rx_pin = 0
        self.tx_pin = 0
        self.serial = pigpio.pi()
        self.receive_data = []

    def run(self):
        print("communication service ... ", "ready to operate")
        self.init_pin()
        while True :
            received_data()
            print 
        
    def init_pin(self):
        self.serial.set_mode(self.rx_pin,pigpio.INPUT)
        self.serial.set_mode(self.tx_pin,pigpio.OUTPUT)
        serialpi.bb_serial_read_open(rxPin,baudrate,8)
        pigpio.exceptions = False
        self.serial.bb_serial_read_close(rxPin)
        pigpio.exceptions = True
        
    def send_data(self,data):
        self.serial.write(self.tx_pin,pigpio.HIGH)
        time.sleep(0.01)
        for bit in data :
            self.serial.write(self.tx_pin,bit)
            time.sleep(0.01)
    
    def receive_data(self):
        pass
        

