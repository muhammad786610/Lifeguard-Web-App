#Importing all my necessary libraries and modules
import email
import streamlit as st
import random
import smtplib
from email.message import EmailMessage
import sqlite3
import hashlib
from st_circular_progress import CircularProgress
#Creating my database class
class Database:
    def __init__(self):
        self.connection = sqlite3.connect("lifeguard.db")
        self.cursor = self.connection.cursor()
        #Added new line as you have to enable foreign keys for sqlite to recognise them
        self.connection.execute("PRAGMA foreign_keys = ON")

    #Creating my user table which will store user information
    def create_user_table(self):
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS users
                 (user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                       name TEXT,
                       surname TEXT,
                       email TEXT UNIQUE,
                       password TEXT,
                       username TEXT UNIQUE,
                       role TEXT,
                       duty_manager_email TEXT,
                       rankings_status INTEGER,
                       dm_results_status INTEGER)''')
        self.connection.commit()

    #Creating a method to add my user details
    def add_user(self,name , surname, email, password, username, role, duty_manager_email, ranking_status, dm_status):
        self.cursor.execute('''INSERT INTO users (name, surname, email, password, username, role, duty_manager_email, rankings_status, dm_results_status)
                               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                            (name , surname, email, password, username, role, duty_manager_email, ranking_status , dm_status))
        self.connection.commit()

    #Creating a method to see if this email already exists in the database
    def email_exists(self, email):
        self.cursor.execute('''SELECT * FROM users WHERE email = ?''',
                            (email,))
        return self.cursor.fetchone()
    
    #Creating a method to see if this username already exists in the database
    def username_exists(self, username):
        self.cursor.execute('''SELECT * FROM users WHERE username = ?''',
                            (username,))
        return self.cursor.fetchone()

    #Creating a method to get user details
    def login_user(self, email_username):
        self.cursor.execute('''SELECT * FROM users WHERE (email = ? OR username = ?)''',
                            (email_username, email_username))
        return self.cursor.fetchone()
    
    #Creating a method to update password
    def update_password(self, new_password, email):
        self.cursor.execute('''UPDATE users SET password = ? WHERE email = ?''',
                            (new_password, email))
        self.connection.commit()

    #Creating a method to add my duty manager email
    def update_dm_email(self, duty_manager_email, user_id):
        self.cursor.execute('''UPDATE users SET duty_manager_email = ? WHERE user_id = ?''',
                            (duty_manager_email, user_id))
        self.connection.commit()

    #Creating a method to add my rankings status to database
    def update_rankings_status(self,rankings_status,user_id):
        self.cursor.execute('''UPDATE users SET rankings_status = ? WHERE user_id = ?''',
                            (rankings_status,user_id))
        self.connection.commit()

    #Creating a method to add my duty manager result status to database
    def update_dm_results_status(self,dm_result_status,user_id):
        self.cursor.execute('''UPDATE users SET dm_results_status = ? WHERE user_id = ?''',
                            (dm_result_status,user_id))
        self.connection.commit()

    #Creating a method to return status
    def return_status(self, user_id):
        self.cursor.execute('''SELECT * FROM users WHERE user_id = ?''',
                            (user_id,))
        return self.cursor.fetchone()
    

    #Creating my topic table which will store unique topic information
    def create_topic_table(self):
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS topic
                 (topic_id INTEGER PRIMARY KEY AUTOINCREMENT,
                       topic_name TEXT,
                       section_number INTEGER)''')
        self.connection.commit()

    #Method to add to my topic table
    def update_topic_table(self,topic_name,section_number):
        self.cursor.execute('''INSERT INTO topic (topic_name, section_number)
                            VALUES (?,?)''',
                            (topic_name,section_number))
        self.connection.commit()

    #Creating a method to add my flashcrad table
    def create_flashcard_table(self):
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS flashcard
                 (flashcard_id INTEGER PRIMARY KEY AUTOINCREMENT,
                       flashcard_question TEXT,
                       flashcard_answer TEXT,
                       flashcard_image TEXT,
                       topic_id INTEGER,
                       FOREIGN KEY (topic_id) REFERENCES topic(topic_id)
                       )''')
        self.connection.commit()

    #Method to add to my topic table
    def update_flashcard_table(self,flashcard_question , flashcard_answer , flashcard_image , topic_id):
        self.cursor.execute('''INSERT INTO flashcard (flashcard_question, flashcard_answer ,
                             flashcard_image , topic_id)
                            VALUES (?,?,?,?)''',
                            (flashcard_question , flashcard_answer , flashcard_image , topic_id))
        self.connection.commit()

    #Creating a method to retrieve my flashcards
    def retrieve_flashcards(self, section_number):

        self.cursor.execute("""
            SELECT flashcard.*
            FROM flashcard
            JOIN topic
            ON flashcard.topic_id = topic.topic_id
            WHERE topic.section_number = ?""",
              (section_number,))

        return self.cursor.fetchall()
    
    #Creating a method to add my quiz table
    def create_quiz_table(self):
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS quiz
                 (quiz_id INTEGER PRIMARY KEY AUTOINCREMENT,
                       quiz_question TEXT,
                       quiz_correct_answer TEXT,
                       quiz_incorrect_answer1 TEXT,
                       quiz_incorrect_answer2 TEXT,
                       quiz_incorrect_answer3 TEXT,
                       quiz_image TEXT,
                       topic_id INTEGER,
                       FOREIGN KEY (topic_id) REFERENCES topic(topic_id)
                       )''')
        self.connection.commit()

    #Method to add to my topic table
    def update_quiz_table(self,quiz_question , quiz_correct_answer , quiz_incorrect_answer1 , 
                          quiz_incorrect_answer2 , quiz_incorrect_answer3 , quiz_image , topic_id):
        self.cursor.execute('''INSERT INTO quiz (quiz_question, quiz_correct_answer , quiz_incorrect_answer1 , 
                            quiz_incorrect_answer2 , quiz_incorrect_answer3 , quiz_image , topic_id)
                            VALUES (?,?,?,?,?,?,?)''',
                            (quiz_question , quiz_correct_answer , quiz_incorrect_answer1 , quiz_incorrect_answer2 ,
                              quiz_incorrect_answer3 , quiz_image , topic_id))
        self.connection.commit()


    #Creating a method to retrieve my quiz
    def retrieve_quiz(self, section_number):
        self.cursor.execute(
            '''SELECT * FROM quiz
            INNER JOIN topic
            ON quiz.topic_id = topic.topic_id
            WHERE topic.section_number = ?''',
            (section_number,))

        return self.cursor.fetchall()

    def create_user_progress_table(self):
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS user_progress
                 (progress_id INTEGER PRIMARY KEY AUTOINCREMENT,
                       user_id INTEGER UNIQUE,
                       section_1_progress_percentage REAL,
                       section_2_progress_percentage REAL,
                       section_3_progress_percentage REAL,
                       FOREIGN KEY (user_id) REFERENCES users(user_id)
                       )''')
        self.connection.commit()

    #Creating a method to add missing rows to my user progress table 
    def create_missing_user_progress_rows(self, user_id):
        self.cursor.execute(
            '''
            INSERT INTO user_progress (
                user_id,
                section_1_progress_percentage,
                section_2_progress_percentage,
                section_3_progress_percentage
            )
            SELECT user_id, 0, 0, 0
            FROM users
            WHERE user_id NOT IN (
                SELECT user_id FROM user_progress
            )
            ''')
        self.connection.commit()

    def update_section_1_progress(self, user_id, section_1_progress_percentage):
        self.cursor.execute(
            '''
            UPDATE user_progress
            SET section_1_progress_percentage = ?
            WHERE user_id = ?
            ''',
            (section_1_progress_percentage, user_id)
        )
        self.connection.commit()

    def update_section_2_progress(self, user_id, section_2_progress_percentage):
        self.cursor.execute(
            '''
            UPDATE user_progress
            SET section_2_progress_percentage = ?
            WHERE user_id = ?
            ''',
            (section_2_progress_percentage, user_id)
        )
        self.connection.commit()

    def update_section_3_progress(self, user_id, section_3_progress_percentage):
        self.cursor.execute(
            '''
            UPDATE user_progress
            SET section_3_progress_percentage = ?
            WHERE user_id = ?
            ''',
            (section_3_progress_percentage, user_id)
        )
        self.connection.commit()

    #Creating a method to return progress
    def return_progress(self, user_id):
        self.cursor.execute('''SELECT * FROM user_progress WHERE user_id = ?''',
                            (user_id,))
        return self.cursor.fetchone()
    

    #My get rankings method which will return average score of users who have turned on their rankings
    def get_rankings(self):
        self.cursor.execute("""
            SELECT 
                users.name,
                users.role,
                user_progress.section_1_progress_percentage,
                user_progress.section_2_progress_percentage,
                user_progress.section_3_progress_percentage,
                (
                    user_progress.section_1_progress_percentage +
                    user_progress.section_2_progress_percentage +
                    user_progress.section_3_progress_percentage
                ) / 3.0 AS average_score
            FROM users
            JOIN user_progress
            ON users.user_id = user_progress.user_id
            WHERE users.rankings_status = 1
            ORDER BY average_score DESC
        """)
        return self.cursor.fetchall()

#Class for sending email results to duty manager
class send_results:
    def __init__(self, smtp_server, port, sender_email, password):
        self.smtp_server = smtp_server
        self.port = port
        self.sender_email = sender_email
        self.password = password
    
    #Method that creates my email and setting the content within it 
    def create_message(self, receiver_email, subject, body):
        msg = EmailMessage()
        msg["From"] = self.sender_email
        msg["To"] = receiver_email
        msg["Subject"] = subject
        msg.set_content(body)
        return msg
    
    #Method to send the email and handling any exceptions that may occur
    def send_email(self, receiver_email, subject, body):
        try:
            #Although typically bad practice to call one method within another , I think this is the best way
            msg = self.create_message(receiver_email, subject, body)

            #Establishing a port connection to the email server and sending the email
            with smtplib.SMTP(self.smtp_server, self.port) as server:
                server.starttls()
                server.login(self.sender_email, self.password)
                server.send_message(msg)

            return True, "Email sent successfully!"

        except Exception as e:
            return False, str(e)

#Constants
#Creating my page variable
if "page" not in st.session_state:
    st.session_state.page = "Welcome"

#Creating my name variable
if "name" not in st.session_state:
    st.session_state.name = ""
#Creating my surname variable
if "surname" not in st.session_state:
    st.session_state.surname = ""

#Creating my username variable
if "username" not in st.session_state:
    st.session_state.username = ""

#Creating my role variable
if "role" not in st.session_state:
    st.session_state.role = ""

#Creating my email/username variable
if "email_username" not in st.session_state:
    st.session_state.email_username = ""

#Creating my duty manager's email variable
if "duty_manager_email" not in st.session_state:
    st.session_state.duty_manager_email = ""

#Creating a logged in variable which will store whether the user is logged in
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

#Creating my user id variable
if "user_id" not in st.session_state:
    st.session_state.user_id = None

#Creating my new password variable
if "new_password" not in st.session_state:
    st.session_state.new_password = ""

#Creating my sign up email variable
if "signup_email" not in st.session_state:
    st.session_state.signup_email = ""

#Creating my reset password email variable
if "reset_password_email" not in st.session_state:
    st.session_state.reset_password_email = ""

    #Creating my new password variable
if "new_password" not in st.session_state:
    st.session_state.new_password = ""

#Creating my sign up password variable
if "signup_password" not in st.session_state:
    st.session_state.signup_password = ""

#Creating my login password variable
if "login_password" not in st.session_state:
    st.session_state.login_password = ""

#Creating my show reset variable which will control whether the second button for reset password is shown
if "show_reset" not in st.session_state:
    st.session_state.show_reset = False

#Creating my duty manager email variable
if "dm_email" not in st.session_state:
    st.session_state.dm_email = ""

if "show_answer" in st.session_state:
    st.session_state.show_answer = False
    
#Creating my Welcome Page Class
class welcome_page:
    #Defining the Constructor with all the buttons needed
    def __init__(self):
        self.title = "Lifeguard Revision App"
        self.header = "Please choose one of the following options:"
        self.login_button = "Login"
        self.signup_button = "Sign Up"
        self.reset_password_button = "Reset Password"
        self.icon = "lifeguard_icon.png"

    #Creating a method to display my title and message
    def display(self):
        col1, col2, col3 = st.columns([1,5,1])
        with col2:  
            st.title(self.title)
            #This is to leave a small gap between the title and header
            st.space(size="small")
        #Centering My image in a different size to my buttons
        col1, col2, col3 = st.columns([1,0.5,1])
        with col2:
            #Adding My icon to the welcome page
            st.image(self.icon,use_container_width=True)       
        st.header(self.header)
        st.space(size="small")
        #This method also displays my buttons and centre's them
        col1, col2, col3 = st.columns([1,3,1])
        with col2:
            if st.button(self.login_button,use_container_width=True) == True:
                st.session_state.page = "Login"
                st.rerun()
            if st.button(self.signup_button,use_container_width=True) == True:
                st.session_state.page = "Sign Up"
                st.rerun()
            if st.button(self.reset_password_button,use_container_width=True):
                st.session_state.page = "Reset Password"
                st.rerun()


#Defining my Signup Class
class sign_up_page:
    #Defining my constructor with all my inputs
    def __init__(self):
        #Setting up all my instances to their designated variables
        self.title = "Sign Up"
        self.name_header = "Please Enter Your Name"
        self.name_input = "For Example: Meli"
        self.surname_header = "Please Enter Your Surname"
        self.surname_input = "For Example: Kurti"
        self.email_header = "Please Enter Your Email address"
        self.email_input = "For Example: meli@stdoms.ac.uk"
        self.password_header = "Please enter your password"
        self.password_input = ""
        self.username_header = "Please enter your username"
        self.username_input = "For example Meli123"
        self.role_header = "Please select your role"
        self.role_input = "Role"
        self.submit_button = "Submit"
        self.back_button = "Back"

    #Creating a method to display my input text fields for signup
    def display_signup(self):
        col1, col2, col3 = st.columns([1,3,1])
        with col2:
            st.title(self.title)
            st.space(size="small")
            st.subheader(self.name_header)
            st.text_input("",placeholder=self.name_input,key="name")
            st.subheader(self.surname_header)
            st.text_input("",placeholder=self.surname_input, key="surname")
            st.subheader(self.email_header)
            st.text_input("",placeholder=self.email_input, key="signup_email")
            st.subheader(self.password_header)
            st.text_input("",placeholder=self.password_input, key="signup_password",type="password")
            st.subheader(self.username_header)
            st.text_input("",placeholder=self.username_input, key="username")
            st.subheader(self.role_header)
            st.session_state.role = st.selectbox(self.role_input,["Lifeguard", "Duty Manager", "First Aid Trainer", "Other"])
        col1,col2,col3 = st.columns([1,2,1])
        with col2:
            #Validation for my submit button
            if st.button(self.submit_button, use_container_width=True) == True:
                #Validating user inputs
                if (len(st.session_state.name) < 3) or (len(st.session_state.name) > 25):
                    st.warning("Please enter a name that is between 3 and 25 characters long")
                elif (len(st.session_state.surname) < 3) or (len(st.session_state.surname) > 25):
                    st.warning("Please enter a surname that is between 3 and 25 characters long")
                elif (len(st.session_state.signup_email) <= 3) or (st.session_state.signup_email.count("@") != 1):
                    #We Send a warning to the user via st.warning
                    st.warning("Please enter a valid email address")
                elif db.email_exists(st.session_state.signup_email):
                    st.warning("Email address is already in use")    
                elif (len(st.session_state.signup_password) < 3) or (len(st.session_state.signup_password) > 20):
                    st.warning("Please enter a password that is between 3 and 20 characters long")
                elif (len(st.session_state.username) < 3) or (len(st.session_state.username) > 15):
                    st.warning("Please enter a username that is between 3 and 15 characters long")
                #Validation construct to see if the username already exists
                elif db.username_exists(st.session_state.username):
                    st.warning("Username is already in use")
                elif st.session_state.role == "Role":
                    st.warning("Please select a role")
                else:
                    #Hashing the inputted password to enter into the database securely
                    hashed_password = hashlib.sha256(st.session_state.signup_password.encode()).hexdigest()
                     #Calling Our add_user method
                    db.add_user(
                        st.session_state.name,
                        st.session_state.surname,
                        st.session_state.signup_email,
                        hashed_password,
                        st.session_state.username,
                        st.session_state.role,
                        st.session_state.duty_manager_email,
                        0,
                        0
                        )
                    st.success("Sign Up Successful")
                    st.session_state.page = "Login"
                    st.rerun()
            if st.button(self.back_button, use_container_width=True) == True:
                st.session_state.page = "Welcome"
                st.rerun()


#Defining my Login Class
class login_page:
    #Defining my constructor with all my inputs
    def __init__(self):
        #Setting up all my instances to their designated variables
        self.title = "Login"
        self.email_header = "Please Enter Your Email address or Username"
        self.login_input ="For Example: meli@stdoms.ac.uk or Meli123"
        self.password_header = "Please enter your password"
        self.password_input = ""
        self.submit_button = "Submit"
        self.back_button = "Back"

    #Creating a method to display my input text fields for login
    def display_login(self):
        st.session_state.user_id = None
        col1, col2, col3 = st.columns([1,3,1])
        with col2:
            st.title(self.title)
            st.space(size="small")
            st.subheader(self.email_header)
            st.text_input("",placeholder=self.login_input, key="email_username")
            st.subheader(self.password_header)
            st.text_input("",placeholder=self.password_input, key="login_password",type="password")
            st.space(size="small")
        col1,col2,col3 = st.columns([1,2,1])
        with col2:
            #Condition controlled loop controlling submit button for login
            if st.button(self.submit_button, use_container_width=True) == True:
                #Validation to check whether inputs are up to standard
                if (len(st.session_state.email_username) < 3) or (len(st.session_state.email_username) > 25):
                    st.warning("Please enter a valid email/username and password")
                elif (len(st.session_state.login_password) < 3) or (len(st.session_state.login_password) > 20):
                    st.warning("Please enter a valid email/username and password")
                else:
                    #Checking in the database that the user exists and their password is correct
                    user = db.login_user(st.session_state.email_username)
                    # This then validates the data we recieve back from the database
                    if user:
                        #Hashing our users inputted password to compare with the hashed password stored in the database
                        hashed_login_password = hashlib.sha256(st.session_state.login_password.encode()).hexdigest()
                        if hashed_login_password != user[4]:
                            st.warning("Incorrect password")

                        elif ((st.session_state.email_username == user[3]) or (st.session_state.email_username == user[5]))and (hashed_login_password == user[4]):
                            st.write("Login Successfully")
                            st.session_state.logged_in = True
                            st.success("Login Successful")
                            st.session_state.user_id = user[0]  
                            st.session_state.name = user[1]
                            st.session_state.page = "Main Menu"
                            db.create_missing_user_progress_rows(st.session_state.user_id)
                            st.rerun()
                    else:
                        #Validation construct if the user does not exist
                        st.warning("User does not exist")

            # Back button and its validation
            if st.button(self.back_button, use_container_width=True) == True:
                st.session_state.page = "Welcome"
                st.rerun()


#Defining my Reset Password Class
class reset_password_page:
    def __init__(self):
        self.title = "Reset Password"
        self.email_header = "Please Enter Your Email address"
        self.email_input = "For Example: meli@stdoms.ac.uk"
        self.submit_button = "Submit"
        self.confirm_button = "Confirm That this is Your New Password"
        self.back_button = "Back"

    #Creating a method to display my input text fields for reset password
    def display_reset_password(self):
        col1, col2, col3 = st.columns([1,3,1])
        with col2:
            st.title(self.title)
            st.space(size="small")
            st.subheader(self.email_header)
            st.text_input("",placeholder=self.email_input,key="reset_password_email")
        col1,col2,col3 = st.columns([1,2,1])
        with col2:
            #Intial submit button which will start the validation process to reset password
            if st.button(self.submit_button, use_container_width=True) == True:
                    #Checking to see if the email exists in the database
                    user = db.email_exists(st.session_state.reset_password_email)
                    if user:
                            st.session_state.show_reset = True
                    else:
                         st.warning("User does not exist")
            if st.session_state.show_reset == True:
                st.text_input("",placeholder="Enter your new password" , key="new_password", type="password")
                if st.button(self.confirm_button, use_container_width=True):
                                #Validation construct to see if the new password is valid
                                if (len(st.session_state.new_password) < 3) or (len(st.session_state.new_password) > 20):
                                    st.warning("New Password must be between 3 and 20 characters long")
                                #Updating database with new password    
                                else:
                                    #Hashing new password to be stored in the database securely
                                    hashed_new_password = hashlib.sha256(st.session_state.new_password.encode()).hexdigest()
                                    db.update_password(hashed_new_password, st.session_state.reset_password_email)
                                    st.success("Password reset successfully")
                                    st.session_state.page = "Login"
                                    st.rerun()
            if st.button(self.back_button, use_container_width=True) == True:
                st.session_state.page = "Welcome"
                st.rerun()


#Creatng my Navigation Bar Class
class navigation_bar:
    def __init__(self):
        #Creating my instances for my navigation bar buttons
        self.Main_Menu_button = "Home\n🏠 "
        self.Flashcard_button = "Flashcards\n📚"
        self.Quiz_button = "Quiz\n📝"
        self.Rankings_button = "Rankings\n🏆"
        self.Video_button = "Videos\n🎥 "
        self.Settings_button = "Settings\n⚙️"
        self.logout_button = "Logout\n🚪"

    def display_navigation_bar(self):
        #Using inline CSS to style my buttons as streamlit
        st.markdown("""
                    <style>
                    div.stButton > button {
                                            height: 52px;
                                            font-size: 18px;
                                            white-space: nowrap;
                                          }
                    </style>
                    """, unsafe_allow_html=True)
        #Using my with function to designate each button to its own column
        col1, col2, col3, col4, col5, col6 = st.columns([1.5,2,1.5,2,1.5,2])
        #Main Menu Button
        with col1:
            if st.button(self.Main_Menu_button, use_container_width=True):
                st.session_state.page = "Main Menu"
                st.rerun()
        #Flashcard Button
        with col2:
            if st.button(self.Flashcard_button, use_container_width=True):
                st.session_state.page = "Flashcards"
                st.rerun()
        #Quiz Button
        with col3:
            if st.button(self.Quiz_button, use_container_width=True):
                st.session_state.page = "Quiz"
                st.rerun()
        #Rankings Button
        with col4:
            if st.button(self.Rankings_button, use_container_width=True):
                st.session_state.page = "Rankings"
                st.rerun()
        #Videos Button
        with col5:
            if st.button(self.Video_button, use_container_width=True):
                st.session_state.page = "Videos"
                st.rerun()
        #Settings Button
        with col6:
            if st.button(self.Settings_button, use_container_width=True):
                st.session_state.page = "Settings"
                st.rerun()
        #Logout Button
        col1,col2,col3 = st.columns([1,0.5,1])
        with col2:
            if st.button(self.logout_button,use_container_width=True):
                st.session_state.page = "Welcome"
                st.rerun()


#Creating my Main Menu class and inheriting the navigation bar class
class main_menu_page(navigation_bar):
    def __init__(self):
        #Used so I can inherit attributes from the navigation bar class
        super().__init__()
        self.title = "Home 🏠"
        self.welcome_message = "Welcome " + st.session_state.name + " to the Lifeguard Revision App!👋"
        self.progress = "This week's progress: "
        self.suggestive_topic = "I suggest revising: "

    #Displaying my main menu with welcome message nav bar and logout button
    def display_main_menu(self):
        col1, col2, col3 = st.columns([1,0.9,1])
        with col2:
            st.title(self.title)
        #Calling my method to display the navigation bar at the top of the page
        self.display_navigation_bar()
        col1, col2, col3 = st.columns([1,100,1])
        with col2:
            st.subheader(self.welcome_message)
        #Returning user's progress from the database and assigning each section's progress to a variable
        progress_current = db.return_progress(st.session_state.user_id)
        progress1 = progress_current[2]
        progress2 = progress_current[3]
        progress3 = progress_current[4]

        #Suggestive Revsion topic based off the data in the database
        if progress1 < (progress2 or progress3) :
            self.suggestive_topic = "Your should revise: Section 1: The Lifeguard, Swimming Pool and Supervision 🏊‍♀️"
        elif progress2 < (progress1 or progress3) :
            self.suggestive_topic = "You should revise: Section 2: Intervention, Rescue and Emergency Action Plan 🆘"
        else:
            self.suggestive_topic = "You should revise: Section 3: CPR, AED, First Aid 🚑"
        Suggestive_container = st.container(border=True)
        Suggestive_container.write(self.suggestive_topic)
        Progress_container = st.container(border=True)
        Progress_container.write(self.progress)
        #Adding my circular progress bars to show the user's progress in each section
        progress_column1, progress_column2, progress_column3 = st.columns(3)
        with progress_column1:
            section1_progress = CircularProgress(
                label="Section 1",
                value=int(progress1),
                #Using dynamic keys so that the program is forced to use new progress values
                key=f"s1_progress_{progress1}"
            ).st_circular_progress()
        with progress_column2:
            section2_progress = CircularProgress(
                label="Section 2",
                value=int(progress2),
                key=f"s2_progress_{progress2}"
            ).st_circular_progress()

        with progress_column3:
            section3_progress = CircularProgress(
                label="Section 3",
                value=int(progress3),
                key=f"s3_progress_{progress3}"
            ).st_circular_progress()
#Creating My Flashcard Class
class flashcard_page(navigation_bar):
    def __init__(self):
        super().__init__()
        self.title = "Flashcards 📚"
    #Creating a method to display my flashcards page
    def display_flashcards(self):
        col1, col2, col3 = st.columns([1,1.6,1])
        with col2:
            st.title(self.title)
        self.display_navigation_bar()
        col1, col2, col3 = st.columns([1,20,1])
        with col2:
            st.subheader("SECTION 1: The Lifeguard , Swimming Pool and Supervision 🏊‍♀️")
            st.subheader("SECTION 2: Intervention , Rescue and Emergency Action Plan 🆘")
            st.subheader("SECTION 3 : CPR , AED , First Aid 🚑")
        # Using Tabs to create a main menu for the flashcard page
        tab1, tab2, tab3 = st.tabs(["SECTION 1","SECTION 2","SECTION 3"])
        
        #Creating my template for my flashacrds in which data will passed into from the database
        def format_flashcard(tab_name,section_number):
            
            #Associating the flashcards with the tab name to ensure that each tab has its own flashcards 
            flashcards_key = f"flashcards_{tab_name}"
            #Ensuring that the flashcards are  in session state
            #Calling our db method inside the condition
            if flashcards_key not in st.session_state:
                st.session_state[flashcards_key] = db.retrieve_flashcards(section_number)
            #Assigning the values from the database into the variable flashcards
            flashcards = st.session_state[flashcards_key]
            #Warning to ensure there are currently no flashacrds on this section
            if not flashcards:
                st.warning("No flashcards found for this section.")
                return
            #New seperate shuffle key which is used to store the shuffled cards
            shuffle_key = f"repeated_flashcards_{tab_name}"
            if tab_name == "tab1":
                progress = db.return_progress(st.session_state.user_id)[2]
            elif tab_name == "tab2":
                progress = db.return_progress(st.session_state.user_id)[3]
            else:
                progress = db.return_progress(st.session_state.user_id)[4]
                
            #My repetitive algorithm controlling how many times the flashscards are repeated
            if progress == 100:
                repeat_count = 2
            elif progress >= 50:
                repeat_count = 3
            else:
                repeat_count = 5
            repeat_count_key = f"repeat_count_{tab_name}"

            if (shuffle_key not in st.session_state or repeat_count_key not in st.session_state
                or st.session_state[repeat_count_key] != repeat_count):
                st.session_state[shuffle_key] = flashcards * repeat_count                    
                st.session_state[repeat_count_key] = repeat_count
            repeated_flashcards = st.session_state[shuffle_key]

            #Flashacrd index which will be used to track which flashcard the user is on
            flashcard_index = f"flashcard_index_{tab_name}"
            #Show answer variable which will control whether the answer is shown or not
            show_answer = f"show_answer_{tab_name}"

            #We introduce a new constants into st.session_state using the [] notation to show its dynamic 
            if flashcard_index not in st.session_state:
                st.session_state[flashcard_index] = 0

            #Setting the show_answer state to false so that if another tab has used show answer it can then
            if show_answer not in st.session_state:
                st.session_state[show_answer] = False

            if "shuffle" not in st.session_state:
                st.session_state["shuffle"] = False
            
            #Setting the index rank to 0 so the first card is displayed
            if st.session_state[flashcard_index] >= len(repeated_flashcards):
                st.session_state[flashcard_index] = 0
            #Setting the index so the last card is set
            if st.session_state[flashcard_index] < 0:
                st.session_state[flashcard_index] = len(repeated_flashcards) - 1
            
            #Adding my progress bar to show clients how many flashcards they have left
            progress = (st.session_state[flashcard_index] + 1) / len(repeated_flashcards)
            st.progress(progress)
            st.write(f"Flashcard {st.session_state[flashcard_index] + 1} of {len(repeated_flashcards)}")


            #This adds the tupules we get back from the database into a list called flashcards
            card = repeated_flashcards[st.session_state[flashcard_index]]

            #Based on our list index we assign each variable to that part of the list
            question = card[1]
            answer = card[2]
            image = card[3]

            #Formatting the question column
            col1, col2, col3 = st.columns([1, 10, 1])
            with col2:
                st.info(question,width="stretch")
                #Placing my image here
                col1, col2, col3 = st.columns([1, 2, 1])
                with col2:
                    #We set this condition as not all cards have an image
                    if image and image.strip():
                        st.image(image, width= "stretch")

                #Seperate formatting for the answer button
                col1, col2, col3 = st.columns(3)
                with col2:
                    #using an f string to make each button between the three tabs unique
                    if st.button("Show Answer", key=f"answer_button_{tab_name}", width="stretch"):
                        st.session_state[show_answer] = True

                #Seperate formatting for the answer itself
                col1, col2, col3 = st.columns([1, 10, 1])
                with col2:
                    if st.session_state[show_answer] == True:
                        st.write("")
                        st.write("")
                        st.success(answer, width="stretch")
                        st.write("")
                        st.write("")

                col1, col2, col3 = st.columns(3)
                #Previous Button
                with col1:
                    st.write("")
                    if st.button("Previous",key=f"previous_button{tab_name}", width="stretch"):
                        st.session_state[flashcard_index] -= 1
                        st.session_state[show_answer] = False
                        st.rerun()
                    #Extra validation to make sure the flashcard index does not go below 0 and cause an error
                    if st.session_state[flashcard_index] < 0:
                        st.session_state[flashcard_index] = len(repeated_flashcards) - 1
                        st.rerun()
                #Hide button
                with col2:
                    st.write("")
                    if st.button("Hide answer",key=f"hide_button{tab_name}" ,width = "stretch"):
                        st.session_state[show_answer] = False
                        st.rerun()
                #Next button
                with col3:
                    st.write("")
                    #Setting our conditions for the next button
                    if st.button("Next", key=f"next_button_{tab_name}", width="stretch"):
                        #We then increment the flashcard index
                        st.session_state[flashcard_index] += 1
                        st.session_state[show_answer] = False
                        st.rerun()
                        #Once all the flashcards have been completed we display the success messaage and reset the index
                        if st.session_state[flashcard_index] >= len(repeated_flashcards) and st.session_state[show_answer] == True:
                            st.rerun()
                with col2:
                    if st.button("Shuffle Flashcards", key=f"shuffle_button_{tab_name}", width="stretch"):
                        #Using the flashcard key variable which is in session state
                        random.shuffle(st.session_state[shuffle_key])
                        st.session_state[flashcard_index] = 0
                        st.session_state[show_answer] = False
                        st.rerun()

        #Formatting for tab1 
        with tab1:
            flashcard_box = st.container(border=True, height=700)
            with flashcard_box:
                format_flashcard("tab1", 1)
        #Formatting tab 2
        with tab2:
            flashcard_box_2 = st.container(border=True, height=700)
            with flashcard_box_2:
                format_flashcard("tab2", 2)
        #Formatting tab 3
        with tab3:
            flashcard_box_3 = st.container(border=True, height=700)
            with flashcard_box_3:
                format_flashcard("tab3", 3)




#Creating My Quiz Class
class quiz_page(navigation_bar):
    def __init__(self):
        super().__init__()
        self.title = "Quiz 📝"
    #Creating a method to display my quiz page
    def display_quiz(self):
        col1, col2, col3 = st.columns([1,0.75,1])
        with col2:
            st.title(self.title)
        self.display_navigation_bar()
        col1, col2, col3 = st.columns([1,20,1])
        with col2:
            section_1_header = st.subheader("SECTION 1: The Lifeguard , Swimming Pool and Supervision 🏊‍♀️")
            section_2_header = st.subheader("SECTION 2: Intervention , Rescue and Emergency Action Plan 🆘")
            section_3_header = st.subheader("SECTION 3 : CPR , AED , First Aid 🚑")
        # Using Tabs to create a main menu for the flashcard page
        tab1, tab2, tab3 = st.tabs(["Quiz for SECTION 1","Quiz for SECTION 2","Quiz for SECTION 3"])

        #Used to format the quiz within the correct tab
        def format_quiz(tab_name, section_number):

            #Used to track the correct quiz within the correct tab 
            quiz_key = f"quiz_{tab_name}"

            #Using sq bracket notation to keep the varaiable name dynamic 
            if quiz_key not in st.session_state:
                st.session_state[quiz_key] = db.retrieve_quiz(section_number)
            
            #Creating a new variable to track the quiz progress for each section
            quiz_progress = f"quiz_progress_{tab_name}"
            if quiz_progress not in st.session_state:
                st.session_state[quiz_progress] = 0

            #Adding our quiz quesstions into a shorter variable for ease of use
            quiz_questions = st.session_state[quiz_key]

            #Variables used to track intenal features of the quiz
            quiz_index = f"quiz_index_{tab_name}"
            answered_key = f"answered_{tab_name}"
            #Used to see whether the user got the question correct or not
            feedback_key = f"feedback_{tab_name}"

            #Creating these session state variables so they index value start from default
            if quiz_index not in st.session_state:
                st.session_state[quiz_index] = 0
            if answered_key not in st.session_state:
                st.session_state[answered_key] = False
            if feedback_key not in st.session_state:
                st.session_state[feedback_key] = ""

            #Extra validation taken for when I have not created a quiz for a specifc section
            if not quiz_questions:
                st.warning("No quiz questions found for this section.")
                return

            #If all the validation checks pass through we then set our index pointer to 0 for tracking
            # Setting the index rank to 0 so the first question is displayed
            if st.session_state[quiz_index] >= len(quiz_questions): 
                #Checks to see if the user has answered the last question
                st.success("Congratulations! You have completed this quiz section! 🎉", width="stretch")
                st.write(f"Your final score is: {st.session_state[quiz_progress]}/{len(quiz_questions)}")
                #Adds all missing people from signup into user progress table
                db.create_missing_user_progress_rows(st.session_state.user_id)
                #Calculating Percenatge score to be sent to the database and duty manager
                percentage_score = int((st.session_state[quiz_progress] / len(quiz_questions)) * 100)
                st.write(f"Your percentage score is: {percentage_score}%")
                if tab_name == "tab1":
                    db.update_section_1_progress(st.session_state.user_id, percentage_score)
                elif tab_name == "tab2":
                    db.update_section_2_progress(st.session_state.user_id, section_number, percentage_score)
                elif tab_name == "tab3":
                    db.update_section_3_progress(st.session_state.user_id, section_number, percentage_score)
                #So if a user wants to retake the quiz they can 
                if st.button("Send Results to Duty Manager", key=f"send_results_{tab_name}", width="stretch"):
                    user = db.return_status(st.session_state.user_id)
                    if user:
                        if (user[7]==""):
                            st.warning("No Duty Manager email found Please add one in settings.")
                            return
                        dm_results_status = bool(user[9])
                        if dm_results_status:
                            send_user_results = send_results(
                                smtp_server="smtp.gmail.com",
                                port=587,
                                sender_email=st.secrets["EMAIL"],
                                password=st.secrets["PASSWORD"])
                            #Formatting my message using f string as each tab section needs dynamic variables
                            section_names = {"tab1": "Section 1: The Lifeguard, Swimming Pool and Supervision",
                                        "tab2": "Section 2: Intervention, Rescue and Emergency Action Plan",
                                        "tab3": "Section 3: CPR, AED, First Aid"}

                            section_title = section_names[tab_name]
                            send_user_results.send_email(user[7], 
                                                             f"{st.session_state.name}'s Quiz Results for {section_title}",
                                                               f"Hello,\n\n{st.session_state.name} has set you as their duty manager and hascompleted the quiz for {section_title} with a score of {percentage_score}% ({st.session_state[quiz_progress]}/{len(quiz_questions)}).\n\nBest regards,\n The Lifeguard Revision App")
                            st.success("Results sent to Duty Manager.")                            
                        else:
                            st.error("You need to allow results to be sent via the settings page")

                #So if a user wants to retake the quiz they can 
                if st.button("Restart Quiz", key=f"restart_quiz_{tab_name}", width="stretch"):
                    #Shuffling the quiz questions
                    random.shuffle(st.session_state[quiz_key])

                    #Using a for loop as we need to clear all old answers
                    for key in list(st.session_state.keys()):
                        if key.startswith(f"answers_{tab_name}_"):
                            del st.session_state[key]

                    st.session_state[quiz_index] = 0
                    st.session_state[quiz_progress] = 0
                    st.session_state[answered_key] = False
                    st.session_state[feedback_key] = ""

                    st.rerun()

                #As we do not want to continue we use return to end the function
                return  

            #In anticiaption of the client , it is better I have a progress bar for the quiz as well
            progress = (st.session_state[quiz_index] + 1) / len(quiz_questions)
            st.progress(progress)
            #Using the of function to denote which list i am referring to
            st.write(f"Question {st.session_state[quiz_index] + 1} of {len(quiz_questions)}")
            
            #Addiing our tupule session state data into a list for tracking 
            question_data = quiz_questions[st.session_state[quiz_index]]
            # Assigning correct indexes of the list to the specifc states that it requires
            question = question_data[1]
            correct_answer = question_data[2]
            quiz_incorrect_answer1 = question_data[3]
            quiz_incorrect_answer2 = question_data[4]
            quiz_incorrect_answer3 = question_data[5]
            image = question_data[6] if len(question_data) > 6 else None 
            #Creates a list of all possible answers
            answers = [
                correct_answer,
                quiz_incorrect_answer1,
                quiz_incorrect_answer2,
                quiz_incorrect_answer3
            ]
            
            #Using a unique key for each tab to shuffle the answers 
            question_id = question_data[0]
            answers_key = f"answers_{tab_name}_{question_id}"
            if answers_key not in st.session_state:
                random.shuffle(answers)
                st.session_state[answers_key] = answers
            #This stores the saved shuffle answer order
            shuffled_answers = st.session_state[answers_key]

            #Displaying the question in the same consistent layout
            col1, col2, col3 = st.columns([1, 10, 1])
            with col2:
                st.info(question, width="stretch")

                #Using the same image formatting like my flashcards
                if image and image.strip():
                    img_col1, img_col2, img_col3 = st.columns([1, 2, 1])
                    with img_col2:
                        st.image(image, use_container_width=300)
                #Using this to make User Interface cleaner and more spaced out
                st.write("")

                col1, col2 = st.columns(2)

                #Using a for loop and the enumerate function as we want all avaialiable options displayed at once
                for i, answer in enumerate(shuffled_answers):
                    if i % 2 == 0:
                        button_col = col1
                    else:
                        button_col = col2

                    #Placing the button within correct column
                    with button_col:
                        #Writing answer within the button
                        if st.button(answer, key=f"answer_{tab_name}_{st.session_state[quiz_index]}_{i}", width="stretch"):
                            # Prevent double counting
                            if not st.session_state[answered_key]:
                                st.session_state[answered_key] = True

                                if answer == correct_answer:
                                    st.session_state[feedback_key] = "correct"
                                    st.session_state[quiz_progress] += 1
                                else:
                                    st.session_state[feedback_key] = "wrong"
                #Shows user answered the question and whether they got it correct or not
                if st.session_state[answered_key]:
                    if st.session_state[feedback_key] == "correct":
                        st.success("Correct! ✅", width="stretch")

                    #Adds specific feedback depending on whether the user got the question correct or not
                    elif st.session_state[feedback_key] == "wrong":
                        st.warning(f"Incorrect ❌ The correct answer is: {correct_answer}", width="stretch")
                    st.write("")
                    #Button to move next question
                    if st.button("Next Question", key=f"next_quiz_{tab_name}", width="stretch"):
                        st.session_state[quiz_index] += 1
                        st.session_state[answered_key] = False
                        st.session_state[feedback_key] = ""
                        st.rerun()
                st.write("")

        with tab1:
            quiz_box = st.container(border=True, height=700)
            with quiz_box:
                format_quiz("tab1", 1)

        with tab2:
            quiz_box_2 = st.container(border=True, height=700)
            with quiz_box_2:
                format_quiz("tab2", 2)

        with tab3:
            quiz_box_3 = st.container(border=True, height=700)
            with quiz_box_3:
                format_quiz("tab3", 3)



#Creating My Rankings Class
class rankings_page(navigation_bar):
    def __init__(self):
        super().__init__()
        self.title = "Rankings 🏆"
    #Creating a method to display my rankings page
    def display_rankings(self):
        col1, col2, col3 = st.columns([1,1.4,1])
        with col2:
            st.title(self.title)
        self.display_navigation_bar()
        #Implement get rankings method from database
        rankings = db.get_rankings()
        #If no one is taking part in the rankings we want to show a warning message to the user
        if not rankings:
            st.warning("No rankings available.")
        else:
            for i, user in enumerate(rankings, start=1):
                name = user[0]
                role = user[1]
                section_1 = user[2]
                section_2 = user[3]
                section_3 = user[4]
                average_score = round(user[5], 1)

                text = (
                    f"{name} ({role}) — Average: {average_score}% "
                    f"| Section 1: {section_1}% | Section 2: {section_2}% | Section 3: {section_3}%"
                )
                #Setting 1st Second and first place in different colour containers 
                if i == 1:
                    st.success(f"🥇 {text}")
                elif i == 2:
                    st.info(f"🥈 {text}")
                elif i == 3:
                    st.warning(f"🥉 {text}")
                else:
                    st.write(f"{i}. {text}")

#Creating My Video Links Class
class video_links_page(navigation_bar):
    def __init__(self):
        super().__init__()
        self.title = "Video Links 🎥"
    #Creating a method to display my video links page
    def display_video_links(self):
        col1, col2, col3 = st.columns([1,1.75,1])
        with col2:
            st.title(self.title)
        self.display_navigation_bar()
        st.subheader("Spinal Management Deep Water Rescue With PXB Board")
        st.video("https://www.youtube.com/watch?v=wZbmTHJiUgQ")
        st.subheader("Spinal Management Shallow Water Rescue with PXB Board")
        st.video("https://www.youtube.com/watch?v=cDj_TDQ8NbE&t=101s")
        st.subheader("Rescue Contact Tows")
        st.video("https://www.youtube.com/watch?v=SZts1gcK3NE")
        st.subheader("Deep Water Recovery and Assisted Lift")
        st.video("https://www.youtube.com/watch?v=DHsu9UeLR4o")
        st.subheader("Torepedo Buoy and Its Use")
        st.video("https://www.youtube.com/watch?v=qNNlpB_WwQM")
        st.subheader("Vice Grip")
        st.video("https://www.youtube.com/watch?v=z6-UhOZ6X1A")
        st.subheader("Extended Arm Roll transfer to Vice Grip")
        st.video("https://www.youtube.com/watch?v=1ANZhOqZs9w")

#Creating My Settings Class
class settings_page(navigation_bar):
    def __init__(self):
        super().__init__()
        self.title = "Settings ⚙️"
        self.dm_header = "Enter Your duty manager's email address"
        self.manager_email = "For Example: leah.stewart@nuffieldhealth.com"
        self.rankings_header ="Do you want to take part in the Rankings Table?"
        self.dm_results = "Do you want your results to go to your duty manager"
    #Creating a method to display my settings page
    def display_settings(self):
        col1, col2, col3 = st.columns([1,1.2,1])
        with col2:
            st.title(self.title)
        self.display_navigation_bar()
        col1, col2, col3 = st.columns([0.5,2,0.5])
        with col2:
            st.subheader(self.dm_header)
            st.text_input("",placeholder=self.manager_email,key="dm_email")
            if st.button("Submit duty manager email"):
                #Validating duty manager email
                if ((len(st.session_state.dm_email) <= 3) or (st.session_state.dm_email.count("@") != 1)):
                    #We Send a warning to the user via st.warning
                    st.warning("Please enter a valid email address")
                else:
                    db.update_dm_email(st.session_state.dm_email,st.session_state.user_id)
                    st.success("You have successfully added your duty manager's email")
            st.space("small")
            #Running my return status check to see what state the user has set the status of
            user = db.return_status(st.session_state.user_id)
            #It will set the value held in the database as a boolean operatorw
            rankings_status = bool(user[8])
            dm_results_status = bool(user[9])
            #Setting My toggle values to the values held in my database
            rankings_toggle = st.toggle(self.rankings_header, value = rankings_status, key = "rankings_toggle")
            dm_results_toggle = st.toggle(self.dm_results, value = dm_results_status , key = "dm_results_toggle")
            #When the toggle status changes it shows the user has updated the status of the toggles
            #Validation for rankings Toggle
            if rankings_toggle != rankings_status:
                    if (rankings_toggle == True):
                        db.update_rankings_status(1,st.session_state.user_id)
                        st.success("You are now taking part in rankings")
                    elif(rankings_toggle == False):
                        db.update_rankings_status(0,st.session_state.user_id)
                        st.success("You are now NOT taking part in rankings")
            #Validation for duty manager results toggle
            if dm_results_toggle != dm_results_status:
                    if (dm_results_toggle == True):
                        db.update_dm_results_status(1,st.session_state.user_id)
                        st.success("You results can now be sent to your duty manager")
                    elif(dm_results_toggle == False):
                        db.update_dm_results_status(0,st.session_state.user_id)
                        st.success("You results will NOT be sent to your duty manager")
            


#Creating my database object and using it's methods
db = Database()
#Running my create quiz / progress methods to create a table in my lg database
db.create_quiz_table()
db.create_user_progress_table()






#Depending on the value of Page we according create an object from the relevant class
if st.session_state.page == "Welcome":
    welcome = welcome_page()
    welcome.display()
elif st.session_state.page == "Login":
    login = login_page()
    login.display_login()
elif st.session_state.page == "Sign Up":
    sign_up = sign_up_page()
    sign_up.display_signup()
elif st.session_state.page == "Reset Password":
    reset_password = reset_password_page()
    reset_password.display_reset_password()
elif st.session_state.page == "Main Menu":
    main_menu = main_menu_page()
    main_menu.display_main_menu()
if st.session_state.page == "Flashcards":
    flashcard = flashcard_page()
    flashcard.display_flashcards()
elif st.session_state.page == "Quiz":
    quiz = quiz_page()
    quiz.display_quiz()
elif st.session_state.page == "Rankings":
    rankings = rankings_page()
    rankings.display_rankings()
elif st.session_state.page == "Videos":
    videos = video_links_page()
    videos.display_video_links()
elif st.session_state.page == "Settings":
    settings = settings_page()
    settings.display_settings()
