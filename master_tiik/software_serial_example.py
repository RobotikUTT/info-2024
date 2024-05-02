import serial
ser = serial.Serial('/dev/ttyACM0',115200,timeout=0)

while True :
    bytesToRead = ser.inWaiting()
    val = ser.read(bytesToRead)
    if (val != b''):
        print(val)
        ser.write(0x01)
    
