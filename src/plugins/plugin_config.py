"""
Plugin configuration page for the Web File Explorer.
Provides a UI for configuring plugin settings.
"""
from flask import render_template, request, jsonify, Blueprint, current_app, abort, redirect, url_for
import os
import json
import logging

# Setup logging
logger = logging.getLogger("plugin_config")

# Create Blueprint for plugin configuration
plugin_config_bp = Blueprint('plugin_config', __name__)

@plugin_config_bp.route('/')
def index():
    """Show list of installed plugins with configuration options"""
    if not hasattr(current_app, 'plugin_manager'):
        abort(500, description="Plugin system not initialized")
        
    # Get all plugins (UI and backend)
    ui_plugins = {pid: p['manifest'] for pid, p in current_app.plugin_manager.plugins.items()}
    backend_plugins = current_app.plugin_manager.get_backend_plugins() if hasattr(current_app.plugin_manager, 'get_backend_plugins') else {}
    
    # Combine all plugins with their settings
    all_plugins = []
    
    # Process UI plugins
    for plugin_id, manifest in ui_plugins.items():
        settings = manifest.get('settings', {})
        all_plugins.append({
            'id': plugin_id,
            'name': manifest.get('name', plugin_id),
            'description': manifest.get('description', ''),
            'version': manifest.get('version', '0.0.0'),
            'type': 'ui',
            'settings': settings,
            'has_settings': bool(settings),
            'icon': manifest.get('icon', '🔌')
        })
    
    # Process backend plugins
    for plugin_id, plugin in backend_plugins.items():
        if hasattr(plugin, 'get_settings'):
            settings = plugin.get_settings()
        else:
            settings = {}
            
        all_plugins.append({
            'id': plugin_id,
            'name': plugin.manifest.get('name', plugin_id) if hasattr(plugin, 'manifest') else plugin_id,
            'description': plugin.manifest.get('description', '') if hasattr(plugin, 'manifest') else '',
            'version': plugin.manifest.get('version', '0.0.0') if hasattr(plugin, 'manifest') else '0.0.0',
            'type': 'backend',
            'settings': settings,
            'has_settings': bool(settings),
            'icon': plugin.manifest.get('icon', '🔌') if hasattr(plugin, 'manifest') else '🔌'
        })
    
    # Sort plugins by name
    all_plugins.sort(key=lambda p: p['name'])
    
    # Render the template
    return render_template('plugin_config.html', 
                          plugins=all_plugins)

@plugin_config_bp.route('/<plugin_id>')
def plugin_detail(plugin_id):
    """Show configuration form for a specific plugin"""
    # Get plugin manager
    if not hasattr(current_app, 'plugin_manager'):
        abort(500, description="Plugin system not initialized")
    
    # Check if it's a UI plugin
    plugin_data = None
    plugin_type = None
    
    if plugin_id in current_app.plugin_manager.plugins:
        # Get UI plugin
        plugin = current_app.plugin_manager.plugins[plugin_id]
        plugin_data = {
            'id': plugin_id,
            'name': plugin['manifest'].get('name', plugin_id),
            'description': plugin['manifest'].get('description', ''),
            'version': plugin['manifest'].get('version', '0.0.0'),
            'settings': plugin['manifest'].get('settings', {}),
            'icon': plugin['manifest'].get('icon', '🔌')
        }
        plugin_type = 'ui'
    elif hasattr(current_app.plugin_manager, 'get_backend_plugins'):
        # Check backend plugins
        backend_plugins = current_app.plugin_manager.get_backend_plugins()
        if plugin_id in backend_plugins:
            plugin = backend_plugins[plugin_id]
            if hasattr(plugin, 'get_settings'):
                settings = plugin.get_settings()
            else:
                settings = {}
                
            plugin_data = {
                'id': plugin_id,
                'name': plugin.manifest.get('name', plugin_id) if hasattr(plugin, 'manifest') else plugin_id,
                'description': plugin.manifest.get('description', '') if hasattr(plugin, 'manifest') else '',
                'version': plugin.manifest.get('version', '0.0.0') if hasattr(plugin, 'manifest') else '0.0.0',
                'settings': settings,
                'icon': plugin.manifest.get('icon', '🔌') if hasattr(plugin, 'manifest') else '🔌'
            }
            plugin_type = 'backend'
    
    if not plugin_data:
        abort(404, description=f"Plugin {plugin_id} not found")
    
    return render_template('plugin_detail.html', 
                          plugin=plugin_data,
                          plugin_type=plugin_type)

@plugin_config_bp.route('/<plugin_id>/save', methods=['POST'])
def save_plugin_settings(plugin_id):
    """Save plugin settings"""
    if not hasattr(current_app, 'plugin_manager'):
        return jsonify({"success": False, "error": "Plugin system not initialized"}), 500
    
    # Get the submitted settings
    try:
        if request.is_json:
            settings = request.get_json()
        else:
            # Handle form data
            settings = {}
            # Handle special case for exclude_patterns which is a list
            if 'exclude_patterns' in request.form:
                settings['exclude_patterns'] = request.form.getlist('exclude_patterns')
            else:
                # Handle regular form fields
                settings = {k: v for k, v in request.form.items()}
    except Exception as e:
        logger.error(f"Error processing settings data: {e}")
        return jsonify({"success": False, "error": f"Invalid settings format: {str(e)}"}), 400
    
    # Check if it's a UI plugin
    updated = False
    plugin_type = None
    
    if plugin_id in current_app.plugin_manager.plugins:
        # Update UI plugin settings
        plugin = current_app.plugin_manager.plugins[plugin_id]
        if 'settings' not in plugin['manifest']:
            plugin['manifest']['settings'] = {}
            
        plugin['manifest']['settings'].update(settings)
        updated = True
        plugin_type = 'ui'
        
        # Save to manifest.json if possible
        try:
            manifest_path = os.path.join(plugin['path'], 'manifest.json')
            if os.path.exists(manifest_path):
                with open(manifest_path, 'r') as f:
                    manifest_data = json.load(f)
                
                if 'settings' not in manifest_data:
                    manifest_data['settings'] = {}
                    
                manifest_data['settings'].update(settings)
                
                with open(manifest_path, 'w') as f:
                    json.dump(manifest_data, f, indent=4)
                    
                logger.info(f"Saved settings to manifest.json for plugin {plugin_id}")
        except Exception as e:
            logger.warning(f"Could not save settings to manifest.json: {e}")
            # Continue anyway, settings are updated in memory
            
    elif hasattr(current_app.plugin_manager, 'get_backend_plugins'):
        # Check backend plugins
        backend_plugins = current_app.plugin_manager.get_backend_plugins()
        if plugin_id in backend_plugins:
            plugin = backend_plugins[plugin_id]
            if hasattr(plugin, 'update_settings'):
                plugin.update_settings(settings)
                updated = True
                plugin_type = 'backend'
    
    if not updated:
        return jsonify({"success": False, "error": f"Plugin {plugin_id} not found or does not support settings"}), 404
    
    if request.is_json:
        return jsonify({"success": True, "message": "Settings saved successfully", "plugin_type": plugin_type})
    else:
        # Redirect back to the plugin configuration page for form submissions
        return redirect(url_for('plugin_config.index'))

def register_blueprint(app):
    """Register the plugin configuration blueprint with the Flask app"""
    app.register_blueprint(plugin_config_bp, url_prefix='/plugin-config')