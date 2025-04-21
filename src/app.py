from flask import Flask, render_template, request, send_file, redirect, url_for, abort, jsonify
import os
import datetime
import mimetypes
from plugins import PluginManager

app = Flask(__name__, static_folder='static')

BASE_DIR = "/home/pals/code"
PLUGIN_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "plugins")

# Initialize the plugin manager
plugin_manager = PluginManager(PLUGIN_DIR)

def get_file_info(base_dir, path, name):
    """Get file information"""
    full_path = os.path.join(base_dir, path, name)
    stat_info = os.stat(full_path)
    modified = datetime.datetime.fromtimestamp(stat_info.st_mtime)
    
    return {
        'name': name,
        'path': os.path.join(path, name) if path else name,
        'size': stat_info.st_size,
        'modified': modified.strftime('%Y-%m-%d %H:%M:%S')
    }

@app.route('/')
def index():
    return redirect(url_for('explore', path=''))

@app.route('/explore/')
@app.route('/explore/<path:path>')
def explore(path=''):
    # Convert the path to absolute path
    abs_path = os.path.abspath(os.path.join(BASE_DIR, path))
    
    # Security check to prevent directory traversal attacks
    if not abs_path.startswith(BASE_DIR):
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
            dirs.append({
                'name': item,
                'path': os.path.join(path, item) if path else item,
                'modified': datetime.datetime.fromtimestamp(os.path.getmtime(item_path)).strftime('%Y-%m-%d %H:%M:%S')
            })
        else:
            files.append(get_file_info(BASE_DIR, path, item))
    
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
    
    return render_template('explorer.html', 
                          current_path=path,
                          parent_path=parent_path,
                          dirs=dirs,
                          files=files,
                          sort_by=sort_by,
                          sort_desc=sort_desc,
                          search=search,
                          plugins=plugin_manager.get_toolbar_items())

@app.route('/plugins/execute/<plugin_id>')
def execute_plugin(plugin_id):
    """Execute a plugin with the given ID"""
    path = request.args.get('path', '')
    abs_path = os.path.abspath(os.path.join(BASE_DIR, path))
    
    # Security check to prevent directory traversal attacks
    if not abs_path.startswith(BASE_DIR):
        return jsonify({
            "success": False,
            "error": "Invalid path"
        }), 403
    
    # Execute the plugin
    result = plugin_manager.execute_plugin(plugin_id, path=abs_path)
    
    if result is None:
        return jsonify({
            "success": False,
            "error": f"Plugin {plugin_id} not found"
        }), 404
    
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)