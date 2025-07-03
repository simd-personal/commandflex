from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
from app.models.log import LogType

class LogType(str, Enum):
    status = "status"
    note = "note"
    dispatch = "dispatch"
    arrival = "arrival"
    resolution = "resolution"

class LogCreate(BaseModel):
    incident_id: int = Field(..., description="ID of the incident")
    unit_id: Optional[int] = Field(None, description="ID of the unit involved")
    type: LogType = Field(..., description="Type of log entry")
    message: str = Field(..., description="Log message")

class LogResponse(BaseModel):
    id: int
    incident_id: int
    unit_id: Optional[int]
    type: LogType
    message: str
    timestamp: datetime

    class Config:
        from_attributes = True

class TimelineEntry(BaseModel):
    id: int
    type: LogType
    message: str
    timestamp: datetime
    unit_name: Optional[str] = None

    class Config:
        from_attributes = True

class LogList(BaseModel):
    logs: List[LogResponse]
    total: int
    page: int
    size: int 