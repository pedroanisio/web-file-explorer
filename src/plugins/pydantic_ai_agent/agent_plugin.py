"""
PydanticAI Agent plugin for FIXIT.
Provides AI-powered code analysis and assistance.
"""
import os
import logging
import pkg_resources
from typing import Dict, Any, List, Optional

# Import PydanticAI
try:
    from pydantic_ai import Agent
    from pydantic_ai.tools import FunctionTool
    from pydantic import BaseModel
    
    # Try to verify version compatibility
    import pkg_resources
    installed_version = pkg_resources.get_distribution("pydantic-ai").version
    
    # Define Pydantic models
    class AnalysisResult(BaseModel):
        """Result of file analysis by PydanticAI agent"""
        issues: List[Dict[str, Any]]
        suggestions: List[Dict[str, Any]]
        summary: str
        
    PYDANTIC_AI_AVAILABLE = True
    PYDANTIC_AI_VERSION = installed_version
except (ImportError, pkg_resources.DistributionNotFound, AttributeError) as e:
    PYDANTIC_AI_AVAILABLE = False
    PYDANTIC_AI_VERSION = None
    # Define a placeholder for when pydantic is not available
    AnalysisResult = None

# Import custom tools
from .tools import file_tools, code_tools
from .prompts import system_prompts

# Setup logging
logger = logging.getLogger("pydantic_ai_plugin")

def create_plugin(plugin_id, manifest, registry):
    """Create the PydanticAI agent plugin instance"""
    return PydanticAIAgentPlugin(plugin_id, manifest, registry)

class PydanticAIAgentPlugin:
    """
    PydanticAI Agent plugin for code analysis and assistance
    """
    
    def __init__(self, plugin_id, manifest, registry):
        self.plugin_id = plugin_id
        self.manifest = manifest
        self.registry = registry
        self.agent = None
        
    def activate(self):
        """Initialize and activate the PydanticAI agent"""
        if not PYDANTIC_AI_AVAILABLE:
            logger.error(f"PydanticAI required features not available. The package may be missing or installed version is incompatible.")
            if PYDANTIC_AI_VERSION:
                logger.error(f"Installed version: {PYDANTIC_AI_VERSION} may not have all required features.")
            return
            
        settings = self.get_settings()
        
        # Set up API key from environment
        api_key_env = settings.get('api_key_env')
        if api_key_env and api_key_env in os.environ:
            api_key = os.environ[api_key_env]
        else:
            logger.warning(f"API key environment variable {api_key_env} not found")
            api_key = None
            
        # Initialize the PydanticAI agent
        try:
            self.agent = Agent(
                name="FIXIT Assistant",
                system_prompt=system_prompts.CODE_ANALYSIS_PROMPT,
                model=settings.get('model', 'gpt-4'),
                model_settings={
                    "temperature": settings.get('temperature', 0.7),
                    "max_tokens": settings.get('max_tokens', 4096)
                }
            )
            
            # Register tools with the agent
            self._register_tools()
            
            logger.info("PydanticAI agent initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize PydanticAI agent: {e}")
    
    def get_settings(self):
        """Return plugin settings"""
        return self.manifest.get('settings', {})
        
    def update_settings(self, settings):
        """Update plugin settings"""
        if 'settings' not in self.manifest:
            self.manifest['settings'] = {}
        self.manifest['settings'].update(settings)
    
    def on_startup(self):
        """Handle application startup"""
        logger.info("PydanticAI Agent plugin started")
    
    def on_query_handler(self, query, context=None):
        """Handle user queries using PydanticAI agent"""
        if not self.agent:
            return {"error": "Agent not initialized", "success": False}
            
        try:
            # Prepare context
            run_context = {
                "query": query,
                **(context or {})
            }
            
            # Run the agent
            result = self.agent.run_sync(query, context=run_context)
            
            return {
                "response": result.final_output,
                "reasoning": result.intermediate_steps,
                "success": True
            }
        except Exception as e:
            logger.error(f"Error running agent query: {e}")
            return {
                "error": str(e),
                "success": False
            }
    
    def on_file_processor(self, file_path, file_content, metadata=None):
        """Process file content using PydanticAI agent"""
        if not self.agent:
            return {"error": "Agent not initialized", "success": False}
        
        try:
            # Create file context
            file_context = {
                "path": file_path,
                "content": file_content,
                "metadata": metadata or {},
                "file_type": self._get_file_type(file_path)
            }
            
            # Create a specific task based on file type
            task = f"Analyze the {file_context['file_type']} file at {file_path} and provide detailed code insights"
            
            # Run the agent with file context
            result = self.agent.run_sync(task, context={"file": file_context})
            
            # Extract structured analysis if available
            analysis = self._parse_analysis(result.final_output)
            
            return {
                "analysis": analysis,
                "raw_output": result.final_output,
                "success": True
            }
        except Exception as e:
            logger.error(f"Error processing file with agent: {e}")
            return {
                "error": str(e),
                "success": False
            }
    
    def _register_tools(self):
        """Register tools with the PydanticAI agent"""
        if not self.agent:
            return
            
        # Register file tools
        self.agent.add_tool(
            FunctionTool.from_function(
                file_tools.read_file,
                name="read_file",
                description="Read content from a file"
            )
        )
        
        self.agent.add_tool(
            FunctionTool.from_function(
                file_tools.list_directory,
                name="list_directory",
                description="List contents of a directory"
            )
        )
        
        # Register code tools
        self.agent.add_tool(
            FunctionTool.from_function(
                code_tools.analyze_syntax,
                name="analyze_syntax",
                description="Analyze code syntax and structure"
            )
        )
        
        self.agent.add_tool(
            FunctionTool.from_function(
                code_tools.suggest_improvements,
                name="suggest_improvements",
                description="Suggest code improvements"
            )
        )
    
    def _get_file_type(self, file_path):
        """Determine file type from extension"""
        ext = os.path.splitext(file_path)[1].lower()
        
        file_types = {
            '.py': 'Python',
            '.js': 'JavaScript',
            '.html': 'HTML',
            '.css': 'CSS',
            '.json': 'JSON',
            '.md': 'Markdown',
            '.txt': 'Text'
        }
        
        return file_types.get(ext, 'Unknown')
    
    def _parse_analysis(self, output):
        """Parse agent output to extract structured analysis"""
        try:
            # If output is already structured as JSON
            if isinstance(output, dict):
                return output
                
            # Attempt to extract structured data from the output
            # In a real implementation, this would be more robust
            issues = []
            suggestions = []
            summary = output
            
            # Simple parsing logic - in practice would be more robust
            if "Issues:" in output:
                issues_section = output.split("Issues:")[1].split("Suggestions:")[0]
                issues = [{"description": issue.strip()} 
                         for issue in issues_section.split("-") 
                         if issue.strip()]
                
            if "Suggestions:" in output:
                suggestions_section = output.split("Suggestions:")[1]
                suggestions = [{"description": sugg.strip()} 
                              for sugg in suggestions_section.split("-") 
                              if sugg.strip()]
            
            return {
                "issues": issues,
                "suggestions": suggestions,
                "summary": summary
            }
        except Exception as e:
            logger.warning(f"Failed to parse analysis: {e}")
            return {"summary": output}
