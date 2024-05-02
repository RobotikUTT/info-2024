import pigpio
import time

baudrate =9600

txPin=24
rxPin=21

serialpi=pigpio.pi()
serialpi.set_mode(rxPin,pigpio.INPUT)
serialpi.set_mode(txPin,pigpio.OUTPUT)

pigpio.exceptions = False
serialpi.bb_serial_read_close(rxPin)
pigpio.exceptions = True

serialpi.bb_serial_read_open(rxPin,baudrate,8)

def Sendline(serialpi):
    serialpi.wave_clear()
    serialpi.wave_add_serial(txPin,baudrate,b'Hello world\r\n')
    wid=serialpi.wave_create()
    serialpi.wave_send_once(wid)
    while serialpi.wave_tx_busy():
        pass
    serialpi.wave_delete(wid)   


Sendline(serialpi) 
print 'sent'
time.sleep(.5)