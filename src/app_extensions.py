"""
Integrates all enhancements into the Web File Explorer application.
"""
import os
import logging
from flask import Flask, render_template_string, redirect, url_for, request, session, g

# Import enhancement modules
from .plugins.plugin_config import register_blueprint as register_plugin_config
from .tailwind_integration import register_blueprint as register_theme
from .file_preview import register_blueprint as register_file_preview

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("explorer_enhancements")

def integrate_enhancements(app):
    """
    Integrate all enhancements into the Flask application
    
    Args:
        app: Flask application instance
    """
    logger.info("Integrating Web File Explorer enhancements")
    
    # Setup session for theme preferences
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'default-explorer-secret-key')
    
    # Register enhancement blueprints
    register_plugin_config(app)
    register_theme(app)
    register_file_preview(app)
    
    # Add routes
    @app.route('/enhanced')
    def enhanced_home():
        """Redirect to enhanced explorer view"""
        return redirect(url_for('explore', path=''))
    
    logger.info("Enhancements integrated successfully")

def setup_enhancements():
    """
    Setup function to be called from the main application
    
    Returns:
        function: Function to integrate enhancements
    """
    def enhance(app):
        # Register preview blueprint
        register_file_preview(app)
        
        # Register plugin configuration blueprint
        register_plugin_config(app)
        
        # Set up theme handling
        register_theme_handler(app)
        
        # Register component CSS
        app.static_folder = 'static'
        
        # Add theme context processor
        @app.context_processor
        def inject_theme():
            theme = get_theme(app)
            return {'theme': theme}
            
        return app
        
    return enhance
    
def register_theme_handler(app):
    """Register theme handler routes"""
    @app.route('/theme/toggle-theme')
    def toggle_theme():
        current_theme = get_theme(app)
        new_theme = 'light' if current_theme == 'dark' else 'dark'
        session['theme'] = new_theme
        return {'theme': new_theme}
        
def get_theme(app):
    """Get current theme from session or default"""
    with app.app_context():
        if 'theme' in session:
            return session['theme']
        return app.config.get('DEFAULT_THEME', 'light')