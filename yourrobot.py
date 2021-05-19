###----------IMPORTING/DEFINING----------###
# This class inherits from the robot interface, it should include any code for sub-routines
from interfaces.robotinterface import RobotInterface
import logging
import time

#This class is encapsualtes routines which execute the elementary functions established in the RobotInterface object
class Robot(RobotInterface):

###----------YOURROBOT SETUP----------###    
    def __init__(self):
        super().__init__()
        self.CurrentRoutine = 'ready' #could be useful to keep track of the current routine
        return

    #gets the current routine
    def get_current_routine(self):
        return self.CurrentRoutine


###----------SEMI AUTO----------###
#Look left
    def servo_turret_face_left(self):
        self.CurrentRoutine = "servo_turret_face_left"
        robot.servo[robot.actuator_servo_turret].angle = 0
        msg = "servo_turret rotate face left (-90deg)"
        return msg
    
#Look right
    def servo_turret_face_right(self):
        self.CurrentRoutine = "servo_turret_face_right"
        robot.servo[robot.actuator_servo_turret].angle = 180
        msg = "servo_turret rotate face right (+90deg)"
        return msg

#Search front
    def search_front(self, type, sensitivity):
        self.CurrentRoutine = "search_front"
        detection = False
        msg = ""
        tir_limit = 100
        if type == "auto": #auto front search
            self.servo_turret_face_left()
            angle = robot.servo[robot.actuator_servo_turret].angle
            angle_limit = 180
            while angle < angle_limit and detection == False:
                robot.servo_turret("+", sensitivity)
                tir = robot.get_sensor_thermal()
                if tir >= tir_limit:
                    detection = True
                    robot.stop_actuator("servo_turret")
                    msg = "semi auto search front auto fire detected"
                    print(msg)
                else:
                    current_cmd = robot.get_current_command()
                    if "stop" in current_cmd:
                        break
                    angle = robot.servo[robot.actuator_servo_turret].angle
        elif type == "semi": #semi auto front search
            while detection == False:
                tir = robot.get_sensor_thermal()
                if tir >= tir_limit:
                    detection = True
                    robot.stop_actuator("servo_turret")
                    msg = "semi auto search front semi fire detected"
                    print(msg)
                else:
                    current_cmd = robot.get_current_command()
                    if "stop" in current_cmd:
                        break
        if msg == "":
            msg = "semi auto search front"
        return msg

#Search forward
    def search_forward(self, sensitivity):
        self.CurrentRoutine = "search_forward"
        msg = ""
        detection = False
        collision = False
        distance_front_limit = 10
        tir_limit = 100
        while detection == False and collision == False:
            robot.servo_traverse("+", sensitivity)
            distance_front = robot.get_sensor_ultra("front")
            if distance_front <= distance_front_limit:
                collision = True
                robot.stop_actuator("servo_traverse")
                msg = "semi auto search forward collision front"
                print(msg)
            else:
                tir = robot.get_sensor_thermal()
                if tir > tir_limit:
                    detection = True
                    robot.stop_actuator("servo_traverse")
                    msg = "semi auto search forward fire detected"
                    print(msg)
                else:
                    current_cmd = robot.get_current_command()
                    if "stop" in current_cmd:
                        break
        if msg == "":
            msg = "semi auto search foward"
        return msg

#Search backward
    def search_backward(self, sensitivity):
        self.CurrentRoutine = "search_backward"
        msg = ""
        detection = False
        tir_limit = 100
        while detection == False:
            robot.servo_traverse("-", sensitivity)
            tir = robot.get_sensor_thermal()
            if tir > tir_limit:
                detection = True
                robot.stop_actuator("servo_traverse")
                msg = "semi auto search forward fire detected"
                print(msg)
            else:
                current_cmd = robot.get_current_command()
                if "stop" in current_cmd:
                    break
        if msg == "":
            msg = "semi auto search backward"
        return msg

#Firing solution
    def get_firing_solution(self):
        self.CurrentRoutine = "get_firing_solution"
        #generally don't have a clue how to do this at the moment, maube work in if get chance, and also if other motors come in time
        msg = "semi auto calculating firing solution"
        return msg

#Extinguish fire
    def fire_extinguish(self, waterpressure):
        self.CurrentRoutine = "fire_extinguish"
        msg = ""
        tir_limit = 100
        extinguished = False
        while extinguished == False:
            robot.pump_water(waterpressure)
            tir = robot.get_sensor_thermal()
            if tir < tir_limit:
                extinguished = True
                robot.stop_actuator("pump_water")
                msg = "semi auto fire extinguished"
                print(msg)
            else:
                current_cmd = robot.get_current_command()
                if "stop" in current_cmd:
                    break
        if msg == "":
            msg = "semi auto extinguishing fire"
        return msg


###----------FULL AUTO----------###
#Full auto
# -look left
# --search forward
# -search front
# -look right
# --search backward
# *if fire detected extinguish, using generated firing solution

#--------------------------------------------------------------------
#Only execute if this is the main file, this section is good for testing code
if __name__ == '__main__':
    robot = Robot()
    logger = logging.getLogger()
    robot.set_log(logger)
    input("Press any key to test")
    test = robot.get_sensor_all()
    print(test)
    robot.safe_exit()
