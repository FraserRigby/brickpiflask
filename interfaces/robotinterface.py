import time
import math
import sys
import logging
import threading
import grovepi

'''need to take out unecessary stuff --> the original code was for brickpi'''
'''need to import sensor and actuator drivers'''

#this needs to go inside the class at somepoint, im trying to avoid confusing students
NOREADING = 999 #just using 999 to represent no reading
ENABLED = 1
DISABLED = 5 #if the sensor returns NOREADING more than 5 times in a row, its permanently disabled

#Created a Class to wrap the robot functionality, one of the features is the idea of keeping track of the CurrentCommand, this is important when more than one process is running...
class RobotInterface():

    ###----------ROBOT SETUP----------###
    #Initialise log and timelimit
    def __init__(self, timelimit=20):
        self.logger = logging.getLogger()
        self.CurrentCommand = "loading"
        self.Configured = False #is the robot yet Configured?
        self.timelimit = timelimit #failsafe timelimit - motors turn off after
        self.set_ports_sensors()
        self.set_ports_actuators()
        self.Calibrated = False
        self.CurrentCommand = "loaded" #when the device is ready for a new instruction it will be set to stop
        return

    #Initialise Sensor Ports
    def set_ports_sensors(self):
        self.thermal = bp.PORT_1 #Thermal infrared Sensor
        self.ultra = bp.PORT_4 #ultraSonic Sensor
        self.thermal_thread = None #DO NOT REMOVE THIS - USED LATER
        self.configure_sensors()
        return

    #Initialise Actuator Ports
    def set_ports_actuators(self):
        return

    #Configure Sensors
    def configure_sensors(self):
        bp = self.BP
        self.config = {} #create a dictionary that represents if the sensor is Configured
        #set up ultrasonic sensor
        try:
            bp.set_sensor_type(self.ultra, bp.SENSOR_TYPE.EV3_ULTRASONIC_CM)
            time.sleep(1.5)
            self.config['ultra'] = ENABLED
        except Exception as error:
            self.log("Ultrasonic Sensor not found")
            self.config['ultra'] = DISABLED
        #set up ultrasonic sensor
        try:
            bp.set_sensor_type(self.thermal, bp.SENSOR_TYPE.I2C, [0, 20])
            time.sleep(1)
            self.config['thermal'] = ENABLED
            self.__start_thermal_infrared_thread()
        except Exception as error:
            self.log("Thermal Sensor not found")
            self.config['thermal'] = DISABLED

        self.Configured = True #there is a 4 second delay - before robot is Configured
        return

    #Start Infrared I2c Thread
    def __start_thermal_infrared_thread(self):
        self.thermal_thread = threading.Thread(target=self.__update_thermal_sensor_thread, args=(1,))
        self.thermal_thread.daemon = True
        self.thermal_thread.start()
        return

    #changes the logger
    def set_log(self, logger):
        self.logger=logger
        return


    ###----------MISCELLANEOUS----------###
    #log message !!!!!THIS IS NOT WORKING UNLESS FLASK LOG USED, DONT KNOW WHY!!!!!
    def log(self, message):
        self.logger.info(message)
        return

    #stop all actuators
    def stop_all(self):
        bp = self.BP
        bp.set_motor_power(self.largemotors+self.mediummotor, 0)
        self.CurrentCommand = "stop"
        return

    #returns the current command
    def get_current_command(self):
        return self.CurrentCommand

    # safely exit applicaiton, safes actuators/sensors
    def safe_exit(self):
        bp = self.BP
        self.CurrentCommand = 'exit' #should exit thread
        self.stop_all() #stop all motors
        self.log("Exiting")
        bp.reset_all() # Unconfigure the sensors, disable the motors
        time.sleep(2) #gives time to reset??
        return
    

    ###----------SENSOR COMMAND----------###
    #get the current voltage - need to work out how to determine battery life
    def get_battery(self):
        return self.BP.get_voltage_battery()

    #get the ultrasonic sensor
    def get_ultra_sensor(self):
        distance = NOREADING
        if self.config['ultra'] >= DISABLED or not self.Configured:
            return distance
        bp = self.BP
        ifMutexAcquire(USEMUTEX)
        try:
            distance = bp.get_sensor(self.ultra)
            time.sleep(0.1)
            self.config['ultra'] = ENABLED
        except brickpi3.SensorError as error:
            self.log("ULTRASONIC: " + str(error))
            self.config['ultra'] += 1
        finally:
            ifMutexRelease(USEMUTEX) 
        return distance

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

    #returns a dictionary of all current sensors
    def get_all_sensors(self):
        sensordict = {} #create a dictionary for the sensors
        sensordict['battery'] = self.get_battery()
        sensordict['colour'] = self.get_colour_sensor()
        sensordict['ultrasonic'] = self.get_ultra_sensor()
        sensordict['thermal'] = self.get_thermal_sensor()
        sensordict['acceleration'] = self.get_linear_acceleration_IMU()
        sensordict['compass'] = self.get_compass_IMU()
        sensordict['gyro'] = self.get_gyro_sensor_IMU()
        sensordict['temperature'] = self.get_temperature_IMU()
        sensordict['orientation'] = self.get_orientation_IMU()
        return sensordict


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
    
#--------------------------------------------------------------------
# Only execute if this is the main file, good for testing code
if __name__ == '__main__':
    robot = BrickPiInterface(timelimit=20)
    logger = logging.getLogger()
    logger.setLevel(logging.info)
    robot.set_log(logger)
    robot.calibrate_imu(timelimit=10) #calibration might requirement movement
    input("Press any key to test: ")
    robot.safe_exit()

