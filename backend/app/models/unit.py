from sqlalchemy import Column, Integer, String, Enum, DateTime, Float, Boolean, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from backend.app.core.database import Base
import enum
from datetime import datetime

class UnitType(str, enum.Enum):
    POLICE = "police"
    FIRE = "fire"
    EMS = "ems"
    SPECIAL = "special"

class UnitStatus(str, enum.Enum):
    available = "available"
    en_route = "en_route"
    on_scene = "on_scene"
    unavailable = "unavailable"

class Unit(Base):
    __tablename__ = "units"
    
    id = Column(Integer, primary_key=True, index=True)
    unit_number = Column(String, unique=True, index=True, nullable=False)
    type = Column(Enum(UnitType), nullable=False)
    status = Column(Enum(UnitStatus), default=UnitStatus.available)
    
    # Location tracking
    current_latitude = Column(Float, nullable=True)
    current_longitude = Column(Float, nullable=True)
    last_location_update = Column(DateTime(timezone=True), nullable=True)
    
    # Assignment
    assigned_incident_id = Column(Integer, ForeignKey("incidents.id"), nullable=True)
    assigned_incident = relationship("Incident", foreign_keys=[assigned_incident_id])
    
    # Personnel
    assigned_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    assigned_user = relationship("User", foreign_keys=[assigned_user_id])
    
    # Details
    description = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    incident = relationship("Incident", back_populates="units")
    responder = relationship("User", back_populates="units")
    logs = relationship("Log", back_populates="unit") 