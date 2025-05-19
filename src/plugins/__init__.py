"""
Plugin system for the file explorer.
Supports both UI-based plugins and backend service plugins.
"""
import os
import json
import importlib
import logging
import sys
import traceback
from collections import defaultdict

# Import the plugin base classes
try:
    from .plugin_base import PluginRegistry, BackendPlugin, HOOK_STARTUP
    from .dependency_manager import DependencyManager
    BACKEND_PLUGINS_ENABLED = True
except ImportError:
    BACKEND_PLUGINS_ENABLED = False

# Setup logging
logging.basicConfig(level=logging.DEBUG, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("plugin_system")

class PluginManager:
    """
    Manages the loading and execution of plugins.
    Supports both UI plugins and backend service plugins.
    """
    def __init__(self, plugin_dir):
        logger.debug(f"Initializing PluginManager with directory: {plugin_dir}")
        self.plugin_dir = plugin_dir
        self.plugins = {}  # UI plugins
        self.toolbar_items = []
        
        # Initialize backend plugin system if available
        if BACKEND_PLUGINS_ENABLED:
            logger.debug("Backend plugins enabled, initializing dependency manager")
            self.dependency_manager = DependencyManager()
            self.registry = PluginRegistry()
        else:
            logger.warning("Backend plugins disabled - dependency support might be limited")
            self.registry = None
            
        self.load_plugins()
        
        # After loading all plugins, register dependencies in the requirements file
        if BACKEND_PLUGINS_ENABLED:
            logger.debug("Updating plugin requirements.txt file with all plugin dependencies")
            self.collect_all_plugin_dependencies()
    
    def collect_all_plugin_dependencies(self):
        """Collect all plugin dependencies and ensure they're in the requirements file"""
        if not BACKEND_PLUGINS_ENABLED or not hasattr(self, 'dependency_manager'):
            logger.warning("Cannot collect dependencies: dependency manager not available")
            return
            
        # This will trigger an update of the requirements file
        for plugin_id, plugin_info in self.plugins.items():
            manifest = plugin_info.get('manifest', {})
            dependencies = manifest.get('dependencies', [])
            if dependencies:
                logger.debug(f"Registering dependencies for UI plugin {plugin_id}: {dependencies}")
                # This just registers the dependencies without trying to install them
                self.dependency_manager.check_dependencies(plugin_id, dependencies)
                
    def load_plugins(self):
        """
        Load all plugins from the plugins directory.
        Each plugin should have a manifest.json file that defines its properties.
        """
        logger.info(f"Loading plugins from {self.plugin_dir}")
        
        if not os.path.exists(self.plugin_dir):
            logger.warning(f"Plugin directory {self.plugin_dir} does not exist")
            return
        
        # Log information about environment
        logger.debug(f"Python version: {sys.version}")
        logger.debug(f"Python executable: {sys.executable}")
        logger.debug(f"Current working directory: {os.getcwd()}")
        
        plugin_count = 0
        for item in os.listdir(self.plugin_dir):
            plugin_path = os.path.join(self.plugin_dir, item)
            
            # Skip non-directories and special module files
            if not os.path.isdir(plugin_path) or item in ['__pycache__', 'plugin_base.py', 'dependency_manager.py']:
                continue
                
            manifest_path = os.path.join(plugin_path, "manifest.json")
            if not os.path.exists(manifest_path):
                logger.warning(f"No manifest.json found in {plugin_path}")
                continue
                
            try:
                logger.debug(f"Loading manifest from {manifest_path}")
                with open(manifest_path, 'r') as f:
                    manifest = json.load(f)
                
                logger.debug(f"Manifest loaded: {manifest.get('id', 'unknown')}")
                
                # Check for required fields
                required_fields = ["id", "name", "version", "entry_point"]
                if not all(field in manifest for field in required_fields):
                    missing = [field for field in required_fields if field not in manifest]
                    logger.warning(f"Manifest in {plugin_path} missing required fields: {missing}")
                    continue
                
                # Log detailed manifest info
                logger.debug(f"Plugin details: ID={manifest['id']}, Name={manifest['name']}, Version={manifest['version']}")
                    
                # Handle different plugin types
                plugin_type = manifest.get("type", "ui")
                logger.debug(f"Plugin type: {plugin_type}")
                
                if plugin_type == "backend" and BACKEND_PLUGINS_ENABLED:
                    self._load_backend_plugin(item, plugin_path, manifest)
                else:
                    self._load_ui_plugin(item, plugin_path, manifest)
                    
                plugin_count += 1
                    
            except json.JSONDecodeError:
                logger.error(f"Invalid manifest.json in {plugin_path}")
            except Exception as e:
                logger.error(f"Error loading plugin {item}: {e}", exc_info=True)
        
        logger.info(f"Loaded {plugin_count} plugins")
    
    def _load_ui_plugin(self, plugin_name, plugin_path, manifest):
        """
        Load a UI-based plugin that appears in the toolbar
        """
        logger.debug(f"Loading UI plugin: {plugin_name} from {plugin_path}")
        try:
            # Check for UI-specific required fields
            if "icon" not in manifest:
                logger.warning(f"UI plugin manifest in {plugin_path} missing 'icon' field")
                return
            
            # Check for dependencies (UI plugins can have dependencies too)
            dependencies = manifest.get("dependencies", [])
            if dependencies and BACKEND_PLUGINS_ENABLED:
                logger.debug(f"UI plugin {manifest['id']} has dependencies: {dependencies}")
                deps_satisfied, missing_deps = self.dependency_manager.check_dependencies(
                    manifest["id"], dependencies
                )
                
                if not deps_satisfied:
                    logger.warning(f"UI plugin {manifest['id']} has missing dependencies: {missing_deps}")
                    
                    # Optionally attempt to install dependencies
                    auto_install = manifest.get("auto_install_dependencies", False)
                    if auto_install:
                        logger.info(f"Attempting to auto-install dependencies for UI plugin {manifest['id']}")
                        success, error = self.dependency_manager.install_dependencies(
                            manifest["id"], dependencies
                        )
                        if not success:
                            logger.error(f"Failed to install dependencies for UI plugin {manifest['id']}: {error}")
                            return
                    else:
                        logger.debug(f"Skipping auto-install for {manifest['id']} (auto_install_dependencies=false)")
                        # Continue but may fail later when executing
            
            # Try to import the module
            module_path = f"plugins.{plugin_name}.{manifest['entry_point']}"
            logger.debug(f"Importing module {module_path}")
            
            try:
                module = importlib.import_module(module_path)
                logger.debug(f"Module imported successfully: {module_path}")
            except ImportError as e:
                logger.error(f"Failed to import module {module_path}: {e}")
                # Check if this is due to missing dependencies
                if "No module named" in str(e):
                    missing_module = str(e).split("'")[1]
                    logger.error(f"Module {missing_module} not found - might be a missing dependency")
                    logger.debug(f"Available modules in sys.modules: {list(sorted(sys.modules.keys()))[:20]}...")
                return
                
            if not hasattr(module, 'execute'):
                logger.warning(f"UI plugin {plugin_name} does not have an execute function")
                return
                
            # Add to plugins dictionary
            self.plugins[manifest["id"]] = {
                "manifest": manifest,
                "module": module,
                "path": plugin_path
            }
            
            # Add to toolbar items
            self.toolbar_items.append({
                "id": manifest["id"],
                "name": manifest["name"],
                "icon": manifest["icon"],
                "description": manifest.get("description", "")
            })
            
            logger.info(f"Successfully loaded UI plugin: {manifest['name']}")
        except Exception as e:
            logger.error(f"Failed to load UI plugin '{plugin_name}' from {plugin_path}: {e}")
            logger.debug(f"Exception traceback: {traceback.format_exc()}")
            # Continue loading other plugins
    
    def _load_backend_plugin(self, plugin_name, plugin_path, manifest):
        """
        Load a backend service plugin with hooks
        """
        logger.debug(f"Loading backend plugin: {plugin_name} from {plugin_path}")
        # Check dependencies first
        dependencies = manifest.get("dependencies", [])
        if dependencies:
            deps_satisfied, missing_deps = self.dependency_manager.check_dependencies(
                manifest["id"], dependencies
            )
            
            if not deps_satisfied:
                logger.warning(f"Plugin {manifest['id']} has missing dependencies: {missing_deps}")
                
                # Optionally attempt to install dependencies
                auto_install = manifest.get("auto_install_dependencies", False)
                if auto_install:
                    logger.info(f"Attempting to auto-install dependencies for {manifest['id']}")
                    success, error = self.dependency_manager.install_dependencies(
                        manifest["id"], dependencies
                    )
                    if not success:
                        logger.error(f"Failed to install dependencies for {manifest['id']}: {error}")
                        return
                else:
                    # Skip this plugin if dependencies aren't satisfied
                    logger.debug(f"Skipping plugin {manifest['id']} due to unsatisfied dependencies (auto-install not enabled)")
                    return
        
        # Import backend plugin module
        try:
            module_path = f"plugins.{plugin_name}.{manifest['entry_point']}"
            logger.debug(f"Importing backend plugin module: {module_path}")
            module = importlib.import_module(module_path)
            
            # Check for create_plugin function
            if not hasattr(module, 'create_plugin'):
                logger.warning(f"Backend plugin {plugin_name} does not have a create_plugin function")
                return
            
            logger.debug(f"Creating plugin instance for {manifest['id']}")
            # Create plugin instance
            plugin = module.create_plugin(manifest["id"], manifest, self.registry)
            self.registry.register_plugin(manifest["id"], plugin)
            
            # Activate the plugin
            logger.debug(f"Activating plugin {manifest['id']}")
            plugin.activate()
            
            # Trigger startup hook if available
            logger.debug(f"Invoking startup hook for plugin {manifest['id']}")
            self.registry.invoke_hook(HOOK_STARTUP)
            
            logger.info(f"Successfully loaded backend plugin: {manifest['name']}")
        except Exception as e:
            logger.error(f"Failed to load or activate backend plugin '{plugin_name}' from {plugin_path}: {e}")
            logger.debug(f"Exception traceback: {traceback.format_exc()}")
            # Continue loading other plugins
    
    def execute_plugin(self, plugin_id, **kwargs):
        """
        Execute a UI plugin by its ID with the given parameters.
        """
        logger.debug(f"Execute plugin requested: {plugin_id}")
        
        if plugin_id not in self.plugins:
            # Check if it's a backend plugin
            if BACKEND_PLUGINS_ENABLED and self.registry and plugin_id in self.registry.plugins:
                return self._execute_backend_plugin(plugin_id, **kwargs)
                
            logger.warning(f"Plugin {plugin_id} not found")
            return None
            
        try:
            plugin = self.plugins[plugin_id]
            logger.debug(f"Executing UI plugin: {plugin_id}")
            
            # Check dependencies again before execution
            manifest = plugin["manifest"]
            dependencies = manifest.get("dependencies", [])
            
            if dependencies and BACKEND_PLUGINS_ENABLED:
                deps_satisfied, missing_deps = self.dependency_manager.check_dependencies(
                    manifest["id"], dependencies
                )
                
                if not deps_satisfied:
                    logger.warning(f"Plugin {manifest['id']} has unmet dependencies: {missing_deps}")
                    
                    # Only try to install if configured to do so
                    auto_install = manifest.get("auto_install_dependencies", False)
                    if auto_install:
                        logger.info(f"Attempting to install missing dependencies before execution: {missing_deps}")
                        success, error = self.dependency_manager.install_dependencies(
                            manifest["id"], dependencies
                        )
                        if not success:
                            return {
                                "success": False,
                                "error": f"Required dependencies not installed: {missing_deps}. Error: {error}"
                            }
                    else:
                        return {
                            "success": False,
                            "error": f"Required dependencies not installed: {missing_deps}. Please restart the application with auto-install enabled."
                        }
            
            # Execute the plugin
            logger.debug(f"Executing plugin module: {plugin_id}")
            result = plugin["module"].execute(**kwargs)
            return result
        except ImportError as e:
            logger.error(f"Import error executing plugin {plugin_id}: {e}")
            return {
                "success": False,
                "error": f"Missing dependency: {str(e)}. Please restart the application to auto-install dependencies."
            }
        except Exception as e:
            logger.error(f"Error executing plugin {plugin_id}: {e}")
            logger.debug(f"Exception traceback: {traceback.format_exc()}")
            return {"error": str(e)}
            
    def _execute_backend_plugin(self, plugin_id, hook_name=None, **kwargs):
        """
        Execute a backend plugin by invoking a specific hook
        """
        logger.debug(f"Executing backend plugin: {plugin_id}, hook: {hook_name}")
        
        if not BACKEND_PLUGINS_ENABLED or not self.registry:
            return {"error": "Backend plugin system not enabled"}
            
        if not hook_name:
            return {"error": "No hook specified for backend plugin"}
            
        try:
            # Invoke the specified hook
            logger.debug(f"Invoking hook {hook_name} on plugin {plugin_id}")
            results = self.registry.invoke_hook(hook_name, **kwargs)
            
            # Find the result for this specific plugin
            for result in results:
                if result['plugin_id'] == plugin_id:
                    if result['success']:
                        logger.debug(f"Plugin {plugin_id} hook execution succeeded")
                        return result['result']
                    else:
                        logger.warning(f"Plugin {plugin_id} hook execution failed: {result.get('error', 'Unknown error')}")
                        return {"error": result.get('error', 'Unknown error')}
            
            logger.warning(f"Plugin {plugin_id} did not respond to hook {hook_name}")
            return {"error": f"Plugin {plugin_id} did not respond to hook {hook_name}"}
        except Exception as e:
            logger.error(f"Error executing backend plugin {plugin_id}: {e}")
            logger.debug(f"Exception traceback: {traceback.format_exc()}")
            return {"error": str(e)}
    
    def get_toolbar_items(self):
        """
        Get all toolbar items for the UI.
        """
        return self.toolbar_items
        
    def get_backend_plugins(self):
        """
        Get all registered backend plugins.
        """
        if BACKEND_PLUGINS_ENABLED and self.registry:
            return self.registry.get_all_plugins()
        return {}
        
    def invoke_hook(self, hook_name, *args, **kwargs):
        """
        Invoke a hook on all registered backend plugins.
        """
        if BACKEND_PLUGINS_ENABLED and self.registry:
            return self.registry.invoke_hook(hook_name, *args, **kwargs)
        return []
