// Home page js

//Variables
var modal = document.getElementById('signup');
var login_data = {};
var message = '';

//SignUp popup js
window.onclick = function(event) {
    if (event.target == modal) {
        modal.style.display = "none";
    }
}

//Signup window open function
function window_signup_open() {
    var origin = document.getElementById('origin');
    origin.classList.toggle('origin_signup_transition')
    document.getElementById('signup').style.display='block';

}

//Login submit function, when login submit button pressed data saved to database
function user_login_submit() {
    login_data['username'] = document.getElementById('login_username').value; //getting form field values
    login_data['password'] = document.getElementById('login_password').value;
    if (login_data['username'] != '' && login_data['password'] != '') { //testing to see if data not submitted
        document.getElementById('message').innerHTML = "No data entered, please try again."; //no data input message
    } else {
        JSONrequest('/login','POST',login_results_return,login_data);
    }
}

//gets data from executed user_login_submit function, if user is "loggedin"
function login_results_return(results, message) {
    if (results.results == "loggedin") {
        window.location.pathname = '/missioncontrol'; //taken to mission control page
    } else{
        document.getElementById('message').innerHTML = message.message; //gives signin error message
    }
}

//Signup submit function, when signup button pressed data processed, sent to server to be saved
function user_sign_up() {
    signup_data['name'] = document.getElementById('signup_name').value; //getting form field values
    signup_data['surname'] = document.getElementById('signup_surname').value;
    signup_data['password'] = document.getElementById('signup_password').value;
    signup_data['confirm_password'] = document.getElementById('confirm_password').value;
    signup_data["role_firefighter"] = document.getElementById('role_firefighter').value;
    signup_data['role_investigator'] = document.getElementById('role_investigator').value;
    signup_data['role_admin'] = document.getElementById('role_admin').value;
    var signup = True;
    var empty_field = false;
    for (i = 0; i < length.signup_data; i++) {
        if (signup_data[i] == '') {
            empty_field = true;
            signup = False
            document.getElementById('message').innerHTML = "Data not entered, please try again.";
            break;
        }
    }
    if (signup != false && signup_data['password'] != signup_data['confirm_data']) {
        signup = False;
        document.getElementById('message').innerHTML = "New password and confirm password do not match, please try again.";
    }
    if (signup == true) {
        JSONrequest('/signup','POST',signup_results_return,signup_data);
    }
}

//
function signup_results_return(results, message) {
        document.getElementById('message').innerHTML = message.message;
}