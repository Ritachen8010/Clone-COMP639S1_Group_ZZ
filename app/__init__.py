from flask import Flask
from flask_bcrypt import Bcrypt

app = Flask(__name__)
app.config['SECRET_KEY'] = 'some_random_string_here'
bcrypt = Bcrypt(app)

from app import public_views
from app import member_views
from app import manager_views
from app import instructor_views
from app import login_register_logout_dashboard_views
from app import manage_edit_user_profile
from app import news