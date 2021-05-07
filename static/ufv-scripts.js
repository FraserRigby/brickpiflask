///Start global variables///
var shutdown = false; //if the server is still live
var recurring_handle_currentcmd = null; //initializes recurring handle var currentcmd
var recurring_handle_sensordata = null; //initializes recurring handle var for sensordata
var recurring_handle_actuatordata = null; //initializes recurring handle var for actuatordata
//recurring_handle = setInterval(get_current_cmd, 1000); //provides recurring event
var message = document.getElementById("msg_box_msg"); //define msg element
var msg = '';
///End global variables///

///Start Robot Functions Code///
//Return message
function return_msg(results) {
    message.innerHTML = results.msg;
}

//Shutdown
function shutdown_server() {//activated when shutdown btn pressed
    if (shutdown != true) {
        element = document.getElementById("shutdown_btn");
        element.classList.toggle('shutdown_btn');
        element.classList.toggle('shutdown_clicked_btn');
        clearInterval(recurring_handle_currentcmd);
        clearInterval(recurring_handle_sensordata);
        clearInterval(recurring_handle_actuatordata);
        setTimeout(() => {console.log("Shutting down");}, 1000);
        JSONrequest('/shutdown', 'POST', return_msg);
        shutdown = true;
    }
}

//Stop Processes
function stop() {//activated when stop btn pressed
    console.log("stop");
    JSONrequest('/stop', 'POST', return_msg);
}

//Update Sensitivity
function sensitivity_update() {
}

//Manual Traverse Forward
function manual_traverse_forward() {
}

//Manual Traverse Backward
function manual_traverse_backward() {
}

//Manual Rotate Turret Left
function manual_turret_left() {
}

//Manual Rotate Turret Right
function manual_turret_right() {
}

//Manual Rotate Nozzle Up
function manual_nozzle_up() {
}

//Manual Rotate Nozzle Down
function manual_nozzle_down() {
}

//Update Water Pressure
function waterpressure_update() {
}

//Manual Water Fire
function manual_waterfire() {
}
///End Robot Functions Code///

///Start Robot Data Code///
///End Robot Data Code///

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
    }
    else {
        button.innerHTML = "Open";
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
}
///End Window Close Code///

///Start Highlight Code/// --> something fishy is going on here
function highlight(elmnt) {
    var element = document.getElementById(elmnt);
    var current_class = element.className;
    console.log(current_class);
    var class_normal = elmnt;
    var class_active = elmnt + '_active';
    if (current_class != class_active) {
        element.classList.toggle(current_class);
        element.classList.toggle(class_active);
    }
    else {
        element.classList.toggle(class_active);
        element.classList.toggle(class_normal);
    }
}
///End Highlight Code///