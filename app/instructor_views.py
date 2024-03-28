from app import app
from flask import flash
from flask import session
from flask import redirect
from flask import url_for
from flask import request
from flask import render_template
import mysql.connector
from app.database import getCursor
from app.database import getConnection
from app import connect
import re
import os
from datetime import datetime
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

@app.context_processor
def timeformat_functions():
    def format_time_slot(time=None):
        if time is None:
            return 'N/A'
        time_str = (datetime.min + time).time().strftime('%I:%M %p')
        return time_str
    return dict(format_time_slot=format_time_slot)

# Convert time to datetime, 'HH:MM AM/PM' format
def format_time_slot(start_time, end_time):
    start_time_str = (datetime.min + start_time).time().strftime('%I:%M %p')
    end_time_str = (datetime.min + end_time).time().strftime('%I:%M %p')
    return f"{start_time_str}-{end_time_str}"

@app.template_filter('formatdate')
def format_date_filter(date):
    return date.strftime("%d/%m/%Y")

def generate_timetable():
    cursor = getCursor()
    cursor.execute("""
        SELECT
            class_name.name,
            class_name.description,
            instructor.first_name,
            instructor.last_name,
            class_schedule.week,
            class_schedule.pool_type,
            class_schedule.start_time,
            class_schedule.end_time,
            class_schedule.capacity
        FROM class_schedule
        JOIN class_name ON class_schedule.class_name_id = class_name.class_name_id
        JOIN instructor ON class_schedule.instructor_id = instructor.instructor_id
    """)
    timetable_data = cursor.fetchall()
    cursor.close()

    timetable_data.sort(key=lambda row: row['start_time'])
    
    timetable = {}

    for row in timetable_data:
        time_slot = format_time_slot(row['start_time'], row['end_time'])

        if time_slot not in timetable:
            timetable[time_slot] = {}

        if row['week'] not in timetable[time_slot]:
            timetable[time_slot][row['week']] = {
                'name': row['name'],
                'description': row['description'],
                'instructor': f"{row['first_name']} {row['last_name']}",
                'pool_type': row['pool_type'],
                'capacity': row['capacity']
            }
    
    return timetable

def generate_filtered_timetable_by_instructor(first_name, last_name):
    full_name = " ".join([first_name, last_name])
    cursor = getCursor()
    cursor.execute("""
        SELECT
            class_name.name,
            class_name.description,
            instructor.first_name,
            instructor.last_name,
            class_schedule.week,
            class_schedule.pool_type,
            class_schedule.start_time,
            class_schedule.end_time,
            class_schedule.capacity
        FROM class_schedule
        JOIN class_name ON class_schedule.class_name_id = class_name.class_name_id
        JOIN instructor ON class_schedule.instructor_id = instructor.instructor_id
        WHERE CONCAT(instructor.first_name, ' ', instructor.last_name) = %s
    """, (full_name,))
    timetable_data = cursor.fetchall()
    cursor.close()

    timetable_data.sort(key=lambda row: row['start_time'])
    
    filtered_timetable = {}

    for row in timetable_data:
        time_slot = format_time_slot(row['start_time'], row['end_time'])

        if time_slot not in filtered_timetable:
            filtered_timetable[time_slot] = {}

        if row['week'] not in filtered_timetable[time_slot]:
            filtered_timetable[time_slot][row['week']] = {
                'name': row['name'],
                'description': row['description'],
                'instructor': f"{row['first_name']} {row['last_name']}",
                'pool_type': row['pool_type'],
                'capacity': row['capacity']
            }
    
    return filtered_timetable

@app.route('/dashboard_instructor')
@login_required
@UserType_required('instructor')
def dashboard_instructor():
    user_id = session.get('UserID')
    cursor = getCursor()
    cursor.execute("SELECT * FROM user WHERE user_id = %s", (user_id,))
    user_info = cursor.fetchone()
    cursor.execute("SELECT * FROM instructor WHERE user_id = %s", (user_id,))
    instructor_info = cursor.fetchone()

    show_own_timetable = request.args.get('show_own_timetable')
    if show_own_timetable:
        timetable = generate_filtered_timetable_by_instructor(instructor_info['first_name'], instructor_info['last_name'])
    else:
        timetable = generate_timetable()

    return render_template('dashboard_instructor.html', user_info=user_info, timetable=timetable, instructor_info=instructor_info)


# @app.route('/dashboard_instructor')
# @login_required
# @UserType_required('instructor')
# def dashboard_instructor():
#     user_id = session.get('UserID')
#     cursor = getCursor()
#     cursor.execute("SELECT * FROM user WHERE user_id = %s", (user_id,))
#     user_info = cursor.fetchone()
#     cursor.execute("SELECT * FROM instructor WHERE user_id = %s", (user_id,))
#     instructor_info = cursor.fetchone()
#     timetable = generate_timetable()
#     return render_template('dashboard_instructor.html', user_info=user_info, timetable=timetable, instructor_info=instructor_info)


