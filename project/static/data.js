
// An object of a single friend 
class Friend {
    constructor(userid, accepted, username, useremail) {
        this.userid = userid;
        this.accepted = accepted;
        this.username = username;
        this.useremail = useremail;
    }
}

// An object of a single post
class Post {
    constructor(postid, userid, content, date, view) {
        this.postid = postid;
        this.userid = userid;
        this.content = content;
        this.date = date;
        this.view = view;
    }
}

//An object of a single user
class User {
    constructor(userid, username, useremail) {
        this.userid = userid;
        this.username = username;
        this.useremail = useremail;
    }
}

// A collection of multiple posts and different ways to edit them
class Posts {
    constructor() {
        this.posts = [];
    }

    // Gets the posts from the server
    async getPosts() {
        let sortmethod = document.getElementById("select-sort").value;
        let response = await fetch("/posts");
        if (response.status == 200){
            let result = await response.json();
            this.posts = [];
            let userids = [];
            // The result of the posts in a json file that retrieves each entry and makes it into a 'Post'
            for (let i = 0; i <= Object.keys(result).length-1; i++) { 
                this.posts.push(new Post(result[i][0], result[i][1], result[i][2], result[i][3], result[i][4]));
                userids.push(result[i][1]);
            }
            await this.sortPosts(sortmethod);
        }
    }

    // Sends a new post to the server
    async addPost(content, view) {
        let response = await fetch("/posts", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({"content": content, "view": view}),
        });
        if (response.status != 200){
            let result = await response.json()
            alert(result)
        }
    }

    // Sends edited content to the server with the posts id
    async editPost(postid, content, view) {
        let response = await fetch("/posts/"+ postid, {
            method: "PUT",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({"content": content, "view": view}),
        });
        if (response.status == 200){
            let result = await response.json()
            console.log(result);
        }
    }

    // Sends the post id to the server which then validates and deletes it
    async removePost(postid) {
        let response = await fetch("/posts/"+ postid, {
            method: "DELETE",
            headers: {
                "Content-Type": "application/json",
            },
        });
        if (response.status == 200){
            let result = await response.json()
            console.log(result)
        }else {
            alert("You cannot delete this post!");
        }
    }

    // Sorts the posts in the 'this.posts' list according to the date
    async sortPosts(sortStyle) {
        let posts = this.posts;
        if (sortStyle === "post-sort-asc") {
            posts.sort( function(a , b){
                if(a.date > b.date) {
                    return 1;
                }
                if(a.date < b.date) {
                    return -1;
                }
                return 0;
            });
        }else if (sortStyle === "post-sort-desc") {
            posts.sort( function(a , b){
                if(a.date < b.date) {
                    return 1;
                }
                if(a.date > b.date) {
                    return -1;
                }
                return 0;
            });
        }
    }
}

// A collection of the accepted friend relation for the session and the pending friend requests *for* the user 
class Friends {
    constructor() {
        this.friends = [];
        this.friendRequests = [];
    }

    async getFriends() {
        let response = await fetch("/friends");
        if (response.status == 200){
            let result = await response.json()
            this.friends = [];
            this.friendRequests = [];
            // Sorts the json reply into the different lists (either confirmed friends or friend requests)
            for (let i = 0; i <= Object.keys(result).length-1; i++) {
                if (result[i][1] === "accepted") {
                    this.friends.push(new Friend(result[i][0], result[i][1], result[i][2], result[i][3]));
                }else {
                    this.friendRequests.push(new Friend(result[i][0], result[i][1], result[i][2], result[i][3]));
                }
            }
            // Checks if the friend request list is not empty and changes the style of the friend request button to visually
            // indicate new requests  
            if (this.friendRequests.length > 0) {
                document.getElementById("friends-button").style.border = "2px solid red"
            }
            return this.friends
        }
    }

    // Sends the username of a user to the server for a initiation of a new 'pending' friend request 
    async addFriend(username) {
        let response = await fetch("/friends", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({"username": username}),
        });
        if (response.status == 200){
            let result = await response.json();
            console.log(result);
        }
        else {
            alert("Bad request meaning it's yourself, someone already in friendslist or already sendt a request")
        }
    }

    // After accepting the friend request the id is sendt to the server to confirm it. 
    async confirmFriend(friendid) {
        let response = await fetch("/friends/" + friendid, {
            method: "PUT",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify([friendid]),
        });
        if (response.status == 200){
            let result = await response.json()
            console.log(result);
            await this.getFriends()
            if (this.friendRequests.length < 1) {
                document.getElementById("friends-button").style.border = "1px solid black"
            }
        }
    }

    // Sends the id of the friend to the server where the friend relation between the friend and the session owner is deleted
    async deleteFriend(friendid) {
        let response = await fetch("/friends/" + friendid, {
            method: "DELETE",
        });
        if (response.status == 200){
            let result = await response.json()
            console.log(result);
            await this.getFriends()
            if (this.friendRequests.length < 1) {
                document.getElementById("friends-button").style.border = "1px solid black"
            }
        }
    }
}

// Initiates a Friends object, Posts object and a variable for the logged in user 
let theposts = new Posts();
let thefriends = new Friends();
let theuser;


// A function that handles the display of the posts for the user 
async function displayPosts() {
    let value = document.getElementById("select-show").value;
    let postdiv = document.getElementById("posts-board");
    postdiv.innerHTML = "";
    await theposts.getPosts();
    
    // Gets the values from the dropdown view and only displayes the posts with those criteria
    if (value === "post-show-public") { // Shows only the public posts
        for (let i = 0; i < theposts.posts.length; i++) {
            if (theposts.posts[i].view === "public") {
                postdiv.innerHTML += postStyle(theposts.posts[i]);
            }
        }
    }
    else if (value === "post-show-friend") { // Shows only the friends posts
        for (let i = 0; i < theposts.posts.length; i++) {
            if (theposts.posts[i].view === "friends") {
                postdiv.innerHTML += postStyle(theposts.posts[i]);
            }
        }
    }
    else { // Shows all the posts the user has access to
        for (let i = 0; i < theposts.posts.length; i++) {
            postdiv.innerHTML += postStyle(theposts.posts[i]);
        }
    }
    if (document.cookie.indexOf('cookieColor=') == -1) {
        document.cookie = "cookieColor=colorfull";
    }
    // Change theme is here to make sure that all the posts displayed get the correct theme that is selected 
    changeTheme(document.cookie);
}

// Basically templating the different types of posts so that the editing option for the owned posts get the needed functionality
function postStyle(post) {
    let postBlock;
    if (theuser.username == post.userid) {
        if (post.view === "public") {
            postBlock = "<div id='post_" + post.postid + "' class='postStyle'>" + 
                            "<p class='postContent'>" + post.content + "</p>" +
                            "<div class='info'>" + 
                            "<select onchange='editPostView(" + post.postid +")'>" + 
                                "<option value='public' selected>public</option>" + 
                                "<option value='friends'>friends</option>" + 
                            "</select>" + 
                            "<button onclick='editPostContent(" + post.postid + ");'><i class='fa fa-edit fa-2x'></i></button>" + 
                            "<button onclick='deletePost(" + post.postid + ");'><i class='fa fa-remove fa-2x'></i></button>" + 
                            "<p class='postDate'>" + post.date + "</p>" + 
                            "<p class='postedby'>" + post.userid + "</p>" +
                        "</div>";
        }
        else {
            postBlock = "<div id='post_" + post.postid + "' class='postStyle'>" + 
                            "<p class='postContent'>" + post.content + "</p>" +
                            "<div class='info'>" + 
                            "<select onchange='editPostView(" + post.postid +")'>" + 
                                "<option value='public'>public</option>" + 
                                "<option value='friends' selected>friends</option>" + 
                            "</select>" + 
                            "<button onclick='editPostContent(" + post.postid + ");'><i class='fa fa-edit fa-2x'></i></button>" + 
                            "<button onclick='deletePost(" + post.postid + ");'><i class='fa fa-remove fa-2x'></i></button>" + 
                            "<p class='postDate'>" + post.date + "</p>" + 
                            "<p class='postedby'>" + post.userid + "</p>" +
                        "</div>";
        }
    }
    else {
        postBlock = "<div id='post_" + post.postid + "' class='postStyle'>" + 
                        "<p class='postContent'>" + post.content + "<p>" +
                        "<div class='info'>" + 
                            "<select disabled style='-moz-appearance: none;'>" + 
                                "<option default>" + post.view + "</option>" + 
                            "</select>" + 
                            "<button style='visibility: hidden;'>Edit</button>" + 
                            "<p class='postDate'>" + post.date + "</p>" + 
                            "<p class='postedby'>" + post.userid + "</p>" +
                        "</div>";
    }
    return postBlock
}

// Is called by the 'post-send' button and users the Class Posts(...).addPost method to add a new post to the database, 
// also empties the post field and hides the form on submit
async function addAPost() {
    let postForm = document.getElementById("post-show");
    let content = document.getElementById("post-content");
    let view = document.getElementById("select-view").value;
    if (content.value == "") {
        alert("Post cannot be empty")
    }
    else {
        await theposts.addPost(content.value, String(view));
        await displayPosts();
        postForm.style.display = "none";
        content.value = "";
    }
}

// Is called every time an owner of a post changes the view option for a post
async function editPostView(id) {
    let post = document.getElementById("post_" + String(id)); //finds the post block that wants to be changed
    let content = post.firstChild.innerHTML; // leads to the content block for the post
    let view = post.getElementsByTagName("select")[0].value; // leads to the value of the select for the post 
    await theposts.editPost(id, content, view)
    await displayPosts();
}

// Is called when a user wants to edit the content of a post 
async function editPostContent(id) {
    let post = document.getElementById("post_" + String(id)); //finds the post block that wants to be changed
    let content = post.firstChild.innerHTML; // leads to the content block for the post
    let view = post.getElementsByTagName("select")[0].value; // leads to the value of the select for the post 
    let newContent = prompt("Edit the post: ", content)
    if (newContent != content && newContent != "") {
        await theposts.editPost(id, newContent, view)
        await displayPosts();
    }
}

// Is called when an owner of a post wants to delete a post
async function deletePost(id) {
    let confirmation = confirm("Are you sure you want to delete this post?");
    if (confirmation) {
        await theposts.removePost(id)
    }
    await displayPosts();
}

// Adds the confirmed friends of a user to the aside friends table and also adds new friend requests to the friend requests button
async function displayFriends() {
    await thefriends.getFriends();
    let friendlist = document.getElementById("friendlist");
    let friendRequestList = document.getElementById("fr");
    friendlist.innerHTML = "";
    friendRequestList.innerHTML = "";

    // Adds the friends to the aside table
    for (let i = 0; i < thefriends.friends.length; i++) {
        friendlist.innerHTML += "<td>" + thefriends.friends[i].username + "</td>" +
                                "<td>" + thefriends.friends[i].useremail + "</td>" +
                                "<td id='" + thefriends.friends[i].userid + "'>" +
                                    "<i class='fa fa-remove' onclick='removeFriend(this.parentNode.id);'></i>" +
                                "</td>";
    }

    // Checks if there are any friend requests and if not then shows that there are none
    if (thefriends.friendRequests.length < 1) {
        friendRequestList.innerHTML += "<div>No friendrequests</div>";
    }

    // If there are any friend requests then it adds them to the friend request button
    for (let i = 0; i < thefriends.friendRequests.length; i++) {
        friendRequestList.innerHTML += "<div id='" + thefriends.friendRequests[i].userid + "'>" + thefriends.friendRequests[i].username + 
                                            "<button class='frb' onclick='acceptFriend(this.parentNode.id)'>" +
                                                "<i class='fa fa-check'></i>" +
                                            "</button>" + 
                                            "<button class='frb' onclick='removeFriend(this.parentNode.id)'>" +
                                                "<i class='fa fa-remove'></i>" + 
                                            "</button>" +
                                        "</div>";
    }
}

// If a user accepts the friend request this triggers and the Class Friends(...).confirmFriend is used to accept the request server side,
// also removes the requests from the div
async function acceptFriend(userid) {
    let fr = document.getElementById("fr");
    await thefriends.confirmFriend(userid);
    for (let i = 0; i < fr.childNodes.length; i++) {
        if (fr.childNodes[i].id === userid) {
            fr.removeChild(fr.childNodes[i]);
        }
    }
    await displayFriends();
    await displayPosts();
}

// If a user denies the request or removes a friend, the request is removed from the database and the table
async function removeFriend(userid) {
    let fr = document.getElementById("fr");
    let confirmation = confirm("Are you sure you want to remove this friend?");
    if (confirmation) {
        await thefriends.deleteFriend(parseInt(userid));
        for (let i = 0; i < fr.childNodes.length; i++) {
            if (fr.childNodes[i].id === userid) {
                fr.removeChild(fr.childNodes[i]);
            }
        }
        await displayFriends();
        await displayPosts();
    }
}

// Makes sure that only the logged in users can search and add friends (also gets verified server side)
function enableSearch() {
    let searchinput = document.getElementById("search-input");
    if (theuser == null || theuser == "") {
        searchinput.disabled = true;
    }
    else {
        searchinput.disabled = false;
    }
}

// Removes the user searches from the and the search query from the search input
function emptySearch() {
    let searchdiv = document.getElementById("search");
    for (let i = 0; i < searchdiv.childNodes.length; i++) {
        searchdiv.removeChild(searchdiv.childNodes[i]);
    }
    searchdiv.innerHTML = '';
    document.getElementById("search-input").value = "";
}

// Is used to query the database for the users that match the search string and adds the matches to a div that displayes them
async function searchUser(string) {
    
    let search = document.getElementById("search");
    document.getElementById("search").innerHTML = "";
    
    let response = await fetch("/search?username=" + string);
    if (response.status == 200){    
        let result = await response.json();
        for (let i = 0; i <= Object.keys(result).length-1; i++) {
            search.innerHTML += "<div id='" + result[i][0] + "' onclick='addAFriend(this.id);' class='usersearch'>" + result[i][0] + "</div>"
        }
    }
}


// Sends a friend request
function addAFriend(name) {
    if (theuser != "" || theuser != null) {
        thefriends.addFriend(name);
        alert("Friend request sendt to: " + name);
    }
    else {
        alert("Not logged in");
    }
}

// Adds a user to the database
async function addUser(username, password, password2, email) {
    let response = await fetch("/register", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({username: username, password: password, password2: password2, email: email})
    });
    
    if (response.status != 200){
        alert("username already exists or username length is not between 4-20 characters");
        clearFields();
        form.style.border = "2px solid red";
        return;
    }
    else if (response.status == 200) {
        let user = await response.json();
        clearFields();
        await checkLogin();
    }
}

// Changes an existing user
async function ChangeUser(type, data, verifymessage) {
    let response = await fetch("/user", {
        method: "PUT",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({"type": type, "data": data, "verification": verifymessage}),
    });
    if (response.status == 200){
        let result = await response.json();
        console.log(result)
        document.forms["editform"]["change"].value = "";
        document.forms["editform"]["verify"].value = "";
        userEdit.style.display="none";
        await checkLogin();
    }
    else{
        if (type == "text") {
            alert("username already exists");
        }
        else if (type == "password") {
            alert("password did not meet the criteria");
        }
        else if (type == "email") {
            alert("email address is invalid");
        }
    }
}


// Deletes an existing user
async function deleteUser(verifymessage) {
    let response = await fetch("/user", {
        method: "DELETE",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({"verification": verifymessage}),
    });
    if (response.status == 200){
        let result = await response.json();
        console.log(result);
        document.forms["deleteform"]["verify"].value = "";
        await logout();
    }
    else {
        alert("Wrong password cannot delete account")
    }
}



// Is used to verify login and get login information from the server 
async function checkLogin() {
    let response = await fetch("/user")
    
    // If a user is not logged in the login form or the register form is displayed
    if (response.status == 404){
        console.log("No user logged in!")
        document.getElementById("login").style.display = "block";
        document.getElementById("app").style.display = "none";
        return
    }

    // If a user is logged in the app and function buttons are displayed, and the current logged in user information is stored  
    if (response.status == 200){
        let user = await response.json();
        theuser = new User(user.userid, user.username, user.useremail);
        document.getElementById("login").style.display = "none";
        document.getElementById("app").style.display = "block";
        document.getElementById("loggedin").innerHTML = "<p>Logged in as: " + theuser.username + "</p>";
        displayPosts();
        displayFriends();
        document.getElementById("function-buttons").style.visibility= "visible";
    }
}

// Clears the registration and login field
function clearFields() {
    document.getElementById("login-username").value = "";
    document.getElementById("login-password").value = "";
    document.getElementById("register-username").value = "";
    document.getElementById("register-password").value = "";
    document.getElementById("register-password2").value = "";
    document.getElementById("register-email").value = "";
}

// Gets the from data and sends the login information to the server, then checks if the login was successfull or not
async function loginfunc() {
    let username = document.getElementById("login-username").value;
    let password = document.getElementById("login-password").value;
    let form = document.getElementById("login");
    let app = document.getElementById("app");
    app.style.display = "none";
    let response = await fetch("/login", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({ username: username, password: password})
    });

    if (response.status != 200){
        alert("Wrong username or password!");
        form.style.border = "2px solid red"
        clearFields();
        return
    }
    let user = await response.json();
    form.style.display = "none";
    app.style.display = "block";
    clearFields();
    await checkLogin();
}

// Validates the email address
function validateEmail(email) {
    let res = /^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$/;
    return res.test(email);
}

// Verifies the user input is up to spec
function verifyInput(username, password, email) {
    if (username.length >= 4 && username.length <= 20) {
        if (password.length >= 4 && password.length <= 120) {
            if (validateEmail(email)) {
                return true;
            }
            alert("bad email not recognized as email")
            return false;
        }
        alert("bad password must be 4 to 120 characters")
        return false;
    }
    alert("bad username must be 4 to 20 characters")
    return false;
}

// Gets the form data for the reqistration form and if the username is not in use and valid then the user id logged in 
async function registerfunc() {
    let username = document.getElementById("register-username").value;
    let password = document.getElementById("register-password").value;
    let password2 = document.getElementById("register-password2").value;
    let email = document.getElementById("register-email").value;
    let form = document.getElementById("login");
    let app = document.getElementById("app");
    app.style.display = "none";
    if (password == password2) {
        if (verifyInput(username, password, email) == true) {
            addUser(username, password, password2, email);
            form.style.display = "none";
            app.style.display = "block";
            clearFields();
        }
        else {
            form.style.border = "2px solid red";
            clearFields();
        }
        
    } else {
        alert("Passwords do not match");
        form.style.border = "2px solid red";
        clearFields();
        return;
    }
    
}

// Logs out the user and removes returns the user to the login screen
async function logout() {
    document.getElementById("fr").innerHTML = "";
    document.getElementById("search").innerHTML = "";
    document.getElementById("friends-button").style.border = "1px solid black";
    emptySearch()
    let response = await fetch("/logout")
    if (response.status != 200){
        alert("Failed to log out!");
        return
    }
    theuser = null;
    document.getElementById("login").style.display = "block";
    document.getElementById("app").style.display = "none";
    document.getElementById("function-buttons").style.visibility= "hidden";
}

// Is used to display different forms based on which information the user wants to edit on itself dependent on the which settings are chosen
function editUser(type) {
    let userEdit = document.getElementById("edit-user-info")
    userEdit.style.display = "block";
    let frame;
    if (type === "username") {
        frame = "<form name='editform' action='javascript:void(0);' onsubmit='verifyUser();'>" + 
                        "<label for='change'>Edit username: </label>" +
                        "<input id='userEdit' type='text' name='change' value='" + theuser.username +"' placeholder='Enter new username...' />" +
                        "<input type='password' name='verify' placeholder='Enter password...' />" +
                        "<input type='submit' value='Verify' />" +
                    "</form>"
    }
    else if (type === "password") {
        frame = "<form name='editform' action='javascript:void(0);' onsubmit='verifyUser();'>" + 
                        "<label for='change'>Edit password: </label>" +
                        "<input id='userEdit' type='password' name='change' placeholder='Enter new password...' />" +
                        "<input type='password' name='reconfirm' placeholder='Confirm new password...' />" +
                        "<input type='password' name='verify' placeholder='Enter old password...' />" +
                        "<input type='submit' value='Verify' />" +
                    "</form>"
        
    }
    else if (type === "email") {
        frame = "<form name='editform' action='javascript:void(0);' onsubmit='verifyUser();'>" + 
                        "<label for='change'>Edit email: </label>" +
                        "<input id='userEdit' type='email' name='change' value='" + theuser.useremail +"' placeholder='Enter new email...' />" +
                        "<input type='password' name='verify' placeholder='Enter old password...' />" +
                        "<input type='submit' value='Verify' />" +
                    "</form>"
    }

    userEdit.innerHTML = frame;
}



function doublecheckPasswords(password1, password2) {
    if (password1 != password2) {
        alert("Passwords do not match!")
        return false;
    }
    return true;
}

// Is used to verify the different forms and send the information to the server
async function verifyUser() {
    let userEdit = document.getElementById("edit-user-info");
    let data = document.forms["editform"]["change"].value;
    let verifymessage = document.forms["editform"]["verify"].value;
    let type = document.getElementById("userEdit").type;
    let confirming;
    let ask = confirm("Are you sure you want to edit the " + String(type));

    // If the user wants to change the password, then the second password field has to be checked to make sure both new passwords are equal
    if (type == "password") {
        confirming = document.forms["editform"]["reconfirm"].value;
        if (!doublecheckPasswords(data, confirming)) {
            ask == false;
        }
        document.forms["editform"]["reconfirm"].value = "";
    }

    // If user has confirmed and everything is OK then changes the user
    if (ask) {
        ChangeUser(type, data, verifymessage);
        document.forms["editform"]["change"].value = "";
        document.forms["editform"]["verify"].value = "";
        userEdit.style.display="none";
    }
    else {
        document.forms["editform"]["change"].value = "";
        document.forms["editform"]["verify"].value = "";
    }
}

// Displayes the delete account option
function deleteAccount() {
    let userEdit = document.getElementById("edit-user-info")
    userEdit.style.display = "block";
    let frame = "<form name='deleteform' action='javascript:void(0);' onsubmit='removeUser();'>" + 
                        "<input type='password' name='verify' placeholder='Enter password...' />" +
                        "<input type='submit' value='Verify' />" +
                    "</form>"
    userEdit.innerHTML = frame;
}

// Verifies the user before requestin account deletion
async function removeUser() {
    let userEdit = document.getElementById("edit-user-info")
    let verifymessage = document.forms["deleteform"]["verify"].value;
    let confirmation = confirm("Are you sure you want to delete the account?");
    if (confirmation) {
        deleteUser(verifymessage);
    }
    userEdit.style.display="none";
}

// Changes the overall theme based on the browser cookie
function changeTheme(type) {
    if (type === "cookieColor=murky") {
        document.getElementsByTagName("body")[0].style.backgroundImage = "linear-gradient(to bottom right, #5D5F60, #8A9EA1)"
        document.getElementsByTagName("header")[0].style.backgroundColor = "#213130"
        document.getElementsByTagName("aside")[0].style.backgroundColor = "#5D5F60"
        document.getElementById("post-frame").style.backgroundColor = "#8A9EA1"
        document.getElementById("post-form").style.backgroundColor = "#213130"
        let poststyle = document.getElementsByClassName("postStyle");
        for (let i = 0; i < poststyle.length; i++){
            poststyle[i].style.backgroundColor = "#213130"
        }
    }
    else if (type === "cookieColor=colorfull") {
        document.getElementsByTagName("body")[0].style.backgroundImage = "linear-gradient(to bottom right, #005377, #06A77D)"
        document.getElementsByTagName("header")[0].style.backgroundColor = "#052F5F"
        document.getElementsByTagName("aside")[0].style.backgroundColor = "#06A77D"
        document.getElementById("post-frame").style.backgroundColor = "#005377"
        document.getElementById("post-form").style.backgroundColor = "#052F5F"
        let poststyle = document.getElementsByClassName("postStyle");
        for (let i = 0; i < poststyle.length; i++){
            poststyle[i].style.backgroundColor = "#052F5F"
        }
    }
}

// Creates the cookie if it does not exist or changes it which gets used to choose the theme
function setColor() {
    if (document.cookie.indexOf('cookieColor=') == -1) {
        document.cookie = "cookieColor=colorfull";
    }
    else if (document.cookie == "cookieColor=murky") {
        document.cookie = "cookieColor=colorfull";
    }
    else if (document.cookie == "cookieColor=colorfull") {
        document.cookie = "cookieColor=murky";
    }
    changeTheme(document.cookie);
}