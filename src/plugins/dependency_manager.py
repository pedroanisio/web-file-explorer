"""
Dependency manager for the FIXIT plugin system.
Handles checking and installing plugin dependencies.
"""
import subprocess
import logging
import pkg_resources
from typing import List, Tuple, Dict, Any

# Setup logging
logger = logging.getLogger("dependency_manager")

class DependencyManager:
    """Handles plugin dependencies"""
    
    def __init__(self):
        self.installed_packages = {}
        self._refresh_installed_packages()
    
    def _refresh_installed_packages(self):
        """Refresh the list of installed packages"""
        try:
            self.installed_packages = {
                pkg.key: pkg.version 
                for pkg in pkg_resources.working_set
            }
        except Exception as e:
            logger.error(f"Error refreshing installed packages: {e}")
    
    def _parse_requirement(self, requirement_str):
        """
        Parse a requirement string into name and version specifier
        Example: "pydantic>=2.0.0" -> ("pydantic", ">=2.0.0")
        """
        req = pkg_resources.Requirement.parse(requirement_str)
        return req.name, str(req.specifier) if req.specifier else None
    
    def _is_satisfied(self, package_name, version_spec=None):
        """Check if a package requirement is satisfied"""
        if package_name.lower() not in self.installed_packages:
            return False
            
        if not version_spec:
            return True
            
        try:
            installed_version = self.installed_packages[package_name.lower()]
            requirement = f"{package_name}{version_spec}"
            req = pkg_resources.Requirement.parse(requirement)
            return pkg_resources.parse_version(installed_version) in req
        except Exception as e:
            logger.error(f"Error checking version requirement: {e}")
            return False
    
    def check_dependencies(self, plugin_id, dependencies):
        """
        Check if dependencies are satisfied
        Returns: (is_satisfied, missing_deps)
        """
        missing = []
        for dep in dependencies:
            try:
                # Parse requirement
                req_name, req_spec = self._parse_requirement(dep)
                if not self._is_satisfied(req_name, req_spec):
                    missing.append(dep)
            except Exception as e:
                logger.error(f"Error parsing dependency '{dep}': {e}")
                missing.append(dep)
                
        return len(missing) == 0, missing
    
    def install_dependencies(self, plugin_id, dependencies):
        """
        Install dependencies for a plugin
        Returns: (success, error_message)
        """
        try:
            if not dependencies:
                return True, None
                
            logger.info(f"Installing dependencies for plugin {plugin_id}: {dependencies}")
            
            # Use pip to install dependencies
            subprocess.check_call(["pip", "install"] + dependencies)
            
            # Refresh installed packages
            self._refresh_installed_packages()
            
            return True, None
        except subprocess.CalledProcessError as e:
            error_msg = f"Failed to install dependencies: {e.stderr if hasattr(e, 'stderr') else str(e)}"
            logger.error(error_msg)
            return False, error_msg
        except Exception as e:
            error_msg = f"Error installing dependencies: {str(e)}"
            logger.error(error_msg)
            return False, error_msg
