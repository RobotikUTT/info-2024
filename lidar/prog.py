from threading import Thread, RLock
from serial import Serial

PACKET_SIZE = 47
CRC_TABLE = b"\x00\x4d\x9a\xd7\x79\x34\xe3\xae\xf2\xbf\x68\x25\x8b\xc6\x11\x5c" \
            b"\xa9\xe4\x33\x7e\xd0\x9d\x4a\x07\x5b\x16\xc1\x8c\x22\x6f\xb8\xf5" \
            b"\x1f\x52\x85\xc8\x66\x2b\xfc\xb1\xed\xa0\x77\x3a\x94\xd9\x0e\x43" \
            b"\xb6\xfb\x2c\x61\xcf\x82\x55\x18\x44\x09\xde\x93\x3d\x70\xa7\xea" \
            b"\x3e\x73\xa4\xe9\x47\x0a\xdd\x90\xcc\x81\x56\x1b\xb5\xf8\x2f\x62" \
            b"\x97\xda\x0d\x40\xee\xa3\x74\x39\x65\x28\xff\xb2\x1c\x51\x86\xcb" \
            b"\x21\x6c\xbb\xf6\x58\x15\xc2\x8f\xd3\x9e\x49\x04\xaa\xe7\x30\x7d" \
            b"\x88\xc5\x12\x5f\xf1\xbc\x6b\x26\x7a\x37\xe0\xad\x03\x4e\x99\xd4" \
            b"\x7c\x31\xe6\xab\x05\x48\x9f\xd2\x8e\xc3\x14\x59\xf7\xba\x6d\x20" \
            b"\xd5\x98\x4f\x02\xac\xe1\x36\x7b\x27\x6a\xbd\xf0\x5e\x13\xc4\x89" \
            b"\x63\x2e\xf9\xb4\x1a\x57\x80\xcd\x91\xdc\x0b\x46\xe8\xa5\x72\x3f" \
            b"\xca\x87\x50\x1d\xb3\xfe\x29\x64\x38\x75\xa2\xef\x41\x0c\xdb\x96" \
            b"\x42\x0f\xd8\x95\x3b\x76\xa1\xec\xb0\xfd\x2a\x67\xc9\x84\x53\x1e" \
            b"\xeb\xa6\x71\x3c\x92\xdf\x08\x45\x19\x54\x83\xce\x60\x2d\xfa\xb7" \
            b"\x5d\x10\xc7\x8a\x24\x69\xbe\xf3\xaf\xe2\x35\x78\xd6\x9b\x4c\x01" \
            b"\xf4\xb9\x6e\x23\x8d\xc0\x17\x5a\x06\x4b\x9c\xd1\x7f\x32\xe5\xa8"

class LidarService(Thread):

    def __init__(self):
        super().__init__()
        self.serial = Serial("/dev/ttyS0", baudrate = 230400)
        self.values = {}
        self.lock = RLock()
        

    def run(self):
        while True:
            i = 0
            while True :
                j = 0
                while self.serial.read() != b"T" and self.serial.read() != b",":
                    j+=1
                packet = bytearray(b"\x54\x2C")
                while len(packet) < PACKET_SIZE :
                    packet.extend(self.serial.read())
                start_angle = stick_bytes(packet[4:6])/100
                end_angle = stick_bytes(packet[42:44])/100
                expected_crc = packet[-1]
                # CRC check
                crc = 0
                for b in packet[:-1]:
                   crc = CRC_TABLE[(crc ^ b) & 0xff]
                if crc != expected_crc:
                    print(crc, expected_crc)
                    continue
                with self.lock:
                    print("AAAAAAAAAAAAAAAAAAAAAHHHHHHHHHHHHHHHHHHHHHHHHHHH")
                    angle_step = (end_angle - start_angle) / 12
                    for i in range(12):
                        self.values[start_angle + angle_step * i] = (data[i * 3] << 8) | data[i * 3 + 1]

    def get_values(self):
        with self.lock:
            return {**self.values}
            
def stick_bytes(bytesList):
        output = 0
        for i in range(len(bytesList)) :
            output |= bytesList[i] << (8*i)
        return output
        

if __name__ == "__main__":
    thread = LidarService()
    thread.start()
    thread.join()
