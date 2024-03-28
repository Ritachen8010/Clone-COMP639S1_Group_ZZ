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

# @app.route('/dashboard_member')
# @login_required
# @UserType_required('member')
# def dashboard_member():
#     user_id = session.get('UserID')
#     cursor = getCursor()
#     cursor.execute("SELECT * FROM user WHERE user_id = %s", (user_id,))
#     user_info = cursor.fetchone()
#     cursor.execute("SELECT * FROM member WHERE user_id = %s", (user_id,))
#     member_info = cursor.fetchone()
#     timetable = generate_timetable()
#     cursor.execute("SELECT * FROM memberships WHERE member_id = %s", (member_info['member_id'],))
#     membership_info = cursor.fetchone()
#     return render_template('dashboard_member.html', user_info=user_info, 
#                            timetable=timetable, member_info=member_info,
#                            membership_info=membership_info)

def get_user_info(user_id):
    cursor = getCursor()
    cursor.execute("SELECT * FROM user WHERE user_id = %s", (user_id,))
    return cursor.fetchone()

def get_member_info(user_id):
    cursor = getCursor()
    cursor.execute("SELECT * FROM member WHERE user_id = %s", (user_id,))
    return cursor.fetchone()

def get_membership_info(member_id):
    cursor = getCursor()
    cursor.execute("SELECT * FROM memberships WHERE member_id = %s", (member_id,))
    return cursor.fetchone()

def get_news_info():
    cursor = getCursor()
    cursor.execute("""
                   SELECT * FROM news
                   ORDER BY publication_date DESC
                   """)
    return cursor.fetchall()

def get_booking(member_id):
    cursor = getCursor()
    cursor.execute("SELECT * FROM bookings WHERE member_id = %s", (member_id,))
    return cursor.fetchall()

def get_member_class_bookings(member_id):
    cursor = getCursor()
    cursor.execute("""
        SELECT 
            bookings.booking_id, 
            class_name.name AS class_name, 
            instructor.first_name, 
            instructor.last_name,
            class_schedule.week, 
            class_schedule.start_time, 
            class_schedule.end_time,
            bookings.schedule_type, 
            bookings.booking_status, 
            bookings.booking_date
        FROM 
            bookings
        LEFT JOIN 
            class_schedule ON bookings.class_id = class_schedule.class_id
        LEFT JOIN 
            class_name ON class_schedule.class_name_id = class_name.class_name_id
        LEFT JOIN 
            instructor ON class_schedule.instructor_id = instructor.instructor_id
        WHERE 
            bookings.schedule_type = 'class'
            AND bookings.member_id = %s
    """, (member_id,))
    return cursor.fetchall()

def get_member_lesson_bookings(member_id):
    cursor = getCursor()
    cursor.execute("""
        SELECT 
            bookings.booking_id, 
            lesson_name.name AS lesson_name, 
            instructor.first_name,
            instructor.last_name,
            lesson_schedule.week, 
            lesson_schedule.start_time, 
            lesson_schedule.end_time,
            bookings.schedule_type, 
            bookings.booking_status, 
            bookings.booking_date
        FROM 
            bookings
        LEFT JOIN 
            lesson_schedule ON bookings.lesson_id = lesson_schedule.lesson_id
        LEFT JOIN 
            lesson_name ON lesson_schedule.lesson_name_id = lesson_name.lesson_name_id
        LEFT JOIN 
            instructor ON lesson_schedule.instructor_id = instructor.instructor_id
        WHERE 
            bookings.schedule_type = 'lesson'
            AND bookings.member_id = %s
    """, (member_id,))
    return cursor.fetchall()

@app.route('/dashboard_member')
@login_required
@UserType_required('member')
def dashboard_member():
    user_id = session.get('UserID')
    user_info = get_user_info(user_id)
    member_info = get_member_info(user_id)
    timetable = generate_timetable()
    membership_info = get_membership_info(member_info['member_id'])
    class_bookings = get_member_class_bookings(member_info['member_id'])
    lesson_bookings = get_member_lesson_bookings(member_info['member_id'])
    bookings = class_bookings + lesson_bookings
    return render_template('dashboard_member.html', user_info=user_info, 
                           timetable=timetable, member_info=member_info,
                           membership_info=membership_info,
                           class_bookings=class_bookings, 
                           lesson_bookings=lesson_bookings, bookings=bookings)

# news for all
@app.route('/news')
@login_required
@UserType_required('member', 'instructor', 'manager')
def news():
    news_info = get_news_info()
    return render_template('news.html', news_info=news_info)

@app.route('/book', methods=['GET', 'POST'])
@login_required
@UserType_required('member')
def book():
    user_id = session.get('UserID')
    member_info = get_member_info(user_id)
    class_bookings = get_member_class_bookings(member_info['member_id'])
    lesson_bookings = get_member_lesson_bookings(member_info['member_id'])

    return render_template('member_booking.html', class_bookings=class_bookings, 
                           lesson_bookings=lesson_bookings, member_info=member_info)

# @app.route('/book_class_lesson', methods=['GET', 'POST'])
# @login_required
# @UserType_required('member')
