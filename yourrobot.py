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

#Look right

#Search front

#Search forward

#Search backward

#Firing solution

#Extinguish fire


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
