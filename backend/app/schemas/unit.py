from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum
from backend.app.models.unit import UnitType, UnitStatus

class UnitStatus(str, Enum):
    available = "available"
    en_route = "en_route"
    on_scene = "on_scene"
    unavailable = "unavailable"

class UnitBase(BaseModel):
    unit_number: str
    type: UnitType
    description: Optional[str] = None

class UnitCreate(BaseModel):
    name: str = Field(..., description="Unit name/number (e.g., 'A12')")
    responder_id: Optional[int] = Field(None, description="ID of assigned responder")

class UnitUpdate(BaseModel):
    status: Optional[UnitStatus] = None
    responder_id: Optional[int] = None
    incident_id: Optional[int] = None

class UnitStatusUpdate(BaseModel):
    status: UnitStatus = Field(..., description="New unit status")
    notes: Optional[str] = Field(None, description="Optional notes about status change")

class UnitResponse(BaseModel):
    id: int
    name: str
    status: UnitStatus
    responder_id: Optional[int]
    incident_id: Optional[int]
    updated_at: datetime

    class Config:
        from_attributes = True

class UnitList(BaseModel):
    units: List[UnitResponse]
    total: int
    page: int
    size: int

class UnitAssignment(BaseModel):
    incident_id: int = Field(..., description="ID of incident to assign unit to")
    notes: Optional[str] = Field(None, description="Optional dispatch notes") 