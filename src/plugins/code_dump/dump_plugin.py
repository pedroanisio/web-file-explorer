"""
Code Dump plugin for the file explorer.
Outputs all code files in a directory while excluding common non-code files.
"""
import subprocess
import os
import html
import logging
import json
from pathlib import Path

# Default exclusion patterns
DEFAULT_PATTERNS = [
    ".venv","venv", "*.md", "node_modules", "*.png", "*-lock.json",
    "*.jpg", "*.lock", ".git", "*.db", "*.pyc", "*git*","*.ico","*.svg",
    "wait-for-it.sh", ".pytest_cache", "htmlcov", ".coverage", "*.log"
]

def get_default_patterns():
    """Returns the default list of exclusion patterns."""
    return DEFAULT_PATTERNS

def get_config():
    """Get the current configuration."""
    config_file = Path(__file__).parent / "config.json"
    if config_file.exists():
        with open(config_file) as f:
            return json.load(f)
    return {"exclude_patterns": DEFAULT_PATTERNS}

def save_config(config):
    """Save the configuration."""
    config_file = Path(__file__).parent / "config.json"
    with open(config_file, "w") as f:
        json.dump(config, f)

def get_config_template():
    """Return the configuration template data."""
    config = get_config()
    return {
        "template": "config.html",
        "data": {
            "default_patterns": DEFAULT_PATTERNS,
            "selected_patterns": config.get("exclude_patterns", DEFAULT_PATTERNS)
        }
    }

def save_plugin_config(data):
    """Save the plugin configuration."""
    config = {
        "exclude_patterns": data.getlist("exclude_patterns") or DEFAULT_PATTERNS
    }
    save_config(config)
    return True

def build_find_command(path, exclude_patterns):
    """Builds the find command with specified exclusion patterns."""
    if not exclude_patterns:
        # If no patterns selected, just find all files
        return f'cd "{path}" && find . -type f -print | xargs -I {{}} sh -c \'echo "File: {{}}"; cat {{}}\''

    # Build the exclusion part of the find command
    exclusion_parts = []
    for pattern in exclude_patterns:
        exclusion_parts.append(f'-name "{pattern}"')

    exclusion_string = " -o ".join(exclusion_parts)

    return f'cd "{path}" && find . \\( {exclusion_string} \\) -prune -o -type f -print | xargs -I {{}} sh -c \'echo "File: {{}}"; cat {{}}\''

def execute(path, **kwargs):
    """
    Execute the code dump command on the given path.
    
    Args:
        path (str): Directory path to scan for code files.
        
    Returns:
        dict: A dictionary containing the result of the command.
    """
    try:
        logger = logging.getLogger(__name__)

        if not os.path.isdir(path):
            logger.warning(f"Path provided is not a directory: {path}")
            return {
                "success": False,
                "error": f"{path} is not a directory"
            }
        
        # Get the current configuration
        config = get_config()
        exclude_patterns = config.get("exclude_patterns", DEFAULT_PATTERNS)
        
        # Build the command with provided patterns
        command = build_find_command(path, exclude_patterns)
        
        logger.info(f"Running code dump command in directory: {path}")
        logger.info(f"Excluding patterns: {exclude_patterns}")
        logger.debug(f"Executing command: {command}")
        
        # Run the command
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            check=False
        )

        if result.returncode != 0:
            logger.error(f"Command failed with exit code {result.returncode}")
            logger.error(f"Stderr: {result.stderr}")
            return {
                "success": False,
                "error": f"Command failed: {result.stderr or 'Unknown error'}",
                "output": result.stderr
            }
        
        # Format the output for HTML display
        output_html = html.escape(result.stdout)
        
        # Add a copy button with enhanced styling and functionality
        output_with_copy = f"""
        <div class="code-dump-container">
            <header class="code-dump-header">
                <h3>Code Dump Results</h3>
                <div class="copy-button-container">
                    <button id="copy-button" class="copy-button">📋 Copy All Code</button>
                    <span id="copy-status" class="copy-status"></span>
                </div>
            </header>
            <pre id="code-dump-content" style="white-space: pre-wrap; max-height: 70vh; overflow-y: auto;">{output_html}</pre>
        </div>
        
        <style>
        .code-dump-container {{
            position: relative;
            border: 1px solid #2c3e50;
            border-radius: 8px;
            padding: 0;
            margin-top: 20px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            max-width: 100%;
            overflow: hidden;
            font-family: sans-serif;
        }}
        
        .code-dump-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            background-color: #2c3e50;
            color: white;
            padding: 10px 15px;
            position: sticky;
            top: 0;
            z-index: 100;
        }}
        
        .code-dump-header h3 {{
            margin: 0;
            font-size: 16px;
        }}
        
        .copy-button-container {{
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        
        .copy-button {{
            background-color: #3498db;
            color: white;
            border: none;
            padding: 8px 16px;
            text-align: center;
            text-decoration: none;
            display: inline-flex;
            align-items: center;
            font-size: 14px;
            border-radius: 4px;
            cursor: pointer;
            transition: all 0.2s ease;
            font-weight: 600;
        }}
        
        .copy-button:hover {{
            background-color: #2980b9;
            transform: translateY(-2px);
            box-shadow: 0 2px 5px rgba(0,0,0,0.2);
        }}
        
        .copy-status {{
            font-size: 12px;
            transition: opacity 0.5s ease;
        }}
        
        .copy-status.success {{
            color: #2ecc71;
        }}
        
        .copy-status.error {{
            color: #e74c3c;
        }}
        
        #code-dump-content {{
            padding: 15px;
            margin: 0;
            background-color: #f8f9fa;
            color: #333;
            font-family: monospace;
            line-height: 1.5;
            border-radius: 0 0 8px 8px;
        }}
        </style>
        """
        
        return {
            "success": True,
            "output": output_with_copy,
            "title": "Code Dump Results",
            "is_html": True
        }
    except subprocess.CalledProcessError as e:
        logger.error(f"CalledProcessError: {e}", exc_info=True)
        return {
            "success": False,
            "error": f"Command failed with exit code {e.returncode}",
            "output": e.stderr
        }
    except Exception as e:
        logger.error(f"Unexpected error in code_dump execute: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e)
        }

# Example of how the plugin system might call this:
# To show config first:
# result = execute("/path/to/user/code") 
#
# To run with specific patterns (e.g., after config submission):
# result = execute("/path/to/user/code", show_config=False, exclude_patterns=["*.log", "temp/"])
#
# To run with default patterns, skipping config:
# result = execute("/path/to/user/code", show_config=False)
