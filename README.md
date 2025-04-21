# Flask File Explorer

A simple web-based file explorer built with Flask that allows you to browse directories and download files.

## Features

- Browse directories in a clean web interface
- Download files with a simple click
- Sort files and directories by name, size, or modification date
- Search within the current directory
- Responsive design that works on desktop and mobile devices

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/flask-file-explorer.git
cd flask-file-explorer

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install the package
pip install -e .
```

## Usage

```bash
# Run the development server
python -m flask_file_explorer
```

Then navigate to http://127.0.0.1:5000/ in your web browser.

## Development

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest
```

## License

MIT License
