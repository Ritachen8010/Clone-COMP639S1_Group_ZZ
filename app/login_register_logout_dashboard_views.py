from app import app
from flask import render_template, flash, session, redirect, url_for, request
from flask_bcrypt import Bcrypt
from functools import wraps
import mysql.connector
from datetime import date, timedelta, datetime
from flask_login import login_required, LoginManager, UserMixin, login_user
from app.database import getCursor, getConnection

app.config['SECRET_KEY'] = 'some_random_string_here'
bcrypt = Bcrypt(app)

login_manager = LoginManager()
login_manager.init_app(app)

ROLES = ['Member', 'Instructor', 'Manager']

connection = None

# Stored user name/type/ID 
class User(UserMixin):
    def __init__(self, user_id, Username, UserType, member_id):
        self.id = user_id
        self.Username = Username
        self.UserType = UserType
        self.MemberID = member_id

# To check if user is logged in with the correct user type
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

# Define member info based on user id     
def get_member_info(user_id):
    cursor = getCursor()
    cursor.execute("SELECT * FROM member WHERE user_id = %s", (user_id,))
    return cursor.fetchone()

# Define instructor info based on user id 
def get_instructor_info(user_id):
    cursor = getCursor()
    cursor.execute("SELECT * FROM instructor WHERE user_id = %s", (user_id,))
    return cursor.fetchone()

# Define manager info based on user id
def get_manager_info(user_id):
    cursor = getCursor()
    cursor.execute("SELECT * FROM manager WHERE user_id = %s", (user_id,))
    return cursor.fetchone()

# Load user based on user id
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
                user_id = cursor.lastrowid

                cursor.execute("INSERT INTO member (user_id, title, first_name, last_name, email, phone, address, dob, occupation, health_info) VALUES ( %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                               (user_id, Title, First_name, Last_name, email, phone, address, dob, occupation, health_info))
                member_id = cursor.lastrowid 

                # Handle subscription type selection
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

                # Insert membership record
                cursor.execute("""
                    INSERT INTO memberships (member_id, type, start_date, end_date, membership_fee) 
                    VALUES (%s, %s, %s, %s, %s)
                """, (member_id, selected_subscription['type'], start_date, end_date, selected_subscription['fee']))
                
                # Get the ID of the newly inserted membership
                membership_id = cursor.lastrowid
                
                # Insert payment record
                manager_id = '1'
                cursor.execute("""
                    INSERT INTO payments (member_id, payment_type, membership_id, manager_id, amount, payment_date) 
                    VALUES (%s, 'membership', %s, %s, %s, %s)
                """, (member_id, membership_id, manager_id, selected_subscription['fee'], date.today().isoformat()))
                payment_id = cursor.lastrowid
                
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

    return render_template('homepage/homepage.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Get username and password from the form
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
                    session['UserID'] = user.id 
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
        
    return render_template('homepage/homepage.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.')
    return redirect(url_for('home'))

@app.route('/change_password', methods=['GET', 'POST'])
@login_required
@UserType_required('member', 'instructor', 'manager')
def change_password():
    UserID = session.get('UserID')
    member_info = get_member_info(UserID)
    instructor_info = get_instructor_info(UserID)
    manager_info = get_manager_info(UserID)

    if request.method == 'POST':
        # Get form data
        old_Password = request.form.get('old_Password')
        new_Password = request.form.get('new_Password')
        confirm_Password = request.form.get('confirm_Password')  # Double-confirm password

        if old_Password and new_Password and confirm_Password:
            if new_Password == confirm_Password:  # Confirm that both new passwords match
                cursor = getCursor()

                try:
                    cursor.execute("SELECT password FROM user WHERE user_id = %s", (UserID,))
                    user_record = cursor.fetchone()
                    
                    if user_record and bcrypt.check_password_hash(user_record['password'], old_Password):
                        # Hash the new password
                        hashed_Password = bcrypt.generate_password_hash(new_Password).decode('utf-8')
                        cursor.execute("UPDATE user SET password = %s WHERE user_id = %s", (hashed_Password, UserID))
                        getConnection().commit() 
                        flash("Password changed successfully.")
                    else:
                        flash("Old password is incorrect.")
                except Exception as e:
                    # Handle potential exceptions
                    print("Error while changing password:", e)
                    flash("An error occurred while changing the password.")
                finally:
                    cursor.close() 
            else:
                flash("New passwords do not match.")
        else:
            flash("Please enter old password, new password, and confirm password.")

        return redirect(url_for('manage_profile'))  # Redirect if password change is successful or there is an error message

    return render_template('manage_profile/change_password.html', member_info=member_info, 
                           instructor_info=instructor_info, manager_info=manager_info)

