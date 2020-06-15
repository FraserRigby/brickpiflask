//Mission control page js

//variables
var shutdown = false;
var recurringhandle = null;  //can be used to delete recurring function if you want
recurringhandle = setInterval(get_current_command, 1000);
var message = '';

var element = document.getElementById("origin");
element.classList.toggle('origin-missioncontrol');

function shutdownserver(){
    clearInterval(recurringhandle);
    setTimeout(() => { console.log("Shutting down"); }, 1000);
    JSONrequest('/shutdown','POST');
    shutdown = true;
}

//THis recurring function gets data using JSON
function get_current_command() {
    if (shutdown == false)
    {
        JSONrequest('/getcurrentcommand','POST', writecurrentcommand); //Once data is received it is passed to the writecurrentcommand
    }
}

//THis recurring function gets data using JSON
function sendtodefaulthandler() {
    if (shutdown == false)
    {
        params = { "var1":"John", "var2":30 };
        JSONrequest('/defaultdatahandler','POST', writecurrentcommand, params); //Once data is received it is passed to the writecurrentcommand
    }
}

//with received json data, send to page
function writecurrentcommand(results) {
    document.getElementById('message').innerHTML = results.currentcommand;
}


//New Mission

//new mission window open function
function new_mission_window() {
    document.getElementById('mc-new').style.display='block';
}

//NewMission popup close js
window.onclick = function(event) {
    if (event.target == modal) {
        modal.style.display = "none";
    }
}

//New mission submit function
function new_mission() {
    var mission_data = {};
    mission_data['address'] = document.getElementById('mc_address').value; //getting form field values
    mission_data['postcode'] = document.getElementById('mc_postcode').value;
    mission_data['description'] = document.getElementById('mc_description').value;
    var mc_new = true;
    var empty_field = false;
    for (i = 0; i < length.signup_data; i++) {
        if (signup_data[i] == '') {
            empty_field = true;
            mc_new = False
            document.getElementById('signup-message').innerHTML = "Data not entered, please try again.";
            break;
        }
    }
    if (mc_new == true) {
        JSONrequest('/new_mission', 'POST', new_mission_results_return, mission_data);
    }
}

//gets return data from /new_mission
function new_mission_results_return(results){
    document.getElementById('mc-new-message').innerHTML = "New mission created."
}
