from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from app.models.unit import UnitType, UnitStatus

class UnitBase(BaseModel):
    unit_number: str
    type: UnitType
    description: Optional[str] = None

class UnitCreate(UnitBase):
    pass

class UnitUpdate(BaseModel):
    unit_number: Optional[str] = None
    type: Optional[UnitType] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None

class UnitStatusUpdate(BaseModel):
    status: UnitStatus
    latitude: Optional[float] = None
    longitude: Optional[float] = None

class UnitResponse(UnitBase):
    id: int
    status: UnitStatus
    current_latitude: Optional[float] = None
    current_longitude: Optional[float] = None
    last_location_update: Optional[datetime] = None
    assigned_incident_id: Optional[int] = None
    assigned_user_id: Optional[int] = None
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class UnitList(BaseModel):
    units: List[UnitResponse]
    total: int
    page: int
    size: int 