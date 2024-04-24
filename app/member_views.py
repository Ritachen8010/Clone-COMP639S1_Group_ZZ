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
from datetime import time, timedelta, datetime
from collections import defaultdict
from flask_login import current_user
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

# Define user info based on user id
def get_user_info(user_id):
    cursor = getCursor()
    cursor.execute("SELECT * FROM user WHERE user_id = %s", (user_id,))
    return cursor.fetchone()

# Define member inf based on user id 
def get_member_info(user_id):
    cursor = getCursor()
    cursor.execute("SELECT * FROM member WHERE user_id = %s", (user_id,))
    return cursor.fetchone()

# Define membership info based on member id
def get_membership_info(member_id):
    cursor = getCursor()
    cursor.execute("SELECT * FROM memberships WHERE member_id = %s", (member_id,))
    return cursor.fetchone()

# Define news info
def get_news_info():
    cursor = getCursor()
    cursor.execute("""
                   SELECT * FROM news
                   ORDER BY publication_date DESC
                   """)
    return cursor.fetchall()

# Define booking info based on member id 
def get_booking(member_id):
    cursor = getCursor()
    cursor.execute("SELECT * FROM bookings WHERE member_id = %s", (member_id,))
    return cursor.fetchall()

# Define member class booking based on member id 
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
            bookings.booking_date,
            bookings.class_id  # Ensure class_id is being selected
        FROM 
            bookings
        JOIN 
            class_schedule ON bookings.class_id = class_schedule.class_id
        JOIN 
            class_name ON class_schedule.class_name_id = class_name.class_name_id
        JOIN 
            instructor ON class_schedule.instructor_id = instructor.instructor_id
        WHERE 
            bookings.member_id = %s AND
            bookings.schedule_type = 'aerobics class' AND
            bookings.booking_status = 'confirmed'
        ORDER BY bookings.booking_id ASC
    """, (member_id,))
    return cursor.fetchall()

# Define member lesson booking based on member id 
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

# Define booking info based on member id
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
    return render_template('dashboard/dashboard_member.html', user_info=user_info, 
                           member_info=member_info,
                           membership_info=membership_info)

# booking
def generate_timetable():
    current_datetime = datetime.now()  # Get the current datetime to compare against class times
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
            cs.datetime as class_date,  # this should be a date
            cs.availability,
            cs.class_status
        FROM class_schedule AS cs
        JOIN class_name AS cn ON cs.class_name_id = cn.class_name_id
        JOIN instructor AS i ON cs.instructor_id = i.instructor_id
    """)
    timetable_data = cursor.fetchall()
    cursor.close()

    timetable = defaultdict(lambda: defaultdict(list))
    for row in timetable_data:
        start_time_obj = datetime.strptime(row['start_time'], '%H:%M:%S').time() if isinstance(row['start_time'], str) else (datetime.min + row['start_time']).time()
        end_time_obj = datetime.strptime(row['end_time'], '%H:%M:%S').time() if isinstance(row['end_time'], str) else (datetime.min + row['end_time']).time()
        
        class_datetime = datetime.combine(row['class_date'], start_time_obj)  # Combine date with time to create a full datetime

        time_slot = f"{start_time_obj.strftime('%I:%M %p')} - {end_time_obj.strftime('%I:%M %p')}"
        
        timetable[row['class_date'].strftime('%Y-%m-%d')][time_slot].append({
            'class_id': row['class_id'],
            'name': row['class_name'],
            'instructor': f"{row['first_name']} {row['last_name']}",
            'availability': row['availability'],
            'class_status': row['class_status'],
            'datetime': class_datetime,  # Full datetime of the class
            'expired': class_datetime < current_datetime  # Check if the class datetime is before the current datetime
        })

    return timetable

@app.route('/swimming-class/', methods=['GET'])
def swimming_class():
    current_datetime = datetime.now()
    user_id = session.get('UserID')
    member_info = get_member_info(user_id)
    
    if not member_info:
        flash("Member session not found.", "error")
        return redirect(url_for('login'))
    
    selected_date = request.args.get('date', default=datetime.today().strftime('%Y-%m-%d'))
    timetable = generate_timetable()

    dates = [datetime.strptime(selected_date, '%Y-%m-%d') + timedelta(days=i) for i in range(-3, 4)]
    time_slots = [f"{(datetime.min + timedelta(hours=h)).strftime('%I:%M %p')} - {(datetime.min + timedelta(hours=h+1)).strftime('%I:%M %p')}" for h in range(6, 21)]

    # Fetch IDs of all classes the user has booked
    user_booked_classes = {booking['class_id'] for booking in get_member_class_bookings(member_info['member_id'])}

    return render_template('member/swimming_class.html', timetable=timetable, selected_date=selected_date,
                           dates=dates, time_slots=time_slots, current_datetime=current_datetime,
                           member_info=member_info, user_booked_classes=user_booked_classes)


@app.template_filter('timeformat')
def timeformat(value):
    """Format a time object to 'HH:MM AM/PM' format."""
    if isinstance(value, time): 
        return value.strftime('%I:%M %p')
    elif isinstance(value, datetime): 
        return value.time().strftime('%I:%M %p')
    else:
        return str(value) 

# Member view my aerobics booking list only
@app.route('/book')
@login_required
@UserType_required('member')
def book():
    user_id = session.get('UserID')
    member_info = get_member_info(user_id)
    if not member_info:
        flash("No member information found.", "error")
        return redirect(url_for('home'))

    # Get class and lesson bookings using a simplified process
    class_bookings = get_member_class_bookings(member_info['member_id'])
    lesson_bookings = get_member_lesson_bookings(member_info['member_id'])

    # Combine class and lesson bookings
    bookings = class_bookings + lesson_bookings

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
    if membership_info and membership_info['end_date'] < class_info['datetime']:
        flash("Your membership has expired.", "warning")
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
                           member_id=current_user.MemberID, user_full_name=user_info['full_name'], member_info=member_info)

@app.route('/cancel_membership/<int:membership_id>', methods=['POST'])
@login_required
def cancel_membership(membership_id):
    cursor = getCursor()
    # Get the membership type, date, and status
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

    # If the membership type is 'Annual', record to the memberships_refund table
    if membership_type in ['Annual', 'Monthly', '6 Month']:
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
            # End date = 90 days from start date and no refund
        elif days_since_start <= 180:  
            refund_amount = 100
            end_date = start_date + timedelta(days=180)
            # End date = 180 days from start date and get $100 refund
        else:  
            refund_amount = 0
            end_date = start_date + timedelta(days=365)
            # End date = 365 days from start date and no refund
    elif membership_type == 'Monthly':
        refund_amount = 0
        end_date = start_date + timedelta(days=30)  # End date = 30 days from current date
    elif membership_type == '6 Month':
        refund_amount = 0
        end_date = start_date + timedelta(days=180)  # End date = 180 days from current date
 
    return refund_amount, end_date

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

# Payment history
@app.route('/membership_payment_history/<int:member_id>', methods=['GET'])
def membership_payment_history(member_id):
    user_id = session.get('UserID')
    member_info = get_member_info(user_id)
    cursor = getCursor()

    # Execute a query to get all membership payment records for the given member
    cursor.execute("""
        SELECT payment_id, member_id, membership_id, amount, payment_date, payment_type FROM payments 
        WHERE member_id = %s AND payment_type = 'membership'
        UNION ALL
        SELECT membership_refund_id, member_id, membership_id, refund_amount, refund_date, 'refund' as payment_type FROM memberships_refund
        WHERE member_id = %s
        ORDER BY payment_date DESC
    """, (member_id, member_id))
    payment_records = cursor.fetchall()
    cursor.close()

    return render_template('member/payment_history.html', payment_records=payment_records, member_info=member_info)