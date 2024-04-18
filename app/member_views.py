from app import app
from flask import flash
from flask import session
from flask import redirect
from flask import url_for
from flask import request
from flask import render_template
from app.database import getCursor
from app.database import getConnection
from flask_login import login_required, LoginManager, UserMixin, login_user
from functools import wraps
<<<<<<< HEAD
from datetime import time, timedelta, datetime
from collections import defaultdict
from flask_login import current_user
from collections import defaultdict
=======
import calendar
from datetime import date, timedelta, datetime, time
>>>>>>> 7a1ab03987d10d39e67546081f7c2767bbc8d4e0


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
<<<<<<< HEAD
=======
from collections import defaultdict
def generate_timetable():
    cursor = getCursor()
    cursor.execute("""
        SELECT
            cs.class_id,  # Ensure this is included
            cn.name,
            i.first_name,
            i.last_name,
            cs.week,
            cs.pool_type,
            cs.start_time,
            cs.end_time,
            cs.capacity,
            cs.datetime,
            cs.availability
        FROM class_schedule AS cs
        JOIN class_name AS cn ON cs.class_name_id = cn.class_name_id
        JOIN instructor AS i ON cs.instructor_id = i.instructor_id
    """)
    timetable_data = cursor.fetchall()
    cursor.close()
    
    timetable = defaultdict(lambda: defaultdict(list))
    for row in timetable_data:
        date = row['datetime'].strftime('%Y-%m-%d')  # Format date as string for consistent access
        time_slot = format_time_slot(row['start_time'], row['end_time'])
        timetable[date][time_slot].append({
            'class_id': row['class_id'],  # Store class_id for URL generation
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
    
    user_booked_classes = []
    if 'UserID' in session:
        user_id = session['UserID']
        cursor = getCursor()
        cursor.execute("""
            SELECT class_id 
            FROM bookings 
            WHERE member_id = (SELECT member_id FROM member WHERE user_id = %s) AND booking_status = 'confirmed'
        """, (user_id,))
        user_booked_classes = [row['class_id'] for row in cursor.fetchall()]

    return render_template('swimming_class.html', timetable=timetable, selected_date=selected_date, dates=dates, time_slots=time_slots, user_booked_classes=user_booked_classes)


@app.template_filter('timeformat')
def timeformat(value):
    """Format a time object to 'HH:MM AM/PM' format."""
    if isinstance(value, time):  # Ensure 'time' is used directly if imported correctly
        return value.strftime('%I:%M %p')
    elif isinstance(value, datetime):  # This handles datetime objects, extracting the time part
        return value.time().strftime('%I:%M %p')
    else:
        return str(value) 

@app.route('/booking_class/<int:class_id>', methods=['GET'])
def booking_class(class_id):
    if 'UserID' not in session:
        flash("Please log in to book classes.", "info")
        return redirect(url_for('login'))  # Assumed 'login' is the endpoint for the login page

    cursor = getCursor()
    try:
        cursor.execute("""
            SELECT
                cs.class_id,
                cn.name AS class_name,
                cn.description,
                CONCAT(i.first_name, ' ', i.last_name) AS instructor_name,
                cs.week,
                cs.pool_type,
                TIME_FORMAT(cs.start_time, '%h:%i %p') AS start_time,
                TIME_FORMAT(cs.end_time, '%h:%i %p') AS end_time,
                cs.capacity,
                cs.datetime,
                cs.availability
            FROM class_schedule AS cs
            JOIN class_name AS cn ON cs.class_name_id = cn.class_name_id
            JOIN instructor AS i ON cs.instructor_id = i.instructor_id
            WHERE cs.class_id = %s
        """, (class_id,))
        class_details = cursor.fetchone()
    except Exception as e:
        flash(str(e), 'danger')
        return redirect(url_for('swimming_class'))

    if not class_details:
        flash("Class not found.", "warning")
        return redirect(url_for('swimming_class'))

    return render_template('booking_class.html', class_details=class_details)


@app.route('/confirm_booking/<int:class_id>', methods=['POST'])
@login_required
@UserType_required('member')
def confirm_booking(class_id):
    user_id = session.get('UserID')
    cursor = getCursor()
    cursor.execute("SELECT member_id FROM member WHERE user_id = %s", (user_id,))
    member_info = cursor.fetchone()

    if not member_info:
        flash("Member not found.", "warning")
        return redirect(url_for('swimming_class'))

    member_id = member_info['member_id']

    cursor.execute("SELECT availability FROM class_schedule WHERE class_id = %s AND availability > 0", (class_id,))
    class_info = cursor.fetchone()

    if class_info and class_info['availability'] > 0:
        try:
            cursor.execute("UPDATE class_schedule SET availability = availability - 1 WHERE class_id = %s", (class_id,))
            cursor.execute("INSERT INTO bookings (member_id, class_id, booking_status, booking_date) VALUES (%s, %s, 'confirmed', NOW())", (member_id, class_id))
            getConnection().commit()
            flash('Booking confirmed successfully.', 'success')
        except Exception as e:
            getConnection().rollback()
            flash('Failed to confirm booking: ' + str(e), 'danger')
    else:
        flash('No available spaces.', 'danger')

    return redirect(url_for('dashboard_member'))

@app.route('/cancel_booking', methods=['POST'])
@login_required
@UserType_required('member')
def cancel_booking():
    user_id = session.get('UserID')
    member_info = get_member_info(user_id)
    booking_id = request.form.get('booking_id')

    cursor = getCursor()

    try:
        # Check if the booking exists and is confirmed
        cursor.execute("""
            SELECT class_id 
            FROM bookings 
            WHERE member_id = %s AND booking_id = %s AND booking_status = 'confirmed'
        """, (member_info['member_id'], booking_id))
        booking_to_cancel = cursor.fetchone()

        if booking_to_cancel:
            class_id = booking_to_cancel['class_id']
            # Update the booking status to 'cancelled'
            cursor.execute("UPDATE bookings SET booking_status = 'cancelled' WHERE booking_id = %s", (booking_id,))
            # Increment the availability of the class
            cursor.execute("UPDATE class_schedule SET availability = availability + 1 WHERE class_id = %s", (class_id,))
            getConnection().commit()
            flash('Booking cancelled successfully.', 'success')
        else:
            flash('Booking not found or not confirmed.', 'warning')
            getConnection().rollback()

    except Exception as e:
        getConnection().rollback()
        flash('Failed to cancel booking: ' + str(e), 'danger')

    return redirect(url_for('book'))


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
>>>>>>> 7a1ab03987d10d39e67546081f7c2767bbc8d4e0

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
            class_schedule.datetime,
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
    membership_info = get_membership_info(member_info['member_id'])
    class_bookings = get_member_class_bookings(member_info['member_id'])
    lesson_bookings = get_member_lesson_bookings(member_info['member_id'])
    bookings = class_bookings + lesson_bookings
    return render_template('dashboard/dashboard_member.html', user_info=user_info, 
                           member_info=member_info,
                           membership_info=membership_info,
                           class_bookings=class_bookings, 
                           lesson_bookings=lesson_bookings, bookings=bookings)

# booking
def generate_timetable():
    cursor = getCursor()
    cursor.execute("""
        SELECT
            cs.class_id,  # Ensure this is included
            cn.name,
            i.first_name,
            i.last_name,
            cs.week,
            cs.pool_type,
            cs.start_time,
            cs.end_time,
            cs.capacity,
            cs.datetime,
            cs.availability
        FROM class_schedule AS cs
        JOIN class_name AS cn ON cs.class_name_id = cn.class_name_id
        JOIN instructor AS i ON cs.instructor_id = i.instructor_id
    """)
    timetable_data = cursor.fetchall()
    cursor.close()
    
    timetable = defaultdict(lambda: defaultdict(list))
    for row in timetable_data:
        date = row['datetime'].strftime('%Y-%m-%d')  # Format date as string for consistent access
        time_slot = format_time_slot(row['start_time'], row['end_time'])
        timetable[date][time_slot].append({
            'class_id': row['class_id'],  # Store class_id for URL generation
            'name': row['name'],
            'availability': row['availability'],
            'instructor': f"{row['first_name']} {row['last_name']}",
            'pool_type': row['pool_type']
        })
    
    return timetable

@app.route('/swimming-class/', methods=['GET'])
def swimming_class():
    user_id = session.get('UserID')
    member_info = get_member_info(user_id)

    selected_date = request.args.get('date') or datetime.today().strftime('%Y-%m-%d')
    timetable = generate_timetable()
    dates = [datetime.strptime(selected_date, '%Y-%m-%d') + timedelta(days=i) for i in range(7)]
    time_slots = [format_time_slot(timedelta(hours=h), timedelta(hours=h+1)) for h in range(6, 20)]
    
    user_booked_classes = []
    if 'UserID' in session:
        user_id = session['UserID']
        cursor = getCursor()
        cursor.execute("""
            SELECT class_id 
            FROM bookings 
            WHERE member_id = (SELECT member_id FROM member WHERE user_id = %s) AND booking_status = 'confirmed'
        """, (user_id,))
        user_booked_classes = [row['class_id'] for row in cursor.fetchall()]

    return render_template('member/swimming_class.html', timetable=timetable, 
                           selected_date=selected_date, dates=dates, time_slots=time_slots, 
                           user_booked_classes=user_booked_classes, member_info=member_info)

@app.template_filter('timeformat')
def timeformat(value):
    """Format a time object to 'HH:MM AM/PM' format."""
    if isinstance(value, time): 
        return value.strftime('%I:%M %p')
    elif isinstance(value, datetime): 
        return value.time().strftime('%I:%M %p')
    else:
        return str(value) 


def get_member_class_bookings(member_id):
    cursor = getCursor()
    cursor.execute("""
        SELECT 
            bookings.booking_id, 
            class_name.name AS class_name,
            CONCAT(instructor.first_name, ' ', instructor.last_name) AS instructor_name,
            bookings.schedule_type,
            bookings.booking_status, 
            bookings.booking_date,
            class_schedule.datetime,  # Make sure this is correctly aliased and fetched
            class_schedule.start_time, 
            class_schedule.end_time
        FROM bookings
        JOIN class_schedule ON bookings.class_id = class_schedule.class_id
        JOIN class_name ON class_schedule.class_name_id = class_name.class_name_id
        JOIN instructor ON class_schedule.instructor_id = instructor.instructor_id
        WHERE bookings.member_id = %s AND bookings.schedule_type = 'aerobics class'
    """, (member_id,))
    return cursor.fetchall()

@app.route('/book')
@login_required
@UserType_required('member')
def book():
    user_id = session.get('UserID')
    member_info = get_member_info(user_id)
    class_bookings = get_member_class_bookings(member_info['member_id'])
    lesson_bookings = get_member_lesson_bookings(member_info['member_id'])
    bookings = class_bookings + lesson_bookings
<<<<<<< HEAD
    return render_template('member/member_booking.html', class_bookings=class_bookings, 
                           lesson_bookings=lesson_bookings, member_info=member_info, bookings=bookings)

@app.route('/booking_class/<int:class_id>', methods=['GET'])
@login_required
@UserType_required('member')
def booking_class(class_id):
    user_id = session.get('UserID')
    member_info = get_member_info(user_id)

    cursor = getCursor()
    try:
        cursor.execute("""
            SELECT
                cs.class_id,
                cn.name AS class_name,
                cn.description,
                CONCAT(i.first_name, ' ', i.last_name) AS instructor_name,
                cs.week,
                cs.pool_type,
                TIME_FORMAT(cs.start_time, '%h:%i %p') AS start_time,
                TIME_FORMAT(cs.end_time, '%h:%i %p') AS end_time,
                cs.capacity,
                cs.datetime,
                cs.availability
            FROM class_schedule AS cs
            JOIN class_name AS cn ON cs.class_name_id = cn.class_name_id
            JOIN instructor AS i ON cs.instructor_id = i.instructor_id
            WHERE cs.class_id = %s
        """, (class_id,))
        class_details = cursor.fetchone()
    except Exception as e:
        flash(str(e), 'danger')
        return redirect(url_for('swimming_class'))

    if not class_details:
        flash("Class not found.", "warning")
        return redirect(url_for('swimming_class'))

    return render_template('member/booking_class.html', class_details=class_details, member_info=member_info)

@app.route('/confirm_booking/<int:class_id>', methods=['POST'])
@login_required
@UserType_required('member')
def confirm_booking(class_id):
    user_id = session.get('UserID')
    member_info = get_member_info(user_id)
    cursor = getCursor()

    if not member_info:
        flash("Member not found.", "warning")
        return redirect(url_for('swimming_class'))

    member_id = member_info['member_id']

    cursor.execute("SELECT availability, datetime, start_time FROM class_schedule WHERE class_id = %s AND availability > 0", (class_id,))
    class_info = cursor.fetchone()

    if not class_info:
        flash("Class not found or no available spaces.", "warning")
        return redirect(url_for('swimming_class'))

    # Get the membership end date
    cursor.execute("SELECT end_date FROM memberships WHERE member_id = %s ORDER BY end_date DESC LIMIT 1", (member_id,))
    membership_info = cursor.fetchone()

    # Check if the membership has expired
    if membership_info or membership_info['end_date'] < class_info['datetime']:
        flash("Your membership has expired.", "warning")
        return redirect(url_for('swimming_class'))
    
    if membership_info or class_info['datetime'] < membership_info['start_date']:
        flash("Your membership does not cover the date of this class.", "warning")
        return redirect(url_for('swimming_class'))

    now = datetime.now()
    start_time = (datetime.min + class_info['start_time']).time()
    class_start_datetime = datetime.combine(class_info['datetime'], start_time)
    if class_start_datetime < now:
        flash("Cannot book past events.", "warning")
        return redirect(url_for('swimming_class'))

    if class_info and class_info['availability'] > 0:
        try:
            cursor.execute("UPDATE class_schedule SET availability = availability - 1 WHERE class_id = %s", (class_id,))
            cursor.execute("INSERT INTO bookings (member_id, class_id, booking_status, booking_date) VALUES (%s, %s, 'confirmed', NOW())", (member_id, class_id))
            getConnection().commit()
            flash('Booking confirmed successfully.', 'success')
        except Exception as e:
            getConnection().rollback()
            flash('Failed to confirm booking: ' + str(e), 'danger')
    else:
        flash('No available spaces.', 'danger')

    return redirect(url_for('swimming_class'))

@app.route('/cancel_booking', methods=['POST'])
@login_required
@UserType_required('member')
def cancel_booking():
    user_id = session.get('UserID')
    member_info = get_member_info(user_id)
    booking_id = request.form.get('booking_id')
=======
    class_schedule = generate_timetable() 

    return render_template('member_booking.html', class_bookings=class_bookings, 
                           lesson_bookings=lesson_bookings, member_info=member_info, 
                           bookings=bookings, class_schedule=class_schedule)

>>>>>>> 7a1ab03987d10d39e67546081f7c2767bbc8d4e0


#@app.route('/cancel_booking', methods=['POST'])
#@login_required
#@UserType_required('member')
#def cancel_booking():
#    user_id = session.get('UserID')
#    member_info = get_member_info(user_id)
#    booking_id = request.form.get('booking_id')

#    cursor = getCursor()

<<<<<<< HEAD
    try:
        # Check if the booking exists and is confirmed
        cursor.execute("""
            SELECT class_id 
            FROM bookings 
            WHERE member_id = %s AND booking_id = %s AND booking_status = 'confirmed'
        """, (member_info['member_id'], booking_id))
        booking_to_cancel = cursor.fetchone()

        if booking_to_cancel:
            class_id = booking_to_cancel['class_id']
            # Update the booking status to 'cancelled'
            cursor.execute("UPDATE bookings SET booking_status = 'cancelled' WHERE booking_id = %s", (booking_id,))
            # Increment the availability of the class
            cursor.execute("UPDATE class_schedule SET availability = availability + 1 WHERE class_id = %s", (class_id,))
            getConnection().commit()
            flash('Booking cancelled successfully.', 'success')
        else:
            flash('Booking not found or not confirmed.', 'warning')
            getConnection().rollback()

    except Exception as e:
        getConnection().rollback()
        flash('Failed to cancel booking: ' + str(e), 'danger')
=======
    # Check if the booking exists and is confirmed
#    cursor.execute("SELECT * FROM bookings WHERE member_id = %s AND booking_id = %s AND booking_status = 'confirmed'", (member_info['member_id'], booking_id))
#    booking_to_cancel = cursor.fetchone()

#    if booking_to_cancel:
        # Update the booking status to 'cancelled'
#        cursor.execute("UPDATE bookings SET booking_status = 'cancelled' WHERE member_id = %s AND booking_id = %s", (member_info['member_id'], booking_id))
#        getConnection().commit()
#        flash('Booking cancelled successfully.')
#    else:
#        flash('Booking not found or not confirmed.')
>>>>>>> 7a1ab03987d10d39e67546081f7c2767bbc8d4e0

#    return redirect(url_for('book'))

<<<<<<< HEAD
# membership
@app.route('/view_membership')
@login_required
def view_membership():
    user_id = session.get('UserID')
    member_info = get_member_info(user_id)
    # Fetch memberships associated with the current user
    cursor = getCursor()
    cursor.execute("SELECT * FROM memberships WHERE member_id = %s", (current_user.MemberID,))  
    memberships = cursor.fetchall()

    # Fetch user's full name
    cursor.execute("SELECT CONCAT(first_name, ' ', last_name) AS full_name FROM member WHERE member_id = %s", (current_user.MemberID,))
    user_info = cursor.fetchone()
    cursor.close()
    return render_template('member/view_membership.html', memberships=memberships, 
                           user_full_name=user_info['full_name'], member_info=member_info)

@app.route('/cancel_membership/<int:membership_id>', methods=['POST'])
@login_required
def cancel_membership(membership_id):
    cursor = getCursor()
    # Get the membership type, start date, and status
    cursor.execute("SELECT type, start_date, end_date, status FROM memberships WHERE membership_id = %s", (membership_id,))
    membership = cursor.fetchone()
    membership_type = membership['type']
    start_date = membership['start_date']
    end_date = membership['end_date']
    membership_status = membership['status']

    # If the membership is already inactive, return a message to the user
    if membership_status == 'Inactive':
        flash('This membership has already been cancelled.', 'error')
        return redirect(url_for('view_membership'))

    # Calculate the refund amount and end date based on the start date and the current date
    refund_amount, end_date = calculate_refund_amount_and_end_date(membership_type, start_date)

    # If the membership type is 'Annual', add a record to the memberships_refund table
    if membership_type == 'Annual':
        refund_date = datetime.now().date()
        cursor.execute("INSERT INTO memberships_refund (membership_id, member_id, refund_amount, refund_date) VALUES (%s, %s, %s, %s)",
                       (membership_id, current_user.MemberID, refund_amount, refund_date))
    # Set the membership status to 'Inactive'
    cursor.execute("UPDATE memberships SET status = 'Inactive', end_date = %s WHERE membership_id = %s", (end_date, membership_id))

    # Cancel bookings for events that occur after the membership end date
    cursor.execute("""
        UPDATE bookings 
        INNER JOIN class_schedule ON bookings.class_id = class_schedule.class_id
        SET booking_status = 'cancelled' 
        WHERE member_id = %s AND booking_status = 'confirmed' AND class_schedule.datetime > %s
    """, (current_user.MemberID, end_date))
    
    getConnection().commit()
    cursor.close()
    flash('Membership cancelled successfully.', 'success')
    return redirect(url_for('view_membership'))

def calculate_refund_amount_and_end_date(membership_type, start_date):

    current_date = datetime.now().date()

    days_since_start = (current_date - start_date).days
  
    if membership_type == 'Annual':
        if days_since_start <= 90:  
            refund_amount = 0
            end_date = start_date + timedelta(days=90)
        elif days_since_start <= 180:  
            refund_amount = 100
            end_date = start_date + timedelta(days=180)
        else:  
            refund_amount = 0
            end_date = start_date + timedelta(days=365)
    else:
        refund_amount = 0
        end_date = current_date  
    return refund_amount, end_date
=======
#@app.route('/add_booking', methods=['POST'])
#@login_required
#@UserType_required('member')
#def add_booking():
#    user_id = session.get('UserID')
#    member_info = get_member_info(user_id)
#    class_id = request.form.get('class_id')

#    cursor = getCursor()

    # Check if the class exists and is not full
#    cursor.execute("SELECT * FROM classes WHERE class_id = %s AND class_status = 'open'", (class_id,))
#    class_to_book = cursor.fetchone()

#    if class_to_book:
        # Check if the member has already booked this class
#        cursor.execute("SELECT * FROM bookings WHERE member_id = %s AND class_id = %s", (member_info['member_id'], class_id))
#        existing_booking = cursor.fetchone()

#       if existing_booking:
#           flash('You have already booked this class.')
#        else:
            # Add the new booking
#            cursor.execute("INSERT INTO bookings (member_id, class_id, booking_status) VALUES (%s, %s, 'confirmed')", (member_info['member_id'], class_id))
#            getConnection().commit()
#            flash('Booking added successfully.')
#    else:
#        flash('Class not found or not open.')
>>>>>>> 7a1ab03987d10d39e67546081f7c2767bbc8d4e0

@app.route('/renew_membership/<int:membership_id>', methods=['POST'])
@login_required
def renew_membership(membership_id):
    cursor = getCursor()
    cursor.execute("SELECT member_id, type, start_date, end_date, membership_fee, status FROM memberships WHERE membership_id = %s", (membership_id,))
    membership = cursor.fetchone()

    if membership['status'] not in ['Inactive', 'Active']:
        flash('This membership status does not allow renewal.', 'error')
        return redirect(url_for('view_membership'))

    # Get the new membership type from the form data
    new_membership_type = request.form.get('type')

    # Get the current end date from the membership record
    current_end_date = membership['end_date']
    start_date = datetime.now().date()

    # Calculate the new end date based on the new membership type
    if new_membership_type == 'Annual':
        end_date = current_end_date + timedelta(days=365)
        membership_fee = 700
    elif new_membership_type == '6 Month':
        end_date = current_end_date + timedelta(days=180)
        membership_fee = 360
    elif new_membership_type == 'Monthly':
        end_date = current_end_date + timedelta(days=30)
        membership_fee = 60
    else:
        flash('Invalid membership type.', 'error')
        return redirect(url_for('view_membership'))

    # Check if the new end date is more than one year after the start date
    if end_date > start_date + timedelta(days=365):
        flash('The membership duration cannot exceed one year.', 'error')
        return redirect(url_for('view_membership'))

    # Update the membership record in the database with the new membership type
    cursor.execute("UPDATE memberships SET type = %s, start_date = %s, end_date = %s, membership_fee = %s, status = 'Active' WHERE membership_id = %s", (new_membership_type, start_date, end_date, membership_fee, membership_id))
    getConnection().commit()
    flash('Membership renewed successfully.', 'success')

    # Insert a new payment record in the database
    payment_date = datetime.now().date()
    payment_type = 'membership'
    manager_id = 1
    cursor.execute("INSERT INTO payments (member_id, membership_id, manager_id, payment_type, payment_date, amount) VALUES (%s, %s, %s, %s, %s, %s)", (membership['member_id'], membership_id, manager_id, payment_type, payment_date, membership_fee))
    getConnection().commit()
    cursor.close()
    return redirect(url_for('view_membership', membership_id=membership_id))
