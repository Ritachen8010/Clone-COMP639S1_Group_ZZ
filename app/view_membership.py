from flask import render_template
from flask_login import current_user, login_required
from app import app
from app.database import getCursor
from flask_login import current_user

@app.route('/view_membership')
@login_required
def view_membership():
    # Fetch memberships associated with the current user
    cursor = getCursor()
    cursor.execute("SELECT * FROM memberships WHERE member_id = %s", (current_user.MemberID,))
    memberships = cursor.fetchall()

    # Fetch user's full name
    cursor.execute("SELECT CONCAT(first_name, ' ', last_name) AS full_name FROM member WHERE member_id = %s", (current_user.MemberID,))
    user_info = cursor.fetchone()

    cursor.close()
    return render_template('view_membership.html', memberships=memberships, user_full_name=user_info['full_name'])
