"""
Plugin system for the file explorer.
"""
import os
import json
import importlib
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("plugin_system")

class PluginManager:
    """
    Manages the loading and execution of plugins.
    """
    def __init__(self, plugin_dir):
        self.plugin_dir = plugin_dir
        self.plugins = {}
        self.toolbar_items = []
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
            
            if not os.path.isdir(plugin_path):
                continue
                
            manifest_path = os.path.join(plugin_path, "manifest.json")
            if not os.path.exists(manifest_path):
                logger.warning(f"No manifest.json found in {plugin_path}")
                continue
                
            try:
                with open(manifest_path, 'r') as f:
                    manifest = json.load(f)
                
                # Check for required fields
                required_fields = ["id", "name", "version", "entry_point", "icon"]
                if not all(field in manifest for field in required_fields):
                    logger.warning(f"Manifest in {plugin_path} missing required fields")
                    continue
                
                module_path = f"plugins.{item}.{manifest['entry_point']}"
                try:
                    module = importlib.import_module(module_path)
                    if not hasattr(module, 'execute'):
                        logger.warning(f"Plugin {item} does not have an execute function")
                        continue
                        
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
                    
                    logger.info(f"Successfully loaded plugin: {manifest['name']}")
                    
                except ImportError as e:
                    logger.error(f"Failed to import plugin {item}: {e}")
                    
            except json.JSONDecodeError:
                logger.error(f"Invalid manifest.json in {plugin_path}")
    
    def execute_plugin(self, plugin_id, **kwargs):
        """
        Execute a plugin by its ID with the given parameters.
        """
        if plugin_id not in self.plugins:
            logger.warning(f"Plugin {plugin_id} not found")
            return None
            
        try:
            plugin = self.plugins[plugin_id]
            result = plugin["module"].execute(**kwargs)
            return result
        except Exception as e:
            logger.error(f"Error executing plugin {plugin_id}: {e}")
            return {"error": str(e)}
    
    def get_toolbar_items(self):
        """
        Get all toolbar items for the UI.
        """
        return self.toolbar_items
