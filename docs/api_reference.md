# Flask File Explorer API Reference

This document provides the API reference for Flask File Explorer, including all available endpoints and their usage.

## REST API Endpoints

### Explore Directory

`GET /explore/[path]`

Retrieve directory contents or download a file.

#### Parameters

| Parameter | Type   | Description                                |
|-----------|--------|--------------------------------------------|
| path      | string | Path to the directory or file (optional)   |
| sort      | string | Sort criterion: 'name', 'modified', 'size' |
| desc      | bool   | Sort in descending order if 'true'         |
| search    | string | Search filter for file/directory names     |

#### Responses

- `200 OK`: Returns HTML page with directory contents or file download
- `403 Forbidden`: Path is outside the base directory or permission denied
- `404 Not Found`: Path does not exist

### Execute Plugin

`GET /plugins/execute/<plugin_id>`

Execute a UI plugin with the specified ID.

#### Parameters

| Parameter | Type   | Description                     |
|-----------|--------|---------------------------------|
| plugin_id | string | ID of the plugin to execute     |
| path      | string | Current directory path          |

#### Responses

- `200 OK`: Returns plugin execution result as JSON
- `403 Forbidden`: Path is outside the base directory
- `404 Not Found`: Plugin not found

```json
{
    "success": true,
    "output": "Plugin output",
    "title": "Result Title",
    "is_html": false
}
```

### Plugin Query

`POST /api/plugins/<plugin_id>/query`

Send a query to a backend plugin.

#### Request Body

```json
{
    "query": "The query string",
    "context": {
        "key1": "value1",
        "key2": "value2"
    }
}
```

#### Responses

- `200 OK`: Returns plugin query result as JSON
- `404 Not Found`: Plugin not found

### Process File

`POST /api/plugins/<plugin_id>/process`

Process a file using a backend plugin.

#### Request Body

```json
{
    "path": "/path/to/file",
    "metadata": {
        "key1": "value1"
    }
}
```

#### Responses

- `200 OK`: Returns file processing result as JSON
- `403 Forbidden`: Path is outside the base directory
- `404 Not Found`: Plugin or file not found

### Invoke Hook

`POST /api/plugins/hooks/<hook_name>`

Invoke a hook on all registered plugins.

#### Request Body

```json
{
    "param1": "value1",
    "param2": "value2"
}
```

#### Responses

- `200 OK`: Returns results from all plugins as JSON
- `404 Not Found`: Hook system not available

```json
{
    "success": true,
    "results": [
        {
            "plugin_id": "plugin1",
            "result": {
                "key": "value"
            },
            "success": true
        },
        {
            "plugin_id": "plugin2",
            "result": {
                "key": "value"
            },
            "success": true
        }
    ]
}
```

## Plugin API

### Plugin Registry

The plugin registry maintains references to all active plugins and provides methods for accessing them:

```python
# Get a plugin by ID
plugin = plugin_registry.get_plugin(plugin_id)

# Get all plugins
all_plugins = plugin_registry.get_all_plugins()
```

### Hook System

The hook system allows plugins to register for specific events:

```python
# Register a hook
plugin_registry.register_hook(hook_name, plugin_id, callback)

# Invoke a hook
results = plugin_registry.invoke_hook(hook_name, *args, **kwargs)
```

Available hooks:
- `file_processor`: Process file content
- `query_handler`: Handle user queries
- `startup`: Called on application startup
- `shutdown`: Called before application shutdown

### Backend Plugin Base Class

Backend plugins should extend the `BackendPlugin` base class:

```python
from plugins.plugin_base import BackendPlugin

class MyPlugin(BackendPlugin):
    def __init__(self, plugin_id, manifest, registry):
        super().__init__(plugin_id, manifest, registry)
        
    def activate(self):
        """Called when the plugin is activated"""
        pass
        
    def on_file_processor(self, file_path, file_content, metadata=None):
        """Process file content"""
        return {
            "success": True,
            "result": "Processing result"
        }
```

## Plugin HTTP API Usage Examples

### Execute a UI Plugin

```bash
curl -X GET "http://127.0.0.1:5000/plugins/execute/file_counter?path=%2Fhome%2Fuser%2Fprojects"
```

### Query a Backend Plugin

```bash
curl -X POST "http://127.0.0.1:5000/api/plugins/py_analyzer/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "analyze_code", "context": {"action": "analyze_directory", "path": "/home/user/projects"}}'
```

### Process a File

```bash
curl -X POST "http://127.0.0.1:5000/api/plugins/py_analyzer/process" \
  -H "Content-Type: application/json" \
  -d '{"path": "/home/user/projects/app.py"}'
```

### Invoke a Hook

```bash
curl -X POST "http://127.0.0.1:5000/api/plugins/hooks/file_processor" \
  -H "Content-Type: application/json" \
  -d '{"file_path": "/home/user/projects/app.py", "file_content": "print(\"Hello World\")"}'
```