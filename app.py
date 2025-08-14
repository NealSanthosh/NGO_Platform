# app.py
from flask import Flask, render_template
from extensions import mongo, login_manager
from config import Config
import os

def create_app():
    """Application factory function"""
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Initialize extensions with app
    mongo.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'
    
    # User loader function - import User here to avoid circular imports
    @login_manager.user_loader
    def load_user(user_id):
        from models.user import User
        return User.get_by_id(user_id)
    
    # Import and register blueprints AFTER app and extensions are set up
    from routes.auth import auth_bp
    from routes.main import main_bp
    from routes.organisation import org_bp
    from routes.campaign import campaign_bp
    from routes.donation import donation_bp
    from routes.user_dashboard import user_dashboard_bp
    from routes.org_dashboard import org_dashboard_bp
    from routes.admin import admin_bp
    
    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(main_bp)
    app.register_blueprint(org_bp, url_prefix='/organisations')
    app.register_blueprint(campaign_bp, url_prefix='/campaigns')
    app.register_blueprint(donation_bp, url_prefix='/donate')
    app.register_blueprint(user_dashboard_bp, url_prefix='/dashboard')
    app.register_blueprint(org_dashboard_bp, url_prefix='/org-dashboard')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    
    # Create upload directory if it doesn't exist
    upload_folder = app.config.get('UPLOAD_FOLDER', 'static/uploads')
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder, exist_ok=True)
    
    # Error handlers
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return render_template('errors/500.html'), 500
    
    @app.errorhandler(403)
    def forbidden_error(error):
        return render_template('errors/403.html'), 403
    
    # Context processors for templates
    @app.context_processor
    def inject_global_vars():
        """Make certain variables available to all templates"""
        return {
            'datetime': __import__('datetime'),
            'len': len,
            'str': str,
            'int': int,
            'float': float
        }
    
    # Template filters
    @app.template_filter('currency')
    def currency_filter(amount):
        """Format amount as currency"""
        return f"${amount:,.2f}"
    
    @app.template_filter('date_format')
    def date_format_filter(date, format='%B %d, %Y'):
        """Format date"""
        return date.strftime(format) if date else ''
    
    @app.template_filter('truncate_words')
    def truncate_words_filter(text, length=50):
        """Truncate text to specified number of characters"""
        if len(text) <= length:
            return text
        return text[:length] + '...'
    
    # Before request handlers
    @app.before_request
    def before_request():
        """Executed before each request"""
        # You can add global before-request logic here
        # For example: check if user is banned, log requests, etc.
        pass
    
    # After request handlers
    @app.after_request
    def after_request(response):
        """Executed after each request"""
        # Add security headers
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        return response
    
    return app

# Create the app instance
app = create_app()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
