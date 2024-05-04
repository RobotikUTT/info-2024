import serial
import time
from threading import Thread
import struct
from math import pi

class CommunicationService(Thread):
    def __init__(self):
        super().__init__()
        self.ser = serial.Serial('/dev/ttyACM1',9600,timeout=0)
        self.is_moving = False
        self.position_to_send = [10,10,2*pi/3]
        self.detected_position = []

    def run(self):
        print("communication service ... ", "ready to operate")
        while True :
            if (not self.is_moving):
                self.send_action()
            self.received_state()
        
    def received_state(self):
        self.ser.close()
        self.ser.open()
        
        temporary_bytes = b''
        first_byte_read = self.ser.readline()
        
        while (first_byte_read == b'') :
            first_byte_read = self.ser.readline()
        if len(first_byte_read) > 1 :
            temporary_bytes += first_byte_read[1:]
            first_byte_read = first_byte_read[0]
        print(first_byte_read)    
        if first_byte_read == b'\x00':
            self.is_moving = False
        elif first_byte_read == b'\x01':
            self.is_moving = True
        
        byte_read = self.ser.readline()
        while len(temporary_bytes) != 12 :
            if byte_read != b'' :
                temporary_bytes+= byte_read
                
            byte_read = self.ser.readline()
        self.detected_position.append(struct.unpack('fff',temporary_bytes))
        self.ser.close()
        print(self.detected_position)
    
    def request_state(self):
        self.ser.close()
        self.ser.open()
        if (self.is_moving):
            self.ser.write(0x02)
            self.ser.write(struct.pack('f',self.position_to_send[0]))
            print(self.position_to_send[0])
            print(struct.pack('!f',self.position_to_send[0]))
            self.ser.write(struct.pack('f',self.position_to_send[1]))
            self.ser.write(struct.pack('f',self.position_to_send[2]))
        self.ser.flush()
        self.ser.close()
        
    def send_action(self):
        self.ser.close()
        self.ser.open()
        self.ser.write(0x02)
        for i in self.position_to_send :
            for j in  struct.pack('f',i):
                print(j)
                self.ser.write(j)
        self.ser.flush()
        self.ser.close()
        
    def send_stop(self):
        self.ser.close()
        self.ser.open()
        if (self.is_moving):
            self.ser.write(0x01)
        self.ser.flush()
        self.ser.close()
        
    
if __name__ == "__main__":
    com_thread = CommunicationService()
    com_thread.start()
    com_thread.join()
    
