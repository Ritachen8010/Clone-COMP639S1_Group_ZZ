from app import app
from flask import render_template

@app.route('/')
def home():
    return render_template('homepage.html')

@app.route('/about_us')
def about_us():
    return render_template('about-us.html')