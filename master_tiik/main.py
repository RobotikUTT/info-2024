import detection as eyes
import game_manager as game
import communication as com
import position

if __name__ == "__main__":
    com_service = com.CommunicationService()
    position_service = position.PositionService()
    data_stocker = eyes.DataStocker()
    lidar_service = eyes.LidarService(position_service, data_stocker)
    detection_service = eyes.DetectionService(data_stocker)
    game_manager = game.GameManager(com_service,position_service)
    
    positionThread = position_service
    positionThread.start()
    
    comThread = com_service
    comThread.start()
    
    gameThread = game_manager
    gameThread.start()

    dataThread = data_stocker
    dataThread.start()

    lidarThread = lidar_service
    lidarThread.start()

    detectionThread = detection_service
    detectionThread.start()

    positionThread.join()
    i2cThread.join()
    gameThread.join()
    dataThread.join()
    lidarThread.join()
    detectionThread.join()
