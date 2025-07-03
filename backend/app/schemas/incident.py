from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum
from backend.app.models.incident import IncidentType, IncidentPriority, IncidentStatus

class IncidentStatus(str, Enum):
    new = "new"
    dispatched = "dispatched"
    on_scene = "on_scene"
    resolved = "resolved"

class IncidentBase(BaseModel):
    type: IncidentType
    priority: IncidentPriority
    address: str
    description: str
    caller_name: Optional[str] = None
    caller_phone: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None

class IncidentCreate(BaseModel):
    type: str = Field(..., description="Type of incident (e.g., 'Armed Robbery')")
    priority: int = Field(..., ge=1, le=4, description="Priority level 1-4")
    location: str = Field(..., description="Address or location description")
    latitude: Optional[float] = Field(None, description="Latitude coordinate")
    longitude: Optional[float] = Field(None, description="Longitude coordinate")
    description: Optional[str] = Field(None, description="Detailed description of the incident")

class IncidentUpdate(BaseModel):
    type: Optional[str] = None
    priority: Optional[int] = Field(None, ge=1, le=4)
    location: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    description: Optional[str] = None
    status: Optional[IncidentStatus] = None
    notes: Optional[str] = None
    resolved_summary: Optional[str] = None

class IncidentResponse(BaseModel):
    id: int
    type: str
    priority: int
    location: str
    latitude: Optional[float]
    longitude: Optional[float]
    description: Optional[str]
    status: IncidentStatus
    created_at: datetime
    updated_at: datetime
    notes: Optional[str]
    resolved_summary: Optional[str]

    class Config:
        from_attributes = True

class IncidentList(BaseModel):
    id: int
    type: str
    priority: int
    location: str
    status: IncidentStatus
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class IncidentResolve(BaseModel):
    summary: str = Field(..., description="Final resolution summary")
    resolution_code: Optional[str] = Field(None, description="Resolution code (e.g., 'suspect_arrested')") 