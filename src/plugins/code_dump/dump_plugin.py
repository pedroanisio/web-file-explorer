"""
Code Dump plugin for the file explorer.
Outputs all code files in a directory while excluding common non-code files.
"""
import subprocess
import os
import html
import logging
import json
import tempfile
import time
import zipfile
from pathlib import Path

# Default exclusion patterns
DEFAULT_PATTERNS = [
    ".venv","venv", "*.md", "node_modules", "*.png", "*-lock.json",
    "*.jpg", "*.lock", ".git", "*.db", "*.pyc", "*git*","*.ico","*.svg",
    "wait-for-it.sh", ".pytest_cache", "htmlcov", ".coverage", "*.log",
    "target", "Cargo.lock", "*.rlib", "*.rmeta", "*.d", "*.fingerprint",
    "bin"
]

def get_default_patterns():
    """Returns the default list of exclusion patterns."""
    return DEFAULT_PATTERNS

def get_manifest():
    """Get the plugin manifest."""
    manifest_path = Path(__file__).parent / "manifest.json"
    if manifest_path.exists():
        with open(manifest_path) as f:
            return json.load(f)
    return {}

def get_settings():
    """Return plugin settings."""
    manifest = get_manifest()
    return manifest.get("settings", {"exclude_patterns": DEFAULT_PATTERNS})

def save_settings(settings):
    """Save plugin settings to manifest."""
    manifest = get_manifest()
    manifest["settings"] = settings
    manifest_path = Path(__file__).parent / "manifest.json"
    with open(manifest_path, "w") as f:
        json.dump(manifest, f, indent=4)
    return True

def get_config_template():
    """Return the configuration template data."""
    settings = get_settings()
    return {
        "template": "config.html",
        "data": {
            "default_patterns": DEFAULT_PATTERNS,
            "selected_patterns": settings.get("exclude_patterns", DEFAULT_PATTERNS)
        }
    }

def save_plugin_config(data):
    """Save the plugin configuration."""
    settings = {
        "exclude_patterns": data.getlist("exclude_patterns") or DEFAULT_PATTERNS
    }
    return save_settings(settings)

def _cat_or_skip():
    """Returns a shell snippet that skips binary files before catting."""
    return (
        'enc=$(file -b --mime-encoding "{}"); '
        'if [ "$enc" = "binary" ]; then '
        'echo "File: {} [binary - skipped]"; '
        'else '
        'echo "File: {}"; cat "{}"; '
        'fi'
    )

def build_find_command(path, exclude_patterns):
    """Builds the find command with specified exclusion patterns."""
    cat_snippet = _cat_or_skip()

    if not exclude_patterns:
        # If no patterns selected, just find all files
        return f'cd "{path}" && find . -type f -print | xargs -I {{}} sh -c \'{cat_snippet}\''

    # Build the exclusion part of the find command
    exclusion_parts = []
    for pattern in exclude_patterns:
        exclusion_parts.append(f'-name "{pattern}"')

    exclusion_string = " -o ".join(exclusion_parts)

    return f'cd "{path}" && find . \\( {exclusion_string} \\) -prune -o -type f -print | xargs -I {{}} sh -c \'{cat_snippet}\''

def execute(path, **kwargs):
    """
    Execute the code dump command on the given path and generate a downloadable file.
    
    Args:
        path (str): Directory path to scan for code files.
        
    Returns:
        dict: A dictionary containing the result of the command and download information.
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
        settings = get_settings()
        exclude_patterns = settings.get("exclude_patterns", DEFAULT_PATTERNS)
        
        # Build the command with provided patterns
        command = build_find_command(path, exclude_patterns)
        
        logger.info(f"Running code dump command in directory: {path}")
        logger.info(f"Excluding patterns: {exclude_patterns}")
        logger.debug(f"Executing command: {command}")
        
        # Run the command as bytes to avoid UTF-8 decode errors from
        # non-UTF-8 text files that slip past the binary check.
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            check=False
        )

        if result.returncode != 0:
            stderr_text = result.stderr.decode("utf-8", errors="replace")
            logger.error(f"Command failed with exit code {result.returncode}")
            logger.error(f"Stderr: {stderr_text}")
            return {
                "success": False,
                "error": f"Command failed: {stderr_text or 'Unknown error'}",
                "output": stderr_text
            }

        stdout_text = result.stdout.decode("utf-8", errors="replace")
        
        # Generate a filename based on the folder name and timestamp in nanoseconds
        folder_name = os.path.basename(os.path.normpath(path))
        timestamp_ns = time.time_ns()
        filename = f"{folder_name}-{timestamp_ns}.zip"

        # Create a zip file containing the dump
        temp_dir = tempfile.gettempdir()
        file_path = os.path.join(temp_dir, filename)
        dump_txt_name = f"{folder_name}.dump.txt"

        with zipfile.ZipFile(file_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            zf.writestr(dump_txt_name, stdout_text)

        logger.info(f"Created dump zip at: {file_path}")

        # Return a response that will initiate a download
        return {
            "success": True,
            "download": {
                "file_path": file_path,
                "filename": filename,
                "content_type": "application/zip"
            },
            "message": f"Code dump created successfully. Downloading {filename}..."
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
