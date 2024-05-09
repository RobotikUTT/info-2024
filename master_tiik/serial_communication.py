from typing import Tuple

import serial
from threading import Thread
import struct
from math import pi

PACKET_SIZE = 15

class SerialService(Thread):
    def __init__(self):
        super().__init__()
        self.ser = serial.Serial('/dev/ttyACM0',9600,timeout=0)
        self.is_moving = False
        self.detected_position = []

    def run(self):
        print("communication service ... ", "ready to operate")
        self.ser.close()
        self.ser.open()
        self.send_action((0,1700,"nan"))
        while True:
            self.listen_state()
        
    def listen_state(self):
        self.ser.close()
        self.ser.open()

        # Wait for firsts byte

        while True :
            byte_read = b''
            while len(byte_read) < 15:
                byte_read += self.ser.readline()
            print("okay ?")
            if byte_read[:1] == b'T,':
                self.read_coord(byte_read[3:])
                print(byte_read[2])
                if byte_read[2] == 0x00:
                    self.is_moving = False
                elif byte_read[2] == 0x01:
                    self.is_moving = True

    def read_coord(self, bytes_received):
        self.detected_position.append(struct.unpack('fff', bytes_received))
        print("received value : ", self.detected_position[-1])
        
    def send_action(self, data: Tuple[float, float, float]):
        x = data[0] 
        y = data[1]
        angle = data[2]
        self.detected_position = [x, y, angle]
        print("communication service ... ", "ready to operate")
        self.ser.write(b'\x02')
        var = b''
        for i in [x, y, angle]:
            if i != 'nan':
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

    def init_values(self):
        self.ser.close()
        self.ser.open()
        self.ser.write(b'\x03\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff')
        self.ser.flush()
        self.ser.close()



if __name__ == "__main__":
    serial_thread = SerialService()
    serial_thread.start()
    serial_thread.join()
    
