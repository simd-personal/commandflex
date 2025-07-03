from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from backend.app.models.dispatch import DispatchStatus

class DispatchBase(BaseModel):
    incident_id: int
    unit_id: int
    dispatch_notes: Optional[str] = None

class DispatchCreate(DispatchBase):
    pass

class DispatchUpdate(BaseModel):
    status: Optional[DispatchStatus] = None
    arrival_notes: Optional[str] = None
    clearance_notes: Optional[str] = None

class DispatchResponse(DispatchBase):
    id: int
    dispatched_by: int
    status: DispatchStatus
    dispatch_time: datetime
    en_route_time: Optional[datetime] = None
    on_scene_time: Optional[datetime] = None
    cleared_time: Optional[datetime] = None
    arrival_notes: Optional[str] = None
    clearance_notes: Optional[str] = None
    
    class Config:
        from_attributes = True 