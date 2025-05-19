"""
Integrates Tailwind CSS into the Web File Explorer.
"""
import logging
import os
from flask import render_template, Blueprint, current_app, request, session

# Setup logging
logger = logging.getLogger("tailwind_integration")

# Create Blueprint for theme management
theme_bp = Blueprint('theme', __name__)

@theme_bp.route('/toggle-theme')
def toggle_theme():
    """Toggle between light and dark mode"""
    current_theme = session.get('theme', 'light')
    new_theme = 'dark' if current_theme == 'light' else 'light'
    session['theme'] = new_theme
    
    # Redirect back to the referring page or home
    redirect_url = request.referrer or '/'
    return {"success": True, "theme": new_theme}

def get_theme():
    """Get the current theme from session or preferences"""
    return session.get('theme', 'light')

def register_blueprint(app):
    """Register the theme management blueprint with the Flask app"""
    app.register_blueprint(theme_bp, url_prefix='/theme')

    # Add template context processor to add theme to all templates
    @app.context_processor
    def inject_theme():
        return {'theme': get_theme()}