from app import app
from flask import flash
from flask import session
from flask import redirect
from flask import url_for
from flask import request, jsonify
from flask import render_template
import mysql.connector
from app.database import getCursor
from app.database import getConnection
from app import connect
import re
import os
from datetime import datetime,time
from flask_login import login_required, LoginManager, UserMixin, login_user
from functools import wraps
import calendar
from datetime import date, timedelta, datetime


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
from collections import defaultdict
def generate_timetable():
    cursor = getCursor()
    cursor.execute("""
        SELECT
            class_name.name,
            instructor.first_name,
            instructor.last_name,
            class_schedule.week,
            class_schedule.pool_type,
            class_schedule.start_time,
            class_schedule.end_time,
            class_schedule.capacity,
            class_schedule.`datetime`,
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
        #if time_slot not in timetable:
        #    timetable[time_slot] = {}

        #if row['week'] not in timetable[time_slot]:
        #    timetable[time_slot][row['week']] = {
        #        'name': row['name'],
        #        'description': row['description'],
        #        'instructor': f"{row['first_name']} {row['last_name']}",
        #        'pool_type': row['pool_type'],
        #        'capacity': row['capacity']
        #    }
        # Populate timetable
        
        if date not in timetable:
            timetable[date] = {}
        if time_slot not in timetable[date]:
            timetable[date][time_slot] = []
        
        timetable[date][time_slot].append({
            'name': row['name'],
            'availability': row['availability'],
            'instructor': f"{row['first_name']} {row['last_name']}",
            'pool_type': row['pool_type']
        })
    
    return timetable

@app.route('/swimming-class/', methods=['GET'])
def swimming_class():
    selected_date = request.args.get('date') or datetime.today().strftime('%Y-%m-%d')
    timetable = generate_timetable()
    dates = [datetime.strptime(selected_date, '%Y-%m-%d') + timedelta(days=i) for i in range(7)]
    
    time_slots = [format_time_slot(timedelta(hours=h), timedelta(hours=h+1)) for h in range(6, 20)]
    
    return render_template('swimming_class.html', timetable=timetable, selected_date=selected_date, dates=dates, time_slots=time_slots)




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
            bookings.schedule_type = 'aerobics class'
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
            bookings.schedule_type = 'swimming lesson'
            AND bookings.member_id = %s
    """, (member_id,))
    return cursor.fetchall()

def get_booking_info(member_id):
    cursor = getCursor()
    cursor.execute("""
        SELECT 
            bookings.*, 
            class_schedule.*, 
            class_name.*, 
            lesson_schedule.*, 
            lesson_name.* 
        FROM bookings 
        LEFT JOIN class_schedule ON bookings.class_id = class_schedule.class_id
        LEFT JOIN class_name ON class_schedule.class_name_id = class_name.class_name_id
        LEFT JOIN lesson_schedule ON bookings.lesson_id = lesson_schedule.lesson_id
        LEFT JOIN lesson_name ON lesson_schedule.lesson_name_id = lesson_name.lesson_name_id
        WHERE bookings.member_id = %s
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

@app.route('/book')
@login_required
@UserType_required('member')
def book():
    user_id = session.get('UserID')
    member_info = get_member_info(user_id)
    class_bookings = get_member_class_bookings(member_info['member_id'])
    lesson_bookings = get_member_lesson_bookings(member_info['member_id'])
    bookings = class_bookings + lesson_bookings
    return render_template('member_booking.html', class_bookings=class_bookings, 
                           lesson_bookings=lesson_bookings, member_info=member_info, bookings=bookings)

@app.route('/cancel_booking', methods=['POST'])
@login_required
@UserType_required('member')
def cancel_booking():
    user_id = session.get('UserID')
    member_info = get_member_info(user_id)
    booking_id = request.form.get('booking_id')

    cursor = getCursor()

    # Check if the booking exists and is confirmed
    cursor.execute("SELECT * FROM bookings WHERE member_id = %s AND booking_id = %s AND booking_status = 'confirmed'", (member_info['member_id'], booking_id))
    booking_to_cancel = cursor.fetchone()

    if booking_to_cancel:
        # Update the booking status to 'cancelled'
        cursor.execute("UPDATE bookings SET booking_status = 'cancelled' WHERE member_id = %s AND booking_id = %s", (member_info['member_id'], booking_id))
        getConnection().commit()
        flash('Booking cancelled successfully.')
    else:
        flash('Booking not found or not confirmed.')

    return redirect(url_for('book'))

@app.route('/add_booking', methods=['POST'])
@login_required
@UserType_required('member')
def add_booking():
    user_id = session.get('UserID')
    member_info = get_member_info(user_id)
    class_id = request.form.get('class_id')

    cursor = getCursor()

    # Check if the class exists and is not full
    cursor.execute("SELECT * FROM classes WHERE class_id = %s AND class_status = 'open'", (class_id,))
    class_to_book = cursor.fetchone()

    if class_to_book:
        # Check if the member has already booked this class
        cursor.execute("SELECT * FROM bookings WHERE member_id = %s AND class_id = %s", (member_info['member_id'], class_id))
        existing_booking = cursor.fetchone()

        if existing_booking:
            flash('You have already booked this class.')
        else:
            # Add the new booking
            cursor.execute("INSERT INTO bookings (member_id, class_id, booking_status) VALUES (%s, %s, 'confirmed')", (member_info['member_id'], class_id))
            getConnection().commit()
            flash('Booking added successfully.')
    else:
        flash('Class not found or not open.')

    return redirect(url_for('book'))


