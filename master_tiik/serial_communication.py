from typing import Tuple

import serial
from threading import Thread
import struct

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
        
    def send_action(self, x, y, angle, speed = "nan"):

        self.detected_position = [x, y, angle]
        self.ser.close()
        self.ser.open()
        self.ser.write(b'\x02')
        var = b''
        for i in [x, y, angle, speed]:
            if i != 'nan':
                self.ser.write(struct.pack('f',i))
                var += struct.pack('f',i)
            else :
                self.ser.write(b'\xff\xff\xff\xff')
        self.is_moving = True
        self.ser.flush()
        self.ser.close()
        
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
    
    def get_mvt_state(self):
        return self.is_moving



if __name__ == "__main__":
    serial_thread = SerialService()
    serial_thread.start()
    serial_thread.join()
    