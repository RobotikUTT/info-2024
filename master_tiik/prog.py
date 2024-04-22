from collections.abc import Callable
from math import acos, inf, pi, sin, sqrt, cos, radians
from threading import Thread, RLock
from typing import Iterable, List, Mapping, Tuple
from serial import Serial
import time
import numpy as np
from scipy.optimize import minimize
import matplotlib.pyplot as plt
import matplotlib.animation as animation

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
DELETE_POINTS_TIMEOUT = 1

class PositionService:
    def get_position(self):
        return (0, 0)
    def get_angle(self):
        return 0


class PointData:
    def __init__(self, angle, distance, robot_position, robot_angle, measured_at):
        super().__setattr__("angle", angle)
        super().__setattr__("distance", distance)
        super().__setattr__("robot_position", robot_position)
        super().__setattr__("robot_angle", robot_angle)
        super().__setattr__("x", cos(robot_angle + angle) * distance + robot_position[0])
        super().__setattr__("y", sin(robot_angle + angle) * distance + robot_position[1])
        super().__setattr__("absolute_angle", (robot_angle + angle) % (2 * pi))
        super().__setattr__("measured_at", measured_at)
    def __setattr__(self, name: str, value: time) -> None:
        raise TypeError("PointData is immutable")

class LidarService(Thread):
    def __init__(self,position_service,data_stocker):
        super().__init__()
        self.serial = Serial("/dev/serial0", baudrate = 230400, timeout=5, bytesize=8, parity="N", stopbits=1)
        self.lock = RLock()
        self.position_service = position_service
        self.data_stocker = data_stocker

    def run(self):
        dataList = []
        print("lidar ... ", "ready to operate")
        while True:
            data = self.serial.read()
            dataTreated = int.from_bytes(data, 'big')
            if (dataTreated == 0x54):
                dataList.append(dataTreated)
                data = self.serial.read()
                dataTreated = int.from_bytes(data, 'big')
                if (dataTreated == 0x2c):
                    dataList.append(dataTreated)
                    if (len(dataList) == PACKET_SIZE):
                        expectedCrc = dataList[-3]
                        crc = 0
                        for b in dataList[-2:]+dataList[0:-3] : 
                            crc = CRC_TABLE[(crc^b) & 0xff]
                        if expectedCrc == crc :
                            robot_position = self.position_service.get_position()
                            robot_angle = self.position_service.get_angle()
                            now = time.time()
                            formatted = sortData(dataList)
                            values = []
                            for distance, angle, confidence in zip(*formatted):
                                values.append(PointData(radians(angle%360), distance, robot_position, robot_angle, now))
                            data_stocker.add_values(values)
                        dataList = []
                    else :
                        dataList = []
            else :
                dataList.append(dataTreated)
    def get_values(self):
        return self.values
    
    def sortData(dataList):
        speed = (dataList[1]<<8 | dataList[0])/100
        startAngle = float(dataList[3]<<8 | dataList[2])/100
        lastAngle = float(dataList[-4]<<8 | dataList[-5])/100
        if (lastAngle > startAngle) :
            step = float(lastAngle - startAngle)/12
        else : 
            step = float(lastAngle + 360 - startAngle)/12
        
        angleList = []
        distanceList = []
        confidenceList = []
        
        for i in range (0,12):
            distanceList.append(dataList[4+(i*3)+1] << 8 | dataList[4+(i*3)])
            confidenceList.append(dataList[4+(i*3)+2])
            angleList.append(step*i + startAngle)
        return (distanceList,angleList, confidenceList)
        
        

class ObjectData:
    def __init__(self):
        self.points: List[PointData] = []
        self.boundary_points: Tuple[PointData, PointData] = []
        self.circle_center = (0, 0)
        self.circle_radius = 0
        self.separations_to_make = []

    def commit(self):
        print("oui")
        
class DataStocker(Thread):
    def __init__(self):
        super().__init__()
        self.values : List[PointData] = []
    
    def run(self):
        print("data stocker ... ", "ready to operate")
        while True:
            delete_before = time.time() - DELETE_POINTS_TIMEOUT
            points = []
            for point in self.values:
                if point.measured_at > delete_before :
                    points.append(point)
            self.values = points
    
    def add_values(self,points):
        self.values += points
    
    def get_values(self):
        return self.values
    

class DetectionService(Thread):
    def __init__(self, data_stocker):
        super().__init__()
        self.objects = [ObjectData()]
        self.data_stocker = data_stocker
        self.values : List[PointData] = []
        self.treated_values : List[PointData] = []

    def run(self):
        print("detection ... ", "ready to operate")
        while True:
            self.values = data_stocker.get_values()
            if len(self.values) == 0:
                continue
            treat_distances = [point for point in self.values if point.distance < 730 and point.angle > 3 and point.distance > 200 ]
            
        
         

if __name__ == "__main__":
    position_service = PositionService()
    data_stocker = DataStocker()
    lidar_service = LidarService(position_service,data_stocker)
    
    dataThread = data_stocker
    dataThread.start()
    
    lidarThread = lidar_service
    lidarThread.start()
    
    detecionThread = DetectionService(data_stocker)
    detecionThread.start()
    
    dataThread.join()
    lidarThread.join()
    detectionThread.join()
    
    
