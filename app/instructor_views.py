from app import app
from flask import flash
from flask import session
from flask import redirect
from flask import url_for
from flask import request
from flask import render_template
from app.database import getCursor
from app.database import getConnection
from datetime import datetime
from flask_login import login_required, LoginManager, UserMixin, login_user
from functools import wraps
from datetime import timedelta

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

def instructor(user_id):
    cursor = getCursor()
    cursor.execute("SELECT * FROM instructor WHERE user_id = %s", (user_id,))
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

def generate_filtered_timetable_by_instructor(instructor_id):
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
        WHERE instructor.instructor_id = %s
    """, (instructor_id,))
    timetable_data = cursor.fetchall()
    cursor.close()

    filtered_timetable = {}

    for row in timetable_data:
        date = row['datetime']
        time_slot = format_time_slot(row['start_time'], row['end_time'])

        if date not in filtered_timetable:
            filtered_timetable[date] = {}
        if time_slot not in filtered_timetable[date]:
            filtered_timetable[date][time_slot] = []

        filtered_timetable[date][time_slot].append({
            'name': row['name'],
            'description': row['description'],
            'availability': row['availability'],
            'instructor': f"{row['first_name']} {row['last_name']}",
        })
    
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

    return render_template('dashboard/dashboard_instructor.html', user_info=user_info, 
                           instructor_info=instructor_info)

@app.route('/timetable_instructor', methods=['GET'])
@login_required
@UserType_required('instructor')
def timetable_instructor():
    user_id = session.get('UserID')
    instructor_info = instructor(user_id)

    cursor = getCursor()
    cursor.execute("""
        SELECT instructor.instructor_id 
        FROM user 
        JOIN instructor ON user.user_id = instructor.user_id 
        WHERE user.user_id = %s
    """, (user_id,))
    instructor_id = cursor.fetchone()['instructor_id']
    cursor.close()

    selected_date = request.args.get('date') or datetime.today().strftime('%Y-%m-%d')
    dates = [datetime.strptime(selected_date, '%Y-%m-%d') + timedelta(days=i) for i in range(7)]
    
    time_slots = [format_time_slot(timedelta(hours=h), timedelta(hours=h+1)) for h in range(6, 20)]

    # Get the show_own_timetable parameter from the GET request
    show_own_timetable = request.args.get('show_own_timetable')
    if show_own_timetable:
        timetable = generate_filtered_timetable_by_instructor(instructor_id)
    else:
        timetable = generate_timetable()

    return render_template('timetable/timetable_instructor.html', timetable=timetable, 
                           instructor_info=instructor_info, selected_date=selected_date, 
                           dates=dates, time_slots=time_slots)
