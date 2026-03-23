"""Application entry point."""
import os
from app import create_app

# Get config from environment or use default
config_name = os.getenv('FLASK_ENV', 'development')
app = create_app(config_name)

if __name__ == '__main__':
    # Use PORT from environment (Railway provides this)
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)