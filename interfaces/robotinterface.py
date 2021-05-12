import os
import time
import math
import sys
import logging
import threading
from grove.grove_ultrasonic_ranger import GroveUltrasonicRanger #grove ultrasonic sensor library
from smbus2 import SMBus #smbus library for thermal sensor I2C communication
from mlx90614 import MLX90614 #mlx90614 library for thermal sensor
from adafruit_servokit import ServoKit #library for actuator output via PCA9685 bonnet
'''need to take out unecessary stuff --> the original code was for brickpi'''
'''need to import sensor and actuator drivers'''

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
        self.sensor_thermal_address = 0x5a #Thermal infrared sensor I2C address
        self.sensor_distance_front_address = 5 #Front ultraSonic sensor port address
        self.sensor_distance_turret_address = 16 #Turret ultrasonic sensor port address
        self.configure_sensors()
        return

    #Configure Sensors
    def configure_sensors(self):
        #if time use this to verify sensor connection
        #set up thermal sensor
        self.bus = SMBus(1)
        self.sensor_thermal = MLX90614(self.bus, self.sensor_thermal_address)
        self.config['sensor_thermal'] = "ENABLED"
        #set up ultrasonic sensor - front
        self.sensor_distance_front = GroveUltrasonicRanger(self.sensor_distance_front_address)
        self.config['sensor_distance_front'] = "ENABLED"
        #set up ultrasonic sensor - turret
        self.sensor_distance_turret = GroveUltrasonicRanger(self.sensor_distance_turret_address)
        self.config['sensor_distance_turret'] = "ENABLED"
        self.Configured_sensors = True
        return

    #Initialise Actuator Ports
    def set_ports_actuators(self):
        self.configure_actuators()
        return

    #Configure Actuators
    def configure_actuators(self):
        #if time use this to verify actuator connection
        self.Configured_actuators = True
        return

    #changes the logger
    def set_log(self, logger):
        self.logger=logger
        return


    ###----------MISCELLANEOUS----------###
    #Log message !!!!!THIS IS NOT WORKING UNLESS FLASK LOG USED, DONT KNOW WHY!!!!!
    def log(self, message):
        self.logger.info(message)
        return

    #Stop all actuators
    def stop_all(self):
        self.CurrentCommand = "stop"
        return

    #Return current command
    def get_current_command(self):
        return self.CurrentCommand

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
        self.CurrentCommand = "Get IR temp."
        if self.config["sensor_thermal"] == "ENABLED":
            temp = self.sensor_thermal.get_obj_temp()
            temp = int("{:.2f}".format(temp))
            return temp
        else:
            temp = "error"
        return temp

    #Get ultrasonic sensor distance reading, depending on input gets specific ultra sensor
    def get_sensor_ultra(self, distance_type):
        self.CurrentCommand = "Get ultra sensor " + distance_type + "."
        distance = None
        if distance_type == "front":
            if self.config["sensor_distance_front"] == "ENABLED":
                distance = self.sensor_distance_front.get_distance()
                distance = int("{:.2f}".format(distance))
                return distance
            else:
                distance = "error"
        elif distance_type == "turret":
            if self.config["sensor_distance_turret"] == "ENABLED":
                distance = self.sensor_distance_turret.get_distance()
                distance = int("{:.2f}".format(distance))
                return distance
            else:
                distance = "error"
        return distance
    
    #Get the current voltage - need to work out how to determine battery life
    def get_sensor_battery_volts(self):
        self.currentCommand = "Get battery voltage."
        volts = "-"
        return volts

    #Get Raspi temperature sensor reading
    def get_sensor_raspi_temp(self):
        self.currentCommand = "Get Raspi temperature."
        temp = os.popen('vcgencmd measure_temp').readline()
        temp = temp.replace("temp=","").replace("'C\n","")
        temp = int(temp)
        temp = int("{:.2f}".format(temp))
        return temp

    #Get and return dictionary of all sensors
    def get_sensor_all(self):
        sensordict = {} #create a dictionary for the sensors
        sensordict['thermal'] = self.get_sensor_thermal()
        #sensordict['distance_front'] = self.get_sensor_ultra("front")
        sensordict['distance_turret'] = self.get_sensor_ultra("turret")
        sensordict['battery'] = self.get_sensor_battery_volts()
        sensordict['raspi_temp'] = self.get_sensor_raspi_temp()
        return sensordict

    '''
    #updates the thermal sensor by making continual I2C transactions through a thread
    def __update_thermal_sensor_thread(self, name):
        while self.CurrentCommand != "exit":
            self.update_thermal_sensor()
        return

    #updates the thermal sensor by making a single I2C transaction
    def update_thermal_sensor(self):
        if self.config['thermal'] >= DISABLED:
            self.CurrentCommand = 'exit' #end thread
            return
        bp = self.BP
        TIR_I2C_ADDR        = 0x0E      # TIR I2C device address 
        TIR_AMBIENT         = 0x00      # Ambient Temp
        TIR_OBJECT          = 0x01      # Object Temp
        TIR_SET_EMISSIVITY  = 0x02      
        TIR_GET_EMISSIVITY  = 0x03
        TIR_CHK_EMISSIVITY  = 0x04
        TIR_RESET           = 0x05
        try:
            bp.transact_i2c(self.thermal, TIR_I2C_ADDR, [TIR_OBJECT], 2)
            time.sleep(0.01)
        except Exception as error:
            self.log("THERMAL UPDATE: " + str(error))
        finally:
            pass
        return

    #return the infrared temperature - if usethread=True - it uses the thread set up in init
    def get_thermal_sensor(self, usethread=True):
        temp = NOREADING
        if self.config['thermal'] >= DISABLED or not self.Configured:
            return temp
        bp = self.BP
        if not usethread:
            self.update_thermal_sensor() #not necessary if thread is running
        ifMutexAcquire(USEMUTEX)
        try:
            value = bp.get_sensor(self.thermal) # read the sensor values
            time.sleep(0.01)
            self.config['thermal'] = ENABLED
            temp = (float)((value[1] << 8) + value[0]) # join the MSB and LSB part
            temp = temp * 0.02 - 0.01                  # Converting to Celcius
            temp = temp - 273.15                       
        except Exception as error:
            self.log("THERMAL READ: " + str(error))
            self.config['thermal'] += 1
        finally:
            ifMutexRelease(USEMUTEX)    
        return float("%3.f" % temp)

    #disable thermal sensor - might be needed to reenable motors (they disable for some reason when thermal sensor is active)
    def disable_thermal_sensor(self):
        bp = self.BP
        bp.set_sensor_type(self.thermal, bp.SENSOR_TYPE.NONE) 
        return


    ###----------MOTOR COMMANDS----------###
    #simply turns motors on
    def move_power(self, power, deviation=0):
        bp = self.BP
        self.CurrentCommand = "move_power"
        bp.set_motor_power(self.rightmotor, power)
        bp.set_motor_power(self.leftmotor, power + deviation)
        return

    #moves for the specified time (seconds) and power - use negative power to reverse
    def move_power_time(self, power, t, deviation=0):
        bp = self.BP
        self.CurrentCommand = "move_power_time"
        timelimit = time.time() + t
        bp.set_motor_power(self.rightmotor, power)
        bp.set_motor_power(self.leftmotor, power + deviation)
        while time.time() < timelimit and self.CurrentCommand != "stop":
            continue
        self.CurrentCommand = "stop"
        self.BP.set_motor_power(self.largemotors, 0)
        return
    

    #UPDATED THIS FUNCTION SINCE INTERFACE TEMPLATE WAS GIVEN
    #moves forward until a colour or an object is detected- return collisiontype
    def move_power_untildistanceto(self, power, distanceto, deviation=0):
        if self.config['ultra'] >= DISABLED or not self.Configured:
            return 0
        self.CurrentCommand = "move_power_untildistanceto"
        bp = self.BP
        distancedetected = 300 # to set an initial distance detected before loop
        elapsedtime = 0; starttime = time.time(); timelimit = starttime + self.timelimit  #all timelimits are a backup plan
        collisiontype = None
        #Turn motors on
        bp.set_motor_power(self.rightmotor, power)
        bp.set_motor_power(self.leftmotor, power + deviation)
        while (self.CurrentCommand != "stop" and time.time() < timelimit):

            ##if sensor fails, or distanceto has been reached quit, or distancedetected = 0
            distancedetected = self.get_ultra_sensor()
            self.log("MOVING - Distance detected: " + str(distancedetected))
            if ((self.config['ultra'] > DISABLED) or (distancedetected < distanceto and distancedetected != 0.0)): 
                collisiontype = "objectdetected"
                break 

            ##insert other tests e.g if red colour
            colour = self.get_colour_sensor()
            if colour == "Red":
                collisiontype = "junctiondetected"
                break
            elif colour == "Green":
                collisiontype = "searchareadetected"
                break
            
        self.CurrentCommand = "stop"
        elapsedtime = time.time() - starttime
        bp.set_motor_power(self.largemotors, 0)
        return {"collisiontype":collisiontype,"elapsedtime":elapsedtime}  

    #Rotate power and time, -power to reverse
    def rotate_power_time(self, power, t):
        self.CurrentCommand = "rotate_power_time"
        bp = self.BP
        target = time.time() + t
        while time.time() < target and self.CurrentCommand != 'stop':
            bp.set_motor_power(self.rightmotor, -power)
            bp.set_motor_power(self.leftmotor, power)
        bp.set_motor_power(self.largemotors, 0) #stop
        self.CurrentCommand = 'stop'
        return
    '''
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

