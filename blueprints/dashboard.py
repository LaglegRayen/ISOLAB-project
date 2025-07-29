"""
Dashboard Blueprint
Handles rendering the dashboard page after login
"""

from flask import Blueprint, render_template, session, redirect, url_for

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/')

@dashboard_bp.route('/dashboard', methods=['GET'])
def dashboard():
    # Require login
    print("Dashboard endpoint called")
    if 'user_id' not in session:
        print("User not logged in, redirecting to home")
        return redirect(url_for('main.home'))
    print("User logged in, rendering dashboard")
    return render_template('dashboard.html')
