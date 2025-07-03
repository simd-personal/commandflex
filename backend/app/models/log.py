from sqlalchemy import Column, Integer, String, Enum, DateTime, Text, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base
import enum

class LogType(str, enum.Enum):
    INCIDENT_CREATED = "incident_created"
    INCIDENT_UPDATED = "incident_updated"
    INCIDENT_RESOLVED = "incident_resolved"
    UNIT_DISPATCHED = "unit_dispatched"
    UNIT_STATUS_CHANGED = "unit_status_changed"
    UNIT_LOCATION_UPDATED = "unit_location_updated"
    USER_LOGIN = "user_login"
    USER_LOGOUT = "user_logout"
    SYSTEM_EVENT = "system_event"

class Log(Base):
    __tablename__ = "logs"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Event details
    type = Column(Enum(LogType), nullable=False)
    message = Column(Text, nullable=False)
    details = Column(JSON, nullable=True)  # Additional structured data
    
    # Relationships
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    incident_id = Column(Integer, ForeignKey("incidents.id"), nullable=True)
    unit_id = Column(Integer, ForeignKey("units.id"), nullable=True)
    
    # Timestamp
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id])
    incident = relationship("Incident", foreign_keys=[incident_id])
    unit = relationship("Unit", foreign_keys=[unit_id]) 