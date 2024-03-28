from app import app
from flask import render_template, flash, session, redirect, url_for, request
from flask_bcrypt import Bcrypt
# from flask_apscheduler import APScheduler
from functools import wraps
import mysql.connector
import re
from datetime import date, timedelta, datetime
from flask_login import login_required, LoginManager, UserMixin, login_user
from app.database import getCursor, getConnection
from app import connect
from app.public_views import generate_timetable

app.config['SECRET_KEY'] = 'some_random_string_here'
bcrypt = Bcrypt(app)

login_manager = LoginManager()
login_manager.init_app(app)

ROLES = ['Member', 'Instructor', 'Manager']

connection = None

# scheduler = APScheduler()
# scheduler.init_app(app)
# scheduler.start()


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
                # Insert user information, with the default UserType as 'member'
                cursor.execute("INSERT INTO user (usertype, username, password) VALUES ('member', %s, %s)", (Username, hashed_Password))
                user_id = cursor.lastrowid  # Get the last inserted id

                # Insert Member information
                # cursor.execute("INSERT INTO member (user_id, title, first_name, last_name, email, phone, address, dob, occupation, health_info, join_date) VALUES ( %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                #                (user_id, Title, First_name, Last_name, email, phone, address, dob, occupation, health_info, DateJoined))
                # removed date of join
                cursor.execute("INSERT INTO member (user_id, title, first_name, last_name, email, phone, address, dob, occupation, health_info) VALUES ( %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                               (user_id, Title, First_name, Last_name, email, phone, address, dob, occupation, health_info))
                member_id = cursor.lastrowid  # Get the last inserted id for member

                # New code to handle subscription type selection
                subscription_type = request.form.get('subscription_type')

                # Define subscription options and corresponding fees
                subscription_options = {
                    "annual": {"type": "Annual", "fee": 700, "duration": 365},
                    "monthly": {"type": "Monthly", "fee": 60, "duration": 30},
                    "6_month": {"type": "6 Month", "fee": 360, "duration": 180}
                }

                # Check if the selected subscription type is valid
                if subscription_type not in subscription_options:
                    flash("Invalid subscription type selected.")
                    return redirect(url_for('register'))

                # Extract subscription details based on the selected type
                selected_subscription = subscription_options[subscription_type]

                # Calculate start and end dates
                start_date = date.today().isoformat()
                end_date = (date.today() + timedelta(days=selected_subscription['duration'])).isoformat()

                # Insert payment record
                cursor.execute("INSERT INTO payments (member_id, payment_type, amount, payment_date) VALUES (%s, 'membership', %s, %s)",
                               (member_id, selected_subscription['fee'], date.today().isoformat()))
                payment_id = cursor.lastrowid

                # Insert membership record
                cursor.execute("INSERT INTO memberships (member_id, type, start_date, end_date, membership_fee) VALUES (%s, %s, %s, %s, %s)",
                               (member_id, selected_subscription['type'], start_date, end_date, selected_subscription['fee']))

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

    # Fetch timetable data
    timetable = generate_timetable()
    
    # Render the template and pass the timetable variable
    return render_template('homepage.html', timetable=timetable)



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
        # changed to redirect to different pages based on the user type    
        if login_successful:
            user_type = session['UserType']
            if user_type == 'manager':
                next_page = url_for('dashboard_manager')
            elif user_type == 'instructor':
                next_page = url_for('dashboard_instructor')
            elif user_type == 'member':
                next_page = url_for('dashboard_member')
            if next_page:
                return redirect(next_page)
        else:
            # Handling failed login
            flash('Login failed. Please check your credentials.')
            return redirect(url_for('login'))  # Reload the login page
        
        # if login_successful:
        #     next_page = session.get('next') or url_for('dashboard_all')  
        #     return redirect(next_page)
        # else:
        #     # Handling failed login
        #     flash('Login failed. Please check your credentials.')
        #     return redirect(url_for('login'))  
        # Reload the login page

    # For GET requests or if the login logic fails
    timetable = generate_timetable()  # Generate the timetable
    return render_template('homepage.html', timetable=timetable)

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.')
    return redirect(url_for('home'))


# # dashboard_all
# @app.route('/dashboard_all')
# @login_required
# @UserType_required('manager', 'instructor', 'member')
# def dashboard_all():
#     user_id = session.get('UserID')
#     cursor = getCursor()
#     cursor.execute("SELECT * FROM user WHERE user_id = %s", (user_id,))
#     user_info = cursor.fetchone()
#     cursor.execute("SELECT * FROM member")
#     members = cursor.fetchall()
#     return render_template('dashboard_all.html', user_info=user_info, UserType=session.get('UserType'), members=members)

# @app.route('/dashboard_member')
# @login_required
# @UserType_required('member')
# def dashboard_member():
#     user_id = session.get('UserID')
#     cursor = getCursor()
#     cursor.execute("SELECT * FROM user WHERE user_id = %s", (user_id,))
#     user_info = cursor.fetchone()
#     return render_template('dashboard_member.html', user_info=user_info)

# @app.route('/dashboard_instructor')
# @login_required
# @UserType_required('instructor')
# def dashboard_instructor():
#     user_id = session.get('UserID')
#     cursor = getCursor()
#     cursor.execute("SELECT * FROM user WHERE user_id = %s", (user_id,))
#     user_info = cursor.fetchone()
#     return render_template('dashboard_instructor.html', user_info=user_info)

# @app.route('/dashboard_manager')
# @login_required
# @UserType_required('manager')
# def dashboard_manager():
#     user_id = session.get('UserID')
#     cursor = getCursor()
#     cursor.execute("SELECT * FROM user WHERE user_id = %s", (user_id,))
#     user_info = cursor.fetchone()
#     return render_template('dashboard_manager.html', user_info=user_info)



@app.route('/change_password', methods=['GET', 'POST'])
@login_required
@UserType_required('member', 'instructor', 'manager')
def change_password():
    UserID = session.get('UserID')

    if request.method == 'POST':
        # Get form data
        old_Password = request.form.get('old_Password')
        new_Password = request.form.get('new_Password')
        confirm_Password = request.form.get('confirm_Password')  # New confirm password

        if old_Password and new_Password and confirm_Password:
            if new_Password == confirm_Password:  # Confirm that both new passwords match
                cursor = getCursor()
                # cursor.execute("SELECT password FROM user WHERE user_id = %s", (UserID,))
                # user_record = cursor.fetchone()
                try:
                    cursor.execute("SELECT password FROM user WHERE user_id = %s", (UserID,))
                    user_record = cursor.fetchone()
                    
                    if user_record and bcrypt.check_password_hash(user_record['password'], old_Password):
                        # Hash the new password
                        hashed_Password = bcrypt.generate_password_hash(new_Password).decode('utf-8')
                        cursor.execute("UPDATE user SET password = %s WHERE user_id = %s", (hashed_Password, UserID))
                        getConnection().commit()  # Corrected the commit call
                        flash("Password changed successfully.")
                    else:
                        flash("Old password is incorrect.")
                except Exception as e:
                    # Handle potential exceptions
                    print("Error while changing password:", e)
                    flash("An error occurred while changing the password.")
                finally:
                    cursor.close()  # Close the cursor
            else:
                flash("New passwords do not match.")
        else:
            flash("Please enter old password, new password, and confirm password.")

        return redirect(url_for('manage_profile'))  # Redirect if password change is successful or there is an error message

    return render_template('change_password.html')

                # if user_record and bcrypt.check_password_hash(user_record['password'], old_Password):
                #     try:
                        # Hash the new password
    #                     hashed_Password = bcrypt.generate_password_hash(new_Password).decode('utf-8')
    #                     cursor.execute("UPDATE user SET password = %s WHERE user_id = %s", (hashed_Password, UserID))
    #                     getConnection().commit()  # Corrected the commit call
    #                     flash("Password changed successfully.")
    #                 except Exception as e:
    #                     # Handle potential exceptions
    #                     print("Error while changing password:", e)
    #                     flash("An error occurred while changing the password.")
    #             else:
    #                 flash("Old password is incorrect.")
    #         else:
    #             flash("New passwords do not match.")
    #     else:
    #         flash("Please enter old password, new password, and confirm password.")

    #     cursor.close()  # Close the cursor

    #     return redirect(url_for('manage_profile'))  # Redirect if password change is successful or there is an error message

    # return render_template('change_password.html')

