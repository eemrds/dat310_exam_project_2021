
# Witter.com examp project

## How to start

1. install python 3 from https://www.python.org/downloads/

2. Install Flask from pip by running 

    > pip3 install Flask

3. Download the files from git or canvas

4. open the file from the terminal and run it with

> python3 app.py

5. The database can be reset by deleting the file `database.db` and then re-create it by using the  `setup_db.py`

> python3 setup_db.py



## Code use:

* some code has been taken/inspired from examples on https://github.com/dat310-spring21/course-info
* colors have been chosen from these urls:
    * https://www.canva.com/colors/color-palettes/blistering-cold/ 
    * https://coolors.co/052f5f-005377-06a77d-d5c67a-f1a208
    



## How to run/use:

The application will at first prompt you with a login screen. If you press the register button the form will change to allow for registration. If you press the Login button that is displayed beneath the registration form then the form is switched back to the login form. 

When registered the new user will be logged inn and shown the header containing:

* **A search field**: where the user can search for names in the database and the users will be shown in a dropdown style div. If a user clicks on one of those names a friend request will be sendt. (will not be shown before the user the request was sendt to accepts it).

* **A friend request button**: Where the friend requests sendt to the user will be shown and the user can accept or deny them (border of the button will be red if there are any requests present)

* **A settings button**: Containing a dropdown div where the user can:

    * Change theme by clicking th field and the themes get swapped back and forth
    * A change username field which lets the user change the username of the account
    * A change password field which lets the user change the password of the account
    * A change email field which lets the user change the email of the account
    * A delete account field which lets the user delete the account

    All of these options needs verification by submitting the password of the account

* **A logout button**: which lets the user log out

The user will also be shown a **sidebar** where the user can see the friends it has and can remove them by clicking the ‘**x**’. The  username of the current logged in user is also displayed there.

The user will also be shown the **post board** where the user can:

*  add a post by clicking the ‘**+**’
    * the user will then be shown a form where the user can write content and change the view for who on the site will be able to view the post
* change the order of the posts from *old-to-new* or *new-to-old*
* change which posts should be shown 
    * all posts
    * friends posts only
    * public posts only
* edit a post, if a user owns it, either by only changing the view option or editing the content
* view the post on th board

The last thing will be the **footer** which contains 111% real contact information



## Usefull information:

* Default user login information:
    1. Username: Erik, Password: erik12345
    2. Username: Eirik, Password: eirik12345
    3. Username: Steinar, Password: steinar12345
    4. Username: Aksel, Password: aksel12345



## Functionality:

* Is mainly built with flexboxes and scales down to 800px in width
* A logged in user has a session length of 3 minutes before getting logged out on refocus
* Uses regex to validate the email for both registration and user edit

### Header

Let’s a user:

* query the database for users that are located in the ‘users’ table and they will be dynamically displayed on keydown
    * only works if a user is logged in
* add the users, that are displayed from the query, as friends. Will **not** allow a user to add:
    * itself 
    * users that are already added as friends
    * users that has sendt a friend request to the user
    *  users that the user has sendt a friend request to
* Retrieve friend requests sendt to the user on login. Displayes them dynamically and let’s the user accept or deny them which them sends an update request or a delete request to the server. 
    * Button will have a red border if there are requests for the user.
    * When a user accepts the request, the posts from the new friend that would only be shown to it’s friends now visible by the user
* swap between two themes (‘murky’ and ‘colorfull’) on click by using a cookie stored client side
* change account information which can be username, password or email. These forms are validated by the user entering the password and then sendt to the server where they are revalidated with the session information.
* delete the account which again is validated client and server side and then the user information, friend relationships and posts, by the user, are also deleted then the user is logged out if successfull
* logout which removes the session and returns the user to the login page



### Aside

Let’s a user:

* See which user that is logged in
* remove friends which removes the relation from the database which then updates which posts the user can see
* Visually see which friends it has and it dynamically updates on a user removal or addition



### Main

Let’s a user:

* Sort the posts displayed by ‘new-to-old’ or ‘old-to-new’
* Choose which posts are displayed. Can be “all posts”, “public posts only” or “friends posts only”.
* add a post where the user can write some text and choose the scope of who can view the post. Can be either “public” meaning that all users can see the posts on login, or “friends” which only let the users that the post owner has in the friends list view it. 
* Update post that the user has written itself. This can either be just quickly update the view scope by changing it in the dropdown select or edit the post content which prompts the user with the text so that it can be changed and then is validated and sendt to the server



### Validation

Validates: 

* usernames on registering and updating to contain at least 4 characters to 20 characters
* passwords on registering and updating to contain at least 4 characters to 120 characters
* the email using regex to try and validate a correct looking email address
* login information server side with ‘werkzeug.security’ by checking the password hash stored in the database with the password given by the user for that specific account
* post content to make sure it is not an empty string
* that only users logged in can add friends, post or use the function buttons 
    * If a user tries to do this without being logged in the request is aborted server side and will not let the user do it client side

