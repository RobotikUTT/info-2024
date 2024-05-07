import serial
import time
from threading import Thread
import struct
from math import pi

PACKET_SIZE = 15

class SerialService(Thread):
    def __init__(self):
        super().__init__()
        self.ser = serial.Serial('COM11',9600,timeout=0)
        self.is_moving = False
        self.position_to_send = [1000,200,pi/2]
        self.detected_position = []

    def run(self):
        self.ser.close()
        self.ser.open()
        dataList = b''
        print("communication service ... ", "ready to operate")
        if (not self.is_moving):
                print ("DATA TRANSMIT")
                print ("send data : ", self.position_to_send)
                print (" ")
                self.send_action()
        while True :
            self.listen_state()
        
    def listen_state(self):
        self.ser.close()
        self.ser.open()
        

        # Wait for firsts byte
        while True :
            byte_read = b''
            while (len(byte_read) < 15) :
                byte_read += self.ser.readline()
            self.read_coord(byte_read[3:])
            print(byte_read[2])
            if (byte_read[2] == 0x00):
                self.is_moving = False
            elif (byte_read[2] == 0x01):
                self.is_moving = True


    def read_coord(self,bytes_received):

        self.detected_position.append(struct.unpack('fff',bytes_received))
        print("received value : ",self.detected_position[-1])
        
    def send_action(self):
        self.ser.write(b'\x02')
        var = b''
        for i in self.position_to_send :
            if (i != 'nan'):
                self.ser.write(struct.pack('f',i))
                var += struct.pack('f',i)
            else :
                self.ser.write(b'\xff\xff\xff\xff')
                var += b'\xff\xff\xff\xff'
        print(var)
        self.is_moving = True
        self.ser.flush()
        
    def send_stop(self):
        self.ser.close()
        self.ser.open()
        self.ser.write(b'\x01\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff')
        self.ser.flush()
        self.ser.close()


    
if __name__ == "__main__":
    serial_thread = SerialService()
    serial_thread.start()
    serial_thread.join()
    
