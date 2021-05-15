///Start global variables///
var shutdown = false; //if the server is still live
var sensitivity = parseFloat(document.getElementById("slider_sensitivity").value);
var waterpressure = parseFloat(document.getElementById("slider_waterpressure").value);
var sensorview_container = false;
var actuatorview_container = false;
var graphview_container = false
var recurring_handle_currentcmd = null; //initializes recurring handle var currentcmd
var recurring_handle_sensordata = null; //initializes recurring handle var for sensordata
var recurring_handle_actuatordata = null; //initializes recurring handle var for actuatordata
//recurring_handle_currentcmd = setInterval(get_current_cmd, 1000); //provides recurring event
var message = document.getElementById("msg_box_msg"); //define msg element
var msg = '';
///End global variables///

///Start Data Functions Code///
//Return message
function return_msg(results) {
    var msg = results.msg
    message.innerHTML = msg;
}

//Get current command
function get_current_cmd() {
    JSONrequest('/get_current_cmd', 'POST', return_cmd);
}

//Return current command
function return_cmd(results) {
    console.log(results.currentcommand);
}

//Get all sensor data
function get_sensor_all() {
    JSONrequest('/get_sensor_all', 'POST', return_sensor_all);
}

//Return all sensor data
function return_sensor_all(results) {
    document.getElementById("sensor_tif").innerHTML = String(results.thermal);
    document.getElementById("sensor_distance_front").innerHTML = String(results.distance_front);
    document.getElementById("sensor_distance_turret").innerHTML = String(results.distance_turret);
    document.getElementById("sensor_battery").innerHTML = String(results.battery);
    document.getElementById("sensor_raspi_temp").innerHTML = String(results.raspi_temp);
}

//Get all actuator data
function get_actuator_all() {
    JSONrequest('/get_actuator_all', 'POST', return_actuator_all);
}

//Return all actuator data
function return_actuator_all(results) {
    document.getElementById("actuator_driveservo").innerHTML = String(results.servo_traverse);
    document.getElementById("actuator_turretservo").innerHTML = String(results.servo_turret);
    document.getElementById("actuator_nozzleservo").innerHTML = String(results.servo_nozzle);
}
///End Data Functions Code///


///Start Robot Functions Code///
//Shutdown
function shutdown_server() {//activated when shutdown btn pressed
    if (shutdown != true) {
        console.log("shutdown")
        element = document.getElementById("shutdown_btn");
        element.classList.toggle('shutdown_btn');
        element.classList.toggle('shutdown_clicked_btn');
        clearInterval(recurring_handle_currentcmd);//ends recurring event
        clearInterval(recurring_handle_sensordata);
        clearInterval(recurring_handle_actuatordata);
        setTimeout(() => {console.log("Shutting down");}, 1000);
        JSONrequest('/shutdown', 'POST', return_msg);
        shutdown = true;
    }
}

//Stop All Processes
function stop_all() {//activated when stop btn pressed
    console.log("stopping");
    JSONrequest('/stop_all', 'POST', return_msg);
}

//Update Slider Variable Value
document.getElementById("actuator_sensitivity").innerHTML = sensitivity;
document.getElementById("actuator_waterpressure").innerHTML = waterpressure;

function slider_update(slider_id, output) {
    var slider = document.getElementById(slider_id);
    var input = parseFloat(slider.value);
    var output_elmnt = null;
    if (output != "none") {
        output_elmnt = document.getElementById(output);
        output_elmnt.innerHTML = input;
    }
    if (slider_id == "slider_sensitivity") {
        sensitivity = input;
    }
    else if (slider_id == "slider_waterpressure") {
        waterpressure = input;
    }
    console.log("slider updating");
}

//Transfer slider variable value
function slider_transfer(slider_id) {
    var data = {};
    if (slider_id == "slider_sensitivity") {
        sensitivity = sensitivity/100;
        data["sensitivity"] = sensitivity;
    }
    else if (slider_id == "slider_waterpressure") {
        waterpressure = waterpressure/100;
        data["waterpressure"] = waterpressure;
    }
    JSONrequest('/var_update', 'POST', return_msg, data);
    console.log("slider transfering");
}

//Manual Actuator Operation
function manual_actuator(actuator, action) {
    if (action != "stop") {
        get_actuator_all()
    }
    commands = {};
    commands["actuator"] = actuator;
    commands["action"] = action;
    JSONrequest('/manual_actuator', 'POST', return_msg, commands);
    console.log(commands);
    if (action == "stop") {
        get_actuator_all()
    }
}
///End Robot Functions Code///


///Start Div Drag Code///
dragElement(document.getElementById("controlmenu_container"));
dragElement(document.getElementById("sensorview_container"));
dragElement(document.getElementById("actuatorview_container"));
dragElement(document.getElementById("graphview_container"));
dragElement(document.getElementById("manual_container"));
dragElement(document.getElementById("semiauto_container"));
dragElement(document.getElementById("auto_container"));

// Make the DIV element draggable: attribute(https://www.w3schools.com/howto/howto_js_draggable.asp)
function dragElement(elmnt) {
  var pos1 = 0, pos2 = 0, pos3 = 0, pos4 = 0;
  document.getElementById(elmnt.id + "_header").onmousedown = dragMouseDown;
  
  function dragMouseDown(e) {
    e = e || window.event;
    e.preventDefault();
    // get the mouse cursor position at startup:
    pos3 = e.clientX;
    pos4 = e.clientY;
    document.onmouseup = closeDragElement;
    // call a function whenever the cursor moves:
    document.onmousemove = elementDrag;
  }

  function elementDrag(e) {
    e = e || window.event;
    e.preventDefault();
    // calculate the new cursor position:
    pos1 = pos3 - e.clientX;
    pos2 = pos4 - e.clientY;
    pos3 = e.clientX;
    pos4 = e.clientY;
    // set the element's new position:
    elmnt.style.top = (elmnt.offsetTop - pos2) + "px";
    elmnt.style.left = (elmnt.offsetLeft - pos1) + "px";
  }

  function closeDragElement() {
    // stop moving when mouse button is released:
    document.onmouseup = null;
    document.onmousemove = null;
  }
}
///End Div Drag Code///


///Start Div Collapse Code///
function collapseElement(elmnt, btn) {
    var button = document.getElementById(btn);
    var element = document.getElementById(elmnt + "_content");
    if (element.style.display == 'none') {
        element.style.display = 'block';
        button.innerHTML = "_";
    }
    else {
        element.style.display = 'none';
        button.innerHTML = "+";
    }
}
///End Div Collapse Code///


///Start Window Open Code///
function openElement(elmnt) {
    var element = document.getElementById(elmnt);
    var button = document.getElementById(elmnt + "_open_btn")
    element.classList.toggle('dragcontainer_init');
    element.classList.toggle('dragcontainer_est');
    if (button.innerHTML == 'Open') {
        button.innerHTML = "Close";
        recurring_start(elmnt);
    }
    else {
        button.innerHTML = "Open";
        recurring_stop(elmnt);
    }
}
///End Window Open Code///


///Start Window Close Code///
function closeElement(elmnt) {
    var element = document.getElementById(elmnt);
    var button = document.getElementById (elmnt + "_open_btn");
    element.classList.toggle('dragcontainer_init');
    element.classList.toggle('dragcontainer_est');
    if (button.innerHTML != 'Open') {
        button.innerHTML = 'Open';
    }
    recurring_stop(elmnt);
}
///End Window Close Code///


///Start Recurring Code///
function recurring_start(elmnt) {
    if (elmnt == "sensorview_container") {
        sensorview_container = true;
    }
    else if (elmnt == "actuatorview_container") {
        actuatorview_container = true;
    }
    else if (elmnt == "graphview_container") {
        graphview_container = true;
    }
    if ((elmnt == "graphview_container" && sensorview_container == false) || (elmnt == "sensorview_container" && graphview_container == false)) {
        recurring_handle_sensordata = setInterval(get_sensor_all, 1000);//provides recurring event
    }
    else if ((elmnt == "graphview_container" && actuatorview_container == false) || (elmnt == "actuatorview_container" && graphview_container == false)) {
        //recurring_handle_actuatordata = setInterval(get_actuator_all, 1000);
    }
}

function recurring_stop(elmnt) {
    if (elmnt == "sensorview_container") {
        sensorview_container = false;
    }
    else if (elmnt == "actuatorview_container") {
        actuatorview_container = false;
    }
    else if (elmnt == "graphview_container") {
        graphview_container = false;
    }
    if ((elmnt == "graphview_container" && sensorview_container == false) || (elmnt == "sensorview_container" && graphview_container == false)) {
        clearInterval(recurring_handle_sensordata);
    }
    else if ((elmnt == "graphview_container" && actuatorview_container == false) || (elmnt == "actuatorview_container" && graphview_container == false)) {
        //clearInterval(recurring_handle_actuatordata);
    }
}
///End Recurring Code///


///Start Toggle Class Code///
function toggle_class(elmnt, normal_class, target_class) {
    var element = document.getElementById(elmnt);
    var current_class = element.className;
    if (current_class != target_class) {
        element.classList.toggle(normal_class);
        element.classList.toggle(target_class);
    }
    else {
        element.classList.toggle(current_class);
        element.classList.toggle(normal_class);
    }
}
///End Highlight Code///