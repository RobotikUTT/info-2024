from typing import Tuple

import serial
from threading import Thread
import struct
from math import pi

PACKET_SIZE = 15

class SerialService(Thread):
    def __init__(self):
        super().__init__()
        self.ser = serial.Serial('/dev/ttyACM0',9600,timeout=None)
        self.is_moving = False
        self.detected_position = []

    def run(self):
        print("communication service ... ", "ready to operate")
        while True:
            self.listen_state()
        
    def listen_state(self):
        #self.ser.close()
        #self.ser.open()

        # Wait for firsts byte

        while True :
            byte_read = self.ser.read(15)
            if byte_read[:2] == b'T,':
                self.read_coord(byte_read[3:])
                print(byte_read[2])
                if byte_read[2] == 0x00:
                    self.is_moving = False
                elif byte_read[2] == 0x01:
                    self.is_moving = True

    def read_coord(self, bytes_received):
        self.detected_position = struct.unpack('fff', bytes_received)
        
    def send_action(self, x, y, angle, speed="nan"):
        self.detected_position = [x, y, angle]
        self.ser.write(b'\x02')
        var = b''
        for i in [x, y, angle]:
            if i != 'nan':
                self.ser.write(struct.pack('f',i))
                var += struct.pack('f',i)
            else :
                self.ser.write(b'\xff\xff\xff\xff')
        self.is_moving = True
        self.ser.flush()
        
    def send_stop(self):
        self.ser.write(b'\x01\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff')
        self.ser.flush()

    def init_values(self):
        self.ser.write(b'\x03\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff')
        self.ser.flush()
    
    def get_mvt_state(self):
        return self.is_moving

    
    def init_position(self, x, y, angle):
        self.detected_position = [x, y, angle]
        self.ser.write(b'\x03')
        for i in [x, y, angle]:
            if i != 'nan':
                print(i, end=" ")
                self.ser.write(struct.pack('f',i))
            else:
                print('nan', end=" ")
                self.ser.write(b'\xff\xff\xff\xff')
        self.ser.flush()


if __name__ == "__main__":
    serial_thread = SerialService()
    serial_thread.start()
    serial_thread.join()
    
