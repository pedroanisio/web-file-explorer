# FIXIT Plugin Development Guide

This guide provides comprehensive information for developers who want to build plugins for the FIXIT application. FIXIT supports two types of plugins:

1. **Frontend (UI) Plugins**: Appear in the toolbar and provide user-facing functionality
2. **Backend Plugins**: Provide server-side functionality through hooks and services

## Table of Contents

- [Plugin System Architecture](#plugin-system-architecture)
- [Frontend Plugin Development](#frontend-plugin-development)
  - [Frontend Plugin Structure](#frontend-plugin-structure)
  - [Manifest File](#frontend-manifest-file)
  - [Entry Point](#frontend-entry-point)
  - [Example: UI Plugin](#example-ui-plugin)
- [Backend Plugin Development](#backend-plugin-development)
  - [Backend Plugin Structure](#backend-plugin-structure)
  - [Manifest File](#backend-manifest-file)
  - [Plugin Base Class](#plugin-base-class)
  - [Hooks System](#hooks-system)
  - [Example: Backend Plugin](#example-backend-plugin)
- [Dependencies Management](#dependencies-management)
- [Integration with FIXIT](#integration-with-fixit)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)

## Plugin System Architecture

The FIXIT plugin system is designed to be modular and extensible. It consists of:

- **Plugin Manager**: Central component that discovers, loads, and manages plugins
- **Plugin Registry**: Maintains references to all active plugins and their hooks
- **Dependency Manager**: Handles plugin dependencies and installation
- **Hook System**: Enables plugins to register for specific events or extension points

Plugins are loaded from the `src/plugins` directory, with each plugin having its own subdirectory.

## Frontend Plugin Development

Frontend plugins provide user-facing functionality through the FIXIT UI. They appear in the toolbar and can be activated by the user.

### Frontend Plugin Structure

A typical frontend plugin has the following structure:

```
src/plugins/your_plugin_name/
├── __init__.py             # Package initialization
├── manifest.json           # Plugin metadata and configuration
├── your_entry_point.py     # Main plugin logic
└── ... (other files)       # Additional resources
```

### Frontend Manifest File

The `manifest.json` file defines the plugin's metadata and configuration:

```json
{
    "id": "your_plugin_id",
    "name": "Your Plugin Name",
    "version": "1.0.0",
    "description": "Description of what your plugin does",
    "entry_point": "your_entry_point",
    "icon": "🔍"
}
```

Required fields:
- `id`: Unique identifier for the plugin
- `name`: Display name shown in the UI
- `version`: Plugin version
- `entry_point`: Python module name (without .py) that contains the execute function
- `icon`: Emoji or character to display in the UI

### Frontend Entry Point

Your entry point module must define an `execute` function that will be called when the plugin is activated:

```python
def execute(path, **kwargs):
    """
    Execute the plugin logic
    
    Args:
        path (str): The absolute path to the current directory in the file explorer
        **kwargs: Additional arguments provided by the application
        
    Returns:
        dict: Result of the plugin execution
    """
    # Your plugin logic here
    
    return {
        "success": True,
        "output": "Plugin output to display",
        "title": "Result Title"
    }
```

#### Important Note on Path Handling

The `path` parameter provided to your plugin's `execute` function is an **absolute path** to the current directory in the file explorer. This is important to understand when running commands or performing file operations in your plugin.

For example, if the user is viewing `/home/user/projects` in the file explorer and activates your plugin, the `path` parameter will be `/home/user/projects` (not a relative path). When running shell commands, you should use this absolute path directly.

##### Example: File Operations

```python
def execute(path, **kwargs):
    # path is already an absolute path like '/home/user/projects'
    # For file operations, use it directly
    files = os.listdir(path)
    
    # To open a file in the current directory
    with open(os.path.join(path, 'some_file.txt'), 'r') as f:
        content = f.read()
    
    return {
        "success": True,
        "output": f"Found {len(files)} files"
    }
```

##### Example: Running Shell Commands

```python
def execute(path, **kwargs):
    # For shell commands, make sure to properly quote the path
    # to handle spaces and special characters
    command = f'cd "{path}" && ls -la'
    
    result = subprocess.run(
        command,
        shell=True,
        capture_output=True,
        text=True
    )
    
    return {
        "success": True,
        "output": result.stdout
    }
```

The return value should be a dictionary with the following keys:
- `success`: Boolean indicating if the plugin executed successfully
- `output`: Text output to display in the modal
- `title`: Title for the modal dialog
- `error`: Error message if success is False

### Example: UI Plugin

Here's a simple example of a UI plugin that counts files in a directory:

#### manifest.json
```json
{
    "id": "file_counter",
    "name": "File Counter",
    "version": "1.0.0",
    "description": "Counts files in the current directory",
    "entry_point": "counter_plugin",
    "icon": "🔢"
}
```

#### counter_plugin.py
```python
import os

def execute(path, **kwargs):
    """
    Count files in the given directory
    
    Args:
        path (str): Directory path
        
    Returns:
        dict: Count results
    """
    try:
        if not os.path.isdir(path):
            return {
                "success": False,
                "error": f"{path} is not a directory"
            }
        
        # Count files and subdirectories
        files = []
        dirs = []
        for item in os.listdir(path):
            item_path = os.path.join(path, item)
            if os.path.isfile(item_path):
                files.append(item)
            elif os.path.isdir(item_path):
                dirs.append(item)
        
        # Prepare output
        output = f"Directory: {path}\n\n"
        output += f"Files: {len(files)}\n"
        output += f"Subdirectories: {len(dirs)}\n"
        
        return {
            "success": True,
            "output": output,
            "title": "File Count Results"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }
```

## Backend Plugin Development

Backend plugins provide server-side functionality through a hook system. They don't necessarily have UI components but extend the application's capabilities.

### Backend Plugin Structure

A typical backend plugin has the following structure:

```
src/plugins/your_backend_plugin/
├── __init__.py             # Package initialization
├── manifest.json           # Plugin metadata and configuration
├── your_entry_point.py     # Main plugin logic
├── tools/                  # Plugin-specific tools or utilities
│   └── ... 
└── ... (other files)       # Additional resources
```

### Backend Manifest File

The `manifest.json` file for a backend plugin includes additional fields:

```json
{
    "id": "your_backend_plugin",
    "name": "Your Backend Plugin",
    "version": "1.0.0",
    "description": "Description of your backend plugin",
    "entry_point": "your_entry_point",
    "type": "backend",
    "hooks": [
        "file_processor",
        "query_handler"
    ],
    "dependencies": [
        "package>=1.0.0"
    ],
    "settings": {
        "setting1": "value1",
        "setting2": "value2"
    },
    "auto_install_dependencies": false
}
```

Additional fields for backend plugins:
- `type`: Set to "backend" to identify as a backend plugin
- `hooks`: List of hooks this plugin will register for
- `dependencies`: List of Python package dependencies
- `settings`: Configuration settings for the plugin
- `auto_install_dependencies`: Whether to automatically install dependencies

### Plugin Base Class

Backend plugins should extend the `BackendPlugin` base class:

```python
from plugins.plugin_base import BackendPlugin

class YourBackendPlugin(BackendPlugin):
    """
    Your backend plugin implementation
    """
    
    def __init__(self, plugin_id, manifest, registry):
        super().__init__(plugin_id, manifest, registry)
        # Initialize your plugin
        
    def activate(self):
        """Called when the plugin is activated"""
        # Setup and initialization
        
    def deactivate(self):
        """Called before the plugin is deactivated"""
        # Cleanup
        
    def on_file_processor(self, file_path, file_content, metadata=None):
        """Hook implementation for file_processor"""
        # Process file content
        return {
            "result": "Processing result",
            "success": True
        }
        
    def on_query_handler(self, query, context=None):
        """Hook implementation for query_handler"""
        # Handle query
        return {
            "response": "Query response",
            "success": True
        }
```

Your entry point module must define a `create_plugin` function:

```python
def create_plugin(plugin_id, manifest, registry):
    """Create the plugin instance"""
    return YourBackendPlugin(plugin_id, manifest, registry)
```

### Hooks System

The hooks system allows plugins to register for specific events or extension points. Hook methods are automatically registered if they follow the naming pattern `on_<hook_name>`.

Available hooks:
- `file_processor`: Process file content
- `query_handler`: Handle user queries
- `startup`: Called on application startup
- `shutdown`: Called before application shutdown
- `content_transform`: Transform content
- `authentication`: Custom auth handlers

### Example: Backend Plugin

Here's a simple example of a backend plugin that analyzes Python files:

#### manifest.json
```json
{
    "id": "py_analyzer",
    "name": "Python Analyzer",
    "version": "1.0.0",
    "description": "Analyzes Python files",
    "entry_point": "analyzer_plugin",
    "type": "backend",
    "hooks": [
        "file_processor"
    ],
    "dependencies": [
        "beautifulsoup4>=4.9.0"
    ],
    "settings": {
        "max_complexity": 10
    }
}
```

#### analyzer_plugin.py
```python
import ast
import logging

# Setup logging
logger = logging.getLogger("py_analyzer")

def create_plugin(plugin_id, manifest, registry):
    """Create the plugin instance"""
    return PythonAnalyzerPlugin(plugin_id, manifest, registry)

class PythonAnalyzerPlugin:
    """
    Python code analyzer plugin
    """
    
    def __init__(self, plugin_id, manifest, registry):
        self.plugin_id = plugin_id
        self.manifest = manifest
        self.registry = registry
        
    def activate(self):
        """Called when the plugin is activated"""
        logger.info("Python Analyzer plugin activated")
        
    def get_settings(self):
        """Return plugin settings"""
        return self.manifest.get('settings', {})
        
    def on_file_processor(self, file_path, file_content, metadata=None):
        """Process Python files and provide analysis"""
        if not file_path.endswith('.py'):
            return {
                "success": True,
                "skipped": True,
                "message": "Not a Python file"
            }
            
        try:
            # Parse the Python code
            tree = ast.parse(file_content)
            
            # Extract information
            functions = []
            classes = []
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    functions.append({
                        "name": node.name,
                        "line": node.lineno,
                        "args": [arg.arg for arg in node.args.args]
                    })
                elif isinstance(node, ast.ClassDef):
                    classes.append({
                        "name": node.name,
                        "line": node.lineno
                    })
            
            return {
                "success": True,
                "analysis": {
                    "functions": functions,
                    "classes": classes,
                    "summary": f"Found {len(functions)} functions and {len(classes)} classes"
                }
            }
        except Exception as e:
            logger.error(f"Error analyzing file: {e}")
            return {
                "success": False,
                "error": str(e)
            }
```

## Dependencies Management

Backend plugins can specify their dependencies in the manifest file. The dependency manager will check if these dependencies are satisfied and optionally install them.

```json
"dependencies": [
    "package>=1.0.0",
    "other-package==2.1.0"
]
```

**Important notes about dependencies:**

1. Only specify **third-party packages** that need to be installed via pip. Do not include built-in Python modules (like `ast`, `os`, `json`, etc.) in the dependencies list.

2. If `auto_install_dependencies` is set to `true`, the system will attempt to install missing dependencies automatically. Default is `false`.

3. Make sure your plugin gracefully handles missing dependencies with proper try/except blocks around imports.

## Integration with FIXIT

### Adding API Endpoints

For backend plugins that need to expose API endpoints, you can add routes to the main Flask application:

```python
# In app.py

@app.route('/api/plugins/<plugin_id>/query', methods=['POST'])
def plugin_query(plugin_id):
    """Handle plugin query"""
    if plugin_id not in app.plugin_registry.plugins:
        return jsonify({"error": "Plugin not found"}), 404
        
    data = request.json
    query = data.get('query', '')
    context = data.get('context', {})
    
    results = app.plugin_registry.invoke_hook(
        'query_handler',
        query,
        context
    )
    
    # Filter results for requested plugin
    plugin_results = next(
        (r for r in results if r['plugin_id'] == plugin_id), 
        {"error": "Plugin did not handle query", "success": False}
    )
    
    return jsonify(plugin_results)
```

### Using Hooks

You can invoke hooks from the main application:

```python
# Invoke a hook on all registered plugins
results = app.plugin_manager.invoke_hook('file_processor', file_path, file_content)
```

### Testing Backend Plugins with cURL

You can test backend plugins directly using cURL commands. Here are examples for testing the Python Analyzer plugin:

#### Testing file processing

```bash
# Process a Python file with py_analyzer plugin
curl -X POST http://127.0.0.1:5000/api/plugins/py_analyzer/process \
  -H "Content-Type: application/json" \
  -d '{"path": "/path/to/your/file.py"}'
```

#### Testing query handling

```bash
# Send a query to a plugin that implements the query_handler hook
curl -X POST http://127.0.0.1:5000/api/plugins/<plugin_id>/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What are the classes in this project?", "context": {"project_path": "/path/to/project"}}'
```

#### Invoking a specific hook

```bash
# Invoke a specific hook on all registered plugins
curl -X POST http://127.0.0.1:5000/api/plugins/hooks/file_processor \
  -H "Content-Type: application/json" \
  -d '{"file_path": "/path/to/file.py", "file_content": "print(\\"Hello World\\")"}'  
```

## Best Practices

1. **Plugin Isolation**: Keep your plugin code isolated and avoid dependencies on other plugins

2. **Error Handling**: Implement robust error handling to prevent plugin failures from affecting the main application
   - Wrap third-party imports in try/except blocks
   - Define fallback behavior when dependencies are not available
   - Validate all inputs before processing

3. **Resource Management**: Clean up resources in the `deactivate` method

4. **Documentation**: Document your plugin's functionality, hooks, and configuration options

5. **Version Management**: Follow semantic versioning for your plugins

6. **Dependency Management**: Only specify external dependencies that need installation
   - Don't include built-in Python modules in dependencies
   - Specify minimum versions required for compatibility
6. **Security**: Validate all inputs, especially for backend plugins

## Troubleshooting

### Common Issues

1. **Plugin not loading**:
   - Check if the plugin directory structure is correct
   - Ensure the manifest.json file is valid JSON
   - Verify all required fields are present in the manifest

2. **Hook not being called**:
   - Ensure the hook is registered in the manifest
   - Check that the hook method follows the naming convention `on_<hook_name>`

3. **Dependencies not resolved**:
   - Verify dependency specifications
   - Check for version conflicts

### Debugging

Enable debug logging to get more information about plugin loading and execution:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Getting Help

If you encounter issues or have questions, please:
- Check the documentation
- Look for similar issues in the issue tracker
- Reach out to the FIXIT development team
