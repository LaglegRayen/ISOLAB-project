"""
ISOLAB Agri Support - Main Flask Application
Restructured with blueprints for better organization
"""

from flask import Flask, request, render_template, Blueprint, redirect
from blueprints.clients import clients_bp
from blueprints.machines import machines_bp
from blueprints.users import users_bp
from blueprints.login import login_bp
from blueprints.stages import stages_bp
from blueprints.dashboard import dashboard_bp
from blueprints.workflow import workflow_bp
import os
from blueprints.firebase_config import initialize_firebase
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv()


# Create Flask application
app = Flask(__name__)
app.secret_key = 'super-secret-key'

# Session configuration for cross-domain cookies
app.config['SESSION_COOKIE_SECURE'] = True  # Require HTTPS
app.config['SESSION_COOKIE_HTTPONLY'] = True  # Prevent XSS
app.config['SESSION_COOKIE_SAMESITE'] = 'None'  # Allow cross-site cookies
app.config['SESSION_COOKIE_DOMAIN'] = None  # Allow cross-domain

app.register_blueprint(login_bp)
app.register_blueprint(clients_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(machines_bp)
app.register_blueprint(users_bp)
app.register_blueprint(stages_bp)
app.register_blueprint(workflow_bp)
# main_bp = Blueprint('main', __name__)

# Configure CORS to allow requests from Firebase frontend
CORS(app, origins=['https://isolab-support.firebaseapp.com'], supports_credentials=True)

# Set template and static folders to match your current structure
app.template_folder = 'static/templates'
app.static_folder = 'static'

app.config['DEBUG'] = os.environ.get('Flask_DEBUG')
# Initialize Firebase

firebase_initialized = initialize_firebase()
if firebase_initialized:
    print("Firebase successfully initialized")
else:
    print("Firebase initialization failed - some features may not work")
    print("Check FIREBASE_SETUP.md for configuration instructions")

    


# Frontend URL configuration
FRONTEND_URL = 'https://isolab-support.firebaseapp.com'

@app.route('/')
def home():
    return redirect(f'{FRONTEND_URL}/login.html')

@app.route('/login')
def goto_login():
    """Redirect to frontend login page"""
    return redirect(f'{FRONTEND_URL}/login.html')

@app.route('/voir-machines')
def voir_machines():
    """Handle direct access to voir-machines.html with optional machine parameter"""
    return redirect(f'{FRONTEND_URL}/voir-machines.html')

@app.route('/clients')
def clients_html():
    """Redirect to frontend clients page"""
    return redirect(f'{FRONTEND_URL}/clients.html')

@app.route('/users')
def users_html():
    """Redirect to frontend users page"""
    return redirect(f'{FRONTEND_URL}/users.html')

@app.route('/dashboard')
def dashboard_html():
    """Redirect to frontend dashboard page"""
    return redirect(f'{FRONTEND_URL}/dashboard.html')

@app.route('/ajouter-client')
def ajouter_client_html():
    """Redirect to frontend add client page"""
    return redirect(f'{FRONTEND_URL}/ajouter-client.html')



if __name__ == '__main__':
    app.run(debug=True)
