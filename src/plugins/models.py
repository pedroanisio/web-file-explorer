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