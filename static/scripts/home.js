// Home page js

//Variables
var modal = document.getElementById('signup');
var login_data = {};
var message = '';

//setting page background
document.getElementById("origin").className = 'origin-home';


//Signup window open function
function window_signup_open() {
    document.getElementById('signup').style.display='block';
}

//SignUp popup close js
window.onclick = function(event) {
    if (event.target == modal) {
        modal.style.display = "none";
    }
}

//Logout function js
function logout() {
    JSONrequest('/logout', 'POST');
}


//Login

//Login submit function, when login submit button pressed data saved to database
function user_login_submit() {
    var login_data = {};
    login_data['username'] = document.getElementById('login_username').value; //getting form field values
    login_data['password'] = document.getElementById('login_password').value;
    if (login_data['username'] == '' && login_data['password'] == '') { //testing to see if data not submitted
        document.getElementById('login-message').innerHTML = "No data entered, please try again."; //no data input message
    } else {
        JSONrequest('/login', 'POST', login_results_return, login_data);
    }
}

//gets data from executed user_login_submit function, if user is "loggedin"
function login_results_return(results) {
    if (results.results == "loggedin") {
        document.getElementById('login-message').innerHTML = "User logged in!"
        window.location.pathname = '/missioncontrol'; //taken to mission control page
    } else{
        document.getElementById('login-message').innerHTML = results.message; //gives signin error message
    }
}


//Signup, new user

//Signup submit function, when signup button pressed data processed, sent to server to be saved
function user_sign_up() {
    var signup_data = {};
    signup_data['name'] = document.getElementById('signup_name').value; //getting form field values
    signup_data['surname'] = document.getElementById('signup_surname').value;
    signup_data['username'] = document.getElementById('signup_username').value;
    signup_data['password'] = document.getElementById('signup_password').value;
    signup_data['password_confirm'] = document.getElementById('password_confirm').value;
    signup_data['role_firefighter'] = document.getElementById('role_firefighter').value;
    signup_data['role_investigator'] = document.getElementById('role_investigator').value;
    signup_data['role_admin'] = document.getElementById('role_admin').value;
    var signup = true;
    var empty_field = false;
    for (i = 0; i < length.signup_data; i++) {
        if (signup_data[i] == '') {
            empty_field = true;
            signup = False
            document.getElementById('signup-message').innerHTML = "Data not entered, please try again.";
            break;
        }
    }
    if (signup != false && signup_data['password'] != signup_data['password_confirm']) {
        signup = False;
        document.getElementById('signup-message').innerHTML = "New password and confirm password do not match, please try again.";
    }
    if (signup == true) {
        JSONrequest('/signup', 'POST', signup_results_return, signup_data);
    }
}

//gets return data from /signup
function signup_results_return(results) {
        document.getElementById('signup-message').innerHTML = results.message;
}