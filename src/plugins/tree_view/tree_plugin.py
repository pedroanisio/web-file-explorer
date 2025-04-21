"""
Tree plugin for the file explorer.
Shows the tree structure of the current directory using the 'tree' command.
"""
import subprocess
import os

def execute(path, **kwargs):
    """
    Execute the tree command on the given path.
    
    Args:
        path (str): The path to show the tree structure for
        
    Returns:
        dict: A dictionary containing the result of the tree command
    """
    try:
        # Run the tree command with --gitignore option
        result = subprocess.run(
            ["tree", "--gitignore", path],
            capture_output=True,
            text=True,
            check=True
        )
        
        return {
            "success": True,
            "output": result.stdout,
            "title": "Tree Structure"
        }
    except subprocess.CalledProcessError as e:
        return {
            "success": False,
            "error": f"Command failed with exit code {e.returncode}",
            "output": e.stderr
        }
    except FileNotFoundError:
        return {
            "success": False,
            "error": "The 'tree' command is not installed on the system",
            "output": "Please install the tree command: sudo apt-get install tree"
        }
