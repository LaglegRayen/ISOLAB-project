"""
Dashboard Blueprint
Handles rendering the dashboard page after login
"""

from flask import Blueprint, render_template, session, redirect, url_for

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/')

# Frontend URL configuration
FRONTEND_URL = 'https://isolab-support.firebaseapp.com/'

@dashboard_bp.route('/dashboard', methods=['GET'])
def dashboard():
    # Require login
    print("Dashboard endpoint called")
    if 'user_id' not in session:
        print("User not logged in, redirecting to home")
        return redirect(f'{FRONTEND_URL}/login.html')
    print("User logged in, redirecting to dashboard")
    return redirect(f'{FRONTEND_URL}/dashboard.html')
