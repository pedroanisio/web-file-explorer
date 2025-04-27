"""Flask File Explorer - A simple web-based file explorer built with Flask."""

__version__ = "0.1.0"

from .app import create_app, app

def main():
    """Run the application."""
    app.run(debug=True)

if __name__ == "__main__":
    main()