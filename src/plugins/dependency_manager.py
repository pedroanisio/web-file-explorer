"""
Dependency manager for the FIXIT plugin system.
Handles checking and installing plugin dependencies.
"""
import subprocess
import logging
import pkg_resources
import sys
import os
from typing import List, Tuple, Dict, Any

# Setup logging with more detailed format
logging.basicConfig(level=logging.DEBUG, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("dependency_manager")

class DependencyManager:
    """Handles plugin dependencies"""
    
    def __init__(self):
        logger.debug("Initializing DependencyManager")
        self.installed_packages = {}
        self.all_plugin_dependencies = set()  # Track all dependencies from all plugins
        self.requirements_file = os.path.join(os.path.dirname(__file__), "requirements.txt")
        logger.debug(f"Requirements file path: {self.requirements_file}")
        self._refresh_installed_packages()
        logger.debug(f"Initial packages detected: {len(self.installed_packages)}")
    
    def _refresh_installed_packages(self):
        """Refresh the list of installed packages"""
        logger.debug("Refreshing installed packages list")
        try:
            self.installed_packages = {
                pkg.key: pkg.version 
                for pkg in pkg_resources.working_set
            }
            logger.debug(f"Found {len(self.installed_packages)} installed packages")
        except Exception as e:
            logger.error(f"Error refreshing installed packages: {e}", exc_info=True)
    
    def _parse_requirement(self, requirement_str):
        """
        Parse a requirement string into name and version specifier
        Example: "pydantic>=2.0.0" -> ("pydantic", ">=2.0.0")
        """
        logger.debug(f"Parsing requirement: {requirement_str}")
        req = pkg_resources.Requirement.parse(requirement_str)
        result = (req.name, str(req.specifier) if req.specifier else None)
        logger.debug(f"Parsed as: {result}")
        return result
    
    def _is_satisfied(self, package_name, version_spec=None):
        """Check if a package requirement is satisfied"""
        logger.debug(f"Checking if requirement satisfied: {package_name}{version_spec or ''}")
        
        if package_name.lower() not in self.installed_packages:
            logger.debug(f"Package {package_name} not installed")
            return False
            
        if not version_spec:
            logger.debug(f"Package {package_name} installed, no version constraint")
            return True
            
        try:
            installed_version = self.installed_packages[package_name.lower()]
            logger.debug(f"Package {package_name} installed version: {installed_version}")
            
            requirement = f"{package_name}{version_spec}"
            req = pkg_resources.Requirement.parse(requirement)
            
            result = pkg_resources.parse_version(installed_version) in req
            logger.debug(f"Version check result: {result} (required: {version_spec}, installed: {installed_version})")
            return result
        except Exception as e:
            logger.error(f"Error checking version requirement: {e}", exc_info=True)
            return False
    
    def check_dependencies(self, plugin_id, dependencies):
        """
        Check if dependencies are satisfied
        Returns: (is_satisfied, missing_deps)
        """
        logger.debug(f"Checking dependencies for plugin {plugin_id}: {dependencies}")
        
        # Add all dependencies to the tracking set
        for dep in dependencies:
            self.all_plugin_dependencies.add(dep)
            
        # Update requirements file
        self._update_requirements_file()
            
        missing = []
        for dep in dependencies:
            try:
                # Parse requirement
                req_name, req_spec = self._parse_requirement(dep)
                satisfied = self._is_satisfied(req_name, req_spec)
                logger.debug(f"Dependency check for {dep}: {'Satisfied' if satisfied else 'Missing'}")
                if not satisfied:
                    missing.append(dep)
            except Exception as e:
                logger.error(f"Error parsing dependency '{dep}': {e}", exc_info=True)
                missing.append(dep)
        
        logger.debug(f"Dependencies check result - All satisfied: {len(missing) == 0}, Missing: {missing}")        
        return len(missing) == 0, missing
    
    def _update_requirements_file(self):
        """Write all plugin dependencies to requirements.txt file"""
        try:
            logger.debug(f"Writing {len(self.all_plugin_dependencies)} dependencies to {self.requirements_file}")
            with open(self.requirements_file, 'w') as f:
                # Sort dependencies for consistent output
                for dependency in sorted(self.all_plugin_dependencies):
                    f.write(f"{dependency}\n")
            logger.info(f"Successfully updated requirements file at {self.requirements_file}")
        except Exception as e:
            logger.error(f"Error writing requirements file: {e}", exc_info=True)
    
    def install_dependencies(self, plugin_id, dependencies):
        """
        Install dependencies for a plugin
        Returns: (success, error_message)
        """
        logger.debug(f"Installing dependencies for plugin {plugin_id}: {dependencies}")
        
        # Add all dependencies to the tracking set
        for dep in dependencies:
            self.all_plugin_dependencies.add(dep)
            
        # Update requirements file
        self._update_requirements_file()
        
        # Log Python executable and environment
        logger.debug(f"Python executable: {sys.executable}")
        logger.debug(f"Python version: {sys.version}")
        logger.debug(f"Platform: {sys.platform}")
        
        try:
            if not dependencies:
                logger.debug("No dependencies to install")
                return True, None
                
            logger.info(f"Installing dependencies for plugin {plugin_id}: {dependencies}")
            
            # Use pip to install dependencies
            cmd = [sys.executable, "-m", "pip", "install"] + dependencies
            logger.debug(f"Running command: {' '.join(cmd)}")
            
            # Capture output for debugging
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            stdout, stderr = process.communicate()
            
            if process.returncode != 0:
                logger.error(f"Pip install failed (exit code {process.returncode})")
                logger.debug(f"Pip output (stdout): {stdout}")
                logger.debug(f"Pip error (stderr): {stderr}")
                return False, f"Pip install failed: {stderr}"
                
            logger.debug(f"Pip install succeeded. Output: {stdout}")
            
            # Refresh installed packages
            logger.debug("Refreshing package list after installation")
            self._refresh_installed_packages()
            
            # Verify dependencies were actually installed
            all_satisfied, still_missing = self.check_dependencies(plugin_id, dependencies)
            if not all_satisfied:
                logger.warning(f"Some dependencies still missing after installation: {still_missing}")
                return False, f"Failed to install dependencies: {still_missing}"
            
            logger.info(f"Successfully installed all dependencies for {plugin_id}")
            return True, None
        except subprocess.CalledProcessError as e:
            error_msg = f"Failed to install dependencies: {e.stderr if hasattr(e, 'stderr') else str(e)}"
            logger.error(error_msg, exc_info=True)
            return False, error_msg
        except Exception as e:
            error_msg = f"Error installing dependencies: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return False, error_msg
