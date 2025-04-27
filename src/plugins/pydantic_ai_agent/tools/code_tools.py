"""
Code analysis tools for the PydanticAI agent
"""
import ast
import json
from typing import Optional, Dict, Any, List

def analyze_syntax(code: str, language: Optional[str] = "python") -> dict:
    """
    Analyze code syntax and structure
    
    Args:
        code: Code to analyze
        language: Programming language of the code
        
    Returns:
        dict: Analysis results
    """
    try:
        if language.lower() == "python":
            return _analyze_python_syntax(code)
        else:
            return {
                "success": False,
                "error": f"Syntax analysis for {language} not implemented"
            }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

def suggest_improvements(code: str, language: Optional[str] = "python") -> dict:
    """
    Suggest code improvements
    
    Args:
        code: Code to analyze
        language: Programming language of the code
        
    Returns:
        dict: Suggested improvements
    """
    try:
        if language.lower() == "python":
            # This would be a more sophisticated analysis in a real implementation
            # For now, we'll return a simple structure
            issues = _identify_python_issues(code)
            
            return {
                "success": True,
                "issues": issues,
                "suggestions": [
                    {
                        "description": issue["suggestion"],
                        "severity": issue["severity"],
                        "line": issue["line"]
                    }
                    for issue in issues if "suggestion" in issue
                ]
            }
        else:
            return {
                "success": False,
                "error": f"Improvement suggestions for {language} not implemented"
            }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

def _analyze_python_syntax(code: str) -> dict:
    """Analyze Python code syntax"""
    try:
        tree = ast.parse(code)
        
        # Extract basic structure information
        functions = []
        classes = []
        imports = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                functions.append({
                    "name": node.name,
                    "line": node.lineno,
                    "args": [arg.arg for arg in node.args.args],
                    "decorators": [
                        ast.unparse(d).strip() for d in node.decorator_list
                    ] if hasattr(ast, 'unparse') else []
                })
            elif isinstance(node, ast.ClassDef):
                classes.append({
                    "name": node.name,
                    "line": node.lineno,
                    "bases": [
                        ast.unparse(b).strip() for b in node.bases
                    ] if hasattr(ast, 'unparse') else []
                })
            elif isinstance(node, ast.Import):
                for name in node.names:
                    imports.append({
                        "name": name.name,
                        "alias": name.asname
                    })
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                for name in node.names:
                    imports.append({
                        "name": f"{module}.{name.name}",
                        "alias": name.asname,
                        "from_import": True
                    })
        
        return {
            "success": True,
            "functions": functions,
            "classes": classes,
            "imports": imports,
            "structure": {
                "function_count": len(functions),
                "class_count": len(classes),
                "import_count": len(imports)
            }
        }
    except SyntaxError as e:
        return {
            "success": False,
            "error": f"Syntax error: {str(e)}",
            "line": e.lineno,
            "offset": e.offset
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

def _identify_python_issues(code: str) -> List[Dict[str, Any]]:
    """Identify potential issues in Python code"""
    issues = []
    
    try:
        tree = ast.parse(code)
        
        # This would be a more complex analysis in a real implementation
        # Simple example checks:
        
        # Check for overly complex functions (too many lines)
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Get function end line
                end_line = 0
                for child in ast.walk(node):
                    if hasattr(child, 'lineno'):
                        end_line = max(end_line, child.lineno)
                
                # Check function length
                if end_line - node.lineno > 30:
                    issues.append({
                        "type": "complexity",
                        "description": f"Function '{node.name}' is too long ({end_line - node.lineno} lines)",
                        "line": node.lineno,
                        "severity": "medium",
                        "suggestion": f"Consider breaking down function '{node.name}' into smaller functions"
                    })
        
        # More checks would be implemented in a real version
                
        return issues
    except Exception:
        # If analysis fails, return empty list
        return []
