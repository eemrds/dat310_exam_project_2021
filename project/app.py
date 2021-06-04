
from setup_db import *

from flask import Flask, request, redirect, url_for, flash, session, g, abort
from werkzeug.security import generate_password_hash, check_password_hash

import sqlite3, json
import datetime
import re

app = Flask(__name__)
app.debug = True
app.secret_key = 'some_secret'


@app.before_request
def make_session_permanent():
    session.permanent = True
    app.permanent_session_lifetime = datetime.timedelta(minutes=3)


def get_db():
    if not hasattr(g, "_database"):
        print("create connection")
        g._database = sqlite3.connect("database.db")
    return g._database


@app.teardown_appcontext
def teardown_db(error):
    """Closes the database at the end of the request."""
    db = getattr(g, '_database', None)
    if db is not None:
        print("close connection")
        db.close()

# Validates the login information
def valid_login(username, password):
    """Checks if username-password combination is valid."""
    conn = get_db()
    hash = get_hash_for_login(conn, username)
    if hash != None:
        return check_password_hash(hash, password)
    return False

# checks if the username exists
def username_exists_check(username):
    '''Checks if a username exists'''
    conn = get_db()
    if get_user_by_name(conn, username)["username"] != -1: 
        print("username already exists")
        return False
    return True

# validates the length of the username
def validate_username(username):
    '''Validates the username length'''
    if len(username) < 4 or len(username) > 20:
        print("username too short")
        return False
    return True

# validates the length of the password
def validate_password_length(password):
    if len(password) < 4 or len(password) > 120:
        print("username too short")
        return False
    print("password too short or too long")
    return True

# Checks the email using regex to see if it is a valid email
def validate_email(email):
    regex = '^(\w|\.|\_|\-)+[@](\w|\_|\-|\.)+[.]\w{2,3}$'
    if re.search(regex, email):
        return True
    print("invalid email")
    return False


@app.route("/")
def index():
    return app.send_static_file("index.html")

# Validates and loggs in a user if it exists in the database
@app.route("/login", methods=["POST"])
def login():
    '''
    Validates the login information and then creates a session for the user
    '''
    data = request.get_json()
    if not valid_login(data.get("username", ""), data.get("password", "")):
        abort(404)
    conn = get_db()
    user = get_user_by_name(conn,data["username"])
    session["userid"] = user["userid"]
    session["username"] = user["username"]
    print(f"user {session['username']} logged in")
    return json.dumps(user)

# Registers a username if the username is not taken and the information given is validated
@app.route("/register", methods=["POST"])
def register():
    '''
    Checks if both registration passwords match and if the username does not exist, then adds a new user to the database
    '''
    data = request.get_json()
    conn = get_db()
    print(data)
    if data["password"] == data["password2"]:
        if validate_username(data["username"]) == False or username_exists_check(data["username"]) == False: 
            print("aborted: username too short or too long or already exists")
            abort(404)
        elif validate_password_length(data["password"]) == False: 
            print("aborted: password too short or too long")
            abort(404)
        else:
            add_user(conn, data["username"], generate_password_hash(data["password"]), data["email"])
            user = get_user_by_name(conn, data["username"])
            session["userid"] = user["userid"]
            session["username"] = user["username"]
            return json.dumps(user)
    return

# Logs out a user by removing the session
@app.route("/logout")
def logout():
    '''Logs out the user if a user is logged in'''
    try:
        session.pop("userid")
    except KeyError as e:
        print(e)
    return json.dumps("OK")


'''
REST USER
'''

# Searches the database for the given queries and returns a list containing the matches
@app.route("/search", methods=["GET"])
def searchUser():
    '''Searches the database for the users starting with the given letters and returns a list of those users'''
    conn = get_db()
    search = request.args.get("username", None)
    usermatches = check_for_user(conn, search)
    if len(usermatches) == 0:
        return json.dumps([["No match found"]])
    return json.dumps(usermatches)

# Gets the user information from the session id
@app.route("/user", methods=["GET"])
def get_User():
    '''Gets the info for the logged in user'''
    userid = session.get("userid", None)
    if userid == None:
        abort(404)
    conn = get_db()
    user = get_user_by_id(conn,userid)
    return json.dumps(user)

# Adds a new user to the database if the name does not already exist and is not empty
@app.route("/user", methods=["POST"])
def addUser():
    '''Creates a user by checking if the username is in the database already or empty'''
    conn = get_db()
    userinfo = request.get_json()
    if userinfo["username"] != "" and get_user_by_name(conn, userinfo["username"]) == -1:
        add_user(conn, userinfo["username"], userinfo["userpasswordhash"], userinfo["useremail"])
    return json.dumps("created a new user")

# Edits user info if the user is the one logged in and checks if the new username exists or is too long / too short
@app.route("/user", methods=["PUT"])
def updateUser():
    '''Updates an existing user'''
    conn = get_db()
    userinfo = request.get_json()
    sessionid = session.get("userid", None)
    user = get_user_by_id(conn, sessionid)
    verified = valid_login(user["username"], userinfo["verification"])
    if verified == True:
        if userinfo["type"] == "text": # Checks the edited username
            if validate_username(userinfo["data"]) == False or username_exists_check(userinfo["data"]) == False: 
                abort(404)
                return json.dumps("aborted: username too short or too long or already exists")
            else: 
                update_username(conn, sessionid, userinfo["data"])
                return json.dumps("updated username")
        elif userinfo["type"] == "password": # Checks the edited password
            if validate_password_length(userinfo["data"]):
                update_userpasshash(conn, sessionid, userinfo["data"])
                return json.dumps("updated password")
            else:
                abort(404, )
                return json.dumps("password too short or too long or")
        elif userinfo["type"] == "email": # Checks the edited email
            if validate_email(userinfo["data"]):
                update_useremail(conn, sessionid, userinfo["data"])
                return json.dumps("updated useremail")
            else:
                abort(404)
                return json.dumps("email is invalid")
        abort(403)
        return json.dumps("blablabla")
    return json.dumps("something went wrong")

# Deletes a user if the user is the one logged in
@app.route("/user", methods=["DELETE"])
def deleteUser():
    '''Deletes an existing user'''
    conn = get_db()
    userinfo = request.get_json()
    userid = session.get("userid", None)
    if userid != None and valid_login(get_user_by_id(conn, userid)["username"], userinfo["verification"]):
        delete_user(conn, session.get("userid", None))
        return json.dumps(f"deleted user: {userid}")
    abort(404)
    return json.dumps("Could not delete account")


'''
REST POST
'''

# Retrieves the posts for a user, the friends and the public posts from the database
@app.route("/posts", methods=["GET"])
def getposts():
    ''' Gets the posts that the user has access to (if not logged in the default will be the public posts)'''
    conn = get_db()
    if session["username"] == None:
        public_posts = get_public_posts(conn)
        return json.dumps(public_posts)
    else:
        posts = []
        friendposts = []
        publicposts = []
        friends = get_friends(conn, session.get("userid"))
        for friend in friends:
            if friend[1] != "pending":
                friendposts.append(get_posts(conn, friend[0])) # Adding the friends posts
        publicposts.append(get_public_posts(conn)) # Adding the public posts
        friendposts.append(get_posts(conn, session.get("userid"))) # Adding the users own posts
        for i in range(len(friendposts)):
            for j in range(len(friendposts[i])):
                posts.append(friendposts[i][j])
        for i in range(len(publicposts)):
            for j in range(len(publicposts[i])):
                posts.append(publicposts[i][j])
        return json.dumps(posts)
    return json.dumps("got addresses")

# Adds a new post to the database and checks to see if it is empty or not
@app.route("/posts", methods=["POST"])
def addPost():
    '''Adds a new post'''
    conn = get_db()
    post = request.get_json()
    print(post)
    if post["content"] != "":
        add_post(conn, session.get("userid", None), post["content"], f"{datetime.datetime.utcnow().replace(microsecond=0)}", post["view"])
        return json.dumps(f"added post with content: {post['content']}")
    return json.dumps(f"post is empty")

# Edits a post if the user owns it and updates the time
@app.route("/posts/<int:postid>", methods=["PUT"])
def editPost(postid):
    '''Edits an existing post'''
    conn = get_db()
    post = request.get_json()
    if get_a_post(conn, postid) == session.get("userid", None) and post["content"] != "": # If the user owns the post
            update_post(conn, postid, post["content"], f"{datetime.datetime.utcnow().replace(microsecond=0)}", post["view"])
            return json.dumps(f"updated post {postid}")
    abort(403) # if it is not the users post
    return json.dumps("Post cannot be empty")
    
# Deletes a post if the user owns it
@app.route("/posts/<int:postid>", methods=["DELETE"])
def deletePost(postid):
    '''Deletes a post'''
    conn = get_db()
    post = get_posts(conn, session.get("userid"))
    if get_a_post(conn, postid) == session.get("userid", None): # If the user owns the post
        delete_post(conn, postid)
    else:
       abort(403)
    return json.dumps(f"deleted post {postid}")


'''
REST FRIENDS
'''

# Retreives the friends and the friend requests for the logged in user from the database
@app.route("/friends", methods=["GET"])
def getFriends():
    '''Get the friends of the user'''
    conn = get_db()
    userid = session.get("userid")
    friendids = get_friends(conn, userid)
    users = []
    for friend in friendids:
        userinfo = get_user_by_id(conn, friend[0])
        users.append([friend[0], friend[1], userinfo["username"], userinfo["useremail"]])
    print(users)
    return json.dumps(users)

# Tries to send a friend request, if the user already has a request or has sendt one to that user it is aborted
@app.route("/friends", methods=["POST"])
def addFriend():
    '''Adds a friend relation'''
    conn = get_db()
    friendinfo = request.get_json()
    print(get_all_friends(conn, session.get("userid", None)))
    if get_user_by_name(conn, friendinfo["username"]) != "" and session.get("username", None) != None:
        # Aborts if the user tries to add a friend already in the friendlist
        friendid = get_user_by_name(conn, friendinfo["username"])["userid"]
        friends = get_all_friends(conn, session.get("userid", None))
        for i in range(len(get_all_friends(conn, session.get("userid", None)))):
            if friends[i][0] == friendid:
                abort(403)
        # Aborts if the user tries to add itself
        if friendinfo["username"] == session.get("username", None):
            abort(403)
        if session.get("userid") not in get_friends(conn, get_user_by_name(conn, friendinfo["username"])["userid"]):
            add_friend(conn, session.get("userid"), get_user_by_name(conn, friendinfo["username"])["userid"])
            return json.dumps(f'added friend request between {session.get("username")} and {friendinfo["username"]}')
        return json.dumps(f'Friend already in friend list')
    return json.dumps(f'User does not exist')

# Updates the friend request to accepted 
@app.route("/friends/<int:friendid>", methods=["PUT"])
def updateFriend(friendid):
    '''Updated a friend relation'''
    conn = get_db()
    friendid = request.get_json()
    update_friends(conn, friendid[0], session.get("userid"))
    return json.dumps(f'accepted friend request between {session.get("userid")} and {friendid}')

# Deletes a friend request or a relationship between friendid and the user
@app.route("/friends/<int:friendid>", methods=["DELETE"])
def deleteFriend(friendid):
    '''Deleted a friend relation'''
    conn = get_db()
    delete_friend(conn, friendid, session.get("userid"))
    return json.dumps(f'deleted friend relation between {session.get("userid")} and {friendid}')

if __name__ == "__main__":
    app.run()