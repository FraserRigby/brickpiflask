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
        return

    #gets the current routine
    def get_current_routine(self):
        return robot.CurrentRoutine


###----------SEMI AUTO----------###
#Look left
    def servo_turret_face_left(self):
        robot.CurrentRoutine = "servo_turret_face_left"
        robot.CurrentCommand = "servo_turret face left"
        robot.servo[robot.actuator_servo_turret].angle = 0
        msg = "servo_turret rotate face left (-90deg)"
        print(msg)
        return msg
    
#Look right
    def servo_turret_face_right(self):
        robot.CurrentRoutine = "servo_turret_face_right"
        robot.CurrentCommand = "servo_turret face right"
        robot.servo[robot.actuator_servo_turret].angle = 180
        msg = "servo_turret rotate face right (+90deg)"
        print(msg)
        return msg

#Search front auto
    def search_front_auto(self, sensitivity):
        robot.CurrentRoutine = "search_front_semi"
        search_front = True
        detection = False
        msg = ""
        tir_limit = 100
        if robot.CurrentRoutine != "ready":
            angle = robot.servo[robot.actuator_servo_turret].angle
            self.servo_turret_face_left()
            angle_limit = 180
            while search_front == True and detection == False:
                angle = robot.servo[robot.actuator_servo_turret].angle
                if angle >= angle_limit:
                    search_front = False
                    robot.stop_actuator("servo_turret")
                else:
                    tir = robot.get_sensor_thermal()
                    if tir >= tir_limit:
                        detection = True
                        robot.stop_actuator("servo_turret")
                        msg = "semiauto search front auto fire detected"
                        print(msg)
                    else:
                        robot.servo_turret("+", sensitivity)
        if msg == "":
            msg = "semiauto search front auto"
        return msg

#Search front semi
    def search_front_semi(self):
        robot.CurrentRoutine = "search_front_semi"
        detection = False
        msg = ""
        tir_limit = 100         
        while detection == False and robot.CurrentRoutine != "ready":
            tir = robot.get_sensor_thermal()
            if tir >= tir_limit:
                detection = True
                robot.stop_actuator("servo_turret")
                msg = "semiauto search front semi fire detected"
                print(msg)        
        if msg == "":
            msg = "semiauto search front semi"
        return msg

#Search forward
    def search_forward(self, sensitivity):
        robot.CurrentRoutine = "search_forward"
        msg = ""
        detection = False
        collision = False
        distance_front_limit = 10
        tir_limit = 100
        while detection == False and collision == False and robot.CurrentRoutine != "ready":
            distance_front = robot.get_sensor_ultra("front")
            if distance_front <= distance_front_limit:
                collision = True
                robot.stop_actuator("servo_traverse")
                msg = "semiauto search forward collision front"
                print(msg)
            else:
                tir = robot.get_sensor_thermal()
                if tir >= tir_limit:
                    detection = True
                    robot.stop_actuator("servo_traverse")
                    msg = "semiauto search forward fire detected"
                    print(msg)
                else:
                    robot.servo_traverse("+", sensitivity)
        if msg == "":
            msg = "semiauto search foward"
        return msg

#Search backward
    def search_backward(self, sensitivity):
        robot.CurrentRoutine = "search_backward"
        msg = ""
        detection = False
        tir_limit = 100
        while detection == False and robot.CurrentRoutine != "ready":
            tir = robot.get_sensor_thermal()
            if tir >= tir_limit:
                detection = True
                robot.stop_actuator("servo_traverse")
                msg = "semiauto search backward fire detected"
                print(msg)
            else:
                robot.servo_traverse("-", sensitivity)
        if msg == "":
            msg = "semiauto search backward"
        return msg

#Firing solution
    def get_firing_solution(self):
        robot.CurrentRoutine = "get_firing_solution"
        '''
        if robot.CurrentRoutine != "ready":
            #write code here
            #generally don't have a clue how to do this at the moment, maube work in if get chance, and also if other motors come in time
        '''
        msg = "semiauto calculating firing solution --> work in progress"
        return msg

#Extinguish fire
    def fire_extinguish(self, waterpressure):
        robot.CurrentRoutine = "fire_extinguish"
        msg = ""
        tir_limit = 100
        extinguished = False
        while extinguished == False and robot.CurrentRoutine != "ready":
            tir = robot.get_sensor_thermal()
            if tir < tir_limit:
                extinguished = True
                robot.stop_actuator("pump_water")
                msg = "semiauto fire extinguished"
                print(msg)
            else:
                robot.pump_water(waterpressure)
        if msg == "":
            msg = "semiauto extinguishing fire"
        return msg


###----------FULL AUTO----------###
#Full auto
# -look left
# --search forward
# -search front
# -look right
# --search backward
# *if fire detected extinguish, using generated firing solution

    def full_auto(self, sensitivity, waterpressure):
        robot.CurrentRoutine = "full_auto"
        msg = ""
        while robot.CurrentRoutine != "ready":
            detection = ""
            self.servo_turret_face_left()
            distance_limit = 10
            search_forward = True
            while search_forward == True and robot.CurrentRoutine != "ready":
                distance = robot.get_sensor_ultra("front")
                if distance <= distance_limit:
                    search_forward = False
                else:
                    detection = self.search_forward(sensitivity)
                    if detection == "semiauto search forward fire detected":
                        self.fire_extinguish(waterpressure)
            search_front = True
            angle_turret_limit = 180
            while search_front == True and robot.CurrentRoutine != "ready":
                angle_turret  = robot.servo[robot.actuator_servo_turret].angle
                if angle_turret >= angle_turret_limit:
                    search_front = False
                else:
                    detection = self.search_front_auto(sensitivity)
                    if detection == "semiauto search front auto fire detected":
                        self.fire_extinguish(waterpressure)
            self.servo_turret_face_right()
            search_backward = True
            while search_backward == True and robot.CurrentRoutine != "ready":
                if robot.CurrentRoutine == "ready":
                    search_backward = False
                else:
                    detection = self.search_backward(sensitivity)
                    if detection == "semiauto search backward fire detected":
                        self.fire_extinguish(waterpressure)
        msg = "full_auto routine completed/stopping"
        return msg

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
