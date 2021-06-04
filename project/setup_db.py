import sqlite3
from werkzeug.security import generate_password_hash , check_password_hash
import datetime
from time import sleep

def create_users_table(conn):
    '''
    Creates the user table and stores [userid, username, userpasshash, useremail]
    
    :param conn: Database connection
    
    :return: Creates the table for the database 
    :rtype: None
    '''
    cur = conn.cursor()
    try:
        sql = ("CREATE TABLE users ("
               "userid INTEGER, "
               "username VARCHAR(20) NOT NULL, "
               "userpasshash VARCHAR(120) NOT NULL, "
               "useremail VARCHAR(120), "
               "PRIMARY KEY(userid) "
               "UNIQUE(username))")
        cur.execute(sql)
        conn.commit
    except sqlite3.Error as err:
        print(f"Error in users: {err}")
    else:
        print("Table 'users' created")
    finally:
        cur.close()

def create_friends_table(conn):
    '''
    Creates a table where the relation between users that are friends are stored.
    |[userid of the sender] | [userid of the receiver] | [pending or accepted]) | (deleted if declined)

    :param conn: Database connection
    
    :return: Creates the table for the database 
    :rtype: None
    '''
    cur = conn.cursor()
    try:
        sql = ("CREATE TABLE friends ("
                "senderid INTEGER, "
                "receiverid INTEGER, "
                "accepted REAL)"
                )
        cur.execute(sql)
        conn.commit()
    except sqlite3.Error as err:
        print(f"Error in friends table: {err}")
    else:
        print("Table 'friends' created")
    finally:
        cur.close()


def create_posts_table(conn):
    '''
    Creates the post table which stores [postid, userid, content, date, view]
    :param conn: Database connection
    
    :return: Creates the table for the database 
    :rtype: None
    '''
    
    cur = conn.cursor()
    try:
        sql = ("CREATE TABLE posts ("
                "postid INTEGER, "
                "userid INTEGER, "
                "content VARCHAR(1024) NOT NULL, "
                "date NUMERIC, "
                "view NUMERIC,"
                "PRIMARY KEY(postid))"
                )
        cur.execute(sql)
        conn.commit()
    except sqlite3.Error as err:
        print(f"Error in posts: {err}")
    else:
        print("Table 'posts' created")
    finally:
        cur.close()


'''
ADDING DATA TO A TABLE
'''


def add_user(conn, username, userpasshash, useremail):
    '''
    Adds a new user to the users table
    
        :param conn: Database connection
        :param username: The username that will be linked to the users account
        :type username: str
        :param userpasshash: The hash of the password for the users account
        :type userpasshash: str
        :param useremail: The email that will be linked to the users account
        :type usermail: str

    :return: The id given to the user or if error: -1
    :rtype: int
    '''
    
    
    cur = conn.cursor()
    try:
        sql = ("INSERT INTO users (username, userpasshash, useremail) VALUES (?,?,?)")
        cur.execute(sql, (username, userpasshash, useremail))
        conn.commit()
    except sqlite3.Error as err:
        print(f"Error adding a user to the database: {err}")
        return -1
    else:
        print(f"User {username} added")
        return cur.lastrowid
    finally:
        cur.close()


def add_friend(conn, senderid, receiverid, accepted="pending"):
    '''
    Adds a new friend relationship request to the friends table
    
    :param conn: Database connection
    :param senderid: The id of the user which initiated the friendrequest
        :type senderid: int or str
    :param receiverid: The id of the user which receives and has to accept the request
        :type receiverid: int or str
    :param accepted: The status of the relation. Defaults to "pending"
        :type accepted: str

    :return: The id of the table or -1 if error
    :rtype: int 
    '''
    cur = conn.cursor()
    try:
        sql = ("INSERT INTO friends (senderid, receiverid, accepted) VALUES (?,?,?)")
        cur.execute(sql, (senderid, receiverid, accepted))
        conn.commit()
        
    except sqlite3.Error as err:
        print(f"Error in adding a new friend request to the friends table: {err}")
        return -1
    else:
        print(f"user {senderid} sendt a friend request to {receiverid}")
        return cur.lastrowid
    finally:
        cur.close()


def add_post(conn, userid, content, date, view):
    '''
    Adds a new post to the 'posts' table
    
    :param conn: Database connection
    :param userid: the userid of the one who wrote the post
        :type userid: int or str
    :param content: The content of the post
        :type content: str
    :param date: The date of which the post was written
        :type date: datetime
    :param view: The scope of the post (who can view it)
        :type view: str

    :return: 1 or -1 if error
    :rtype: int
    '''
    cur = conn.cursor()
    try:
        sql = ("INSERT INTO posts (userid, content, date, view) VALUES (?,?,?,?)")
        cur.execute(sql, (userid, content, date, view))
        conn.commit()
    except sqlite3.Error as err:
        print(f"Error adding a post to the posts database: {err}")
        return -1
    else:
        print(f"User {userid} added a new post")
        return 1
    finally:
        cur.close()
        

'''
GETTING TABLE DATA
'''

def check_for_user(conn, username):
    '''
    Checks for users starting with similar names (case insensitive)
    
    :param conn: Database connection
    :param username: The search string for finding the user in the database
        :type username: str

    :return: A nested list of usernames with useremail
    :rtype: list
    '''
    cur = conn.cursor()
    try:
        users = []
        sql = ("SELECT  username, useremail FROM users WHERE username LIKE ? COLLATE NOCASE")
        userstring = f"{username}%"
        cur.execute(sql, (userstring,))
        for (username, useremail) in cur:
            users.append([username, useremail])
        return users
    except sqlite3.Error as err:
        print(f"Error when getting the users password hash: {err}")
    else:
        print("users information returned")
    finally:
        cur.close()


def get_user_by_name(conn, username):
    """
    Get user details by entering the username.
    
    :param conn: Database connection
    :param username: The username of the user
        :type username: str
    
    :return: A dictionary containing the userdetails for the username
    :rtype: dict
    """
    cur = conn.cursor()
    try:
        sql = ("SELECT userid, username, useremail FROM users WHERE username = ?")
        cur.execute(sql, (username,))
        for row in cur:
            (id, username, useremail) = row
            return {
                "username": username,
                "userid": id,
                "useremail": useremail
            }
        else:
            #user does not exist
            return {
                "username": -1
            }
    except sqlite3.Error as err:
        print("Error: {}".format(err))
    finally:
        cur.close()

def get_user_by_id(conn, userid):
    """
    Get user details for the user by searching on the userid.
    
    :param conn: Database connection
    :param userid: The id of the user
        :type userid: int
    
    :return: A dictionary containing the userdetails for the username
    :rtype: dict
    """
    cur = conn.cursor()
    try:
        sql = ("SELECT userid, username, useremail FROM users WHERE userid = ?")
        cur.execute(sql, (userid,))
        for row in cur:
            (id, username, useremail) = row
            return {
                "username": username,
                "userid": id,
                "useremail": useremail
            }
        else:
            #user does not exist
            return {
                "username": None,
                "userid": None,
                "useremail": None
            }
    except sqlite3.Error as err:
        print("Error: {}".format(err))
    finally:
        cur.close()


def get_hash_for_login(conn, username):
    """
    Get the users password hash from entering the username.
    
    :param conn: database connection
    :param username: The username of the user
        :type username: str

    :return: The users password hash
    :rtype: str
    """
    cur = conn.cursor()
    try:
        sql = ("SELECT userpasshash FROM users WHERE username=?")
        cur.execute(sql, (username,))
        for row in cur:
            (userpasshash,) = row
            return userpasshash
        else:
            return None
    except sqlite3.Error as err:
        print(f"Error when getting the users password hash: {err}")
    finally:
        cur.close()

def get_friends(conn, userid):
    '''
    Getting the friends list information for a user that only contains the users friends and friendrequests **to** the user

    :param conn: Database connection
    :param userid: The id of the user you want the friends for

    :return: a double nested list with the friends in one list and the requests in the other
    :rtype: list  
    '''
    cur = conn.cursor()
    try:
        friends = []
        sql = ("SELECT receiverid, accepted FROM friends WHERE senderid = ? AND accepted = ?")
        cur.execute(sql, (userid, "accepted"))
        for (receiverid, accepted) in cur:
            friends.append([receiverid, accepted])
        sql2 = ("SELECT senderid, accepted FROM friends WHERE receiverid = ? AND accepted = ?")
        cur.execute(sql2, (userid, "pending"))
        for (receiverid, accepted) in cur:
            friends.append([receiverid, accepted])
        return friends
    except sqlite3.Error as err:
        print(f"Error in getting the friends for user {userid}: {err}")
    else:
        print(f"friendslist for user {userid} returned")
    finally:
        cur.close()


def get_all_friends(conn, userid):
    '''
    Getting the friends list information for a user that contains the users friends and friendrequests **to and from** the user

    :param conn: Database connection
    :param userid: The id of the user you want the friends for

    :return: a double nested list with the friends in one list and the requests in the other
    :rtype: list 
    '''
    cur = conn.cursor()
    try:
        friends = []
        sql = ("SELECT receiverid, accepted FROM friends WHERE senderid = ?")
        cur.execute(sql, (userid,))
        for (receiverid, accepted) in cur:
            friends.append([receiverid, accepted])
        sql2 = ("SELECT senderid, accepted FROM friends WHERE receiverid = ? AND accepted = ?")
        cur.execute(sql2, (userid, "pending"))
        for (receiverid, accepted) in cur:
            friends.append([receiverid, accepted])
        return friends
    except sqlite3.Error as err:
        print(f"Error in getting the friends for user {userid}: {err}")
    else:
        print(f"friendslist for user {userid} returned")
    finally:
        cur.close()



def get_posts(conn, userid):
    '''
    Getting the posts by a specific user that can only be seen by the friends
    
    :param conn: Database connection
    :param userid: The id of the user
        :type userid: int

    :return: A nested list of posts from a user
    :rtype: list
    '''
    cur = conn.cursor()
    posts = []
    try:
        sql = ("SELECT postid, content, date, view  FROM posts WHERE userid = ? AND view = ?")
        cur.execute(sql, (userid, "friends"))
        for (postid, content, date, view) in cur:
            posts.append([postid, get_user_by_id(conn, userid)["username"], content, date, view])
        return posts
    except sqlite3.Error as err:
        print(f"Error in getting the posts by the user {userid}: {err}")
    else:
        print(f"posts by user {userid} returned")
    finally:
        cur.close()


def get_public_posts(conn):
    '''
    Getting the public post from the database
    
    :param conn: Database connection

    :return: A nested list of posts where the view scope is public
    :rtype: list
    '''
    cur = conn.cursor()
    try:
        public = []
        sql = ("SELECT postid, userid, content, date, view FROM posts WHERE view = ?")
        cur.execute(sql, ('public',))
        for (postid, userid, content, date, view) in cur:
            public.append([postid, get_user_by_id(conn, userid)["username"], content, date, view])
        return public
    except sqlite3.Error as err:
        print(f"Error in getting the public posts")
    else:
        print(f"public posts has been returned")
    finally:
        cur.close()


def get_a_post(conn, postid):
    '''
    Getting the ownerid for a specific post
    
    :param conn: Database connection
    :param postid: The id of the post in question
        :type postid: int

    :return: The userid of the post owner
    :rtype: int
    '''
    cur = conn.cursor()
    try:
        sql = ("SELECT userid FROM posts WHERE postid = ?")
        cur.execute(sql, (postid,))
        for (userid,) in cur:
            return userid
    except sqlite3.Error as err:
        print(f"Error in getting the posts{postid}: {err}")
    else:
        print(f"postid returned")
    finally:
        cur.close()


'''
UPDATING TABLE DATA
'''

def update_username(conn, userid, username):
    '''
    Updates the username of a user
    
    :param conn: Database connection
    :param userid: The id of the user
        :type userid: int
    :param username: The new username that will be given to a specific user
        :type username: str

    :return: Nothing if everything went fine
    '''
    cur = conn.cursor()
    try:
        sql = ("UPDATE users SET username = ? WHERE userid = ?;")
        cur.execute(sql, (username, userid))
        conn.commit()
    except sqlite3.Error as err:
        print(f"Error: {err}")
        return -1
    else:
        print(f"user {username} updated")
        return None
    finally:
        cur.close()


def update_userpasshash(conn, userid, password):
    '''
    Updates the userpasshash in the database
    
    :param conn: Database connection
    :param userid: The id of the user
        :type userid: int
    :param password: The new password hash that will be given to a specific user
        :type password: str

    :return: Nothing if everything went fine
    '''
    cur = conn.cursor()
    try:
        sql = ("UPDATE users SET userpasshash = ? WHERE userid = ?;")
        cur.execute(sql, (generate_password_hash(password), userid))
        conn.commit()
    except sqlite3.Error as err:
        print(f"Error: {err}")
        return -1
    else:
        print(f"user password updated")
        return None
    finally:
        cur.close()


def update_useremail(conn, userid, useremail):
    '''
    Updates the useremail in the database
    
    :param conn: Database connection
    :param userid: The id of the user
        :type userid: int
    :param useremail: The new email that will be given to a specific user
        :type useremail: str

    :return: Nothing if everything went fine
    '''
    cur = conn.cursor()
    try:
        sql = ("UPDATE users SET useremail = ? WHERE userid = ?;")
        cur.execute(sql, (useremail, userid))
        conn.commit()
    except sqlite3.Error as err:
        print(f"Error: {err}")
        return -1
    else:
        print(f"user email updated")
        return None
    finally:
        cur.close()



def update_friends(conn, senders_userid, reciever_userid):
    '''
    Updates a users friend request from pending to accepted in the database. Also adds a new row into the friends table where the first column has the receiverid and the second column has the senderid
    
    :param conn: Database connection
    :param senders_userid: The userid of the one who initiated the relation
        :type senders_userid:  int
    :param receiver_userid: The userid of the one who received the request and is updating the status to 'accepted'
        :type receiver_userid: int

    :return: Nothing if everything went fine
    '''
    #example
    #|senderid|recieverid|accepted  |        (after accepted)        |senderid|recieverid|accepted  |
    #--------------------------------            --->                --------------------------------
    #|1       |2         |"pending" |                                |1       |2         |"accepted"|
    #                                                                |2       |1         |"accepted"|
    cur = conn.cursor()
    try:
        sql = ("UPDATE friends SET accepted = ? WHERE senderid = ? AND receiverid = ?;")
        cur.execute(sql, ('accepted', senders_userid, reciever_userid))
        conn.commit()
        sql2 = ("INSERT INTO friends (senderid, receiverid, accepted) VALUES (?,?,?)")
        cur.execute(sql2, (reciever_userid, senders_userid, "accepted"))
        conn.commit()
    except sqlite3.Error as err:
        print(f"Error while updating the friends table: {err}")
        return -1
    else:
        print(f"updated the friendslist for users {senders_userid} and {reciever_userid} to accepted")
        return None
    finally:
        cur.close()


def update_post(conn, postid, content, date, view):
    '''
    Updates a users posts in the database
    
    :param conn: Database connection
    :param postid: The id of the post that is to be edited
        :type postid: int
    :param content: The new content for the post
        :type content: str
    :param date: The new date that is the time of update
        :type date: datetime
    :param view: The new view scope for the post
        :type view: str

    :return: Nothing if everything went fine
    '''
    cur = conn.cursor()
    try:
        sql = ("UPDATE posts SET content = ?, date = ?, view = ? WHERE postid = ?;")
        cur.execute(sql, (content, date, view, postid))
        conn.commit()
    except sqlite3.Error as err:
        print(f"Error while updating the posts table: {err}")
        return -1
    else:
        print(f"updated the post with id {postid}")
        return None
    finally:
        cur.close()


'''
DELETING TABLE DATA
'''


def delete_user(conn, userid):
    '''
    Deletes a user (also deletes posts and friend relations) from the database
    
    :param conn: Database connection
    :param userid: The id of the user that is to be deleted
        :type userid: int

    :return: Nothing if everything went fine
    '''
    cur = conn.cursor()
    try:
        #deletes the user
        sql = ("DELETE FROM users WHERE userid = ?;")
        cur.execute(sql, (userid,))
        conn.commit()
        #deletes the posts
        sql = ("DELETE FROM posts WHERE userid = ?;")
        cur.execute(sql, (userid,))
        conn.commit()
        #deletes the friend relations
        sql = ("DELETE FROM friends WHERE senderid = ? OR receiverid = ?;")
        cur.execute(sql, (userid, userid))
        conn.commit()
    except sqlite3.Error as err:
        print(f"Error: {err}")
        return -1
    else:
        print(f"DELETED user with userid {userid}")
        return None
    finally:
        cur.close()


def delete_friend(conn, friendid, selfid):
    '''
    Deletes a friend relation from the database
    
    :param conn: Database connection
    :param friendid: The id of user you want to remove
        :type friendid: int
    :param selfid: Your user id
        :type selfid: int

    :return: Nothing if everything went fine
    '''
    cur = conn.cursor()
    print("SELFID: ", selfid)
    print("Receiverid: ", friendid)
    try:
        sql = ("DELETE FROM friends WHERE (senderid = ? AND receiverid = ?);")
        cur.execute(sql, (friendid, selfid))
        conn.commit()
        sql2 = ("DELETE FROM friends WHERE (senderid = ? AND receiverid = ?);")
        cur.execute(sql2, (selfid, friendid))
        conn.commit()
    except sqlite3.Error as err:
        print(f"Error while deleting a friend: {err}")
        return -1
    else:
        print(f"DELETED friendrelation between users {friendid} and {selfid}")
        return None
    finally:
        cur.close()


def delete_post(conn, postid):
    '''
    Deletes a owners post
    
    :param conn: Database connection
    :param postid: The id of the post that is to be deleted
        :type postid: int

    :return: Nothing if everything went fine
    '''
    cur = conn.cursor()
    try:
        sql = ("DELETE FROM posts WHERE postid = ?;")
        cur.execute(sql, (postid,))
        conn.commit()
    except sqlite3.Error as err:
        print(f"Error while deleting a post: {err}")
        return -1
    else:
        print(f"DELETED post with postid {postid}")
        return None
    finally:
        cur.close()




if __name__ == "__main__":
    try:
        conn = sqlite3.connect("database.db")
    except sqlite3.Error as err:
        print(err)
    else:
        create_users_table(conn)
        create_friends_table(conn)
        create_posts_table(conn)

        #adding default users
        add_user(conn, "Erik", generate_password_hash("erik12345"), "erik@mail.com")
        add_user(conn, "Eirik", generate_password_hash("eirik12345"), "eirik@mail.com")
        add_user(conn, "Steinar", generate_password_hash("steinar12345"), "steinar@mail.com")
        add_user(conn, "Aksel", generate_password_hash("aksel12345"), "aksel@mail.com")

        #adding default friendships
        add_friend(conn, 1, 2)
        add_friend(conn, 2, 3)
        add_friend(conn, 4, 2)
        update_friends(conn, 1, 2)
        update_friends(conn, 2, 3)

        #adding default posts with a 1 second time interval inbetween each one 
        add_post(conn, 1, "First post!", f"{datetime.datetime.utcnow().replace(microsecond=0)}", "public")
        sleep(1)
        add_post(conn, 1, "Second post!", f"{datetime.datetime.utcnow().replace(microsecond=0)}", "public")
        sleep(1)
        add_post(conn, 1, "Steinar cannot see this (only Erik and Eirik)", f"{datetime.datetime.utcnow().replace(microsecond=0)}", "friends")
        sleep(1)
        add_post(conn, 1, "Steinar cannot see this either (only Erik and Eirik)", f"{datetime.datetime.utcnow().replace(microsecond=0)}", "friends")
        sleep(1)
        add_post(conn, 3, "Only Eirik and Steinar can see this", f"{datetime.datetime.utcnow().replace(microsecond=0)}", "friends")
        sleep(1)
        add_post(conn, 3, "Everyone can see this!", f"{datetime.datetime.utcnow().replace(microsecond=0)}", "public")
        sleep(1)
        add_post(conn, 4, "If Eirik can see this he accepted Aksels friend request!", f"{datetime.datetime.utcnow().replace(microsecond=0)}", "friends")


        conn.close()