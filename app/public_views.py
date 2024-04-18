from app import app
from flask import render_template
from flask import request
from app.database import getCursor, getConnection
from datetime import timedelta, datetime

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

def profile_instructor():
    cursor = getCursor()
    cursor.execute("SELECT * FROM instructor")
    instructor = cursor.fetchall()
    cursor.close()
    return instructor

@app.route('/')
def home():
    timetable = generate_timetable()
    instructor = profile_instructor()
    return render_template('homepage/homepage.html', timetable=timetable, instructor=instructor)

@app.route('/about_us')
def about_us():
    return render_template('homepage/about-us.html')

@app.route('/home_swimming_class/')
def home_swimming_class():
    selected_date = request.args.get('date') or datetime.today().strftime('%Y-%m-%d')
    timetable = generate_timetable()
    dates = [datetime.strptime(selected_date, '%Y-%m-%d') + timedelta(days=i) for i in range(7)]
    
    time_slots = [format_time_slot(timedelta(hours=h), timedelta(hours=h+1)) for h in range(6, 20)]
    
    return render_template('homepage/home_swimming_class.html', timetable=timetable, selected_date=selected_date, dates=dates, time_slots=time_slots)
