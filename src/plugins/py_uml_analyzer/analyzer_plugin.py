"""
Python UML Analyzer plugin for FIXIT.
Analyzes Python code and extracts class/method information for UML generation.
"""
import ast
import os
import logging
import json
from typing import Dict, Any, List, Optional
from ..plugin_base import BackendPlugin

# Setup logging
logger = logging.getLogger("py_uml_analyzer")

def create_plugin(plugin_id, manifest, registry):
    """Create the Python UML Analyzer plugin instance"""
    return PythonUMLAnalyzerPlugin(plugin_id, manifest, registry)

class ClassInfo:
    """Class to store information about a Python class"""
    def __init__(self, name, bases=None, docstring=None, file_path=None, line_number=None):
        self.name = name
        self.bases = bases or []
        self.docstring = docstring
        self.methods = []
        self.attributes = []
        self.file_path = file_path
        self.line_number = line_number
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            "name": self.name,
            "bases": self.bases,
            "docstring": self.docstring,
            "methods": self.methods,
            "attributes": self.attributes,
            "file_path": self.file_path,
            "line_number": self.line_number
        }

class PythonUMLAnalyzerPlugin(BackendPlugin):
    """
    Python UML Analyzer plugin for extracting class information for UML diagrams
    """
    
    def __init__(self, plugin_id, manifest, registry):
        super().__init__(plugin_id, manifest, registry)
        # Store analyzed classes by file path
        self.class_cache = {}
        
    def activate(self):
        """Called when the plugin is activated"""
        logger.info("Python UML Analyzer plugin activated")
        
    def deactivate(self):
        """Called before the plugin is deactivated"""
        logger.info("Python UML Analyzer plugin deactivated")
        
    def get_settings(self):
        """Return plugin settings"""
        return self.manifest.get('settings', {})
        
    def on_query_handler(self, query, context=None):
        """
        Handle queries for UML data
        
        Args:
            query (str): The query string
            context (dict, optional): Additional context
            
        Returns:
            dict: Response with UML data
        """
        if not context or 'action' not in context:
            return {
                "success": False,
                "error": "No action specified in context"
            }
            
        action = context.get('action')
        
        if action == 'get_all_classes':
            # Return all analyzed classes
            return {
                "success": True,
                "plugin_id": self.plugin_id,
                "classes": [class_info.to_dict() for file_classes in self.class_cache.values() 
                           for class_info in file_classes]
            }
        elif action == 'analyze_directory':
            # Analyze a directory of Python files
            dir_path = context.get('path')
            if not dir_path or not os.path.isdir(dir_path):
                return {
                    "success": False,
                    "error": f"Invalid directory path: {dir_path}"
                }
                
            return self._analyze_directory(dir_path)
        else:
            return {
                "success": False,
                "error": f"Unknown action: {action}"
            }
    
    def on_file_processor(self, file_path, file_content, metadata=None):
        """
        Process Python file and extract class information
        
        Args:
            file_path (str): Path to the file
            file_content (str): Content of the file
            metadata (dict, optional): Additional metadata
            
        Returns:
            dict: Analysis results
        """
        if not file_path.endswith('.py'):
            return {
                "success": True,
                "plugin_id": self.plugin_id,
                "skipped": True,
                "message": "Not a Python file"
            }
            
        try:
            # Parse the Python code and extract class information
            classes = self._analyze_python_file(file_path, file_content)
            
            # Store in cache
            self.class_cache[file_path] = classes
            
            return {
                "success": True,
                "plugin_id": self.plugin_id,
                "file_path": file_path,
                "classes": [class_info.to_dict() for class_info in classes],
                "class_count": len(classes)
            }
        except Exception as e:
            logger.error(f"Error analyzing file {file_path}: {e}")
            return {
                "success": False,
                "plugin_id": self.plugin_id,
                "error": str(e)
            }
    
    def _analyze_directory(self, dir_path):
        """
        Recursively analyze all Python files in a directory
        
        Args:
            dir_path (str): Path to the directory
            
        Returns:
            dict: Analysis results
        """
        try:
            python_files = []
            class_count = 0
            
            # Walk the directory recursively
            for root, _, files in os.walk(dir_path):
                for file in files:
                    if file.endswith('.py'):
                        python_files.append(os.path.join(root, file))
            
            # Analyze each Python file
            for file_path in python_files:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        file_content = f.read()
                        
                    result = self.on_file_processor(file_path, file_content)
                    if result.get('success') and not result.get('skipped'):
                        class_count += result.get('class_count', 0)
                except Exception as e:
                    logger.error(f"Error processing file {file_path}: {e}")
            
            # Return all analyzed classes
            return {
                "success": True,
                "plugin_id": self.plugin_id,
                "directory": dir_path,
                "python_files": len(python_files),
                "class_count": class_count,
                "classes": [class_info.to_dict() for file_classes in self.class_cache.values() 
                           for class_info in file_classes]
            }
        except Exception as e:
            logger.error(f"Error analyzing directory {dir_path}: {e}")
            return {
                "success": False,
                "plugin_id": self.plugin_id,
                "error": str(e)
            }
    
    def _analyze_python_file(self, file_path, file_content):
        """
        Analyze a Python file and extract class information
        
        Args:
            file_path (str): Path to the file
            file_content (str): Content of the file
            
        Returns:
            list: List of ClassInfo objects
        """
        try:
            # Parse the Python code
            tree = ast.parse(file_content)
            
            # Extract class information
            classes = []
            
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    # Extract base classes
                    bases = []
                    for base in node.bases:
                        if isinstance(base, ast.Name):
                            bases.append(base.id)
                        elif isinstance(base, ast.Attribute):
                            bases.append(self._get_full_attribute_name(base))
                    
                    # Get docstring if available
                    docstring = ast.get_docstring(node)
                    
                    # Create class info
                    class_info = ClassInfo(
                        name=node.name,
                        bases=bases,
                        docstring=docstring,
                        file_path=file_path,
                        line_number=node.lineno
                    )
                    
                    # Extract methods
                    for item in node.body:
                        if isinstance(item, ast.FunctionDef):
                            # Extract method parameters
                            params = [arg.arg for arg in item.args.args]
                            # Remove 'self' from parameters
                            if params and params[0] == 'self':
                                params = params[1:]
                                
                            # Get method docstring
                            method_docstring = ast.get_docstring(item)
                            
                            # Determine method visibility (private, protected, public)
                            visibility = 'public'
                            if item.name.startswith('__'):
                                visibility = 'private'
                            elif item.name.startswith('_'):
                                visibility = 'protected'
                                
                            method_info = {
                                "name": item.name,
                                "params": params,
                                "docstring": method_docstring,
                                "line_number": item.lineno,
                                "visibility": visibility
                            }
                            
                            class_info.methods.append(method_info)
                        elif isinstance(item, ast.Assign):
                            # Extract class attributes
                            for target in item.targets:
                                if isinstance(target, ast.Name):
                                    # Extract attribute value if it's a simple literal
                                    value = None
                                    if isinstance(item.value, (ast.Str, ast.Num, ast.NameConstant)):
                                        try:
                                            value = ast.literal_eval(item.value)
                                        except (ValueError, SyntaxError):
                                            pass
                                    
                                    # Determine attribute visibility
                                    visibility = 'public'
                                    if target.id.startswith('__'):
                                        visibility = 'private'
                                    elif target.id.startswith('_'):
                                        visibility = 'protected'
                                        
                                    attr_info = {
                                        "name": target.id,
                                        "value": value,
                                        "line_number": item.lineno,
                                        "visibility": visibility
                                    }
                                    
                                    class_info.attributes.append(attr_info)
                    
                    classes.append(class_info)
            
            return classes
        except SyntaxError as e:
            logger.error(f"Syntax error in {file_path}: {e}")
            return []
        except Exception as e:
            logger.error(f"Error analyzing {file_path}: {e}")
            return []
    
    def _get_full_attribute_name(self, node):
        """
        Get the full name of an attribute (e.g., module.Class)
        
        Args:
            node (ast.Attribute): AST node representing an attribute
            
        Returns:
            str: Full attribute name
        """
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return f"{self._get_full_attribute_name(node.value)}.{node.attr}"
        return ""
