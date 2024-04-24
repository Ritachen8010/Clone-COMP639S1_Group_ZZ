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
from datetime import datetime, timedelta, time, date
from flask_login import login_required, LoginManager, UserMixin, login_user
from functools import wraps
from collections import defaultdict
import mysql.connector

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
    current_datetime = datetime.now()
    cursor = getCursor()
    cursor.execute("""
        SELECT
            cs.class_id,
            cn.name,
            i.first_name,
            i.last_name,
            cs.week,
            cs.pool_type,
            cs.start_time,
            cs.end_time,
            cs.capacity,
            cs.datetime,
            cs.availability,
            cs.class_status  # Ensure to fetch the class_status
        FROM class_schedule AS cs
        JOIN class_name AS cn ON cs.class_name_id = cn.class_name_id
        JOIN instructor AS i ON cs.instructor_id = i.instructor_id
        ORDER BY cs.datetime, cs.start_time;
    """)
    rows = cursor.fetchall()
    cursor.close()
    
    timetable = {}
    for row in rows:
        class_datetime = datetime.combine(row['datetime'], row['start_time'])
        # Convert times to strings for easier handling
        time_slot = format_time_slot(row['start_time'], row['end_time'])

        if row['datetime'] not in timetable:
            timetable[row['datetime']] = {}
        if time_slot not in timetable[row['datetime']]:
            timetable[row['datetime']][time_slot] = []

        class_info = {
            'class_id': row['class_id'],
            'name': row['name'],
            'description': row['description'],
            'instructor': f"{row['first_name']} {row['last_name']}",
            'start_datetime': class_datetime,
            'expired': class_datetime < current_datetime,  # Check if the class datetime is before the current datetime
            'status': row['class_status'],  # Store the class status
            'availability': row['availability'] if class_datetime >= current_datetime else 'Expired'  # Change availability to 'Expired' if the datetime has passed
        }
        timetable[row['datetime']][time_slot].append(class_info)

    return timetable

@app.route('/dashboard_manager')
@login_required
@UserType_required('manager')
def dashboard_manager():
    user_id = session.get('UserID')
    user_info = get_user_info(user_id)
    manager_info = get_manager_info(user_id)
    return render_template('dashboard/dashboard_manager.html', user_info=user_info, manager_info=manager_info)

# @app.route('/timetable_manager')
# @login_required
# @UserType_required('manager')
# def timetable_manager():
#     current_datetime = datetime.now()
#     user_id = session.get('UserID')
#     manager_info = get_manager_info(user_id)

#     selected_date = request.args.get('date', default=datetime.today().strftime('%Y-%m-%d'))
#     timetable = generate_timetable()

#     dates = [datetime.strptime(selected_date, '%Y-%m-%d') + timedelta(days=i) for i in range(-3, 4)]
#     time_slots = [f"{(datetime.min + timedelta(hours=h)).strftime('%I:%M %p')} - {(datetime.min + timedelta(hours=h+1)).strftime('%I:%M %p')}" for h in range(6, 21)]

#     return render_template('manager/timetable_manager.html', timetable=timetable,
#                            selected_date=selected_date, dates=dates, time_slots=time_slots,
#                            current_datetime=current_datetime, manager_info=manager_info)

@app.template_filter('timeformat')
def timeformat(value):
    """Format a time object to 'HH:MM AM/PM' format."""
    if isinstance(value, time): 
        return value.strftime('%I:%M %p')
    elif isinstance(value, datetime): 
        return value.time().strftime('%I:%M %p')
    else:
        return str(value)  # Default case if the input is not time or datetime

@app.route('/review_class')
@login_required
@UserType_required('manager')
def review_class():
    user_id = session.get('UserID')
    manager_info = get_manager_info(user_id)
    date = request.args.get('date', datetime.today().strftime('%Y-%m-%d'))
    timetable, available_slots = generate_timetable(date)  # Make sure two values are expected here
    return render_template('manager/review_class.html', timetable=timetable, available_slots=available_slots, 
                           selected_date=date, manager_info=manager_info)


def generate_timetable(date):
    cursor = getCursor()
    query = """
        SELECT cs.class_id, cn.name, i.first_name, i.last_name, cs.week,
               cs.pool_type, cs.start_time, cs.end_time, cs.capacity, cs.availability,
               cs.datetime, cs.class_status
        FROM class_schedule AS cs
        JOIN class_name AS cn ON cs.class_name_id = cn.class_name_id
        JOIN instructor AS i ON cs.instructor_id = i.instructor_id
        WHERE DATE(cs.datetime) = %s
        AND cs.start_time >= '06:00:00'
        AND cs.end_time <= '20:00:00'
        ORDER BY cs.start_time;
    """
    cursor.execute(query, (date,))
    rows = cursor.fetchall()
    cursor.close()
    
    timetable = {}
    available_slots = []  # This will capture slots for 'Empty' status
    for row in rows:
        time_slot = format_time_slot(row['start_time'], row['end_time'])
        if row['class_status'] == 'Empty':
            available_slots.append(time_slot)  # Add to available slots if status is 'Empty'

        if time_slot not in timetable:
            timetable[time_slot] = {
                'classes': [],
                'status': row['class_status']
            }

        timetable[time_slot]['classes'].append({
            'class_id': row['class_id'],
            'name': row['name'],
            'instructor': f"{row['first_name']} {row['last_name']}",
            'pool_type': row['pool_type'],
            'availability': row['availability']
        })

    return timetable, available_slots




def generate_time_slots(start, end, duration):
    start = datetime.strptime(start, '%H:%M:%S')
    end = datetime.strptime(end, '%H:%M:%S')
    slots = []

    while start < end:
        slot_end = start + timedelta(minutes=duration)
        slots.append(f"{start.strftime('%H:%M')} - {slot_end.strftime('%H:%M')}")
        start = slot_end

    return slots


def get_class_info(class_id):
    cursor = getCursor()
    query = """
        SELECT cs.class_id, cn.name, i.first_name, i.last_name, cs.week,
               cs.pool_type, cs.start_time, cs.end_time, cs.capacity, cs.datetime, cs.availability
        FROM class_schedule AS cs
        JOIN class_name AS cn ON cs.class_name_id = cn.class_name_id
        JOIN instructor AS i ON cs.instructor_id = i.instructor_id
        WHERE cs.class_id = %s
    """
    cursor.execute(query, (class_id,))
    class_info = cursor.fetchone()
    cursor.close()
    
    if class_info:
        # Formatting instructor's full name properly
        class_info['instructor'] = f"{class_info['first_name']} {class_info['last_name']}"
        class_info['start_time'] = (datetime.min + class_info['start_time']).time() if isinstance(class_info['start_time'], timedelta) else class_info['start_time']
        class_info['end_time'] = (datetime.min + class_info['end_time']).time() if isinstance(class_info['end_time'], timedelta) else class_info['end_time']
        
    return class_info



def insert_new_class(class_name_id, instructor_id, date, start_time, end_time):
    """Insert a new class into the database."""
    cursor = getCursor()
    cursor.execute("""
        INSERT INTO class_schedule (class_name_id, instructor_id, datetime, start_time, end_time, availability)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (class_name_id, instructor_id, date, start_time, end_time, 15))  # default capacity and availability is 15
    getConnection().commit()
    cursor.close()

def cancel_existing_class(class_id):
    cursor = getCursor()
    cursor.execute("UPDATE class_schedule SET availability = 0 WHERE class_id = %s", (class_id,))
    cursor.execute("UPDATE bookings SET booking_status = 'cancelled' WHERE class_id = %s AND booking_status = 'confirmed'", (class_id,))
    cursor.execute("UPDATE class_schedule SET class_status = 'Cancelled' WHERE class_id = %s", (class_id,))
    getConnection().commit()
    cursor.close()

def convert_time(time_str):
    """Convert 12-hour formatted time with AM/PM to 24-hour format."""
    return datetime.strptime(time_str, '%I:%M %p').strftime('%H:%M:%S')

@app.route('/add_class', methods=['GET', 'POST'])
@login_required
@UserType_required('manager')
def add_class():
    user_id = session.get('UserID')
    manager_info = get_manager_info(user_id)
    if request.method == 'POST':
        class_name_id = request.form.get('class_name_id')
        instructor_id = request.form.get('instructor_id')
        date = request.form.get('datetime')
        time_slot = request.form.get('time_slot')

        try:
            start_time, end_time = [convert_time(time.strip()) for time in time_slot.split("-")]
        except ValueError:
            flash("Invalid time slot format. Please use the format 'HH:MM AM - HH:MM PM'.", 'error')
            return redirect(url_for('add_class'))

        cursor = getCursor()
        cursor.execute("""
            UPDATE class_schedule
            SET class_name_id = %s, instructor_id = %s, class_status = 'Open'
            WHERE datetime = %s AND start_time = %s AND end_time = %s
            AND class_status IN ('Empty', 'Cancelled')
        """, (class_name_id, instructor_id, date, start_time, end_time))
        updated_rows = cursor.rowcount
        getConnection().commit()
        cursor.close()

        if updated_rows == 0:
            flash('No available slots to update or slot not found.', 'error')
        else:
            flash('Class updated successfully!', 'success')

        return redirect(url_for('review_class'))

    # Fetch class names and instructors for dropdown
    cursor = getCursor()
    cursor.execute("SELECT class_name_id, name FROM class_name")
    class_names = cursor.fetchall()
    cursor.execute("SELECT instructor_id, CONCAT(first_name, ' ', last_name) as name FROM instructor")
    instructors = cursor.fetchall()
    cursor.close()

    date = request.args.get('date', datetime.today().strftime('%Y-%m-%d'))
    _, available_slots = generate_timetable(date)  # Fetch available slots for the selected date

    return render_template('manager/add_class.html', available_slots=available_slots, date=date, 
                           class_names=class_names, instructors=instructors, manager_info=manager_info)


@app.route('/cancel_class/<int:class_id>', methods=['GET', 'POST'])
@login_required
@UserType_required('manager')
def cancel_class(class_id):
    user_id = session.get('UserID')
    manager_info = get_manager_info(user_id)
    class_info = get_class_info(class_id)
    if request.method == 'POST':
        cancel_existing_class(class_id)
        flash('Class cancelled successfully!', 'success')
        return redirect(url_for('review_class'))

    return render_template('manager/cancel_class.html', class_info=class_info,
                           manager_info=manager_info)

@app.route('/confirm_cancel_class/<int:class_id>', methods=['POST'])
@login_required
@UserType_required('manager')
def confirm_cancel_class(class_id):
    cancel_existing_class(class_id)
    flash('Class cancelled successfully!', 'success')
    return redirect(url_for('review_class'))

@app.route('/edit_class/', methods=['GET', 'POST'])
@login_required
@UserType_required('manager')
def edit_class():
    user_id = session.get('UserID')
    manager_info = get_manager_info(user_id)
    cursor = getCursor()
    class_id = request.form.get('class_id')
    selected_class = None

    # Fetch all classes for dropdown
    cursor.execute("SELECT class_name_id, name FROM class_name ORDER BY name")
    classes = cursor.fetchall()

    if request.method == 'POST':
        description = request.form.get('description')

        if 'update' in request.form:
            # Update class description
            cursor.execute("UPDATE class_name SET description = %s WHERE class_name_id = %s", (description, class_id))
            getConnection().commit()
            flash('Class description updated successfully!', 'success')

        elif 'delete' in request.form:
            try:
                # Attempt to delete the class
                cursor.execute("DELETE FROM class_name WHERE class_name_id = %s", (class_id,))
                getConnection().commit()
                flash('Class deleted successfully!', 'success')
            except mysql.connector.Error as e:
                if 'foreign key constraint fails' in str(e):
                    flash('Cannot delete class: it is being used in scheduled classes.', 'error')
                else:
                    flash(f'Failed to delete class: {str(e)}', 'error')

    if class_id:
        cursor.execute("SELECT class_name_id, name, description FROM class_name WHERE class_name_id = %s", (class_id,))
        selected_class = cursor.fetchone()

    return render_template('manager/edit_class.html', classes=classes, selected_class=selected_class,
                           manager_info=manager_info)

#Report
@app.route('/financial_report', methods=['GET', 'POST'])
@login_required
@UserType_required('manager')
def financial_report():
    user_id = session.get('UserID')
    manager_info = get_manager_info(user_id)
    current_month = datetime.now().month
    current_year = datetime.now().year

    if request.method == 'POST':
        selected_year = int(request.form.get('year', datetime.now().year))
        session['selected_year'] = selected_year  # Store the selected year in the session
        selected_month = int(request.form.get('month', datetime.now().month))
        session['selected_month'] = selected_month
    else:
        selected_year = session.get('selected_year', datetime.now().year)
        selected_month = session.get('selected_month', datetime.now().month)

    cursor = getCursor()
    cursor.execute("""
        SELECT MONTH(p.payment_date) as month, SUM(p.amount) as total_payments
        FROM payments p
        WHERE YEAR(p.payment_date) = %s AND p.payment_type = 'membership'
        GROUP BY MONTH(p.payment_date)
    """, (selected_year,))
    
    monthly_payments = cursor.fetchall()

    cursor.execute("""
        SELECT MONTH(r.refund_date) as month, SUM(r.refund_amount) as total_refunds
        FROM memberships_refund r
        WHERE YEAR(r.refund_date) = %s
        GROUP BY MONTH(r.refund_date)
    """, (selected_year,))
    
    monthly_refunds = cursor.fetchall()

    # Convert the result to a dictionary
    payments_dict = {result['month']: result['total_payments'] for result in monthly_payments}
    refunds_dict = {result['month']: result['total_refunds'] for result in monthly_refunds}

    # Create a list for each month of the year
    payments_list = [payments_dict.get(month, 0) for month in range(1, 13)]
    refunds_list = [refunds_dict.get(month, 0) for month in range(1, 13)]

    cursor.execute("""
        SELECT SUM(p.amount) as total_payments
        FROM payments p
        WHERE YEAR(p.payment_date) = %s
    """, (selected_year,))
    
    annual_payments = cursor.fetchone()['total_payments']

    cursor.execute("""
        SELECT SUM(r.refund_amount) as total_refunds
        FROM memberships_refund r
        WHERE YEAR(r.refund_date) = %s
    """, (selected_year,))
    
    annual_refunds = cursor.fetchone()['total_refunds']
    cursor.close()

    return render_template('manager/financial_report.html', manager_info=manager_info,
                           monthly_payments=payments_list, monthly_refunds=refunds_list,
                           annual_payments=annual_payments, annual_refunds=annual_refunds,
                           selected_year=selected_year, current_year=current_year)

@app.route('/monthly_class_report', methods=['GET', 'POST'])
@login_required
@UserType_required('manager')
def monthly_class_report():
    user_id = session.get('UserID')
    manager_info = get_manager_info(user_id)
    current_month = datetime.now().month
    current_year = datetime.now().year

    if request.method == 'POST':
        selected_year = int(request.form.get('selected_year', current_year))
        selected_month = int(request.form.get('selected_month', current_month))
        session['selected_year'] = selected_year  # Store the selected year in the session
        session['selected_month'] = selected_month  # Store the selected month in the session
    else:
        selected_year = session.get('selected_year', current_year)
        selected_month = session.get('selected_month', current_month)

    cursor = getCursor()
    cursor.execute("""
        SELECT cn.name, COUNT(b.class_id) as total_bookings
        FROM bookings b
        JOIN class_schedule cs ON b.class_id = cs.class_id
        JOIN class_name cn ON cs.class_name_id = cn.class_name_id
        WHERE MONTH(b.booking_date) = %s AND YEAR(b.booking_date) = %s
        AND b.booking_status = 'confirmed'
        GROUP BY cn.name
        ORDER BY total_bookings DESC
    """, (selected_month, selected_year))
    
    class_bookings = cursor.fetchall()
    cursor.close()

    # Calculate total bookings for percentage calculations
    total_bookings = sum([booking['total_bookings'] for booking in class_bookings])
    # Prepare percentages
    for booking in class_bookings:
        booking['percentage'] = (booking['total_bookings'] / total_bookings) * 100 if total_bookings > 0 else 0

    return render_template('manager/monthly_class_report.html', class_bookings=class_bookings,
                           total_bookings=total_bookings, month=selected_month, year=selected_year,
                           manager_info=manager_info, current_year=current_year)



