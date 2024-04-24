from app import app
from flask import flash
from flask import session
from flask import redirect
from flask import url_for
from flask import render_template
from app.database import getCursor
from app.database import getConnection
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

def get_user_info(user_id):
    cursor = getCursor()
    cursor.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
    return cursor.fetchone()

def get_member_info(user_id):
    cursor = getCursor()
    cursor.execute("SELECT * FROM member WHERE user_id = %s", (user_id,))
    return cursor.fetchone()

def get_instructor_info(user_id):
    cursor = getCursor()
    cursor.execute("SELECT * FROM instructor WHERE user_id = %s", (user_id,))
    return cursor.fetchone()

def get_manager_info(user_id):
    cursor = getCursor()
    cursor.execute("SELECT * FROM manager WHERE user_id = %s", (user_id,))
    return cursor.fetchone()

def get_news_list():
    cursor = getCursor()
    cursor.execute("""
                   SELECT * FROM news
                   ORDER BY publication_date DESC
                   """)
    return cursor.fetchall()

def get_news_info(news_id):
    cursor = getCursor()
    cursor.execute("""
                   SELECT * FROM news
                   WHERE news_id = %s
                   """, (news_id,))
    return cursor.fetchone()

# news for all
@app.route('/news')
@login_required
@UserType_required('member', 'instructor')
def news():
    user_id = session.get('UserID')
    UserType=session.get('UserType')
    member_info = get_member_info(user_id)
    instructor_info = get_instructor_info(user_id)
    news_list = get_news_list()
    return render_template('news/news.html', member_info=member_info, instructor_info=instructor_info, 
                           UserType=session.get('UserType'), news_list=news_list)

@app.route('/news/<int:news_id>')
@login_required
@UserType_required('member', 'instructor')
def view_news(news_id):
    user_id = session.get('UserID')
    member_info = get_member_info(user_id)
    instructor_info = get_instructor_info(user_id)
    news_info = get_news_info(news_id)
    return render_template('news/view_news.html', member_info=member_info, instructor_info=instructor_info, 
                           news_info=news_info)

