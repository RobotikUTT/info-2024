from position import PositionService
from detection import DataStocker, LidarService
import pygame
from math import cos, sin

if __name__ == "__main__":
    data_stocker = DataStocker()
    lidar = LidarService(PositionService(), data_stocker)

    data_stocker.start()

    lidar.start()

    pygame.init()
    screen = pygame.display.set_mode((500, 500))
    clock = pygame.time.Clock()
    while True:
        values = data_stocker.get_values()
        screen.fill(0);
        for value in values:
            pygame.draw.line(screen, 0xffffff, (250, 250), (250 + cos(value.absolute_angle) * value.distance/10, 250 + sin(value.absolute_angle) * value.distance/10))
        pygame.display.flip()
        clock.tick()
        print(clock.get_fps())
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit(0)

    lidar.join()
    data_stocker.join()
