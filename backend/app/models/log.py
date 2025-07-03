from sqlalchemy import Column, Integer, String, Enum, DateTime, Text, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from backend.app.core.database import Base
import enum
from datetime import datetime

class LogType(str, enum.Enum):
    status = "status"
    note = "note"
    dispatch = "dispatch"
    arrival = "arrival"
    resolution = "resolution"

class Log(Base):
    __tablename__ = "logs"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Event details
    type = Column(Enum(LogType), default=LogType.status)
    message = Column(Text, nullable=False)
    details = Column(JSON, nullable=True)  # Additional structured data
    
    # Relationships
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    incident_id = Column(Integer, ForeignKey("incidents.id"), nullable=False)
    unit_id = Column(Integer, ForeignKey("units.id"), nullable=True)
    
    # Timestamp
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id])
    incident = relationship("Incident", foreign_keys=[incident_id], back_populates="timeline")
    unit = relationship("Unit", foreign_keys=[unit_id], back_populates="logs") 