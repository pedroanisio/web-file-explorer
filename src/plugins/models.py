from typing import List, Dict, Any, Literal
from pydantic import BaseModel, Field


class PluginManifest(BaseModel):
    """Schema for a plugin's manifest.json file."""

    id: str
    name: str
    version: str
    entry_point: str
    # ui (default) or backend
    type: Literal["ui", "backend"] = "ui"

    # Optional UI fields
    icon: str | None = None
    description: str | None = None

    # Runtime behaviour / requirements
    dependencies: List[str] = Field(default_factory=list)
    auto_install_dependencies: bool = False
    hooks: List[str] = Field(default_factory=list)

    # Arbitrary user-defined settings block
    settings: Dict[str, Any] = Field(default_factory=dict)
    
    # V2 Fields - Simple and focused
    schema_version: Literal["1.0", "2.0"] = "1.0"
    supports_page_mode: bool = False  # Simple flag to enable page mode
    page_title: str | None = None     # Optional custom page title 