"""
StudentTracker Flask Application
Main entry point for the application
"""
import os
from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from models import db
from config import config


def create_app(config_name=None):
    """Application factory function"""
    
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')
    
    app = Flask(__name__, static_folder='static', static_url_path='') 
    
    # Load configuration
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    CORS(app, resources={r"/api/*": {"origins": app.config.get('CORS_ORIGINS', '*')}})
    jwt = JWTManager(app)
    
    # JWT error handlers
    @jwt.user_lookup_loader
    def user_lookup_callback(_jwt_header, jwt_data):
        identity = jwt_data["sub"]
        return identity
    
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({
            'success': False,
            'message': 'Token has expired'
        }), 401
    
    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return jsonify({
            'success': False,
            'message': 'Invalid token'
        }), 401
    
    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return jsonify({
            'success': False,
            'message': 'Authorization header is missing'
        }), 401
    
    # Register blueprints
    from routes.auth import auth_bp
    from routes.admin import admin_bp
    from routes.course import course_bp
    from routes.attendance import attendance_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(course_bp)
    app.register_blueprint(attendance_bp)

    
    
    # Health check endpoint
    @app.route('/api/health', methods=['GET'])
    def health_check():
        return jsonify({
            'status': 'healthy',
            'service': 'StudentTracker API'
        }), 200
    
   
       
      

    # Serve frontend
    @app.route('/')
    def index():
        return app.send_static_file('index.html')
    @app.route('/test-page')
    def test_page():
        return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Test</title>
        <link rel="stylesheet" href="/styles.css">
    </head>
    <body>
        <h1>Test Page</h1>
        <button class="btn btn-primary">Test Button</button>
        <div class="auth-box">
            <h1>If this is styled, CSS is working!</h1>
        </div>
    </body>
    </html>
    '''

    



    
    
   # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'success': False,
            'message': 'Resource not found'
        }), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({
            'success': False,
            'message': 'Internal server error'
        }), 500
    
    # Database initialization
    with app.app_context():
        db.create_all()
        print("Database tables created successfully!")
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)
