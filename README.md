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
pip install web-file-explorer
```

### From Source

```bash
# Clone the repository
git clone https://github.com/pedroanisio/web-file-explorer.git
cd web-file-explorer

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

## Docker Deployment for Web File Explorer

## Prerequisites

- Docker installed on your system
- Docker Compose (optional, but recommended)

## Quick Start with Docker Compose

1. Clone the repository:
```bash
git clone https://github.com/yourusername/web-file-explorer.git
cd web-file-explorer
   ```

2. Create a `.env` file (optional) to configure the deployment:
```
FLASK_DEBUG=0
HOST_DIR=/path/to/directory/to/explore
```

3. Start the application:
```bash
docker compose up -d
```

4. Access the application in your browser at http://localhost:5000

## Manual Docker Deployment

If you prefer not to use Docker Compose, you can build and run the container directly:

1. Build the Docker image:
```bash
docker build -t file-explorer .
```

2. Run the container:
```bash
docker run -p 5000:5000 -v /path/to/directory:/data file-explorer
```

## Configuration Options

### Environment Variables

- `FLASK_DEBUG`: Set to 1 to enable debug mode (default: 0)
- `FLASK_FILE_EXPLORER_BASE_DIR`: Base directory to explore (default: /data inside the container)
- `HOST_DIR`: Local directory to mount in the container (when using docker-compose)

### Persistent Volumes

The container mounts the specified directory to `/data` inside the container. This is where the file explorer will browse files from.

## Security Considerations

- The application runs as a non-root user inside the container for improved security
- Consider using a reverse proxy like Nginx or Traefik with HTTPS if deploying to production
- Review access permissions for the mounted directories

## Troubleshooting

1. **Permission issues with mounted volumes**: 
   Ensure the user inside the container (UID 1000) has read access to the mounted directory.

2. **Port conflicts**:
   If port 5000 is already in use, modify the port mapping in docker-compose.yml or the docker run command.

3. **Plugins not working**:
   Some plugins may require additional dependencies. You can customize the Dockerfile to install them.

## License

MIT License - See the LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a pull request.
