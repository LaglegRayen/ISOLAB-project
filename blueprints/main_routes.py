"""
Main routes blueprint - Simplified
Handles only essential application routes
"""

from flask import Blueprint, send_from_directory, jsonify
from datetime import datetime
from .firebase_config import is_firebase_available

# Create main routes blueprint
main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Serve the main index page"""
    try:
        return send_from_directory('.', 'index.html')
    except Exception as e:
        return f"Error serving index.html: {str(e)}", 500

