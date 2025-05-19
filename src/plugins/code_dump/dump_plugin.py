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
        settings = get_settings()
        exclude_patterns = settings.get("exclude_patterns", DEFAULT_PATTERNS)
        
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
        <div class="code-dump-container card">
            <div class="code-dump-header card-header">
                <h3 class="card-title">Code Dump Results</h3>
                <button id="copy-button" class="btn-blue">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-1" viewBox="0 0 20 20" fill="currentColor">
                        <path d="M8 3a1 1 0 011-1h2a1 1 0 110 2H9a1 1 0 01-1-1z" />
                        <path d="M6 3a2 2 0 00-2 2v11a2 2 0 002 2h8a2 2 0 002-2V5a2 2 0 00-2-2 3 3 0 01-3 3H9a3 3 0 01-3-3z" />
                    </svg>
                    Copy All Code
                </button>
            </div>
            <div class="card-body p-0">
                <pre id="code-dump-content" class="source-code">{output_html}</pre>
            </div>
        </div>
        
        <script>
        document.addEventListener('DOMContentLoaded', function() {{
            const copyButton = document.getElementById('copy-button');
            const codeContent = document.getElementById('code-dump-content');
            
            copyButton.addEventListener('click', function() {{
                const originalText = copyButton.innerHTML;
                
                // Create a temporary textarea element to copy the text
                const textArea = document.createElement('textarea');
                textArea.value = codeContent.textContent;
                document.body.appendChild(textArea);
                textArea.select();
                
                try {{
                    const successful = document.execCommand('copy');
                    if (successful) {{
                        copyButton.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-1" viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" /></svg> Copied!';
                        
                        setTimeout(function() {{
                            copyButton.innerHTML = originalText;
                        }}, 2000);
                    }}
                }} catch (err) {{
                    console.error('Failed to copy: ', err);
                }}
                
                document.body.removeChild(textArea);
            }});
        }});
        </script>
        """
        
        return {
            "success": True,
            "output": output_with_copy,
            "title": "Code Dump Results",
            "content_type": "html",
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
