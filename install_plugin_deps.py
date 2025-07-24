#!/usr/bin/env python3
"""
Utility script to install plugin dependencies from requirements.txt
"""
import subprocess
import os
import sys
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("dependency_installer")

def install_plugin_dependencies():
    """Install all plugin dependencies from the requirements file"""
    # Get the requirements.txt path
    script_dir = os.path.dirname(os.path.abspath(__file__))
    req_file = os.path.join(script_dir, "src", "plugins", "requirements.txt")
    
    if not os.path.exists(req_file):
        logger.error(f"Requirements file not found at {req_file}")
        return False
        
    logger.info(f"Installing plugin dependencies from {req_file}")
    
    try:
        # Run pip install with the requirements file
        cmd = [sys.executable, "-m", "pip", "install", "-r", req_file]
        logger.info(f"Running: {' '.join(cmd)}")
        
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        stdout, stderr = process.communicate()
        
        if process.returncode != 0:
            logger.error(f"Installation failed with exit code {process.returncode}")
            logger.error(f"Error: {stderr}")
            return False
            
        logger.info("Successfully installed plugin dependencies")
        logger.info(stdout)
        return True
        
    except Exception as e:
        logger.error(f"Error installing dependencies: {e}")
        return False

if __name__ == "__main__":
    success = install_plugin_dependencies()
    sys.exit(0 if success else 1) 