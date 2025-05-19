"""
CLOC Analyzer plugin implementation.
Runs cloc on directories and returns reports as JSON.
"""
import json
import logging
import os
import subprocess
import shutil
from ..plugin_base import BackendPlugin

# Setup logging
logger = logging.getLogger("cloc_analyzer")

def create_plugin(plugin_id, manifest, registry):
    """Create the plugin instance"""
    return ClocAnalyzerPlugin(plugin_id, manifest, registry)

class ClocAnalyzerPlugin(BackendPlugin):
    """
    CLOC Analyzer plugin for counting lines of code in directories
    """
    
    def __init__(self, plugin_id, manifest, registry):
        super().__init__(plugin_id, manifest, registry)
        
    def activate(self):
        """Called when the plugin is activated"""
        logger.info("CLOC Analyzer plugin activated")
        self._check_cloc_installed()
        
    def _check_cloc_installed(self):
        """Check if cloc is installed on the system"""
        if not shutil.which("cloc"):
            logger.warning("cloc is not installed. This plugin requires cloc to function.")
            return False
        return True
        
    def on_query_handler(self, query, context=None):
        """
        Handle API queries to analyze directories
        
        Args:
            query (str): The query string (e.g., 'analyze', 'list_languages')
            context (dict): Additional context data
            
        Returns:
            dict: The analysis results
        """
        if context is None:
            context = {}
            
        if query == "analyze":
            return self._analyze_directory(context)
        elif query == "list_languages":
            return self._list_languages()
        else:
            return {
                "success": False,
                "error": f"Unknown query: {query}",
                "available_queries": ["analyze", "list_languages"]
            }
    
    def _analyze_directory(self, context):
        """
        Analyze a directory using cloc
        
        Args:
            context (dict): Contains 'path' - the directory to analyze
                           Optional: 'exclude' - patterns to exclude
                           Optional: 'include_lang' - languages to include
            
        Returns:
            dict: The analysis results
        """
        if not self._check_cloc_installed():
            return {
                "success": False,
                "error": "cloc is not installed. Please install it to use this plugin."
            }
            
        # Get the path from context
        path = context.get('path')
        base_dir = context.get('base_dir', '')
        
        if not path:
            return {
                "success": False,
                "error": "No path provided in context"
            }
            
        # Build the absolute path
        if not os.path.isabs(path):
            path = os.path.abspath(os.path.join(base_dir, path))
            
        # Check if path exists
        if not os.path.exists(path):
            return {
                "success": False,
                "error": f"Path {path} does not exist"
            }
            
        # Check if path is a directory
        if not os.path.isdir(path):
            return {
                "success": False,
                "error": f"Path {path} is not a directory"
            }
            
        # Build cloc command
        cmd = ["cloc", path, "--json"]
        
        # Add exclude patterns if provided
        exclude = context.get('exclude')
        if exclude:
            if isinstance(exclude, list):
                for pattern in exclude:
                    cmd.extend(["--exclude-dir", pattern])
            else:
                cmd.extend(["--exclude-dir", exclude])
                
        # Add included languages if provided
        include_lang = context.get('include_lang')
        if include_lang:
            if isinstance(include_lang, list):
                cmd.extend(["--include-lang", ",".join(include_lang)])
            else:
                cmd.extend(["--include-lang", include_lang])
                
        try:
            # Run cloc
            logger.info(f"Running command: {' '.join(cmd)}")
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )
            
            # Parse the JSON output
            try:
                cloc_data = json.loads(result.stdout)
                return {
                    "success": True,
                    "data": cloc_data,
                    "path": path
                }
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse cloc output: {e}")
                return {
                    "success": False,
                    "error": "Failed to parse cloc output",
                    "output": result.stdout
                }
                
        except subprocess.CalledProcessError as e:
            logger.error(f"cloc execution failed: {e}")
            return {
                "success": False,
                "error": f"cloc execution failed: {e}",
                "stderr": e.stderr,
                "stdout": e.stdout
            }
        except Exception as e:
            logger.error(f"Error running cloc: {e}")
            return {
                "success": False,
                "error": f"Error running cloc: {e}"
            }
    
    def _list_languages(self):
        """
        List languages supported by cloc
        
        Returns:
            dict: List of supported languages
        """
        if not self._check_cloc_installed():
            return {
                "success": False,
                "error": "cloc is not installed. Please install it to use this plugin."
            }
            
        try:
            # Run cloc to get supported languages
            result = subprocess.run(
                ["cloc", "--show-lang"],
                capture_output=True,
                text=True,
                check=True
            )
            
            # Parse the output to extract languages
            lines = result.stdout.strip().split("\n")
            languages = []
            
            # Skip the header lines
            started = False
            for line in lines:
                if not started and "-------" in line:
                    started = True
                    continue
                    
                if started and line.strip():
                    parts = line.split()
                    if len(parts) >= 2:
                        languages.append({
                            "name": parts[0],
                            "extensions": " ".join(parts[1:])
                        })
            
            return {
                "success": True,
                "languages": languages
            }
                
        except subprocess.CalledProcessError as e:
            logger.error(f"cloc execution failed: {e}")
            return {
                "success": False,
                "error": f"Failed to list languages: {e}",
                "stderr": e.stderr
            }
        except Exception as e:
            logger.error(f"Error listing languages: {e}")
            return {
                "success": False,
                "error": f"Error listing languages: {e}"
            } 