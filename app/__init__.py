from flask import Flask
from flask_hashing import Hashing

app = Flask(__name__)
hashing = Hashing(app)
app.secret_key = '1234' # could be any key if anyone want to change it

from app import public_views
from app import member_views
from app import manager_views
from app import instructor_views
from app import login_register_logout_views