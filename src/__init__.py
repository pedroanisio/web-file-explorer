"""Flask File Explorer - A simple web-based file explorer built with Flask."""

__version__ = "0.1.0"

from .app import create_app, app
import os

def main():
    """Run the application."""
    # Use create_app to ensure config is loaded and plugins initialized
    flask_app = create_app() 
    # Use flask_app instance instead of module-level app
    # Read FLASK_DEBUG from environment, default to '0' (False)
    is_debug = os.environ.get('FLASK_DEBUG', '0') == '1'
    # Read host and port from ENV variables for Docker
    host = os.environ.get('FLASK_RUN_HOST', '127.0.0.1')
    port = int(os.environ.get('FLASK_RUN_PORT', 5000))
    flask_app.run(host=host, port=port, debug=is_debug)