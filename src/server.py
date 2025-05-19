"""
Updated app.py file to integrate the enhancements.
"""
from flask import Flask, render_template, request, send_file, redirect, url_for, abort, jsonify
import os
import datetime
import io
import zipfile
import logging
from .plugins import PluginManager
from .app_extensions import setup_enhancements
from .api_models import QueryRequest, ProcessRequest
from pydantic import ValidationError

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("flask_file_explorer")

# Create Flask application
app = Flask(__name__, static_folder='static')

# Default plugin directory
PLUGIN_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "plugins")

def create_app(config=None):
    """
    Create and configure the Flask application
    
    Args:
        config: Configuration dictionary or object
        
    Returns:
        Flask application instance
    """
    # Initialize the plugin manager
    plugin_manager = PluginManager(PLUGIN_DIR)
    
    # Make plugin registry available to the app
    app.plugin_manager = plugin_manager
    app.plugin_registry = plugin_manager.registry if hasattr(plugin_manager, 'registry') else None

    # Set default base directory configuration if not provided
    default_base_dir = os.environ.get('FLASK_FILE_EXPLORER_BASE_DIR', os.path.expanduser('~'))
    app.config.setdefault('BASE_DIR', default_base_dir)
    
    # Apply provided configuration (potentially overriding BASE_DIR for tests)
    if config:
        app.config.update(config)
    
    # Setup enhancements
    enhance = setup_enhancements()
    enhance(app)
    
    return app

def get_file_info(base_dir, path, name):
    """Get file information"""
    # Ensure base_dir is used correctly
    full_path = os.path.abspath(os.path.join(base_dir, path, name))
    # Check if path is within base_dir (security check)
    if not full_path.startswith(os.path.abspath(base_dir)):
        logger.warning(f"Attempt to access restricted path: {full_path}")
        return None # Or raise an error

    try:
        stat_info = os.stat(full_path)
        modified = datetime.datetime.fromtimestamp(stat_info.st_mtime)
        
        return {
            'name': name,
            'path': os.path.join(path, name) if path else name,
            'size': stat_info.st_size,
            'modified': modified.strftime('%Y-%m-%d %H:%M:%S')
        }
    except FileNotFoundError:
        logger.error(f"File not found during get_file_info: {full_path}")
        return None
    except Exception as e:
        logger.error(f"Error getting file info for {full_path}: {e}")
        return None

@app.route('/')
def index():
    """Redirect to the explorer view"""
    return redirect(url_for('explore', path=''))

@app.route('/explore/')
@app.route('/explore/<path:path>')
def explore(path=''):
    """
    Main explorer view for browsing directories and files
    
    Args:
        path (str): Relative path to explore
        
    Returns:
        Rendered template or file download
    """
    # Use configured BASE_DIR
    base_dir = app.config.get('BASE_DIR')
    if not base_dir:
        logger.error("BASE_DIR is not configured in the application.")
        abort(500, description="Application base directory not configured.")
        
    # Convert the path to absolute path relative to configured BASE_DIR
    abs_path = os.path.abspath(os.path.join(base_dir, path))
    
    # Security check to prevent directory traversal attacks
    if not abs_path.startswith(os.path.abspath(base_dir)):
        abort(403)  # Forbidden
    
    # Check if path is a file, if so, download it
    if os.path.isfile(abs_path):
        return send_file(abs_path, as_attachment=True)
    
    # Get list of files and directories
    try:
        items = os.listdir(abs_path)
    except PermissionError:
        abort(403)  # Forbidden
    except FileNotFoundError:
        abort(404)  # Not Found
    
    # Get sort parameters
    sort_by = request.args.get('sort', 'name')
    sort_desc = request.args.get('desc', 'false') == 'true'
    
    # Get search parameter
    search = request.args.get('search', '').lower()
    
    # Separate directories and files
    dirs = []
    files = []
    
    for item in items:
        # Apply search filter
        if search and search not in item.lower():
            continue
            
        item_path = os.path.join(abs_path, item)
        if os.path.isdir(item_path):
            try:
                modified_time = os.path.getmtime(item_path)
                dirs.append({
                    'name': item,
                    'path': os.path.join(path, item) if path else item,
                    'modified': datetime.datetime.fromtimestamp(modified_time).strftime('%Y-%m-%d %H:%M:%S')
                })
            except Exception as e:
                 logger.error(f"Error getting directory info for {item_path}: {e}")
        else:
            # Pass the configured base_dir to get_file_info
            file_info = get_file_info(base_dir, path, item)
            if file_info:
                 files.append(file_info)
            else:
                 logger.warning(f"Could not get file info for: {item}")
    
    # Sort directories and files
    if sort_by == 'name':
        dirs.sort(key=lambda x: x['name'].lower(), reverse=sort_desc)
        files.sort(key=lambda x: x['name'].lower(), reverse=sort_desc)
    elif sort_by == 'size':
        files.sort(key=lambda x: x['size'], reverse=sort_desc)
    elif sort_by == 'modified':
        dirs.sort(key=lambda x: x['modified'], reverse=sort_desc)
        files.sort(key=lambda x: x['modified'], reverse=sort_desc)
    
    # Get parent directory
    parent_path = os.path.dirname(path) if path else None
    
    # Get toolbar items from plugin manager
    plugins = app.plugin_manager.get_toolbar_items() if hasattr(app, 'plugin_manager') else []
    
    return render_template('explorer.html', 
                          current_path=path,
                          parent_path=parent_path,
                          dirs=dirs,
                          files=files,
                          sort_by=sort_by,
                          sort_desc=sort_desc,
                          search=search,
                          plugins=plugins)

@app.route('/plugins/execute/<plugin_id>')
def execute_plugin(plugin_id):
    """
    Execute a plugin with the given ID
    
    Args:
        plugin_id (str): ID of the plugin to execute
        
    Returns:
        JSON response with plugin execution results
    """
    # Use configured BASE_DIR
    base_dir = app.config.get('BASE_DIR')
    if not base_dir:
        logger.error("BASE_DIR is not configured in the application.")
        return jsonify({"success": False, "error": "Application base directory not configured."}), 500
        
    path = request.args.get('path', '')
    abs_path = os.path.abspath(os.path.join(base_dir, path))
    
    # Security check to prevent directory traversal attacks
    if not abs_path.startswith(os.path.abspath(base_dir)):
        return jsonify({
            "success": False,
            "error": "Invalid path"
        }), 403
    
    # Execute the plugin
    if not hasattr(app, 'plugin_manager'):
        return jsonify({
            "success": False,
            "error": "Plugin system not initialized"
        }), 500
        
    result = app.plugin_manager.execute_plugin(plugin_id, path=abs_path)
    
    if result is None:
        return jsonify({
            "success": False,
            "error": f"Plugin {plugin_id} not found"
        }), 404
    
    return jsonify(result)

# API endpoints for backend plugins
@app.route('/api/plugins/<plugin_id>/query', methods=['POST'])
def plugin_query(plugin_id):
    """
    Handle plugin query
    
    Args:
        plugin_id (str): ID of the plugin to query
        
    Returns:
        JSON response with query results
    """
    if not hasattr(app, 'plugin_manager') or not app.plugin_manager.registry or plugin_id not in app.plugin_manager.registry.plugins:
        return jsonify({"error": "Plugin not found"}), 404

    try:
        payload = QueryRequest.model_validate(request.get_json() or {})
    except ValidationError as exc:
        return jsonify({"error": "Invalid request format", "details": exc.errors()}), 400

    # Enrich context with base_dir
    context = {**payload.context, "base_dir": app.config.get('BASE_DIR')}

    # Execute the plugin using the query_handler hook
    result = app.plugin_manager.execute_plugin(
        plugin_id,
        hook_name='query_handler',
        query=payload.query,
        context=context
    )

    return jsonify(result)

@app.route('/api/plugins/<plugin_id>/process', methods=['POST'])
def plugin_process_file(plugin_id):
    """
    Process a file with a plugin
    
    Args:
        plugin_id (str): ID of the plugin to use for processing
        
    Returns:
        JSON response with processing results
    """
    if not hasattr(app, 'plugin_manager') or not app.plugin_manager.registry or plugin_id not in app.plugin_manager.registry.plugins:
        return jsonify({"error": "Plugin not found"}), 404

    try:
        payload = ProcessRequest.model_validate(request.get_json() or {})
    except ValidationError as exc:
        return jsonify({"error": "Invalid request format", "details": exc.errors()}), 400

    file_path = payload.path

    # Security check to prevent directory traversal attacks
    base_dir = app.config.get('BASE_DIR')
    if not base_dir:
        logger.error("BASE_DIR is not configured in the application.")
        return jsonify({"error": "Application base directory not configured."}), 500

    abs_path = os.path.abspath(os.path.join(base_dir, file_path))
    if not abs_path.startswith(os.path.abspath(base_dir)):
        return jsonify({"error": "Invalid path"}), 403

    if not os.path.exists(abs_path):
        return jsonify({"error": "File not found"}), 404

    try:
        with open(abs_path, 'r') as f:
            content = f.read()

        # Execute the plugin using the file_processor hook
        result = app.plugin_manager.execute_plugin(
            plugin_id,
            hook_name='file_processor',
            file_path=abs_path,
            file_content=content,
            metadata=payload.metadata
        )

        # Fallback to direct call if hook not handled
        if (
            isinstance(result, dict)
            and result.get('error')
            and 'did not respond to hook' in result.get('error')
        ):
            plugin_instance = app.plugin_manager.registry.get_plugin(plugin_id)
            if hasattr(plugin_instance, 'on_file_processor'):
                direct_result = plugin_instance.on_file_processor(
                    abs_path, content, payload.metadata
                )
                if direct_result:
                    return jsonify(direct_result)

        return jsonify(result)
    except Exception as e:
        logger.error(f"Error processing file with plugin {plugin_id}: {e}")
        return jsonify({"error": str(e), "success": False}), 500

@app.route('/api/plugins/hooks/<hook_name>', methods=['POST'])
def invoke_hook(hook_name):
    """
    Invoke a hook on all registered plugins
    
    Args:
        hook_name (str): Name of the hook to invoke
        
    Returns:
        JSON response with results from all plugins
    """
    if not hasattr(app, 'plugin_manager') or not hasattr(app.plugin_manager, 'invoke_hook'):
        return jsonify({"error": "Hook system not available"}), 404
        
    data = request.json or {}
    
    # Invoke the hook on all registered plugins
    results = app.plugin_manager.invoke_hook(hook_name, **data)
    
    return jsonify({
        "success": True,
        "results": results
    })


@app.route('/download-selected', methods=['POST'])
def download_selected():
    """Download multiple selected files and folders as a ZIP archive."""
    base_dir = app.config.get('BASE_DIR')
    if not base_dir:
        logger.error("BASE_DIR is not configured in the application.")
        abort(500, description="Application base directory not configured.")

    data = request.get_json() or {}
    paths = data.get("paths")
    if not isinstance(paths, list) or not paths:
        return jsonify({"error": "No paths provided"}), 400

    memory_file = io.BytesIO()
    with zipfile.ZipFile(memory_file, "w", zipfile.ZIP_DEFLATED) as zipf:
        for rel_path in paths:
            abs_path = os.path.abspath(os.path.join(base_dir, rel_path))
            if not abs_path.startswith(os.path.abspath(base_dir)):
                abort(403)
            if os.path.isdir(abs_path):
                for root_dir, _, files in os.walk(abs_path):
                    for fname in files:
                        abs_file = os.path.join(root_dir, fname)
                        arcname = os.path.relpath(abs_file, base_dir)
                        zipf.write(abs_file, arcname)
            elif os.path.isfile(abs_path):
                zipf.write(abs_path, rel_path)

    memory_file.seek(0)
    return send_file(
        memory_file,
        download_name="selected_files.zip",
        mimetype="application/zip",
        as_attachment=True,
    )
