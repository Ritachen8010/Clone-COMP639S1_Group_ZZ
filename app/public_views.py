from app import app
from flask import render_template
from app.database import getCursor, getConnection
import mysql.connector
from datetime import date, timedelta, datetime
from pprint import pprint



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
    return render_template('homepage.html', timetable=timetable, instructor=instructor)

@app.route('/about_us')
def about_us():
    return render_template('about-us.html')