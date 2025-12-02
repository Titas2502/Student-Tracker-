"""
Utility functions for StudentTracker application
"""
from functools import wraps
from flask import jsonify

def api_response(message=None, data=None, status_code=200):
    """Generate a standardized API response"""
    response = {
        'success': status_code < 400,
        'status_code': status_code,
    }
    if message:
        response['message'] = message
    if data is not None:
        response['data'] = data
    return jsonify(response), status_code

def handle_exceptions(fn):
    """Decorator to handle exceptions in route handlers"""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except ValueError as e:
            return api_response(str(e), status_code=400)
        except PermissionError as e:
            return api_response(str(e), status_code=403)
        except Exception as e:
            return api_response('An error occurred: ' + str(e), status_code=500)
    return wrapper

class ValidationError(Exception):
    """Custom validation error"""
    pass

def validate_email(email):
    """Validate email format"""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def paginate(items, page=1, per_page=20):
    """Paginate a list of items"""
    total = len(items)
    start = (page - 1) * per_page
    end = start + per_page
    return {
        'items': items[start:end],
        'total': total,
        'page': page,
        'per_page': per_page,
        'pages': (total + per_page - 1) // per_page
    }
