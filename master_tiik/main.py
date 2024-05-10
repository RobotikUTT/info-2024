import detection as eyes
import game_manager as game
import communication as com
import position
from serial_communication import SerialService
from i2c_communication import I2CCommunication

if __name__ == "__main__":
    position_service = position.PositionService()
    serial_communication = SerialService()
    i2c_communication = I2CCommunication()
    com_service = com.CommunicationService(serial_communication, i2c_communication)
    data_stocker = eyes.DataStocker()
    lidar_service = eyes.LidarService(position_service, data_stocker, com_service)
    detection_service = eyes.DetectionService(data_stocker, com_service)
    game_manager = game.GameManager(com_service,position_service, detection_service)
        
    serial_communication.start()
    
    gameThread = game_manager
    gameThread.start()

    dataThread = data_stocker
    dataThread.start()

    lidarThread = lidar_service
    lidarThread.start()

    detectionThread = detection_service
    detectionThread.start()

    serial_communication.join()
    gameThread.join()
    dataThread.join()
    lidarThread.join()
    detectionThread.join()
