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
from datetime import datetime, timedelta
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
            class_schedule.capacity,
            class_schedule.datetime,
            class_schedule.availability
            
        FROM class_schedule
        JOIN class_name ON class_schedule.class_name_id = class_name.class_name_id
        JOIN instructor ON class_schedule.instructor_id = instructor.instructor_id
    """)
    timetable_data = cursor.fetchall()
    cursor.close()
    
    timetable = {}

    for row in timetable_data:
        # Extract datetime
        date = row['datetime']
        # Format time slot
        time_slot = format_time_slot(row['start_time'], row['end_time'])

        if date not in timetable:
            timetable[date] = {}
        if time_slot not in timetable[date]:
            timetable[date][time_slot] = []
        
        timetable[date][time_slot].append({
            'name': row['name'],
            'description': row['description'],
            'availability': row['availability'],
            'instructor': f"{row['first_name']} {row['last_name']}",
        })
    
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
    timetable = generate_timetable()
    dates = [datetime.strptime(selected_date, '%Y-%m-%d') + timedelta(days=i) for i in range(7)]
    
    time_slots = [format_time_slot(timedelta(hours=h), timedelta(hours=h+1)) for h in range(6, 20)]

    return render_template('manager/timetable_manager.html', manager_info=manager_info,
                           timetable=timetable, selected_date=selected_date, dates=dates, time_slots=time_slots)



