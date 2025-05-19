from typing import Dict, Any
from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    """Schema for /api/plugins/{plugin_id}/query POST body."""

    query: str = ""
    context: Dict[str, Any] = Field(default_factory=dict)


class ProcessRequest(BaseModel):
    """Schema for /api/plugins/{plugin_id}/process POST body."""

    path: str
    metadata: Dict[str, Any] = Field(default_factory=dict) 