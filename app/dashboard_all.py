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

@app.template_filter('formatdate')
def format_date_filter(date):
    return date.strftime("%d/%m/%Y")

# Convert time to datetime, 'HH:MM AM/PM' format
def format_time_slot(start_time, end_time):
    start_time_str = (datetime.min + start_time).time().strftime('%I:%M %p')
    end_time_str = (datetime.min + end_time).time().strftime('%I:%M %p')
    return f"{start_time_str}-{end_time_str}"

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

def get_user_info():
    user_id = session.get('UserID')
    cursor = getCursor()
    cursor.execute("SELECT * FROM user WHERE user_id = %s", (user_id,))
    user_info = cursor.fetchone()
    print(user_info)
    cursor.close()
    return user_info

def get_member():
    user_id = session.get('UserID')
    cursor = getCursor()
    cursor.execute("SELECT * FROM member WHERE user_id = %s", (user_id,))
    member_info = cursor.fetchone()
    print(member_info)
    cursor.close()
    return member_info

def get_instructor():
    user_id = session.get('UserID')
    cursor = getCursor()
    cursor.execute("SELECT * FROM instructor WHERE user_id = %s", (user_id,))
    instructor_info = cursor.fetchone()
    print(instructor_info)
    cursor.close()
    return instructor_info

def get_manager():
    user_id = session.get('UserID')
    cursor = getCursor()
    cursor.execute("SELECT * FROM manager WHERE user_id = %s", (user_id,))
    manager_info = cursor.fetchone()
    print(manager_info)
    cursor.close()
    return manager_info

def get_membership_info(member_id):
    cursor = getCursor()
    cursor.execute("SELECT * FROM memberships WHERE member_id = %s", (member_id,))
    membership_info = cursor.fetchone()
    cursor.close()
    return membership_info

@app.route('/dashboard_all')
@login_required
@UserType_required('manager', 'instructor', 'member')
def dashboard_all():
    user_info = get_user_info()
    member_info = get_member()
    instructor_info = get_instructor()
    manager_info = get_manager()
    timetable = generate_timetable()
    if member_info is not None:
        membership_info = get_membership_info(member_info['member_id'])
    else:
        membership_info = None
    return render_template('dashboard_all.html', user_info=user_info, 
                           UserType=user_info['usertype'], member_info=member_info, 
                           instructor_info=instructor_info, manager_info=manager_info, 
                           timetable=timetable, membership_info=membership_info)

@app.route('/dashboard_by_instructor/<first_name>/<last_name>', methods=['GET', 'POST'])
@login_required
@UserType_required('manager', 'instructor', 'member')
def dashboard_by_instructor(first_name, last_name):
    user_info = get_user_info()
    member_info = get_member()
    instructor_info = get_instructor()
    manager_info = get_manager()

    if 'form_submitted' in request.args and 'show_own_timetable' not in request.args:
        timetable = generate_timetable()
    else:
        timetable = generate_filtered_timetable_by_instructor(first_name, last_name)

    return render_template('dashboard_all.html', user_info=user_info, UserType=user_info['usertype'], member_info=member_info, instructor_info=instructor_info, manager_info=manager_info, timetable=timetable)