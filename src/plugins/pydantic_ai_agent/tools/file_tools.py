"""
File-related tools for the PydanticAI agent
"""
import os
from typing import Optional

def read_file(path: str) -> dict:
    """
    Read content from a file
    
    Args:
        path: Path to the file to read
        
    Returns:
        dict: File content and metadata
    """
    try:
        if not os.path.exists(path):
            return {
                "success": False,
                "error": f"File not found: {path}"
            }
            
        with open(path, 'r') as f:
            content = f.read()
            
        return {
            "success": True,
            "content": content,
            "size": os.path.getsize(path),
            "extension": os.path.splitext(path)[1],
            "path": path
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

def list_directory(path: str) -> dict:
    """
    List contents of a directory
    
    Args:
        path: Path to the directory
        
    Returns:
        dict: Directory contents
    """
    try:
        if not os.path.exists(path) or not os.path.isdir(path):
            return {
                "success": False,
                "error": f"Directory not found: {path}"
            }
            
        items = []
        for item in os.listdir(path):
            item_path = os.path.join(path, item)
            items.append({
                "name": item,
                "is_dir": os.path.isdir(item_path),
                "size": os.path.getsize(item_path) if os.path.isfile(item_path) else None,
                "path": item_path
            })
            
        return {
            "success": True,
            "items": items,
            "count": len(items),
            "path": path
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }
