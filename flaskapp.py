###----------IMPORTING/DEFINING----------###
from flask import Flask, render_template, jsonify, redirect, request, session, flash, Response
import logging #allow loggings
import time, sys, json
from datetime import datetime
import yourrobot #import in your own robot functionality --> need to develop
from interfaces.camerainterface import Camera

'''
Attribute:
The code in this project is based-off that developed by Brad Nielsen.
Many thanks to Brad for allowing the use of his code in this project,
and for his assistance in troubleshooting.
The base code can be found in Brad's brickpi-flask repo:
https://github.com/bradnielsen2981/brickpi-flask
'''

#Global Variables
app = Flask(__name__)
app.config.from_object(__name__) #Set app configuration using above SETTINGS
sensitivity = float(0.5)
waterpressure = float(0.5)

robot = None #Create the Robot
ROBOTENABLED = True #this can be used to disable the robot and still edit the webserver
if ROBOTENABLED:
    robot = yourrobot.Robot() 
    robot.set_log(app.logger) #set the logger inside the robot
    #if needed, add parameters to whether ROBOTENABLED remain true

###----------HTML REQUEST HANDLERS----------###
#UFV website, one page to rule them all!
@app.route('/', methods=['GET','POST'])
def index():
    return render_template('ufv-website.html')

def gen(camera):
    """Video streaming generator function."""
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


@app.route('/video_feed')
def video_feed():
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(gen(Camera()), mimetype='multipart/x-mixed-replace; boundary=frame')


###----------JSON REQUEST HANDLERS----------###
#Shutdown the web server
@app.route('/shutdown', methods=['GET','POST'])
def shutdown():
    if ROBOTENABLED:
        robot.safe_exit()
    func = request.environ.get('werkzeug.server.shutdown')
    func()
    return jsonify({"msg":"shutting down"})

#Stop current process
@app.route('/stop', methods=['GET','POST'])
def stop():
    if ROBOTENABLED:
        robot.CurrentRoutine = "ready"
        robot.CurrentCommand = "stop"
        robot.stop_all()
    return jsonify({"msg":"stopping"})

#Updating variables from user input
@app.route('/var_update', methods=['GET','POST'])
def var_update():
    data = request.form
    global sensitivity, waterpressure
    for entry in data:
        if entry == "sensitivity":
            sensitivity = data.get(entry)
        elif entry == "waterpressure":
            waterpressure = data.get(entry)
    return jsonify({"msg":"variable updated"})

#Get current command from robotinterface
@app.route('/get_current_cmd', methods=['GET','POST'])
def get_current_cmd():
    currentcommand = None
    if ROBOTENABLED:
        currentcommand = robot.CurrentCommand    
    return jsonify({"currentcommand":currentcommand})

#Get all sensor data
@app.route('/get_sensor_all', methods=['GET','POST'])
def get_sensor_all():
    results = None
    if ROBOTENABLED:
        results = robot.get_sensor_all()
    return jsonify(results)

#Get all actuator data
@app.route('/get_actuator_all', methods=['GET','POST'])
def get_actuator_all():
    results = None
    if ROBOTENABLED:
        results = robot.get_actuator_all()
    return jsonify(results)

#Manual actuator operation
@app.route('/manual_actuator', methods=['GET','POST'])
def manual_actuator():
    global sensitivity, waterpressure
    #float(sensitivity)
    #float(waterpressure)
    actuator = request.form.get("actuator")
    action = request.form.get("action")
    action_msg = "actuator not active"
    print(actuator, action)
    print(sensitivity, waterpressure)
    if action == "stop":
        #stop actuator
        action_msg = robot.stop_actuator(actuator)
    else:
        if actuator == "servo_traverse":
            #move forward/back 
            action_msg = robot.servo_traverse(action, sensitivity)
            print("move, or at least do something!!!")
        elif actuator ==  "servo_turret":
            #rotate left/right 
            action_msg = robot.servo_turret(action, sensitivity)
        elif actuator == "servo_nozzle":
            #rotate up/down 
            action_msg = robot.servo_nozzle(action, sensitivity)
        elif actuator == "pump_water":
            #shoot water 
            action_msg = robot.pump_water(action, waterpressure)
    return jsonify({"msg":action_msg})


'''
#start robot moving
@app.route('/start', methods=['GET','POST'])
def start():
    collisiondata = None
    if ROBOTENABLED: #make sure robot is
        #collisiondata = {"collisiontype":collisiontype,"elapsedtime":elapsedtime} 
        collisiondata = robot.move_power_untildistanceto(POWER,20,4) #use a third number if you need to correct a dev
    return jsonify({ "message":"collision detected", "collisiondata":collisiondata }) #jsonify take any type and makes a JSON 


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

'''
'''

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

#---------------------------------------------------------------#
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True, threaded=True)

#Threaded mode is important if using shared resources e.g. sensor, each user request launches a thread.. However, with Threaded Mode on errors can occur if resources are not locked down e.g trying to access live readings - conflicts can occur due to processor lock. Use carefully..
