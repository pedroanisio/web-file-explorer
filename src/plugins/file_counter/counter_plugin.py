"""
Counter plugin for the file explorer.
Counts files and directories in the current directory.
"""
import os

def execute(path, **kwargs):
    """
    Count files in the given directory
    
    Args:
        path (str): Directory path
        
    Returns:
        dict: Count results
    """
    try:
        if not os.path.isdir(path):
            return {
                "success": False,
                "error": f"{path} is not a directory"
            }
        
        # Count files and subdirectories
        files = []
        dirs = []
        for item in os.listdir(path):
            item_path = os.path.join(path, item)
            if os.path.isfile(item_path):
                files.append(item)
            elif os.path.isdir(item_path):
                dirs.append(item)
        
        # Prepare output
        output = f"Directory: {path}\n\n"
        output += f"Files: {len(files)}\n"
        output += f"Subdirectories: {len(dirs)}\n"
        
        return {
            "success": True,
            "output": output,
            "title": "File Count Results"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }
