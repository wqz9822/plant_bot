import serial
import time

class mySensors(object):
    def __init__(self):
        self.ser = serial.Serial('/dev/ttyACM0', 9600)
        self.ser.close()
        self.temperature = 0
        self.humidity = 0
        self.soilMoisture = 0
        
    def getSensorValues(self):
        self.ser.open()
        cmds = self.ser.readline().decode('utf-8')
        cmds = cmds.strip().split(",\t");
        if( cmds[0] == 'DHT11'):
            self.humidity = float(cmds[2])
            self.temperature = float(cmds[3])
            self.soilMoisture = int(cmds[4])
        # print(cmds)
        self.ser.close()
        return self.temperature, self.humidity, self.soilMoisture