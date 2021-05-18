###----------IMPORTING/DEFINING----------###
import os
import time
import math
import sys
import logging
import threading
import RPi.GPIO as GPIO
from grove.grove_ultrasonic_ranger import GroveUltrasonicRanger #grove ultrasonic sensor library
from smbus2 import SMBus #smbus library for thermal sensor I2C communication
from mlx90614 import MLX90614 #mlx90614 library for thermal sensor
#from adafruit_servokit import ServoKit #library for actuator output via PCA9685 bonnet
from interfaces.adafruit_servokit_adapted import ServoKit #library for actuator output via PCA9685 bonnet

'''
Libraries:
grove.py Seeed-Studio MIT License--> https://github.com/Seeed-Studio/grove.py
PyMLX90614 Connor Kneebone MIT License--> https://github.com/sightsdev/PyMLX90614
Adafruit_CircuitPython_ServoKit Adafruit MIT License--> https://github.com/adafruit/Adafruit_CircuitPython_ServoKit
'''

#Created a Class to wrap the robot functionality, one of the features is the idea of keeping track of the CurrentCommand, this is important when more than one process is running...
class RobotInterface():

###----------ROBOT SETUP----------###
    #Initialise Robot
    def __init__(self):
        self.logger = logging.getLogger()
        self.CurrentCommand = "loading"
        self.Configured_sensors = False
        self.Configured_actuators = False
        self.config = {} #create a dictionary that represents if the component is configured
        self.set_ports_sensors()
        self.set_ports_actuators()
        self.CurrentCommand = "loaded" #when the device is ready for a new instruction it will be set to stop
        return

    #Initialise Sensor Ports
    def set_ports_sensors(self):
        self.CurrentCommand = "initialise sensors"
        self.sensor_thermal_address = 0x5a #Thermal infrared sensor I2C address
        self.sensor_distance_front_address = 5 #Front ultraSonic sensor port address
        self.sensor_distance_turret_address = 16 #Turret ultrasonic sensor port address
        self.configure_sensors()
        return

    #Configure Sensors
    def configure_sensors(self):
        self.CurrentCommand = "configure sensors"
        #Set up thermal sensor
        self.bus = SMBus(1)
        self.sensor_thermal = MLX90614(self.bus, self.sensor_thermal_address)
        self.config['sensor_thermal'] = "ENABLED"
        #Set up ultrasonic sensor - front
        self.sensor_distance_front = GroveUltrasonicRanger(self.sensor_distance_front_address)
        self.config['sensor_distance_front'] = "ENABLED"
        #Set up ultrasonic sensor - turret
        self.sensor_distance_turret = GroveUltrasonicRanger(self.sensor_distance_turret_address)
        self.config['sensor_distance_turret'] = "ENABLED"
        self.Configured_sensors = True
        return

    #Initialise Actuator Ports
    def set_ports_actuators(self):
        self.CurrentCommand = "initialise actuators"
        self.actuator = ServoKit(channels=16) #initialise actuators
        self.actuator_servo_traverse = 0 #traverse servo
        self.actuator_servo_turret = 1 # turret servo
        self.actuator_servo_nozzle = 2 #nozzle servo
        self.actuator_pump_water = 3 #water pump
        #self.actuator_pump_water = 16 #water pump backup gpio address
        self.configure_actuators()
        return

    #Configure Actuators
    def configure_actuators(self):
        self.CurrentCommand = "configure actuators"
        self.servo = self.actuator.servo
        #self.servo_continuous = self.actuator.continuous_servo
        self.actuator_shutdown_reset_list = [self.actuator_servo_turret, self.actuator_servo_nozzle]
        #Set up traverse servo
        self.config['servo_traverse'] = "ENABLED"
        #Set up turret servo
        self.config['servo_turret'] = "ENABLED"
        #Set up nozzle servo
        self.config['servo_nozzle'] = "ENABLED"
        #set up water pump
        #GPIO.setup(self.actuator_pump_water, GPIO.OUT)
        self.config['pump_water'] = "ENABLED"
        self.Configured_actuators = True
        return

    #changes the logger
    def set_log(self, logger):
        self.CurrentCommand = "initialise logger"
        self.logger=logger
        return


###----------MISCELLANEOUS----------###
    #Log message !!!!!THIS IS NOT WORKING UNLESS FLASK LOG USED, DONT KNOW WHY!!!!!
    def log(self, message):
        self.CurrentCommand = "activate logger"
        self.logger.info(message)
        return

    #Return current command
    def get_current_command(self):
        return self.CurrentCommand

    #Stop all actuators
    def stop_all(self):
        self.CurrentCommand = "stop all"
        self.servo.throttle = 0
        msg = "stopping"
        return msg

    #Return select actuators to default position on shutdown
    def actuator_shutdown_reset(self):
        self.CurrentCommand = "actuator shutdown reset"
        '''
        for actuator in self.actuator_shutdown_reset_list:
            self.actuator.servo[actuator].angle = 0
        '''
        return

    #Safely exit applicaiton, safes actuators/sensors
    def safe_exit(self):
        self.CurrentCommand = 'exit' #should exit thread
        self.stop_all() #stop all actuators
        self.log("Exiting")
        time.sleep(2) #gives time to reset??
        return
    

###----------SENSOR COMMANDS----------##
    #Get thermal IR sensor reading
    def get_sensor_thermal(self):
        self.CurrentCommand = "get ir temp"
        if self.config["sensor_thermal"] == "ENABLED":
            temp = self.sensor_thermal.get_obj_temp()
            temp = float("{:.2f}".format(temp))
            return temp
        else:
            temp = "error"
        return temp

    #Get ultrasonic sensor distance reading, depending on input gets specific ultra sensor
    def get_sensor_ultra(self, distance_type):
        self.CurrentCommand = "get ultra sensor " + distance_type
        distance = None
        if distance_type == "front":
            if self.config["sensor_distance_front"] == "ENABLED":
                distance = self.sensor_distance_front.get_distance()
                distance = float("{:.2f}".format(distance))
                return distance
            else:
                distance = "error"
        elif distance_type == "turret":
            if self.config["sensor_distance_turret"] == "ENABLED":
                distance = self.sensor_distance_turret.get_distance()
                distance = float("{:.2f}".format(distance))
                return distance
            else:
                distance = "error"
        return distance
    
    #Get the current voltage - need to work out how to determine battery life
    def get_sensor_battery_volts(self):
        self.CurrentCommand = "get battery voltage"
        volts = "-"
        return volts

    #Get Raspi temperature sensor reading
    def get_sensor_raspi_temp(self):
        self.CurrentCommand = "get Raspi temperature"
        temp = os.popen('vcgencmd measure_temp').readline()
        temp = temp.replace("temp=","").replace("'C\n","")
        temp = float(temp)
        temp = float("{:.2f}".format(temp))
        return temp

    #Get and return dictionary of all sensors
    def get_sensor_all(self):
        self.CurrentCommand = "get all sensor data"
        sensordict = {} #create a dictionary for the sensors
        sensordict['thermal'] = self.get_sensor_thermal()
        sensordict['distance_front'] = self.get_sensor_ultra("front")
        sensordict['distance_turret'] = self.get_sensor_ultra("turret")
        sensordict['battery'] = self.get_sensor_battery_volts()
        sensordict['raspi_temp'] = self.get_sensor_raspi_temp()
        return sensordict


###----------ACTUATOR COMMANDS----------###
    #Get traverse servo data
    def get_actuator_servo_traverse(self):
        data = "-"
        return data

    #Get turret servo data
    def get_actuator_servo_turret(self):
        data = "-"
        '''data = self.servo[self.actuator_servo_turret].angle
        data = float(angle%360)
        data = float("{:.2f}".format(data))'''
        return data

    #Get nozzle servo data
    def get_actuator_servo_nozzle(self):
        data = "-"
        '''data = self.servo[self.actuator_servo_nozzle].angle
        data = float(angle%360)
        data = float("{:.2f}".format(data))'''
        return data

    #Get all actuator data
    def get_actuator_all(self):
        self.CurrentCommand = "get all actuator data"
        actuatordict = {}
        actuatordict['servo_traverse'] = self.get_actuator_servo_traverse()
        actuatordict['servo_turret'] = self.get_actuator_servo_turret()
        actuatordict['servo_nozzle'] = self.get_actuator_servo_nozzle()
        return actuatordict

    #Stop actuator
    def stop_actuator(self, actuator):
        self.CurrentCommand = "stop " + actuator
        port = eval("self.actuator_" + actuator)
        '''if actuator == "pump_water":
            GPIO.output(port, GPIO.LOW)
        else:
            self.servo[port].throttle = 0'''
        self.servo[port].throttle = 0
        msg = actuator + " stopping"
        return msg

    #Traverse servo
    def servo_traverse(self, action, sensitivity):
        port = self.actuator_servo_traverse
        if action == "+":
            self.CurrentCommand = "traverse forward"
            self.servo[port].throttle = sensitivity
            msg = "servo_traverse forward"
        elif action == "-":
            self.CurrentCommand = "traverse backward"
            self.servo[port].throttle = -1*sensitivity
            msg = "servo_traverse backward"
        return msg

    #Turret servo
    def servo_turret(self, action, sensitivity):
        port = self.actuator_servo_turret
        if action == "+":
            self.CurrentCommand = "rotate turret right"
            self.servo[port].throttle = -1*sensitivity
            msg = "servo_turret rotate right"
        elif action == "-":
            self.CurrentCommand = "rotate turret left"
            self.servo[port].throttle = sensitivity
            msg = "servo_turret rotate left"
        return msg

    #Nozzle servo
    def servo_nozzle(self, action, sensitivity):
        port = self.actuator_servo_nozzle
        if action == "+":
            self.CurrentCommand = "rotate nozzle up"
            self.servo[port].throttle = sensitivity
            msg = "servo_nozzle rotate up"
        elif action == "-":
            self.CurrentCommand = "rotate nozzle down"
            self.servo[port].throttle = -1*sensitivity
            msg = "servo_nozzle rotate down"
        return msg

    #Water pump
    def pump_water(self, action, waterpressure):
        port = self.actuator_pump_water
        if action == "fire":
            self.CurrentCommand = "fire water"
            self.servo[port].throttle = waterpressure
            #GPIO.output(port, GPIO.HIGH)
            msg = "pump_water firing"
        return msg

#--------------------------------------------------------------------
# Only execute if this is the main file, good for testing code
if __name__ == '__main__':
    robot = RobotInterface()
    logger = logging.getLogger()
    robot.set_log(logger)
    input("Press any key to test: ")
    test = robot.get_sensor_all()
    print(test)
    robot.safe_exit()

