#Importing libraries
from flask import Flask, render_template, jsonify, redirect, request, session, flash
import logging #allow loggings
import time, sys, json
import yourrobot #import in your own robot functionality
from interfaces.databaseinterface import DatabaseHelper
from datetime import datetime

ROBOTENABLED = True #this can be used to disable the robot and still edit the webserver
POWER = 30 #constant power/speed
TPOWER = 20 #constant turning power
DEVIATION = -0.5 #value accounting for motor deviations
DISTANCETO = 20 #Stopping distance
MOF = 2 #Turning margin of error

#Server intialize
app = Flask(__name__)
SECRET_KEY = 'my random key can be anything' #this is used for encrypting sessions
app.config.from_object(__name__) #Set app configuration using above SETTINGS

#Connect to database
database = DatabaseHelper('legofire.sqlite')
database.set_log(app.logger) #set the logger inside the database

#Create the Robot
robot = None
if ROBOTENABLED:
    #Create Robot first. It take 4 seconds to initialise the robot, sensor view wont work until robot is created...
    robot = yourrobot.Robot()
    robot.set_log(app.logger) #set the logger inside the robot
    if robot.get_battery() < 6: #the robot motors will disable at 6 volts
        robot.safe_exit()
        ROBOTENABLED = False
    else:
        ROBOTENABLED = robot.Configured #if the robot didnt load disable robot, otherwise Robot is enabled
        robot.set_database(database) #store a handle to the database inside the robot



#-----------------HTML REQUEST HANDLERS----------------------------------#


#---Page Request Handlers---#

@app.route('/', methods=['GET','POST']) #home page
def index():
    #if user is already logged in (userid in session), redirected to missioncontrol
    '''if 'userid' in session:
        return redirect('./missioncontrol') #no form data is carried across using 'dot/'
    '''
    #post methods, mainly for forms
    #forms processed via json, preventing need for refreshes
    #login & signup functions assoicated with home page controlled via json functions
    return render_template('home.html') #renders home page


@app.route('/missioncontrol') #mission control page
def missioncontrol():
    if 'userid' not in session:
        return redirect('./') #no form data is carried across using 'dot/'
    voltage = None
    if ROBOTENABLED:
        voltage = robot.get_battery()
    return render_template("missioncontrol.html", configured = ROBOTENABLED, voltage = voltage)


@app.route('/missionhistory') #map or table of fire and path data
def missionhistory():
    if 'userid' not in session:
        return redirect('./') #no form data is carried across using 'dot/'
    results = None
    if ROBOTENABLED: #make sure robot is
        pass
    return render_template('missionhistory.html', results=results, configured = ROBOTENABLED)


@app.route('/sensorview', methods=['GET','POST'])#sensor view
def sensorview():
    if 'userid' not in session:
        return redirect('./')
    if ROBOTENABLED: #make sure robot is
        pass
    return render_template("sensorview.html", configured = ROBOTENABLED) 


#-------------END HTML REQUEST HANDLERS----------------------------------#



#----------------JSON REQUEST HANDLERS--------------------#


#--Sensor Handlers--#

@app.route('/getallstats', methods=['GET','POST'])#get all stats and return through JSON
def getallstats():
    results=None
    if ROBOTENABLED: #make sure robot is
        results = robot.get_all_sensors()
    return jsonify(results)


@app.route('/getcalibration', methods=['GET','POST'])#Start callibration of the IMU sensor
def getcalibration():
    calibration = None
    if ROBOTENABLED:
        if not robot.Calibrated:
            calibration = robot.calibrate_imu()
    return jsonify({"calibration":calibration})


@app.route('/reconfigIMU', methods=['GET','POST'])#Reconfigure IMU sensor
def reconfigIMU():
    if ROBOTENABLED:
        robot.reconfig_IMU()
    return jsonify({"message":"reconfiguring_IMU"})


#--Actuator Handlers Traversal--#

@app.route('/forward', methods=['GET','POST'])#Moves robot foward
def forward():
    message = None    
    if ROBOTENABLED:
        #Local Variables
        distance_start = robot.get_ultra_sensor() #get ultra sensor for starting distance to obstacle
        #results = None #don't need right now
        #process_occurred = False #don't think i need this --> for proofing valid process occurred
        '''
        #Full Manual Control
        if session[control_type] == "manual_control":
            message = 'Manual forward.'
            while True:
                robot.move_power(POWER,DEVIATION) #should move forward until while loop broken, intended to be when arrorws held down, etc
                break
        '''
        '''
        #Auto Action Control --> robot moved forward until variable limit reached
        elif session[control_type] == "auto_control"
            message = 'Auto forward.'
            #collisiondata = {"collisiontype":collisiontype,"elapsedtime":elapsedtime}
            collisiondata = robot.move_power_untildistanceto(POWER, DISTANCETO, DEVIATION) #robot moves forward until object detected within specified distance
        '''
        ''' database stuff
        distance_traversed = robot.get_traversed_distance(distance_start)
        #if distance_traversed > 1: #checking if distance greater than 1 to account for invalid processes, assumed to be less than 1
            #process_occurred = True
        if process_occurred = True:
            results = robot.get_all_sensors()
            battery = results[battery]
            colour = results[colour]
            tir = results[thermal]
            acceleration = results[acceleration]
            gyro = results[gyro]
            compass = results[compass]
            temperature = results[temperature]
        database.ModifyQueryHelper('INSERT INTO blah blah blah', (Pram1,Pram1,Pram1)) #Database Entry
    '''
        message = 'Auto forward.'
        #collisiondata = {"collisiontype":collisiontype,"elapsedtime":elapsedtime}
        collisiondata = robot.move_power_untildistanceto(POWER, DISTANCETO, DEVIATION) #robot moves forward until object detected within specified distance
    
    else:
        message = 'Robot not enabled.'
    return jsonify({"Message":message, "collision data":collisiondata})


@app.route('/backward', methods=['GET','POST'])#Moves robot backwards
def backwards():
    message = None
    if ROBOTENABLED:
        #Local Variables
        distance_start = robot.get_ultra_sensor()
        '''
        #Full Manual Control
        if session[control_type] == "manual_control":
            message = 'Manual reverse.'
            while True:
                robot.move_power(-POWER,-DEVIATION)
            distance_traversed = robot.get_traversed_distance(distance_start)
        '''
        '''
        #Auto Action Control
        elif session[control_type] == 'auto_control':
            message = 'Turning around.'
            robot.rotate_power_degrees_IMU(TPOWER, 180, MOF)
        '''
        message = 'Auto turning around, 180 degrees.'
        robot.rotate_power_degrees_IMU(TPOWER, 180, MOF) #rotates robot 180 degrees, turning around
   
    else:
        message = 'Robot not enabled.'
    return jsonify({"message": message})


@app.route('/t_right', methods=['GET','POST'])#Rotates robot right
def t_right():
    message =''
    if ROBOTENABLED:
        '''
        #Full Manual Control
        if session[control_type] = 'manual_control':
            message = 'Manual right turn.'
            heading_start = robot.get_compass_IMU()
            while True:
                robot.rotate_power(RTPOWER)
            heading_traversed = robot.get_rotated_heading(heading_start)
        '''
        '''
        #Auto Action Control
        elif session[control_type] == 'auto_control':
            message = 'Auto right turn, 90 degrees.'
            robot.rotate_power_degrees_IMU(RTPOWER, 90, MOF)
        '''
        message = 'Auto right turn, 90 degrees.'
        robot.rotate_power_degrees_IMU(TPOWER, 90, MOF)

    else:
        message = 'Robot not enabled.'
    return jsonify({"message":message})


@app.route('/t_left', methods=['GET','POST'])#Rotates robot left
def t_left():
    message = ''
    if ROBOTENABLED:
        '''
        #Full Manual Control
        if session[control_type] == 'manual_control':
            message = 'Manual left turn.'
            heading_start = robot.get_compass_IMU()
            while True:
                robot.rotate_power(LTPOWER)
            heading_traversed = robot.get_rotated_heading(heading_start)
        '''
        '''
        #Auto Control
        elif session[control_type] == 'auto_control':
            message = 'Auto left turn, -90 degrees.'
            robot.rotate_power_degrees_IMU(LTPOWER, -90, MOF)
        '''
        message = 'Auto left turn, -90 degrees.'
        robot.rotate_power_degrees_IMU(TPOWER, -90, MOF)

    else:
        message = 'Robot not enabled.'
    return jsonify({"message":message})


#--Actuator Handlers Claw--#

@app.route('/claw_open', methods=['GET','POST'])#Opens robot claw
def claw_open():
    message = ''
    if ROBOTENABLED:
        robot.open_claw()
        message = 'Claw opening.'
    else:
        message = 'Robot not enabled.'
    return jsonify({"message": message})


@app.route('/claw_close', methods=['GET','POST'])#Closes claw
def claw_close():
    message = ''
    if ROBOTENABLED:
        robot.close_claw()
        message = 'Close claw.'
    else:
        message = 'Robot not enabled.'
    return jsonify({"message":message})


#--Database Handlers--#

'''
#Insert Handlers
@app.route('/newdata', methods=['GET','POST'])#New database entry, modular handler allowing specified entry to specfied table
def newdata():

#Select Handlers
@app.route('getdata', methods=['GET','POST'])#Gets data from db, modular handler able to get specified data from specified location
def getdata():

#Modify Handlers
@app.route('modifydata', methods=['GET','POST'])#Modifies data in db, modular handler
def modifydata():

#DeleteHandlers
@app.route('deletedata', methods=['GET','POST'])#Deletes data from db, modular handler
def deletedata():

@app.route('/getallusers', methods=['GET','POST'])#creates a route to get all the user data
def get_all_users():
    results = database.ViewQueryHelper("SELECT * FROM users") #gets all user entries
    return jsonify([dict(row) for row in results]) #jsonify doesnt work with an SQLite.Row
'''


#--Data Transfer Handlers--#

@app.route('/login', methods=['GET','POST']) #Login handler, called when login button activated
def login():
    if ROBOTENABLED:#checking if robot enabled
        #Local variables
        username = ''
        password = ''
        results = "failed"
        message = ''
        if len(session["userid"]) >= 1: #checking if user is already logged in
            if request.method == "POST":
                username = request.form.get('username') #gets username from login form
                password = request.form.get('password') #gets password from login form
                userdetails = database.ViewQueryHelper("SELECT * FROM usertable WHERE username = ? AND password = ?",(username,password)) #gets rows where username & password = inputted values
                if len(userdetails) != 0: #checks whether any acutual results were returned
                    row = userdetails[0]
                    session["userid"] = row["userid"] #assigns session/cookie userid to user's id
                    results = "loggedin" #when results returned via json, js directs to mission control bc logged in
                else:
                    message = "Sorry no user found, password or username incorrect." #no user found message
        else:
            message = "System already being controlled, please logout and try again." #user already logged in message
    else:
        message = "Robot not activated, please activate."
    return jsonify({"results":results, "message":message}) #returns whether user logged in, and error message if necessary


@app.route('/signup', methods=['GET','POST']) #Signup handler, called when signup button activated
def signup():
    if ROBOTENABLED:#checking if robot enabled
        #Local variables
        name = ''
        surname = ''
        username = ''
        password = ''
        userroles = []
        message = ''
        if request.method == "POST":
            name = request.form.get('name') #gets name from singup form
            surname = request.form.get('surname') #gets surname from signup form
            username = request.form.get('username') #gets username from signup form
            password = request.form.get('password') #gets password from signup form
            taken_username = database.ViewQueryHelper('SELECT * FROM usertable WHERE username = ?',(username,)) #getting data entries with same username as inputted
            if len(taken_username) == 0: #checking that username is unique
                database.ModifyQueryHelper("INSERT INTO usertable (name, surname, username, password) VALUES (?,?,?,?)",(name, surname, username, password)) #creating new user entry
                if request.form.get('role_firefighter') == "firefighter": #checks whether firefighter role selected
                    userroles.append(1)
                if request.form.get('role_investigator') == "investigator": #checks whether investigator role selected
                    userroles.append(2)
                if request.form.get('role_admin') == "admin": #checks whether admin role selected
                    userroles.append(3) #if role selected, role code added to list
                userid = database.ViewQueryHelper("SELECT userid FROM usertable WHERE username = ? AND password = ?",(username,password)) #userid fetched
                row = userid[0]
                session["userid"] = row["userid"] #gets userid
                for role in userroles:
                    database.ModifyQueryHelper("INSERT INTO userrole (userid, rolecode) VALUES (?,?)",(session["userid"],role)) #creating new role entry for user
                message = "New user created, please log in to access fire robot system." #signup confirmation message
            else:
                message = "Username is taken, please choose a different one." #error message
        else:
            message = "Robot not activated, please activate."
    return jsonify({"message":message}) #returns mssages

            
#--Miscellaneous Request Handlers--#

@app.route('/getcurrentcommand', methods=['GET','POST'])#Get the current command from brickpiinterface.py
def getcurrentcommand():
    currentcommand = None
    if ROBOTENABLED:
        currentcommand = robot.CurrentCommand    
    return jsonify({"currentcommand":currentcommand})


@app.route('/getcurrentroutine', methods=['GET','POST'])#get the current routine from robot.py
def getcurrentroutine():
    currentroutine= None
    if ROBOTENABLED:
        currentroutine = robot.CurrentRoutine
    return jsonify({"currentroutine":currentroutine})


@app.route('/getconfigured', methods=['GET','POST'])#get the configuration status from brickpiinterface
def getconfigured():
    return jsonify({"configured":ROBOTENABLED})


@app.route('/stop', methods=['GET','POST'])#Stop current process
def stop():
    if ROBOTENABLED:
        robot.CurrentRoutine = "ready"
        robot.CurrentCommand = "stop"
        robot.stop_all()
    return jsonify({ "message":"Stopping" })


@app.route('/shutdown', methods=['GET','POST'])#Shutdown the web server
def shutdown():
    if ROBOTENABLED:
        robot.safe_exit()
    func = request.environ.get('werkzeug.server.shutdown')
    func()
    return jsonify({ "message":"shutting down" })


@app.route('/defaultdatahandler', methods=['GET','POST'])#An example of how to receive data from a JSON object
def defaultdatahandler():
    if request.method == 'POST':
        var1 = request.form.get('var1')
        var2 = request.form.get('var2')
    return jsonify({"message":"just an example"})



#------------END JSON REQUEST HANDLERS--------------------#



#Log a message
def log(message):
    app.logger.info(message)
    return

#---------------------------------------------------------------
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True, threaded=True)

#Threaded mode is important if using shared resources e.g. sensor, each user request launches a thread.. However, with Threaded Mode on errors can occur if resources are not locked down e.g trying to access live readings - conflicts can occur due to processor lock. Use carefully..
