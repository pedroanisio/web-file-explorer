# Web File Explorer

A simple web-based file explorer built with Flask that allows you to browse directories and download files.

## Features

- Browse directories in a clean web interface
- Download files with a simple click
- Sort files and directories by name, size, or modification date
- Search within the current directory
- Responsive design that works on desktop and mobile devices
- Plugin system for extending functionality

## Installation

### From PyPI

```bash
pip install flask-file-explorer
```

### From Source

```bash
# Clone the repository
git clone https://github.com/yourusername/flask-file-explorer.git
cd flask-file-explorer

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install the package
pip install -e .

# Install development dependencies (optional)
pip install -e ".[dev]"
```

## Usage

### Running the Development Server

```bash
# Run the application with the default settings
flask-file-explorer

# Alternatively, you can set environment variables to customize behavior
export FLASK_FILE_EXPLORER_BASE_DIR=/path/to/directory
export FLASK_DEBUG=1
flask-file-explorer
```

Then navigate to http://127.0.0.1:5000/ in your web browser.

### As a Python Module

```python
from flask_file_explorer import create_app

# Create the application
app = create_app({
    'BASE_DIR': '/path/to/directory',
})

# Run the application
if __name__ == '__main__':
    app.run(debug=True)
```

## Plugin System

Flask File Explorer includes a flexible plugin system that allows you to extend its functionality.

### Types of Plugins

- **UI Plugins**: Add buttons to the toolbar and provide user-facing functionality
- **Backend Plugins**: Provide server-side functionality through hooks

### Creating a Plugin

Create a directory with the following structure:

```
my_plugin/
├── __init__.py                 # Package initialization
├── manifest.json               # Plugin metadata
└── my_plugin_implementation.py # Plugin implementation
```

#### Example UI Plugin

```json
{
    "id": "my_plugin",
    "name": "My Plugin",
    "version": "1.0.0",
    "description": "Example plugin",
    "entry_point": "my_plugin_implementation",
    "icon": "🔧"
}
```

```python
def execute(path, **kwargs):
    """
    Execute the plugin
    
    Args:
        path (str): The current directory path
        
    Returns:
        dict: Result of the plugin execution
    """
    return {
        "success": True,
        "output": f"Executed plugin on {path}",
        "title": "Plugin Result"
    }
```

See the [Plugin Development Guide](docs/plugin_development_guide.md) for more information.

## Development

### Running Tests

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest
```

### Code Quality

```bash
# Run linting
flake8 src tests

# Run type checking
mypy src

# Format code
black src tests
```

## License

MIT License - See the LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a pull request.