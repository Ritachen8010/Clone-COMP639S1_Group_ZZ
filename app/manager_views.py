from app import app
from flask import flash
from flask import session
from flask import redirect
from flask import url_for
from flask import request
from flask import render_template
from app.database import getCursor
from app.database import getConnection
import re
import os
from datetime import datetime, timedelta, time
from flask_login import login_required, LoginManager, UserMixin, login_user
from functools import wraps

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
    
# Convert time to datetime, 'HH:MM AM/PM' format
def format_time_slot(start_time, end_time):
    start_time_str = (datetime.min + start_time).time().strftime('%I:%M %p')
    end_time_str = (datetime.min + end_time).time().strftime('%I:%M %p')
    return f"{start_time_str}-{end_time_str}"

def get_user_info(user_id):
    cursor = getCursor()
    cursor.execute("SELECT * FROM user WHERE user_id = %s", (user_id,))
    return cursor.fetchone()

def get_manager_info(user_id):
    cursor = getCursor()
    cursor.execute("SELECT * FROM manager WHERE user_id = %s", (user_id,))
    return cursor.fetchone()

def generate_timetable():
    current_datetime = datetime.now()
    cursor = getCursor()
    cursor.execute("""
        SELECT
            cs.class_id,
            cn.name,
            i.first_name,
            i.last_name,
            cs.week,
            cs.pool_type,
            cs.start_time,
            cs.end_time,
            cs.capacity,
            cs.datetime,
            cs.availability,
            cs.class_status  # Ensure to fetch the class_status
        FROM class_schedule AS cs
        JOIN class_name AS cn ON cs.class_name_id = cn.class_name_id
        JOIN instructor AS i ON cs.instructor_id = i.instructor_id
        ORDER BY cs.datetime, cs.start_time;
    """)
    rows = cursor.fetchall()
    cursor.close()
    
    timetable = {}
    for row in rows:
        class_datetime = datetime.combine(row['datetime'], row['start_time'])
        # Convert times to strings for easier handling
        time_slot = format_time_slot(row['start_time'], row['end_time'])

        if row['datetime'] not in timetable:
            timetable[row['datetime']] = {}
        if time_slot not in timetable[row['datetime']]:
            timetable[row['datetime']][time_slot] = []

        class_info = {
            'class_id': row['class_id'],
            'name': row['name'],
            'description': row['description'],
            'instructor': f"{row['first_name']} {row['last_name']}",
            'start_datetime': class_datetime,
            'expired': class_datetime < current_datetime,  # Check if the class datetime is before the current datetime
            'status': row['class_status'],  # Store the class status
            'availability': row['availability'] if class_datetime >= current_datetime else 'Expired'  # Change availability to 'Expired' if the datetime has passed
        }
        timetable[row['datetime']][time_slot].append(class_info)

    return timetable

@app.route('/dashboard_manager')
@login_required
@UserType_required('manager')
def dashboard_manager():
    user_id = session.get('UserID')
    user_info = get_user_info(user_id)
    manager_info = get_manager_info(user_id)
    return render_template('dashboard/dashboard_manager.html', user_info=user_info, manager_info=manager_info)

@app.route('/timetable_manager')
@login_required
@UserType_required('manager')
def timetable_manager():
    user_id = session.get('UserID')
    manager_info = get_manager_info(user_id)

    selected_date = request.args.get('date') or datetime.today().strftime('%Y-%m-%d')
    current_datetime = datetime.now()  

    
    timetable = generate_timetable(selected_date)

    return render_template('homepage/home_swimming_class.html', timetable=timetable,
                           selected_date=selected_date, current_datetime=current_datetime)

@app.template_filter('timeformat')
def timeformat(value):
    """Format a time object to 'HH:MM AM/PM' format."""
    if isinstance(value, time): 
        return value.strftime('%I:%M %p')
    elif isinstance(value, datetime): 
        return value.time().strftime('%I:%M %p')
    else:
        return str(value)  # Default case if the input is not time or datetime

@app.route('/review_class')
@login_required
@UserType_required('manager')
def review_class():
    date = request.args.get('date', datetime.today().strftime('%Y-%m-%d'))
    timetable = generate_timetable(date)
    return render_template('review_class.html', timetable=timetable, selected_date=date)

def generate_timetable(date):
    cursor = getCursor()
    query = """
        SELECT cs.class_id, cn.name, i.first_name, i.last_name, cs.week,
               cs.pool_type, cs.start_time, cs.end_time, cs.capacity, cs.availability,
               cs.datetime
        FROM class_schedule AS cs
        JOIN class_name AS cn ON cs.class_name_id = cn.class_name_id
        JOIN instructor AS i ON cs.instructor_id = i.instructor_id
        WHERE DATE(cs.datetime) = %s
        AND cs.start_time >= '06:00:00'
        AND cs.end_time <= '20:00:00'
        ORDER BY cs.start_time;
    """
    cursor.execute(query, (date,))
    rows = cursor.fetchall()
    cursor.close()
    return format_timetable_data(rows)

def format_timetable_data(rows):
    timetable = {}
    for row in rows:
        time_slot = format_time_slot(row['start_time'], row['end_time'])
        if time_slot not in timetable:
            timetable[time_slot] = []
        timetable[time_slot].append({
            'class_id': row['class_id'],
            'name': row['name'],
            'instructor': f"{row['first_name']} {row['last_name']}",
            'pool_type': row['pool_type'],
            'availability': row['availability']
        })
    return timetable

def get_class_info(class_id):
    cursor = getCursor()
    query = """
        SELECT cs.class_id, cn.name, i.first_name, i.last_name, cs.week,
               cs.pool_type, cs.start_time, cs.end_time, cs.capacity, cs.datetime, cs.availability
        FROM class_schedule AS cs
        JOIN class_name AS cn ON cs.class_name_id = cn.class_name_id
        JOIN instructor AS i ON cs.instructor_id = i.instructor_id
        WHERE cs.class_id = %s
    """
    cursor.execute(query, (class_id,))
    class_info = cursor.fetchone()
    cursor.close()
    
    if class_info:
        # Formatting instructor's full name properly
        class_info['instructor'] = f"{class_info['first_name']} {class_info['last_name']}"
        class_info['start_time'] = (datetime.min + class_info['start_time']).time() if isinstance(class_info['start_time'], timedelta) else class_info['start_time']
        class_info['end_time'] = (datetime.min + class_info['end_time']).time() if isinstance(class_info['end_time'], timedelta) else class_info['end_time']
        
    return class_info



def insert_new_class(class_name_id, instructor_id, date, start_time, end_time):
    """Insert a new class into the database."""
    cursor = getCursor()
    cursor.execute("""
        INSERT INTO class_schedule (class_name_id, instructor_id, datetime, start_time, end_time, availability)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (class_name_id, instructor_id, date, start_time, end_time, 15))  # Assuming default capacity and availability is 15
    getConnection().commit()
    cursor.close()

def cancel_existing_class(class_id):
    cursor = getCursor()
    cursor.execute("UPDATE class_schedule SET availability = 0 WHERE class_id = %s", (class_id,))
    cursor.execute("UPDATE bookings SET booking_status = 'cancelled' WHERE class_id = %s AND booking_status = 'confirmed'", (class_id,))
    cursor.execute("UPDATE class_schedule SET class_status = 'Cancelled' WHERE class_id = %s", (class_id,))
    getConnection().commit()
    cursor.close()


@app.route('/add_class', methods=['GET', 'POST'])
@login_required
@UserType_required('manager')
def add_class():
    if request.method == 'POST':
        # Extract form data
        class_name_id = request.form.get('class_name_id')
        instructor_id = request.form.get('instructor_id')
        start_time = request.form.get('start_time')
        date = request.form.get('date')
        
        # Convert start_time to datetime.time object
        start_time = datetime.strptime(start_time, '%I:%M %p').time()
        end_time = (datetime.combine(date.min, start_time) + timedelta(hours=1)).time()

        # Insert new class into the database
        insert_new_class(class_name_id, instructor_id, date, start_time, end_time)
        flash('New class added successfully!', 'success')
        return redirect(url_for('review_class', date=date))
    
    date = request.args.get('date')
    timeslot = request.args.get('timeslot')
    
    return render_template('add_class.html', date=date, timeslot=timeslot)

@app.route('/cancel_class/<int:class_id>', methods=['GET', 'POST'])
@login_required
@UserType_required('manager')
def cancel_class(class_id):
    class_info = get_class_info(class_id)
    if request.method == 'POST':
        cancel_existing_class(class_id)
        flash('Class cancelled successfully!', 'success')
        return redirect(url_for('review_class'))

    return render_template('cancel_class.html', class_info=class_info)

@app.route('/confirm_cancel_class/<int:class_id>', methods=['POST'])
@login_required
@UserType_required('manager')
def confirm_cancel_class(class_id):
    cancel_existing_class(class_id)
    flash('Class cancelled successfully!', 'success')
    return redirect(url_for('review_class'))

