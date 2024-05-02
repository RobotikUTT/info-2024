from math import pi
from threading import Thread
from typing import List, Tuple

from communication import CommunicationService
from detection import LidarService, DataStocker, PointData
from position import PositionService
from utils import fit_circle_to_points, Point
from statistics import mean

PILLARS = Point(0, 0), Point(10, 10), Point(100, 100)
PILLAR_RADIUS = 10


class TriangulationService(Thread):

    def __init__(self, position_service: PositionService, data_stocker: DataStocker, communication_service: CommunicationService):
        super().__init__()
        self.position_service = position_service
        self.data_stocker = data_stocker
        self.communication_service = communication_service

    def run(self):
        while True:
            values = self.data_stocker.get_values()
            objects: List[Tuple[int, float, List[PointData]]] = [(0, 2*pi, [])]
            for value in values:
                is_object = abs(value.x) < 10 and abs(value.y) < 10 and abs(2000 - value.x) < 10 and abs(3000 - value.y) < 10
                new_objects: List[Tuple[int, float, List[PointData]]] = []
                for obj in objects:
                    if not (obj[0] < value.distance < obj[1]):
                        continue
                    if not is_object:
                        obj = (obj[0], value.angle, [measure for measure in obj[2] if measure.angle < value.angle])
                        new_objects.append((value.angle, obj[1], [measure for measure in obj[2] if measure.angle > value.angle]))
                    else:
                        obj[2].append(value)
                objects.extend(new_objects)
            objects = [obj for obj in objects if len(obj[2]) > 0]
            positions_computed = []
            for obj in objects:
                circle = fit_circle_to_points(obj[2])
                for pillar in PILLARS:
                    circle_center = Point(circle.x, circle.y)
                    if abs(circle_center - pillar) > 10:
                        continue
                    self_position = Point(*self.position_service.get_position())
                    self_angle = self.position_service.get_angle()
                    reconstructed_ray = PointData.invert(circle_center, self_position, self_angle)
                    inverted_ray = PointData(reconstructed_ray.angle + pi, reconstructed_ray.distance - PILLAR_RADIUS, (pillar.x, pillar.y), self_angle)
                    positions_computed.append(Point(inverted_ray.x, inverted_ray.y))
