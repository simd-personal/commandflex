from sqlalchemy import Column, Integer, String, Enum, DateTime, Text, Float, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base
import enum

class IncidentType(str, enum.Enum):
    FIRE = "fire"
    MEDICAL = "medical"
    POLICE = "police"
    TRAFFIC = "traffic"
    OTHER = "other"

class IncidentPriority(str, enum.Enum):
    CRITICAL = "1"
    HIGH = "2"
    MODERATE = "3"
    LOW = "4"

class IncidentStatus(str, enum.Enum):
    NEW = "new"
    DISPATCHED = "dispatched"
    EN_ROUTE = "en_route"
    ON_SCENE = "on_scene"
    RESOLVED = "resolved"
    CANCELLED = "cancelled"

class Incident(Base):
    __tablename__ = "incidents"
    
    id = Column(Integer, primary_key=True, index=True)
    incident_number = Column(String, unique=True, index=True, nullable=False)
    type = Column(Enum(IncidentType), nullable=False)
    priority = Column(Enum(IncidentPriority), nullable=False)
    status = Column(Enum(IncidentStatus), default=IncidentStatus.NEW)
    
    # Location
    address = Column(String, nullable=False)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    
    # Details
    description = Column(Text, nullable=False)
    caller_name = Column(String, nullable=True)
    caller_phone = Column(String, nullable=True)
    
    # Assignment
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    assigned_units = relationship("Dispatch", back_populates="incident")
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    resolved_at = Column(DateTime(timezone=True), nullable=True) 