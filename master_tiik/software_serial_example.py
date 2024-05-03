import serial
import time
from threading import Thread

ser = serial.Serial('/dev/ttyACM0',115200,timeout=0)





class CommunicationService(Thread):
    def __init__(self):
        super().__init__()
        self.ser = serial.Serial('/dev/ttyACM0',115200,timeout=0)
        self.is_moving = True

    def run(self):
        print("communication service ... ", "ready to operate")
        
        

        
    def received_state(self):
        self.ser.close()
        self.ser.open()
        bytes_to_read = b'' 
        first_byte_read = self.ser.readline()
        while first_byte_read = b'' :
            first_byte_read = self.ser.readline()
        
        while len(bytes_to_read) != 12:
            byte_read = self.ser.readline() 
            if byte_read != b'':
                bytes_to_read += byte_read
        return bytes_to_read
    
    def request_state(self):
        
        
    def send_action(self):
        
    def send_stop(self):
        
    
if __name__ == "__main__":
    com_thread = CommunicationService()
    com_thread.start()
    com_thread.join()
    
