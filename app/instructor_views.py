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
from collections import defaultdict

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

# define instructor based on user id 
def instructor(user_id):
    cursor = getCursor()
    cursor.execute("SELECT * FROM instructor WHERE user_id = %s", (user_id,))
    return cursor.fetchone()

# def generate_timetable(selected_date=None):
#     cursor = getCursor()
#     cursor.execute("""
#         SELECT
#             class_name.name,
#             class_name.description,
#             instructor.first_name,
#             instructor.last_name,
#             class_schedule.week,
#             class_schedule.pool_type,
#             class_schedule.start_time,
#             class_schedule.end_time,
#             class_schedule.capacity,
#             class_schedule.datetime,
#             class_schedule.availability
            
#         FROM class_schedule
#         JOIN class_name ON class_schedule.class_name_id = class_name.class_name_id
#         JOIN instructor ON class_schedule.instructor_id = instructor.instructor_id
#     """)
#     timetable_data = cursor.fetchall()
#     cursor.close()
    
#     timetable = {}

#     for row in timetable_data:
#         date = row['datetime']
#         time_slot = format_time_slot(row['start_time'], row['end_time'])

#         if date not in timetable:
#             timetable[date] = {}
#         if time_slot not in timetable[date]:
#             timetable[date][time_slot] = []
        
#         timetable[date][time_slot].append({
#             'name': row['name'],
#             'description': row['description'],
#             'availability': row['availability'],
#             'instructor': f"{row['first_name']} {row['last_name']}",
#         })
    
#     return timetable

# define timetable
def generate_timetable(instructor_id=None):
    cursor = getCursor()
    query = """
        SELECT
            cs.class_id,
            cn.name as class_name,
            cn.description,       
            i.first_name,
            i.last_name,
            cs.week,
            cs.pool_type,
            cs.start_time,
            cs.end_time,
            cs.capacity,
            cs.datetime as class_date,
            cs.availability,
            cs.class_status
        FROM class_schedule AS cs
        JOIN class_name AS cn ON cs.class_name_id = cn.class_name_id
        JOIN instructor AS i ON cs.instructor_id = i.instructor_id
    """
    # If an instructor_id is provided, add a WHERE clause to the query
    if instructor_id:
        query += " WHERE i.instructor_id = %s"
        cursor.execute(query, (instructor_id,))
    else:
        cursor.execute(query)

    # Fetch all rows from the executed query
    timetable_data = cursor.fetchall()
    cursor.close()

    # Initialize a default dictionary to store the timetable
    timetable = defaultdict(lambda: defaultdict(list))
    # Loop through each row in the fetched data
    for row in timetable_data:
        # Convert start and end times to time objects
        start_time_obj = (datetime.min + row['start_time']).time() if isinstance(row['start_time'], timedelta) else datetime.strptime(row['start_time'], '%H:%M:%S').time()
        end_time_obj = (datetime.min + row['end_time']).time() if isinstance(row['end_time'], timedelta) else datetime.strptime(row['end_time'], '%H:%M:%S').time()
        
        # Combine class date and start time to get class datetime
        class_datetime = datetime.combine(row['class_date'], start_time_obj)
        # Format time slot as a string
        time_slot = f"{start_time_obj.strftime('%I:%M %p')} - {end_time_obj.strftime('%I:%M %p')}"

        # Add class details to the timetable dictionary
        timetable[row['class_date'].strftime('%Y-%m-%d')][time_slot].append({
            'class_id': row['class_id'],
            'name': row['class_name'],
            'description': row['description'] if row['description'] else 'No description provided.',
            'availability': row['availability'],
            'instructor': f"{row['first_name']} {row['last_name']}",
            'class_status': row['class_status'],
            'datetime': class_datetime,
            'expired': class_datetime < datetime.now()
        })

    return timetable



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

@app.route('/timetable_instructor')
@login_required
@UserType_required('instructor')
def timetable_instructor():
    user_id = session.get('UserID')
    # Retrieve the instructor information using the user ID
    instructor_info = instructor(user_id) 

    # Get the instructor ID from the instructor info, if it exists
    instructor_id = instructor_info['instructor_id'] if instructor_info else None

    # Get the selected date from the request arguments, default to today's date if not provided
    selected_date = request.args.get('date', default=datetime.today().strftime('%Y-%m-%d'))
    # Generate a list of dates for the week centered around the selected date
    dates = [datetime.strptime(selected_date, '%Y-%m-%d') + timedelta(days=i) for i in range(-3, 4)]
    # Generate a list of time slots for the day
    time_slots = [f"{(datetime.min + timedelta(hours=h)).strftime('%I:%M %p')} - {(datetime.min + timedelta(hours=h+1)).strftime('%I:%M %p')}" for h in range(6, 21)]

    # Generate the timetable filtered by the instructor ID
    timetable = generate_timetable(instructor_id=instructor_id)
    
    return render_template('instructor/timetable_instructor.html', timetable=timetable, 
                           instructor_info=instructor_info, selected_date=selected_date, 
                           dates=dates, time_slots=time_slots)

