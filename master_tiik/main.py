import detection as eyes
import find_best_strategy as strat

if __name__ == "__main__":
    position_service = eyes.PositionService()
    data_stocker = eyes.DataStocker()
    lidar_service = eyes.LidarService(position_service, data_stocker)

    dataThread = data_stocker
    dataThread.start()

    lidarThread = lidar_service
    lidarThread.start()

    detectionThread = eyes.DetectionService(data_stocker)
    detectionThread.start()

    dataThread.join()
    lidarThread.join()
    detectionThread.join()