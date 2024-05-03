import random
from math import pi, sin, cos
from threading import Thread
from typing import List, Tuple

from detection import LidarService, DataStocker, PointData
from position import PositionService
from utils import fit_circle_to_points, Point, Line, mean

PILLARS = Point(0, 0), Point(0, 3000), Point(2000, 0)
PILLAR_RADIUS = 10


class TriangulationService(Thread):

    def __init__(self, position_service: PositionService, data_stocker: DataStocker):
        super().__init__()
        self.position_service = position_service
        self.data_stocker = data_stocker
        self.corrected_position = position_service.x, position_service.y

    def run(self):
        i = 0
        while i == 0:
            i = 1
            values = self.data_stocker.get_values()
            objects: List[Tuple[int, float, List[PointData]]] = [(0, 2*pi, [])]
            for value in values:
                is_object = (value.x > -10 and value.y > -10 and value.x < 2010 and value.y < 3010 and
                             not (value.x > 10 and value.y > 10 and value.x < 1990 and value.y < 2990))
                new_objects: List[Tuple[int, float, List[PointData]]] = objects[:]
                for i, obj in enumerate(objects):
                    if not (obj[0] < value.angle < obj[1]):
                        continue
                    if not is_object:
                        new_objects[i] = (obj[0], value.angle, [measure for measure in obj[2] if measure.angle < value.angle])
                        new_objects.append((value.angle, obj[1], [measure for measure in obj[2] if measure.angle > value.angle]))
                    else:
                        obj[2].append(value)
                objects = new_objects
            objects = [obj for obj in objects if len(obj[2]) > 0]
            positions_computed = []
            for obj in objects:
                circle = fit_circle_to_points([(point.x, point.y) for point in obj[2]])
                circle_center = Point(circle.x, circle.y)
                for pillar in PILLARS:
                    if abs(circle_center - pillar) > 100:
                        continue
                    self_position = Point(*self.position_service.get_position())
                    self_angle = self.position_service.get_angle()
                    reconstructed_ray = PointData.invert(circle_center, self_position, self_angle)
                    inverted_ray = PointData(reconstructed_ray.angle + pi, reconstructed_ray.distance - PILLAR_RADIUS, (pillar.x, pillar.y), self_angle)
                    positions_computed.append(Point(inverted_ray.x, inverted_ray.y))
            if len(positions_computed) == 0:
                self.corrected_position = (None, None)
            else:
                self.corrected_position = (mean([pos.x for pos in positions_computed]), mean([pos.y for pos in positions_computed]))


if __name__ == '__main__':
    import pygame
    position = PositionService()
    position.x = 100
    position.y = 100
    screen = pygame.display.set_mode((600, 850))
    class DataStockerOverride(DataStocker):
        def update(self):
            self.values = []
            for i in range(100):
                angle = random.random() * pi * 2
                line = Line.from_points(position.x, position.y, position.x + cos(angle), position.y + sin(angle))
                for pillar in PILLARS:
                    d = line.distance_to_point(pillar.x, pillar.y)
                    if d < 10:
                        # measure = PointData.invert(pillar + Point(int(random.random()), int(random.random())),
                        #                             Point(position.x, position.y),
                        #                             position.angle)
                        measure = PointData.invert(pillar + Point(int(random.random() * 100 - 50), int(random.random() * 100 - 50)),
                                                  Point(position.x, position.y),
                                                  position.angle)
                    else:
                        measure = PointData(angle, 99999, (position.x, position.y), position.angle, 0)
                    self.values.append(measure)
    data_stocker = DataStockerOverride()
    triangulation = TriangulationService(position, data_stocker)
    data_stocker.update()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    position.y -= 10
                    data_stocker.update()
                if event.key == pygame.K_DOWN:
                    position.y += 10
                    data_stocker.update()
                if event.key == pygame.K_LEFT:
                    position.x -= 10
                    data_stocker.update()
                if event.key == pygame.K_RIGHT:
                    position.x += 10
                    data_stocker.update()
        screen.fill((0, 0, 0))
        pygame.draw.rect(screen, (255, 255, 255), (50, 50, 500, 750))
        pygame.draw.circle(screen, (255, 0, 0), (int(position.x / 4 + 50), int(position.y / 4 + 50)), 10)
        for pillar in PILLARS:
            pygame.draw.circle(screen, (0, 255, 0), (int(pillar.x / 4 + 50), int(pillar.y / 4 + 50)), 10)
        measures = data_stocker.get_values()
        for measure in measures:
            pygame.draw.line(screen,
                             (0, 0, 255),
                             (int(measure.robot_position[0] / 4 + 50), int(measure.robot_position[1] / 4 + 50)),
                             (int(measure.x / 4 + 50), int(measure.y / 4 + 50)))
        pygame.display.flip()
        triangulation.run()
        #break
        print("Real position", position.x, position.y)
        print("Triangulated position", triangulation.corrected_position)
