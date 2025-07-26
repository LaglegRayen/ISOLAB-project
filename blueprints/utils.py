"""
Utility functions for ISOLAB Agri Support - Simplified
Contains only essential helper functions for CRUD operations
"""

from datetime import datetime


def get_timestamp():
    """Get current timestamp in ISO format"""
    return datetime.now().isoformat()


def format_client_data(data):
    """Format and validate client data for storage"""
    formatted_data = {
        'nom': data.get('nom', '').strip(),
        'prenom': data.get('prenom', '').strip(),
        'telephone': data.get('telephone', '').strip(),
        'adresse': data.get('adresse', '').strip(),
        'type': data.get('type', '').strip(),
        'location': data.get('location', '').strip(),
        'status': data.get('status', '').strip(),
        'updated_at': get_timestamp()
    }
    return formatted_data


def format_machine_data(data):
    """Format and validate machine data for storage"""
    formatted_data = {
        'serialNumber': data.get('serialNumber', '').strip(),
        'machineType': data.get('machineType', '').strip(),
        'marque': data.get('marque', '').strip(),
        'modele': data.get('modele', '').strip(),
        'puissance': data.get('puissance', '').strip(),
        'status': data.get('status', '').strip(),
        'clientId': data.get('clientId', '').strip(),
        'updated_at': get_timestamp()
    }
    
    # Handle numeric fields
    for field in ['prixHT', 'prixTTC']:
        if field in data and data[field]:
            try:
                formatted_data[field] = float(data[field])
            except (ValueError, TypeError):
                formatted_data[field] = 0.0
    
    return formatted_data


def validate_required_fields(data, required_fields):
    """Check if all required fields are present and not empty"""
    missing_fields = []
    for field in required_fields:
        if not data.get(field) or str(data[field]).strip() == '':
            missing_fields.append(field)
    return missing_fields


def create_error_response(message, status_code=400):
    """Create standardized error response"""
    return {
        "success": False,
        "error": message,
        "timestamp": get_timestamp()
    }, status_code


def create_success_response(data=None, message="Operation successful"):
    """Create standardized success response"""
    response = {
        "success": True,
        "message": message,
        "timestamp": get_timestamp()
    }
    if data is not None:
        response["data"] = data
    return response
