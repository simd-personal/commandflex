from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
from app.models.log import LogType

class LogResponse(BaseModel):
    id: int
    type: LogType
    message: str
    details: Optional[Dict[str, Any]] = None
    user_id: Optional[int] = None
    incident_id: Optional[int] = None
    unit_id: Optional[int] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

class LogList(BaseModel):
    logs: List[LogResponse]
    total: int
    page: int
    size: int 