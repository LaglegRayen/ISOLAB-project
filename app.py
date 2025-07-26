"""
ISOLAB Agri Support - Main Flask Application
Restructured with blueprints for better organization
"""

from flask import Flask, request
import os
from blueprints.firebase_config import initialize_firebase
from blueprints.main_routes import main_bp
from blueprints.clients import clients_bp
from blueprints.machines import machines_bp
from blueprints.users import users_bp
from blueprints.stages import stages_bp

def create_app():
    """Application factory function"""
    # Create Flask application
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-here-change-in-production')
    app.config['DEBUG'] = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'
    
    # Set template and static folders to match your current structure
    app.template_folder = '.'  # Current directory
    app.static_folder = '.'    # Current directory for static files
    
    # Initialize Firebase
    firebase_initialized = initialize_firebase()
    if firebase_initialized:
        print("Firebase successfully initialized")
    else:
        print("Firebase initialization failed - some features may not work")
        print("Check FIREBASE_SETUP.md for configuration instructions")
    
    # Register blueprints
    app.register_blueprint(main_bp)
    app.register_blueprint(clients_bp)
    app.register_blueprint(machines_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(stages_bp)
    
    # Error handlers
    @app.errorhandler(404)
    def not_found_error(error):
        return {"error": "Not found"}, 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return {"error": "Internal server error"}, 500
    
    # Request logging (development only)
    if app.config['DEBUG']:
        @app.after_request
        def log_request(response):
            print(f"{response.status} - {request.method} {request.path}")
            return response
    
    return app

# Create the application instance
app = create_app()

if __name__ == '__main__':
    try:
        app.run(
            host='0.0.0.0',
            port=int(os.environ.get('PORT', 5000)),
            debug=app.config['DEBUG']
        )
    except KeyboardInterrupt:
        print("\nServer stopped by user")
    except Exception as e:
        print(f"Error starting server: {e}")
