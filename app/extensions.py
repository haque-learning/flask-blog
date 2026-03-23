"""Flask extensions initialization."""
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_wtf.csrf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from sqlalchemy.orm import DeclarativeBase

# Define base class for SQLAlchemy models
class Base(DeclarativeBase):
    pass

# Initialize extensions (don't bind to app yet)
db = SQLAlchemy(model_class=Base)
login_manager = LoginManager()
bcrypt = Bcrypt()
csrf = CSRFProtect()

# Rate limiter
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"
)

# Configure login manager
login_manager.login_view = 'auth.login'  # Blueprint prefix!
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'info'


# User loader for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    from app.models import User
    return User.query.get(int(user_id))