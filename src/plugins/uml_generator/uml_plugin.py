"""
UML Diagram Generator plugin for FIXIT.
Generates UML diagrams from Python code using the Python UML Analyzer plugin.
"""
import os
import json
import logging
import requests
from urllib.parse import quote
from string import Template

# Setup logging
logger = logging.getLogger("uml_generator")

# PlantUML server URL
PLANTUML_SERVER = "https://www.plantuml.com/plantuml/svg/"

def execute(path, **kwargs):
    """
    Execute the UML generator plugin
    
    Args:
        path (str): Directory path to generate UML diagrams for
        
    Returns:
        dict: Result of the execution
    """
    try:
        # Validate path
        if not os.path.exists(path):
            return {
                "success": False,
                "error": f"Path does not exist: {path}"
            }
            
        # Use the backend plugin to analyze the Python files
        analysis_result = analyze_directory(path)
        
        if not analysis_result.get("success", False):
            return {
                "success": False,
                "error": analysis_result.get("error", "Failed to analyze directory")
            }
            
        # Get the class data
        classes = analysis_result.get("classes", [])
        
        if not classes:
            return {
                "success": False,
                "error": "No Python classes found in the specified directory"
            }
            
        # Generate PlantUML code from the class data
        plantuml_code = generate_plantuml_code(classes)
        
        # Generate the UML diagram using the PlantUML web service
        uml_image = generate_uml_diagram(plantuml_code)
        
        # Generate the HTML result with the UML diagram
        output_html = generate_output_html(plantuml_code, uml_image, classes, path)
        
        return {
            "success": True,
            "output": output_html,
            "title": "UML Class Diagram",
            "is_html": True
        }
    except Exception as e:
        logger.error(f"Error generating UML diagram: {e}")
        return {
            "success": False,
            "error": str(e)
        }

def analyze_directory(path):
    """
    Use the Python UML Analyzer plugin to analyze the directory
    
    Args:
        path (str): Directory path to analyze
        
    Returns:
        dict: Analysis results
    """
    try:
        # Check if Flask app is running by making a request to the API
        api_url = "http://127.0.0.1:5000/api/plugins/py_uml_analyzer/query"
        
        # Prepare the query payload
        payload = {
            "query": "analyze_directory",
            "context": {
                "action": "analyze_directory",
                "path": path
            }
        }
        
        # Make the API request
        response = requests.post(api_url, json=payload, timeout=30)
        
        # Check if request was successful
        if response.status_code == 200:
            return response.json()
        else:
            # Fall back to direct code analysis if API is not available
            logger.warning(f"API request failed with status {response.status_code}. Falling back to direct analysis.")
            return direct_analysis(path)
    except requests.RequestException:
        logger.warning("Could not connect to API. Falling back to direct analysis.")
        return direct_analysis(path)
    except Exception as e:
        logger.error(f"Error analyzing directory: {e}")
        return {
            "success": False,
            "error": str(e)
        }

def direct_analysis(path):
    """
    Direct analysis of directory without using the API
    This is a fallback method if the API is not available
    
    Args:
        path (str): Directory path to analyze
        
    Returns:
        dict: Analysis results
    """
    try:
        # Import the analyzer plugin directly
        # Note: This is a fallback and not the preferred method
        from plugins.py_uml_analyzer.analyzer_plugin import PythonUMLAnalyzerPlugin
        
        # Create a temporary plugin instance
        plugin = PythonUMLAnalyzerPlugin("py_uml_analyzer", {}, None)
        
        # Analyze the directory
        return plugin._analyze_directory(path)
    except ImportError:
        logger.error("Could not import the Python UML Analyzer plugin")
        return {
            "success": False,
            "error": "Python UML Analyzer plugin is not available"
        }
    except Exception as e:
        logger.error(f"Error in direct analysis: {e}")
        return {
            "success": False,
            "error": str(e)
        }

def generate_plantuml_code(classes):
    """
    Generate PlantUML code from class information
    
    Args:
        classes (list): List of class information dictionaries
        
    Returns:
        str: PlantUML code
    """
    uml_code = ["@startuml", "skinparam monochrome true", "skinparam shadowing false", "skinparam defaultFontName Arial"]
    
    # Group classes by file
    file_classes = {}
    for cls in classes:
        file_path = cls.get('file_path', 'unknown')
        if file_path not in file_classes:
            file_classes[file_path] = []
        file_classes[file_path].append(cls)
    
    # Create packages for each file
    for file_path, class_list in file_classes.items():
        # Get just the filename without path
        file_name = os.path.basename(file_path)
        uml_code.append(f'package "{file_name}" {{')
        
        for cls in class_list:
            class_name = cls.get('name', 'UnknownClass')
            
            # Start class definition
            if cls.get('type') == 'class':
                uml_code.append(f'class {class_name} {{')
            elif cls.get('type') == 'module':
                uml_code.append(f'object {class_name} <<module>> {{')
            else:
                uml_code.append(f'class {class_name} {{')
            
            # Add methods
            methods = cls.get('methods', [])
            for method in methods:
                method_name = method.get('name', 'unknown_method')
                method_params = ", ".join(method.get('params', []))
                uml_code.append(f'  +{method_name}({method_params})')
            
            # Add attributes
            attributes = cls.get('attributes', [])
            for attr in attributes:
                attr_name = attr.get('name', 'unknown_attr')
                attr_type = attr.get('type', '')
                type_str = f': {attr_type}' if attr_type else ''
                uml_code.append(f'  +{attr_name}{type_str}')
            
            uml_code.append('}')
        
        uml_code.append('}')
    
    # Add relationships
    for cls in classes:
        class_name = cls.get('name', 'UnknownClass')
        
        # Add inheritance relationships
        inherits = cls.get('inherits', [])
        for parent in inherits:
            uml_code.append(f'{parent} <|-- {class_name}')
        
        # Add composition/association relationships
        has_attrs = cls.get('has_attrs', [])
        for attr in has_attrs:
            uml_code.append(f'{class_name} *-- {attr}')
    
    uml_code.append("@enduml")
    return "\n".join(uml_code)

def generate_uml_diagram(plantuml_code):
    """
    Generate a UML diagram using the PlantUML web service
    
    Args:
        plantuml_code (str): PlantUML code
        
    Returns:
        str: URL to the generated diagram
    """
    # Encode the PlantUML code for use with the PlantUML server
    encoded_uml = encode_plantuml(plantuml_code)
    
    # Use the PlantUML web service
    image_url = f"https://www.plantuml.com/plantuml/svg/{encoded_uml}"
    
    return image_url

def encode_plantuml(uml_text):
    """
    Encode PlantUML diagram text into a format that can be used in a URL
    """
    try:
        plantuml_server = requests.get("https://www.plantuml.com/plantuml/encode", params={"text": uml_text})
        return plantuml_server.text
    except Exception as e:
        logger.error(f"Error encoding PlantUML: {e}")
        return None

def generate_output_html(plantuml_code, uml_image_url, classes, path):
    """
    Generate HTML output with the UML diagram
    
    Args:
        plantuml_code (str): PlantUML code
        uml_image_url (str): URL to the UML diagram image
        classes (list): List of class information dictionaries
        path (str): Directory path that was analyzed
        
    Returns:
        str: HTML content
    """
    class_count = len(classes)
    file_count = len(set(cls.get('file_path', '') for cls in classes))
    
    # Use Template with $ placeholders to avoid conflicts with HTML/JS braces
    template = Template("""
    <div class="card">
        <div class="card-header">
            <h2 class="card-title">UML Class Diagram</h2>
            <div class="flex items-center gap-2">
                <button id="toggle-code-btn" class="btn-gray text-sm">
                    Show PlantUML Code
                </button>
                <a href="$uml_image_url" target="_blank" class="btn-blue text-sm">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-1" viewBox="0 0 20 20" fill="currentColor">
                        <path d="M11 3a1 1 0 100 2h2.586l-6.293 6.293a1 1 0 101.414 1.414L15 6.414V9a1 1 0 102 0V4a1 1 0 00-1-1h-5z" />
                        <path d="M5 5a2 2 0 00-2 2v8a2 2 0 002 2h8a2 2 0 002-2v-3a1 1 0 10-2 0v3H5V7h3a1 1 0 000-2H5z" />
                    </svg>
                    Open in New Tab
                </a>
            </div>
        </div>
        
        <div class="card-body p-0">
            <div class="flex flex-col md:flex-row">
                <div class="uml-stats p-4 flex flex-wrap gap-4 border-b md:border-b-0 md:border-r border-gray-200 dark:border-gray-700">
                    <div class="badge-secondary flex items-center">
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-1" viewBox="0 0 20 20" fill="currentColor">
                            <path d="M2 6a2 2 0 012-2h5l2 2h5a2 2 0 012 2v6a2 2 0 01-2 2H4a2 2 0 01-2-2V6z" />
                        </svg>
                        <span>Directory: $path</span>
                    </div>
                    <div class="badge-secondary flex items-center">
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-1" viewBox="0 0 20 20" fill="currentColor">
                            <path fill-rule="evenodd" d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4zm2 6a1 1 0 011-1h6a1 1 0 110 2H7a1 1 0 01-1-1zm1 3a1 1 0 100 2h6a1 1 0 100-2H7z" clip-rule="evenodd" />
                        </svg>
                        <span>Files: $file_count</span>
                    </div>
                    <div class="badge-secondary flex items-center">
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-1" viewBox="0 0 20 20" fill="currentColor">
                            <path d="M9 4.804A7.968 7.968 0 005.5 4c-1.255 0-2.443.29-3.5.804v10A7.969 7.969 0 015.5 14c1.669 0 3.218.51 4.5 1.385A7.962 7.962 0 0114.5 14c1.255 0 2.443.29 3.5.804v-10A7.968 7.968 0 0014.5 4c-1.255 0-2.443.29-3.5.804V12a1 1 0 11-2 0V4.804z" />
                        </svg>
                        <span>Classes: $class_count</span>
                    </div>
                </div>
            </div>
            
            <div class="uml-diagram-container p-4 overflow-auto text-center">
                <img src="$uml_image_url" alt="UML Diagram" class="mx-auto">
            </div>
            
            <div id="plantuml-code" class="hidden">
                <div class="border-t border-gray-200 dark:border-gray-700 mt-4"></div>
                <div class="p-4">
                    <h3 class="font-medium mb-2 text-gray-800 dark:text-gray-200">PlantUML Code</h3>
                    <pre class="bg-gray-100 dark:bg-gray-800 p-4 rounded-md overflow-x-auto"><code>$plantuml_code</code></pre>
                </div>
            </div>
        </div>
    </div>

    <script>
        document.addEventListener('DOMContentLoaded', function() {
            const toggleBtn = document.getElementById('toggle-code-btn');
            const codeBlock = document.getElementById('plantuml-code');
            
            toggleBtn.addEventListener('click', function() {
                if (codeBlock.classList.contains('hidden')) {
                    codeBlock.classList.remove('hidden');
                    toggleBtn.textContent = 'Hide PlantUML Code';
                } else {
                    codeBlock.classList.add('hidden');
                    toggleBtn.textContent = 'Show PlantUML Code';
                }
            });
        });
    </script>
    """)
    
    # Substitute values into the template
    output_html = template.substitute(
        uml_image_url=uml_image_url,
        path=path,
        file_count=file_count,
        class_count=class_count,
        plantuml_code=plantuml_code
    )
    
    return output_html

def process_file(path, **kwargs):
    """
    Process a directory and generate a UML diagram
    
    Args:
        path (str): Path to the directory
        
    Returns:
        dict: Result with the generated UML diagram
    """
    try:
        logger.info(f"Generating UML diagram for {path}")
        
        from plugins.py_uml_analyzer.analyzer_plugin import process_file as analyze
        
        # Get class information from the analyzer
        result = analyze(path)
        
        if not result.get('success', False):
            logger.error(f"Error analyzing directory: {result.get('error', 'Unknown error')}")
            return {
                "success": False,
                "error": f"Error analyzing directory: {result.get('error', 'Unknown error')}"
            }
        
        classes = result.get('classes', [])
        
        if not classes:
            logger.warning(f"No classes found in {path}")
            return {
                "success": True,
                "output": f"<div class='card'><div class='card-body text-center p-8'><h3 class='text-xl font-medium mb-4'>No Classes Found</h3><p>No Python classes were found in the directory: {path}</p></div></div>",
                "is_html": True
            }
        
        # Generate PlantUML code
        plantuml_code = generate_plantuml_code(classes)
        
        # Encode the PlantUML code
        encoded_uml = encode_plantuml(plantuml_code)
        
        if not encoded_uml:
            logger.error("Error encoding PlantUML")
            return {
                "success": False,
                "error": "Error encoding PlantUML"
            }
        
        # Create the URL to the generated UML diagram
        uml_image_url = f"{PLANTUML_SERVER}{encoded_uml}"
        
        # Generate the HTML output
        output_html = generate_output_html(plantuml_code, uml_image_url, classes, path)
        
        return {
            "success": True,
            "output": output_html,
            "is_html": True
        }
    except Exception as e:
        logger.error(f"Error generating UML diagram: {e}")
        return {
            "success": False,
            "error": f"Error generating UML diagram: {str(e)}"
        }
