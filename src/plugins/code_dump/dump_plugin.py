"""
Code Dump plugin for the file explorer.
Outputs all code files in a directory while excluding common non-code files.
"""
import subprocess
import os
import html
import logging

# Default exclusion patterns
DEFAULT_PATTERNS = [
    ".venv","venv", "*.md", "node_modules", "*.png", "*-lock.json",
    "*.jpg", "*.lock", ".git", "*.db", "*.pyc", "*git*","*.ico","*.svg",
    "wait-for-it.sh", ".pytest_cache", "htmlcov", ".coverage", "*.log"
]

def get_default_patterns():
    """Returns the default list of exclusion patterns."""
    return DEFAULT_PATTERNS

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

def generate_config_panel(path):
    """Generates the HTML configuration panel for selecting exclusion patterns."""
    default_patterns = get_default_patterns()
    
    # Generate pattern checkboxes
    pattern_checkboxes = []
    for pattern in default_patterns:
        pattern_checkboxes.append(f"""
        <div class="pattern-item">
            <input type="checkbox" id="{pattern}" name="exclude_patterns" value="{pattern}" checked>
            <label for="{pattern}">{pattern}</label>
        </div>
        """)
    
    # Ensure the path is properly escaped for use in JavaScript string
    escaped_path = path.replace("'", "\\'")

    # Create the HTML content with embedded JavaScript
    html_content = f"""
    <div id="code-dump-config" data-path="{escaped_path}">
        <div class="config-panel">
            <h3>Configure Code Dump Patterns</h3>
            <div class="pattern-section">
                <h4>Files/Folders to Exclude:</h4>
                <div class="pattern-container">
                    {"".join(pattern_checkboxes)}
                </div>
                <div class="custom-pattern">
                    <input type="text" id="custom-pattern" placeholder="Add custom pattern (e.g. *.log)">
                    <button id="add-pattern" class="add-button">Add</button>
                </div>
            </div>
            <div class="button-row">
                <button id="select-all" class="config-button">Select All</button>
                <button id="deselect-all" class="config-button">Deselect All</button>
                <button id="run-dump" class="run-button">Run Code Dump</button>
            </div>
        </div>
    </div>

    <style>
    #code-dump-config .config-panel {{
        background-color: #fff;
        border-radius: 8px;
        padding: 20px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        margin-bottom: 20px;
        font-family: system-ui, -apple-system, sans-serif;
    }}
    #code-dump-config .config-panel h3, 
    #code-dump-config .config-panel h4 {{
        color: #2c3e50;
        margin: 0 0 15px 0;
    }}
    #code-dump-config .pattern-section {{
        margin: 15px 0;
    }}
    #code-dump-config .pattern-container {{
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
        gap: 10px;
        max-height: 300px;
        overflow-y: auto;
        padding: 10px;
        border: 1px solid #eee;
        border-radius: 5px;
        margin-bottom: 15px;
        background: #f8f9fa;
    }}
    #code-dump-config .pattern-item {{
        display: flex;
        align-items: center;
        padding: 8px;
        background: white;
        border-radius: 4px;
        border: 1px solid #e9ecef;
    }}
    #code-dump-config .pattern-item:hover {{
        background-color: #f8f9fa;
        border-color: #dee2e6;
    }}
    #code-dump-config .pattern-item input[type="checkbox"] {{
        margin-right: 8px;
        width: 16px;
        height: 16px;
    }}
    #code-dump-config .pattern-item label {{
        margin-left: 4px;
        cursor: pointer;
        color: #333;
        font-size: 14px;
    }}
    #code-dump-config .custom-pattern {{
        display: flex;
        gap: 10px;
        margin-top: 10px;
    }}
    #code-dump-config .custom-pattern input {{
        flex-grow: 1;
        padding: 8px 12px;
        border: 1px solid #ddd;
        border-radius: 4px;
        font-size: 14px;
    }}
    #code-dump-config .custom-pattern input:focus {{
        outline: none;
        border-color: #3498db;
        box-shadow: 0 0 0 2px rgba(52,152,219,0.2);
    }}
    #code-dump-config .add-button {{
        background-color: #27ae60;
        color: white;
        border: none;
        padding: 8px 15px;
        border-radius: 4px;
        cursor: pointer;
        font-weight: 600;
        font-size: 14px;
        display: flex;
        align-items: center;
        gap: 5px;
    }}
    #code-dump-config .add-button:hover {{
        background-color: #219a52;
    }}
    #code-dump-config .button-row {{
        display: flex;
        justify-content: flex-end;
        margin-top: 20px;
        gap: 10px;
    }}
    #code-dump-config .config-button, 
    #code-dump-config .run-button {{
        color: white;
        border: none;
        padding: 10px 18px;
        border-radius: 4px;
        cursor: pointer;
        font-weight: 600;
        font-size: 14px;
        transition: all 0.2s ease;
    }}
    #code-dump-config .config-button {{
        background-color: #f39c12;
    }}
    #code-dump-config .config-button:hover {{
        background-color: #e67e22;
        transform: translateY(-1px);
    }}
    #code-dump-config .run-button {{
        background-color: #3498db;
        min-width: 120px;
    }}
    #code-dump-config .run-button:hover {{
        background-color: #2980b9;
        transform: translateY(-1px);
    }}
    </style>

    <script>
    // Initialize Code Dump Configuration
    (function() {{
        function initCodeDumpConfig() {{
            const config = document.getElementById('code-dump-config');
            if (!config) return;  // Exit if config panel not found

            const path = config.dataset.path;
            
            // Add Pattern Button
            config.querySelector('#add-pattern')?.addEventListener('click', function() {{
                const customPatternInput = config.querySelector('#custom-pattern');
                if (!customPatternInput) return;
                
                const customPattern = customPatternInput.value.trim();
                if (customPattern) {{
                    addPatternCheckbox(customPattern);
                    customPatternInput.value = '';
                }}
            }});
            
            // Enter Key on Input
            config.querySelector('#custom-pattern')?.addEventListener('keypress', function(e) {{
                if (e.key === 'Enter') {{
                    config.querySelector('#add-pattern')?.click();
                }}
            }});
            
            // Select All Button
            config.querySelector('#select-all')?.addEventListener('click', function() {{
                config.querySelectorAll('input[name="exclude_patterns"]')
                    .forEach(cb => cb.checked = true);
            }});
            
            // Deselect All Button
            config.querySelector('#deselect-all')?.addEventListener('click', function() {{
                config.querySelectorAll('input[name="exclude_patterns"]')
                    .forEach(cb => cb.checked = false);
            }});
            
            // Run Dump Button
            config.querySelector('#run-dump')?.addEventListener('click', function() {{
                const selectedPatterns = [];
                config.querySelectorAll('input[name="exclude_patterns"]:checked')
                    .forEach(cb => selectedPatterns.push(cb.value));

                // Show loading state in the modal
                const modalContent = document.querySelector('.modal-content');
                if (modalContent) {{
                    modalContent.innerHTML = '<div style="text-align: center; padding: 20px;">Executing code dump, please wait...</div>';
                }}

                // Execute the plugin
                fetch(`/plugins/execute/code_dump?path=${{encodeURIComponent(path)}}`, {{
                    method: 'POST',
                    headers: {{
                        'Content-Type': 'application/json',
                    }},
                    body: JSON.stringify({{
                        exclude_patterns: selectedPatterns,
                        show_config: false
                    }})
                }})
                .then(response => response.json())
                .then(data => {{
                    if (data.success) {{
                        const isHtml = data.content_type === 'html';
                        modalContent.innerHTML = data.output;
                        if (isHtml) {{
                            modalContent.classList.add('html-content');
                        }}
                    }} else {{
                        modalContent.innerHTML = `<div class="error-message">${{data.error}}\n\n${{data.output || ''}}</div>`;
                    }}
                }})
                .catch(error => {{
                    modalContent.innerHTML = `<div class="error-message">Failed to execute plugin: ${{error.message}}</div>`;
                }});
            }});
            
            function addPatternCheckbox(pattern) {{
                const container = config.querySelector('.pattern-container');
                if (!container) return;
                
                const div = document.createElement('div');
                div.className = 'pattern-item';
                div.innerHTML = `
                    <input type="checkbox" id="${{pattern}}" name="exclude_patterns" value="${{pattern}}" checked>
                    <label for="${{pattern}}">${{pattern}}</label>
                `;
                container.appendChild(div);
            }}
        }}

        // Initialize immediately if DOM is ready, otherwise wait for DOMContentLoaded
        if (document.readyState === 'loading') {{
            document.addEventListener('DOMContentLoaded', initCodeDumpConfig);
        }} else {{
            initCodeDumpConfig();
        }}
    }})();
    </script>
    """

    # Return in the format expected by the plugin system
    return {
        "success": True,
        "output": html_content,
        "title": "Configure Code Dump",
        "content_type": "html"
    }

def execute(path, **kwargs):
    """
    Execute the code dump command on the given path.
    
    Args:
        path (str): Directory path to scan for code files.
        show_config (bool): Whether to show the configuration panel first. Defaults to True.
        exclude_patterns (list): List of patterns to exclude.
        
    Returns:
        dict: A dictionary containing the result of the command.
    """
    try:
        logger = logging.getLogger(__name__)  # Initialize logger at the beginning of the try block

        if not os.path.isdir(path):
            logger.warning(f"Path provided is not a directory: {path}")
            return {
                "success": False,
                "error": f"{path} is not a directory"
            }
        
        # Check if we need to display the configuration panel first.
        # Configuration is shown if 'show_config' is True (or not provided) 
        # AND 'exclude_patterns' are not already provided (meaning it's not a callback from the config panel).
        if kwargs.get('show_config', True) and 'exclude_patterns' not in kwargs:
            return generate_config_panel(path)
        
        # Extract patterns from kwargs or use defaults if not running from config.
        # If 'exclude_patterns' is in kwargs, it means the config panel submitted them.
        # If 'show_config' was false, or if patterns were directly passed, use those.
        exclude_patterns = kwargs.get('exclude_patterns', get_default_patterns())
        
        # Build the command with provided patterns
        command = build_find_command(path, exclude_patterns)
        
        logger.info(f"Running code dump command in directory: {path}")
        logger.info(f"Excluding patterns: {exclude_patterns}")
        logger.debug(f"Executing command: {command}") # Log the command for debugging
        
        # Run the command
        result = subprocess.run(
            command,
            shell=True, # Be cautious with shell=True if 'path' or 'patterns' can be manipulated by user input outside of controlled UI.
            capture_output=True,
            text=True,
            check=False # Changed to False to handle errors manually
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
