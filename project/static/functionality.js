
//hides the login form components and displays the register form components
function registerSwap() {
    document.getElementById("login-window").style.display = "none";
    document.getElementById("register-window").style.display = "block";
    document.getElementById("login-swap").style.display = "block";
    document.getElementById("register-swap").style.display = "none";
}

//hides the register form components and displays the login form components
function loginSwap() {
    document.getElementById("login-window").style.display = "block";
    document.getElementById("register-window").style.display = "none";
    document.getElementById("login-swap").style.display = "none";
    document.getElementById("register-swap").style.display = "block";
}

// Displays the form to add a new post
function writePost() {
    document.getElementById("post-show").style.display = "block";
}

// Hides the form to add a new post and resets the content
function cancelPost() {
    document.getElementById("post-show").style.display = "none";
    document.getElementById("post-content").value = "";
}
