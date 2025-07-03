from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from app.models.incident import IncidentType, IncidentPriority, IncidentStatus

class IncidentBase(BaseModel):
    type: IncidentType
    priority: IncidentPriority
    address: str
    description: str
    caller_name: Optional[str] = None
    caller_phone: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None

class IncidentCreate(IncidentBase):
    pass

class IncidentUpdate(BaseModel):
    type: Optional[IncidentType] = None
    priority: Optional[IncidentPriority] = None
    status: Optional[IncidentStatus] = None
    address: Optional[str] = None
    description: Optional[str] = None
    caller_name: Optional[str] = None
    caller_phone: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None

class IncidentResponse(IncidentBase):
    id: int
    incident_number: str
    status: IncidentStatus
    created_by: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class IncidentList(BaseModel):
    incidents: List[IncidentResponse]
    total: int
    page: int
    size: int 