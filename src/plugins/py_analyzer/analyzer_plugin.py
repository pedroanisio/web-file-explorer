"""
Python code analyzer plugin.
Analyzes Python files and provides information about their structure.
"""
import ast
import logging

# Setup logging
logger = logging.getLogger("py_analyzer")

def create_plugin(plugin_id, manifest, registry):
    """Create the plugin instance"""
    return PythonAnalyzerPlugin(plugin_id, manifest, registry)

class PythonAnalyzerPlugin:
    """
    Python code analyzer plugin
    """
    
    def __init__(self, plugin_id, manifest, registry):
        self.plugin_id = plugin_id
        self.manifest = manifest
        self.registry = registry
        
    def activate(self):
        """Called when the plugin is activated"""
        logger.info("Python Analyzer plugin activated")
        
    def get_settings(self):
        """Return plugin settings"""
        return self.manifest.get('settings', {})
        
    def on_file_processor(self, file_path, file_content, metadata=None):
        """Process Python files and provide analysis"""
        if not file_path.endswith('.py'):
            return {
                "success": True,
                "skipped": True,
                "message": "Not a Python file"
            }
            
        try:
            # Parse the Python code
            tree = ast.parse(file_content)
            
            # Extract information
            functions = []
            classes = []
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    functions.append({
                        "name": node.name,
                        "line": node.lineno,
                        "args": [arg.arg for arg in node.args.args]
                    })
                elif isinstance(node, ast.ClassDef):
                    classes.append({
                        "name": node.name,
                        "line": node.lineno
                    })
            
            return {
                "success": True,
                "analysis": {
                    "functions": functions,
                    "classes": classes,
                    "summary": f"Found {len(functions)} functions and {len(classes)} classes"
                }
            }
        except Exception as e:
            logger.error(f"Error analyzing file: {e}")
            return {
                "success": False,
                "error": str(e)
            }
