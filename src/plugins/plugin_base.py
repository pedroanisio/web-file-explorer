"""
Base plugin system for the FIXIT application.
Provides infrastructure for backend plugins with hook system.
"""
import logging
from collections import defaultdict
from typing import Dict, List, Any, Callable, Optional

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("plugin_system")

class PluginRegistry:
    """
    Central registry for all backend plugins with lifecycle management
    """
    def __init__(self):
        self.plugins = {}
        self.hook_registry = defaultdict(list)
        
    def register_plugin(self, plugin_id, plugin_instance):
        """Register a plugin in the registry"""
        self.plugins[plugin_id] = plugin_instance
        logger.info(f"Registered plugin: {plugin_id}")
        
    def register_hook(self, hook_name, plugin_id, callback):
        """Register a hook callback for a specific plugin"""
        self.hook_registry[hook_name].append({
            'plugin_id': plugin_id,
            'callback': callback
        })
        logger.info(f"Registered hook '{hook_name}' for plugin '{plugin_id}'")
        
    def invoke_hook(self, hook_name, *args, **kwargs):
        """Invoke all callbacks registered for a hook"""
        results = []
        for handler in self.hook_registry.get(hook_name, []):
            try:
                result = handler['callback'](*args, **kwargs)
                results.append({
                    'plugin_id': handler['plugin_id'],
                    'result': result,
                    'success': True
                })
            except Exception as e:
                logger.error(f"Error invoking hook '{hook_name}' for plugin '{handler['plugin_id']}': {e}")
                results.append({
                    'plugin_id': handler['plugin_id'],
                    'error': str(e),
                    'success': False
                })
        return results
    
    def get_plugin(self, plugin_id):
        """Get a plugin by ID"""
        return self.plugins.get(plugin_id)
    
    def get_all_plugins(self):
        """Get all registered plugins"""
        return self.plugins

class BackendPlugin:
    """Base class for all backend plugins"""
    
    def __init__(self, plugin_id, manifest, registry):
        self.plugin_id = plugin_id
        self.manifest = manifest
        self.registry = registry
        self._initialize()
        
    def _initialize(self):
        """Register hooks defined in manifest"""
        for hook_name in self.manifest.get('hooks', []):
            if hasattr(self, f"on_{hook_name}"):
                self.registry.register_hook(
                    hook_name,
                    self.plugin_id,
                    getattr(self, f"on_{hook_name}")
                )
    
    def activate(self):
        """Called when the plugin is activated"""
        pass
        
    def deactivate(self):
        """Called before the plugin is deactivated"""
        pass
        
    def get_settings(self):
        """Return plugin settings"""
        return self.manifest.get('settings', {})
        
    def update_settings(self, settings):
        """Update plugin settings"""
        if 'settings' not in self.manifest:
            self.manifest['settings'] = {}
        self.manifest['settings'].update(settings)

# Available hooks
HOOK_FILE_PROCESSOR = "file_processor"     # Process file content
HOOK_QUERY_HANDLER = "query_handler"       # Handle user queries
HOOK_STARTUP = "startup"                   # Called on application startup
HOOK_SHUTDOWN = "shutdown"                 # Called before application shutdown
HOOK_CONTENT_TRANSFORM = "transform"       # Transform content
HOOK_AUTHENTICATION = "authentication"     # Custom auth handlers
