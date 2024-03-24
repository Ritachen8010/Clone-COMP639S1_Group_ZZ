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

app.config['SECRET_KEY'] = 'some_random_string_here'
bcrypt = Bcrypt(app)

login_manager = LoginManager()
login_manager.init_app(app)

ROLES = ['Member', 'Instructor', 'Manager']

connection = None


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


@app.route('/manage_profile', methods=['GET', 'POST'])
@login_required
@UserType_required('member', 'instructor', 'manager')
def manage_profile():
    Username = session.get('Username')
    UserID = session.get('UserID')
    UserType = session.get('UserType')

    cursor = getCursor()

    try:
        if request.method == 'POST':
            new_First_name = request.form.get('First_name')
            new_Last_name = request.form.get('Last_name')
            new_phone = request.form.get('phone')
            new_Title = request.form.get('title')
            new_email = request.form.get('email')
            new_health_info = request.form.get('health_info')
            new_address = request.form.get('address')
            new_dob = request.form.get('dob')
            new_occupation = request.form.get('occupation')
            
            if UserType == 'member':
                cursor.execute("UPDATE member SET first_name = %s, last_name = %s, phone = %s, title = %s, email = %s, health_info = %s, address = %s, dob = %s, occupation = %s WHERE user_id = %s",
                               (new_First_name, new_Last_name, new_phone, new_Title, new_email, new_health_info, new_address, new_dob, new_occupation, UserID))
            elif UserType == 'instructor':
                cursor.execute("UPDATE instructor SET first_name = %s, last_name = %s, phone = %s WHERE user_id = %s",
                               (new_First_name, new_Last_name, new_phone, UserID))
            elif UserType == 'manager':
                cursor.execute("UPDATE manager SET first_name = %s, last_name = %s, phone = %s WHERE user_id = %s",
                               (new_First_name, new_Last_name, new_phone, UserID))

            getConnection().commit()

            flash("Profile updated successfully.")
            
    except Exception as e:
        print("Database update error:", e)
        flash("An error occurred while updating profile.")

    profile_info = {}

    if UserType == 'member':
        cursor.execute("SELECT * FROM member WHERE user_id = %s", (UserID,))
        profile_info = cursor.fetchone()
    elif UserType == 'instructor':
        cursor.execute("SELECT * FROM instructor WHERE user_id = %s", (UserID,))
        profile_info = cursor.fetchone()
    elif UserType == 'manager':
        cursor.execute("SELECT * FROM manager WHERE user_id = %s", (UserID,))
        profile_info = cursor.fetchone()

    return render_template('manage_profile.html', profile_info=profile_info, UserType=UserType)


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
                cursor.execute("SELECT password FROM user WHERE user_id = %s", (UserID,))
                user_record = cursor.fetchone()

                if user_record and bcrypt.check_password_hash(user_record['password'], old_Password):
                    try:
                        # hashed_Password = generate_Password_hash(new_Password)
                        hashed_Password = bcrypt.generate_password_hash(new_Password).decode('utf-8')
                        cursor.execute("UPDATE user SET password = %s WHERE user_id = %s", (hashed_Password, UserID))
                        connection.commit()
                        flash("Password changed successfully.")
                    except Exception as e:
                        # Handle potential exceptions
                        flash("An error occurred while changing the password.")
                else:
                    flash("Old password is incorrect.")
            else:
                flash("New passwords do not match.")
        else:
            flash("Please enter old password, new password, and confirm password.")

        return redirect(url_for('manage_profile'))  # Redirect if password change is successful or there is an error message

    return render_template('change_password.html')