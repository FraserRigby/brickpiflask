###----------IMPORTING/DEFINING----------###
# This class inherits from the robot interface, it should include any code for sub-routines
from interfaces.robotinterface import RobotInterface
import logging
import time

#This class is encapsualtes routines which execute the elementary functions established in the RobotInterface object
class Robot(RobotInterface):
    
    def __init__(self):
        super().__init__()
        self.CurrentRoutine = 'ready' #could be useful to keep track of the current routine
        return

    #gets the current routine
    def get_current_routine(self):
        return self.CurrentRoutine

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
