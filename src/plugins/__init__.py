"""
Plugin system for the file explorer.
Supports both UI-based plugins and backend service plugins.
"""
import os
import json
import importlib
import logging
from collections import defaultdict

# Import the plugin base classes
try:
    from .plugin_base import PluginRegistry, BackendPlugin, HOOK_STARTUP
    from .dependency_manager import DependencyManager
    BACKEND_PLUGINS_ENABLED = True
except ImportError:
    BACKEND_PLUGINS_ENABLED = False

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("plugin_system")

class PluginManager:
    """
    Manages the loading and execution of plugins.
    Supports both UI plugins and backend service plugins.
    """
    def __init__(self, plugin_dir):
        self.plugin_dir = plugin_dir
        self.plugins = {}  # UI plugins
        self.toolbar_items = []
        
        # Initialize backend plugin system if available
        if BACKEND_PLUGINS_ENABLED:
            self.dependency_manager = DependencyManager()
            self.registry = PluginRegistry()
        else:
            self.registry = None
            
        self.load_plugins()
    
    def load_plugins(self):
        """
        Load all plugins from the plugins directory.
        Each plugin should have a manifest.json file that defines its properties.
        """
        logger.info(f"Loading plugins from {self.plugin_dir}")
        
        if not os.path.exists(self.plugin_dir):
            logger.warning(f"Plugin directory {self.plugin_dir} does not exist")
            return
        
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
                with open(manifest_path, 'r') as f:
                    manifest = json.load(f)
                
                # Check for required fields
                required_fields = ["id", "name", "version", "entry_point"]
                if not all(field in manifest for field in required_fields):
                    logger.warning(f"Manifest in {plugin_path} missing required fields")
                    continue
                    
                # Handle different plugin types
                plugin_type = manifest.get("type", "ui")
                
                if plugin_type == "backend" and BACKEND_PLUGINS_ENABLED:
                    self._load_backend_plugin(item, plugin_path, manifest)
                else:
                    self._load_ui_plugin(item, plugin_path, manifest)
                    
            except json.JSONDecodeError:
                logger.error(f"Invalid manifest.json in {plugin_path}")
    
    def _load_ui_plugin(self, plugin_name, plugin_path, manifest):
        """
        Load a UI-based plugin that appears in the toolbar
        """
        # Check for UI-specific required fields
        if "icon" not in manifest:
            logger.warning(f"UI plugin manifest in {plugin_path} missing 'icon' field")
            return
            
        module_path = f"plugins.{plugin_name}.{manifest['entry_point']}"
        try:
            module = importlib.import_module(module_path)
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
            
        except ImportError as e:
            logger.error(f"Failed to import UI plugin {plugin_name}: {e}")
    
    def _load_backend_plugin(self, plugin_name, plugin_path, manifest):
        """
        Load a backend service plugin with hooks
        """
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
                    return
        
        # Import backend plugin module
        module_path = f"plugins.{plugin_name}.{manifest['entry_point']}"
        try:
            module = importlib.import_module(module_path)
            
            # Check for create_plugin function
            if not hasattr(module, 'create_plugin'):
                logger.warning(f"Backend plugin {plugin_name} does not have a create_plugin function")
                return
                
            # Create plugin instance
            plugin = module.create_plugin(manifest["id"], manifest, self.registry)
            self.registry.register_plugin(manifest["id"], plugin)
            
            # Activate the plugin
            plugin.activate()
            
            # Trigger startup hook if available
            self.registry.invoke_hook(HOOK_STARTUP)
            
            logger.info(f"Successfully loaded backend plugin: {manifest['name']}")
        except Exception as e:
            logger.error(f"Error activating backend plugin {plugin_name}: {e}")
            return
    
    def execute_plugin(self, plugin_id, **kwargs):
        """
        Execute a UI plugin by its ID with the given parameters.
        """
        if plugin_id not in self.plugins:
            # Check if it's a backend plugin
            if BACKEND_PLUGINS_ENABLED and self.registry and plugin_id in self.registry.plugins:
                return self._execute_backend_plugin(plugin_id, **kwargs)
                
            logger.warning(f"Plugin {plugin_id} not found")
            return None
            
        try:
            plugin = self.plugins[plugin_id]
            result = plugin["module"].execute(**kwargs)
            return result
        except Exception as e:
            logger.error(f"Error executing plugin {plugin_id}: {e}")
            return {"error": str(e)}
            
    def _execute_backend_plugin(self, plugin_id, hook_name=None, **kwargs):
        """
        Execute a backend plugin by invoking a specific hook
        """
        if not BACKEND_PLUGINS_ENABLED or not self.registry:
            return {"error": "Backend plugin system not enabled"}
            
        if not hook_name:
            return {"error": "No hook specified for backend plugin"}
            
        try:
            # Invoke the specified hook
            results = self.registry.invoke_hook(hook_name, **kwargs)
            
            # Find the result for this specific plugin
            for result in results:
                if result['plugin_id'] == plugin_id:
                    if result['success']:
                        return result['result']
                    else:
                        return {"error": result.get('error', 'Unknown error')}
                        
            return {"error": f"Plugin {plugin_id} did not respond to hook {hook_name}"}
        except Exception as e:
            logger.error(f"Error executing backend plugin {plugin_id}: {e}")
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
