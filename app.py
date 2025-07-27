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
import os
from blueprints.firebase_config import initialize_firebase



# Create Flask application
app = Flask(__name__)


main_bp = Blueprint('main', __name__)

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



app.register_blueprint(clients_bp)
app.register_blueprint(machines_bp)
app.register_blueprint(users_bp)
app.register_blueprint(stages_bp)
app.register_blueprint(login_bp)
    


@main_bp.route('/')
def home():
    return render_template('login.html')

app.register_blueprint(main_bp) 

if __name__ == '__main__':
    app.run(debug=True)
