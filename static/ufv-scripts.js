///Start global variables///
var shutdown = false; //if the server is still live
var recurring_handle = null; //initializes recurring handle var
//recurring_handle = setInterval(get_current_cmd, 1000); //provides recurring event
var message = document.getElementById("msg_box_msg"); //define msg element
var msg = ''

///End global variables///

///Start Robot Functions Code///
//Return message
function return_msg(results) {
    message.innerHTML = results.msg;
}

//Shutdown
function shutdown_server() {
    if (shutdown != False) {
        element = document.getElementById("shutdown_btn");
        element.classList.toggle('shutdown_btn');
        element.classList.toggle('shutdown_clicked_btn');
        clearInterval(recurring_handle);
        setTimeout(() => {console.log("Shutting down");}, 1000);
        JSONrequest('/shutdown', 'POST', return_msg);
        shutdown = true;
    }
}

//Stop Button
function stop() {
    console.log("stop")
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
