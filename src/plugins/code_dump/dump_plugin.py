"""
Code Dump plugin for the file explorer.
Outputs all code files in a directory while excluding common non-code files.
"""
import subprocess
import os
import html
import logging

def execute(path, **kwargs):
    """
    Execute the code dump command on the given path.
    
    Args:
        path (str): Directory path to scan for code files, provided by the plugin system
        
    Returns:
        dict: A dictionary containing the result of the command
    """
    try:
        if not os.path.isdir(path):
            return {
                "success": False,
                "error": f"{path} is not a directory"
            }
        
        # Construct the command - path is already absolute as provided by the plugin system
        command = f"""
        cd "{path}" && find . \( -name "venv" -o -name "*.md" -o -name "node_modules" -o -name "*.png" -o -name "*-lock.json" -o -name "*.jpg" -o -name "*.lock" -o -name ".git" -o -name ".db" -o -name "*.pyc" -o -name "*git*" -o -name "wait-for-it.sh" -o -name ".pytest_cache" -o -name htmlcov -o -name .coverage \) -prune -o -type f -print | xargs -I {{}} sh -c 'echo "File: {{}}"; cat {{}}'
        """
        
        logger = logging.getLogger('code_dump')
        logger.info(f"Running code dump command in directory: {path}")
        
        # Run the command
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True
        )
        
        # Format the output for HTML display
        output_html = html.escape(result.stdout)
        
        # Add a copy button with enhanced styling and functionality
        # Note: JavaScript functionality is now defined in plugins.js
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
        return {
            "success": False,
            "error": f"Command failed with exit code {e.returncode}",
            "output": e.stderr
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }
