"""
Code Dump plugin for FIXIT.
Outputs all code files in a directory while excluding common non-code files.
"""

from .dump_plugin import execute, get_config_template, save_plugin_config

__all__ = ['execute', 'get_config_template', 'save_plugin_config']
