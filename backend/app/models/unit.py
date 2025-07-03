from sqlalchemy import Column, Integer, String, Enum, DateTime, Float, Boolean, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base
import enum

class UnitType(str, enum.Enum):
    POLICE = "police"
    FIRE = "fire"
    EMS = "ems"
    SPECIAL = "special"

class UnitStatus(str, enum.Enum):
    AVAILABLE = "available"
    EN_ROUTE = "en_route"
    ON_SCENE = "on_scene"
    CLEARED = "cleared"
    OUT_OF_SERVICE = "out_of_service"

class Unit(Base):
    __tablename__ = "units"
    
    id = Column(Integer, primary_key=True, index=True)
    unit_number = Column(String, unique=True, index=True, nullable=False)
    type = Column(Enum(UnitType), nullable=False)
    status = Column(Enum(UnitStatus), default=UnitStatus.AVAILABLE)
    
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
    updated_at = Column(DateTime(timezone=True), onupdate=func.now()) 