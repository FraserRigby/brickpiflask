// Home page js

//Variables
var modal = document.getElementById('signup');
var login_data = {};

//SignUp popup js
window.onclick = function(event) {
    if (event.target == modal) {
        modal.style.display = "none";
    }
}

//Login submit function, when login submit button pressed data saved to database
function user_login_submit() {
    login_data[username] = document.getElementById('login_username').value
    login_data[password] = document.getElementById('login_password').value
    JSONrequest('/login', 'POST')
}