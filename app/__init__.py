"""Application factory and configuration."""
import os
from flask import Flask
from flask_talisman import Talisman
from config import config


def create_app(config_name=None):
    """Create and configure the Flask application."""
    
    # Use environment variable or default to development
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')
    
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    from app.extensions import db, login_manager, bcrypt, csrf, limiter
    
    db.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    csrf.init_app(app)
    limiter.init_app(app)
    
    # Security Headers (Talisman)
    talisman = Talisman(
        app,
        force_https=False,  # Set to True in production
        strict_transport_security=False,  # Set to True in production with HTTPS
        content_security_policy={
            'default-src': "'self'",
            'script-src': [
                "'self'",
                "'unsafe-inline'",  # For inline scripts (Bootstrap, animations)
                "https://cdn.jsdelivr.net",  # Bootstrap CDN
            ],
            'style-src': [
                "'self'",
                "'unsafe-inline'",  # For inline styles
                "https://cdn.jsdelivr.net",  # Bootstrap CDN
            ],
            'img-src': [
                "'self'",
                "data:",
                "https://www.gravatar.com",  # Gravatar avatars
            ],
            'font-src': [
                "'self'",
                "https://cdn.jsdelivr.net",  # Bootstrap icons
            ],
        }
    )
    
    # Register blueprints
    from app.auth.routes import auth_bp
    from app.main.routes import main_bp
    from app.admin.routes import admin_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(admin_bp)
    
    # Error handlers
    @app.errorhandler(429)
    def ratelimit_handler(e):
        """Handle rate limit exceeded errors."""
        from flask import flash, render_template
        flash('Too many requests. Please slow down and try again later.', 'warning')
        return render_template('errors/429.html'), 429
    
    # Create database tables
    with app.app_context():
        db.create_all()
    
    return app