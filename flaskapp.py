from flask import Flask, render_template, jsonify, redirect, request, session, flash
import logging #allow loggings
import time, sys, json
#import yourrobot #import in your own robot functionality --> need to develop
from datetime import datetime

ROBOTENABLED = True #this can be used to disable the robot and still edit the webserver
POWER = 30 #constant power/speed

#Global Variables
app = Flask(__name__)
app.config.from_object(__name__) #Set app configuration using above SETTINGS

'''#Create the Robot
robot = None
if ROBOTENABLED:
    #Create Robot first. It take 4 seconds to initialise the robot, sensor view wont work until robot is created...
    robot = yourrobot.Robot()
    robot.set_log(app.logger) #set the logger inside the robot
    if robot.get_battery() < 5: #the robot motors will disable at 6 volts
        robot.safe_exit()
        ROBOTENABLED = False
    else:
        ROBOTENABLED = robot.Configured #if the robot didnt load disable robot, otherwise Robot is enabled
'''
#-----------------HTML REQUEST HANDLERS----------------------------------#
#ufv website, one page to rule them all
@app.route('/', methods=['GET','POST'])
def index():
    return render_template('ufv-website.html')

'''
#----------------JSON REQUEST HANDLERS--------------------#
#get all stats and return through JSON
@app.route('/getallstats', methods=['GET','POST'])
def getallstats():
    results=None
    if ROBOTENABLED: #make sure robot is
        results = robot.get_all_sensors()
    return jsonify(results)

#start robot moving
@app.route('/start', methods=['GET','POST'])
def start():
    collisiondata = None
    if ROBOTENABLED: #make sure robot is
        #collisiondata = {"collisiontype":collisiontype,"elapsedtime":elapsedtime} 
        collisiondata = robot.move_power_untildistanceto(POWER,20,4) #use a third number if you need to correct a dev
    return jsonify({ "message":"collision detected", "collisiondata":collisiondata }) #jsonify take any type and makes a JSON 

#creates a route to get all the user data
@app.route('/getallusers', methods=['GET','POST'])
def getallusers():
    results = database.ViewQueryHelper("SELECT * FROM users")
    return jsonify([dict(row) for row in results]) #jsonify doesnt work with an SQLite.Row

#Get the current command from brickpiinterface.py
@app.route('/getcurrentcommand', methods=['GET','POST'])
def getcurrentcommand():
    currentcommand = None
    if ROBOTENABLED:
        currentcommand = robot.CurrentCommand    
    return jsonify({"currentcommand":currentcommand})

#get the current routine from robot.py
@app.route('/getcurrentroutine', methods=['GET','POST'])
def getcurrentroutine():
    currentroutine= None
    if ROBOTENABLED:
        currentroutine = robot.CurrentRoutine
    return jsonify({"currentroutine":currentroutine})

#get the configuration status from brickpiinterface
@app.route('/getconfigured', methods=['GET','POST'])
def getconfigured():
    return jsonify({"configured":ROBOTENABLED})

#Start callibration of the IMU sensor
@app.route('/getcalibration', methods=['GET','POST'])
def getcalibration():
    calibration = None
    if ROBOTENABLED:
        if not robot.Calibrated:
            calibration = robot.calibrate_imu()
    return jsonify({"calibration":calibration})

#Start callibration of the IMU sensor
@app.route('/reconfigIMU', methods=['GET','POST'])
def reconfigIMU():
    if ROBOTENABLED:
        robot.reconfig_IMU()
    return jsonify({"message":"reconfiguring_IMU"})

#Stop current process
@app.route('/stop', methods=['GET','POST'])
def stop():
    if ROBOTENABLED:
        robot.CurrentRoutine = "ready"
        robot.CurrentCommand = "stop"
        robot.stop_all()
    return jsonify({ "message":"stopping" })

#Shutdown the web server
@app.route('/shutdown', methods=['GET','POST'])
def shutdown():
    if ROBOTENABLED:
        robot.safe_exit()
    func = request.environ.get('werkzeug.server.shutdown')
    func()
    return jsonify({ "message":"shutting down" })

#An example of how to receive data from a JSON object
@app.route('/defaultdatahandler', methods=['GET','POST'])
def defaultdatahandler():
    if request.method == 'POST':
        var1 = request.form.get('var1')
        var2 = request.form.get('var2')
    return jsonify({"message":"just an example"})

#Log a message
def log(message):
    app.logger.info(message)
    return
'''

#---------------------------------------------------------------
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True, threaded=True)

#Threaded mode is important if using shared resources e.g. sensor, each user request launches a thread.. However, with Threaded Mode on errors can occur if resources are not locked down e.g trying to access live readings - conflicts can occur due to processor lock. Use carefully..
