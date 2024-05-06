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
        self.position_to_send = [10,10,"nan"]
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
            print("received data : ",byte_read)
            
#        print ("here")
#        while (second_byte_read == b'') :
#            print(second_byte_read)
#            second_byte_read = self.ser.readline()
#
#        if (second_byte_read == b'\x2c'):
#            while (len(byte_read) < 14) :
#                byte_read += self.ser.readline()
#            if len(byte_read) >= 14 :
#                first_byte_read = byte_read[13:]
#                byte_read = byte_read[:13]
#            if byte_read[0] == b'\x00':
#                self.is_moving = False
#                self.read_coord(byte_read)
#            elif byte_read[0] == b'\x01':
#                self.is_moving = True
#                self.read_coord(byte_read)
        
#        elif first_byte_read == b'\x02':
#            # debug state
#            byte_read = b''
#            while byte_read == b'' :
#                byte_read = self.ser.readline()
#            print ("debug : ",byte_read)
#        print (" ")


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
        print(var)
        self.is_moving = True
        self.ser.flush()
        
    def send_stop(self):
        self.ser.close()
        self.ser.open()
        if (self.is_moving):
            self.ser.write(0x01)
        self.ser.flush()
        self.ser.close()


    
if __name__ == "__main__":
    serial_thread = SerialService()
    serial_thread.start()
    serial_thread.join()
    
