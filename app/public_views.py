from app import app
from flask import render_template
from flask import request
from app.database import getCursor, getConnection
from datetime import timedelta, datetime
from collections import defaultdict

# Convert time to datetime, 'HH:MM AM/PM' format
def format_time_slot(start_time, end_time):
    start_time_str = (datetime.min + start_time).time().strftime('%I:%M %p')
    end_time_str = (datetime.min + end_time).time().strftime('%I:%M %p')
    return f"{start_time_str}-{end_time_str}"

def generate_timetable():
    current_datetime = datetime.now()
    cursor = getCursor()
    cursor.execute("""
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
    """)
    timetable_data = cursor.fetchall()
    cursor.close()

    # Create a nested dictionary to store the timetable data
    timetable = defaultdict(lambda: defaultdict(list))
    # Iterate over each row in the fetched data
    for row in timetable_data:
        # Check if start_time and end_time are instances of timedelta and convert them to time
        # If not, parse them as strings in the format '%H:%M:%S' to get time objects
        if isinstance(row['start_time'], timedelta):  # Handling timedelta if fetched as such
            start_time = (datetime.min + row['start_time']).time()
        else:
            start_time = datetime.strptime(row['start_time'], '%H:%M:%S').time()

        if isinstance(row['end_time'], timedelta):
            end_time = (datetime.min + row['end_time']).time()
        else:
            end_time = datetime.strptime(row['end_time'], '%H:%M:%S').time()
        # Combine the class date and start time to get a full datetime object
        full_datetime = datetime.combine(row['class_date'], start_time)
        # Create a time slot string in the format '%I:%M %p' - '%I:%M %p'
        time_slot = f"{start_time.strftime('%I:%M %p')} - {end_time.strftime('%I:%M %p')}"

        # Append the class details to the corresponding date and time slot in the timetable
        timetable[row['class_date'].strftime('%Y-%m-%d')][time_slot].append({
            'name': row['class_name'],
            'description': row['description'] if row['description'] else 'No description provided.',
            'availability': row['availability'],
            'instructor': f"{row['first_name']} {row['last_name']}",
            'class_status': row['class_status'],
            'datetime': full_datetime,
            'expired': full_datetime < datetime.now()
        })

    return timetable


def profile_instructor():
    cursor = getCursor()
    cursor.execute("SELECT * FROM instructor")
    instructor = cursor.fetchall()
    cursor.close()
    return instructor

@app.route('/')
def home():
    instructor = profile_instructor()
    return render_template('homepage/homepage.html', instructor=instructor)

@app.route('/about_us')
def about_us():
    return render_template('homepage/about-us.html')

@app.route('/home_swimming_class/')
def home_swimming_class():
    # Get the current date and time
    current_datetime = datetime.now()
    # Get the selected date from the request arguments, default to today's date if not provided
    selected_date = request.args.get('date') or datetime.today().strftime('%Y-%m-%d')
    # Generate a list of dates for the week starting from the selected date
    dates = [datetime.strptime(selected_date, '%Y-%m-%d') + timedelta(days=i) for i in range(7)]
    # Generate a list of time slots from 6 AM to 8 PM
    time_slots = [f"{(datetime.min + timedelta(hours=h)).strftime('%I:%M %p')} - {(datetime.min + timedelta(hours=h+1)).strftime('%I:%M %p')}" for h in range(6, 20)]

    timetable = generate_timetable()

    return render_template('homepage/home_swimming_class.html', timetable=timetable,
                           selected_date=selected_date, dates=dates, time_slots=time_slots,
                           current_datetime=current_datetime)

@app.context_processor
def inject_now():
    return {'now': datetime.now}


