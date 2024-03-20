from app import app
from flask import render_template, flash, session, redirect, url_for, request
from flask_bcrypt import Bcrypt
from flask_apscheduler import APScheduler
from functools import wraps
import mysql.connector
import re
from datetime import date, timedelta, datetime
from flask_login import login_required, LoginManager, UserMixin, login_user
from app.database import getCursor, getConnection
from app import connect

app.config['SECRET_KEY'] = 'some_random_string_here'
bcrypt = Bcrypt(app)

login_manager = LoginManager()
login_manager.init_app(app)

ROLES = ['Member', 'Instructor', 'Manager']

connection = None

scheduler = APScheduler()
scheduler.init_app(app)
scheduler.start()


class User(UserMixin):
    def __init__(self, user_id, Username, UserType, member_id):
        self.id = user_id
        self.Username = Username
        self.UserType = UserType
        self.MemberID = member_id

def UserType_required(*UserTypes):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'UserType' not in session or session['UserType'] not in UserTypes:
                flash("You do not have permission to access this page.")
                return redirect(url_for('home'))
            return f(*args, **kwargs)

        return decorated_function

    return decorator

def convert_date_format(original_date):
    try:
        date_object = datetime.strptime(original_date, "%Y-%m-%d")
        new_date_format = date_object.strftime("%d/%m/%Y")
        return new_date_format
    except ValueError:
        return "Invalid Date Format"

@login_manager.user_loader
def load_user(user_id):
    try:
        cursor = getCursor()
        cursor.execute("SELECT user_id, Username, UserType FROM user WHERE user_id = %s", (user_id,))
        user_record = cursor.fetchone()

        if user_record:
            MemberID = None
            if user_record['UserType'] == 'member':
                cursor.execute("SELECT member_id FROM member WHERE user_id = %s", (user_id,))
                member_record = cursor.fetchone()
                if member_record:
                    MemberID = member_record['member_id']

            user = User(user_record['user_id'], user_record['Username'], user_record['UserType'], MemberID)
            return user
    except mysql.connector.Error as err:
        print("Database error: ", err)
        return None
    finally:
        cursor.close()   

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        try:
            First_name = request.form.get('First_name')
            Last_name = request.form.get('Last_name')
            Username = request.form.get('Username')
            Password = request.form.get('Password')
            confirm_Password = request.form.get('confirm_Password')
            phone = request.form.get('phone')
            Title = request.form.get('title')
            email = request.form.get('email')
            health_info = request.form.get('health_info')
            address = request.form.get('address')
            dob = request.form.get('dob')
            occupation = request.form.get('occupation')
            # position = request.form.get('position')
            DateJoined = date.today().isoformat()
            

            # Hash the Password
            hashed_Password = bcrypt.generate_password_hash(Password).decode('utf-8')

            cursor = getCursor()
            cursor.execute("SELECT * FROM user WHERE Username = %s", (Username,))
            existing_user = cursor.fetchone()

            if existing_user:
                flash('Username already exists, please choose a different one.')
                return redirect(url_for('register'))

            if Password == confirm_Password:
                # Insert user information, with the default UserType as 'Member'
                cursor.execute("INSERT INTO user (usertype, username, password) VALUES ('member', %s, %s)", ( Username, hashed_Password))
                user_id = cursor.lastrowid  # Get the last inserted id

                # Insert Member information 
                # Remove the position field from the member table
                cursor.execute("INSERT INTO member (user_id, title, first_name, last_name, email, phone, address, dob, occupation, health_info, join_date) VALUES ( %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
               (user_id, Title, First_name, Last_name, email, phone, address, dob, occupation, health_info, DateJoined))
                getConnection().commit()

                flash('Registration successful! You can now login.')
                return redirect(url_for('login'))
            else:
                flash("Passwords do not match.")
                return redirect(url_for('register'))
        except mysql.connector.Error as err:
            # Handle database errors
            print("Error executing SQL statement: ", err)
            flash(f"An error occurred: {err}")
            return redirect(url_for('register'))

    return render_template('homepage.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Retrieve username and password from the form
        Username = request.form.get('Username').strip()
        entered_Password = request.form.get('Password').strip()
        login_successful = False

        try:
            cursor = getCursor()
            # Fetch user record from the database
            cursor.execute("SELECT user_id, Password, UserType FROM user WHERE Username = %s", (Username,))
            user_record = cursor.fetchone()

            print("User record:", user_record)

            if user_record:
                # Check if entered password matches the stored hash
                if bcrypt.check_password_hash(user_record['Password'], entered_Password):
                    # User authentication successful
                    user_id = user_record['user_id']

                    # Fetch member_id from the member table
                    cursor.execute("SELECT member_id FROM member WHERE user_id = %s", (user_id,))
                    member_record = cursor.fetchone()
                    member_id = member_record['member_id'] if member_record else None

                    # Create a User instance
                    user = User(user_id, Username, user_record['UserType'], member_id)

                    login_user(user)
                    # Set session variables
                    session['UserID'] = user.id  # 设置为 set up session['UserID']
                    session['Username'] = user.Username
                    session['UserType'] = user_record['UserType']
                    session['member_id'] = member_id if member_id else None
                    login_successful = True
                    flash(f'{Username} login successfully.')
                else:
                    flash('Invalid Username or Password')
        except Exception as e:
            flash('An error occurred during login: ' + str(e))
        if login_successful:
            next_page = session.get('next') or url_for('home')  # Redirect to the home page if there is no next page
            return redirect(next_page)
        else:
            # Handling failed login
            flash('Login failed. Please check your credentials.')
            return redirect(url_for('login'))  # Reload the login page

    # For GET requests or if the login logic fails
    return render_template('homepage.html')


@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.')
    return redirect(url_for('home'))


# dashboard_all
@app.route('/dashboard_all')
@login_required
@UserType_required('manager', 'instructor', 'member')
def dashboard_all():
    user_id = session.get('UserID')
    cursor = getCursor()
    cursor.execute("SELECT * FROM user WHERE user_id = %s", (user_id,))
    user_info = cursor.fetchone()
    cursor.execute("SELECT * FROM member")
    members = cursor.fetchall()
    return render_template('dashboard_all.html', user_info=user_info, UserType=session.get('UserType'), members=members)

@app.route('/dashboard_member')
@login_required
@UserType_required('member')
def dashboard_member():
    user_id = session.get('UserID')
    cursor = getCursor()
    cursor.execute("SELECT * FROM user WHERE user_id = %s", (user_id,))
    user_info = cursor.fetchone()
    return render_template('dashboard_member.html', user_info=user_info)

@app.route('/dashboard_instructor')
@login_required
@UserType_required('instructor')
def dashboard_instructor():
    user_id = session.get('UserID')
    cursor = getCursor()
    cursor.execute("SELECT * FROM user WHERE user_id = %s", (user_id,))
    user_info = cursor.fetchone()
    return render_template('dashboard_instructor.html', user_info=user_info)

@app.route('/dashboard_manager')
@login_required
@UserType_required('manager')
def dashboard_manager():
    user_id = session.get('UserID')
    cursor = getCursor()
    cursor.execute("SELECT * FROM user WHERE user_id = %s", (user_id,))
    user_info = cursor.fetchone()
    return render_template('dashboard_manager.html', user_info=user_info)