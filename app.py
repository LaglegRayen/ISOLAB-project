"""
ISOLAB Agri Support - Main Flask Application
Restructured with blueprints for better organization
"""

from flask import Flask, request, render_template, Blueprint
from blueprints.clients import clients_bp
from blueprints.machines import machines_bp
from blueprints.users import users_bp
from blueprints.login import login_bp
from blueprints.stages import stages_bp
from blueprints.dashboard import dashboard_bp
from blueprints.workflow import workflow_bp
import os
from blueprints.firebase_config import initialize_firebase



# Create Flask application
app = Flask(__name__)
app.secret_key = 'super-secret-key'
app.register_blueprint(login_bp)
app.register_blueprint(clients_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(machines_bp)
app.register_blueprint(users_bp)
app.register_blueprint(stages_bp)
app.register_blueprint(workflow_bp)
# main_bp = Blueprint('main', __name__)

# Set template and static folders to match your current structure
app.template_folder = 'templates'
app.static_folder = 'static'

# Initialize Firebase

firebase_initialized = initialize_firebase()
if firebase_initialized:
    print("Firebase successfully initialized")
else:
    print("Firebase initialization failed - some features may not work")
    print("Check FIREBASE_SETUP.md for configuration instructions")

    


@app.route('/')
def home():
    return render_template('login.html')

@app.route('/voir-machines.html')
def voir_machines():
    """Handle direct access to voir-machines.html with optional machine parameter"""
    return render_template('voir-machines.html')


# app = Flask(__name__)
# @app.route('/login', methods=['POST'])
# def login():
#     """Simple login - store user ID in session"""
#     print(1)
#     return "OK"

if __name__ == '__main__':
    app.run(debug=True)
