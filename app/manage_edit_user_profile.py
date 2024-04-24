from app import app
from flask import render_template, flash, session, redirect, url_for, request
from flask_bcrypt import Bcrypt
from functools import wraps
import mysql.connector
import os
from datetime import datetime
from flask_login import login_required, LoginManager, UserMixin, login_user
from app.database import getCursor, getConnection
from werkzeug.utils import secure_filename

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

# Define allowed file types for image upload
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
MAX_FILENAME_LENGTH = 500
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS and \
           len(filename) <= MAX_FILENAME_LENGTH

# Define a name for upload image profile
def upload_image_profile(user_id, file):
    UserType = session.get('UserType')
    filename = secure_filename(file.filename)
    unique_filename = f"user_{user_id}_{filename}"

    # Set the upload folder based on the user type
    base_dir = os.path.dirname(os.path.abspath(__file__))
    if UserType == 'member':
        upload_folder = os.path.join(base_dir, 'static/member/')
    elif UserType == 'instructor':
        upload_folder = os.path.join(base_dir, 'static/instructor/')
    elif UserType == 'manager':
        upload_folder = os.path.join(base_dir, 'static/manager/')
    # if UserType == 'member':
    #     upload_folder = 'app/static/member/'
    # elif UserType == 'instructor':
    #     upload_folder = 'app/static/instructor/'
    # elif UserType == 'manager':
    #     upload_folder = 'app/static/manager/'

    file.save(os.path.join(upload_folder, unique_filename))
    cursor = getCursor()
    if UserType == 'member':
        cursor.execute("UPDATE member SET image_profile = %s WHERE user_id = %s", (unique_filename, user_id))
    elif UserType == 'instructor':
        cursor.execute("UPDATE instructor SET image_profile = %s WHERE user_id = %s", (unique_filename, user_id))
    elif UserType == 'manager':
        cursor.execute("UPDATE manager SET image_profile = %s WHERE user_id = %s", (unique_filename, user_id))
    getConnection().commit()

@app.route('/upload_image_profile', methods=['POST'])
@login_required
def handle_upload_image_profile():
    # Check if the post request has the file part
    if 'image_profile' not in request.files:
        flash('No file part')
        return redirect(url_for('manage_profile')) 
    file = request.files['image_profile']
    # If user does not select file, browser also
    # submit an empty part without filename
    if file.filename == '':
        flash('No selected file')
        return redirect(url_for('manage_profile')) 
    if len(file.filename) > 500: # Limit the filename length
        flash('File name is too long')
        return redirect(url_for('manage_profile')) 
    if file and allowed_file(file.filename):
        user_id = session.get('UserID')
        upload_image_profile(user_id, file)
        flash('Profile image successfully uploaded')
        return redirect(url_for('manage_profile')) 
    else:
        flash('Allowed file types are .png, .jpg, .jpeg, .gif')
        return redirect(url_for('manage_profile')) 

@app.route('/manage_profile', methods=['GET', 'POST'])
@login_required
@UserType_required('member', 'instructor', 'manager')
def manage_profile():
    Username = session.get('Username')
    UserID = session.get('UserID')
    UserType = session.get('UserType')
    member_info = get_member_info(UserID)
    instructor_info = get_instructor_info(UserID)
    manager_info = get_manager_info(UserID)

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
            # Added position for instructor and manager
            new_position = request.form.get('position')
            # Added bio for instructor
            new_bio = request.form.get('bio')
            
            if UserType == 'member':
                cursor.execute("UPDATE member SET first_name = %s, last_name = %s, phone = %s, title = %s, email = %s, health_info = %s, address = %s, dob = %s, occupation = %s WHERE user_id = %s",
                               (new_First_name, new_Last_name, new_phone, new_Title, new_email, new_health_info, new_address, new_dob, new_occupation, UserID))
            elif UserType == 'instructor':
                # Added new position and bio | title, email and phone
                cursor.execute("UPDATE instructor SET first_name = %s, last_name = %s, title = %s, phone = %s, email = %s, position = %s, bio = %s WHERE user_id = %s",
                               (new_First_name, new_Last_name, new_Title, new_phone, new_email, new_position, new_bio, UserID))
            elif UserType == 'manager':
                # Added new position, title, email and phone
                cursor.execute("UPDATE manager SET first_name = %s, last_name = %s, title = %s, phone = %s, email = %s, position = %s WHERE user_id = %s",
                               (new_First_name, new_Last_name, new_Title, new_phone, new_email, new_position, UserID))

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

    return render_template('manage_profile/manage_profile.html', profile_info=profile_info, UserType=UserType, 
                           member_info=member_info, instructor_info=instructor_info, manager_info=manager_info)



