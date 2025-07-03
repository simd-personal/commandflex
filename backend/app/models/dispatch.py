from sqlalchemy import Column, Integer, String, Enum, DateTime, Text, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from backend.app.core.database import Base
import enum

class DispatchStatus(str, enum.Enum):
    DISPATCHED = "dispatched"
    EN_ROUTE = "en_route"
    ON_SCENE = "on_scene"
    CLEARED = "cleared"
    CANCELLED = "cancelled"

class Dispatch(Base):
    __tablename__ = "dispatches"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Relationships
    incident_id = Column(Integer, ForeignKey("incidents.id"), nullable=False)
    unit_id = Column(Integer, ForeignKey("units.id"), nullable=False)
    dispatched_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Status tracking
    status = Column(Enum(DispatchStatus), default=DispatchStatus.DISPATCHED)
    
    # Timestamps
    dispatch_time = Column(DateTime(timezone=True), server_default=func.now())
    en_route_time = Column(DateTime(timezone=True), nullable=True)
    on_scene_time = Column(DateTime(timezone=True), nullable=True)
    cleared_time = Column(DateTime(timezone=True), nullable=True)
    
    # Notes
    dispatch_notes = Column(Text, nullable=True)
    arrival_notes = Column(Text, nullable=True)
    clearance_notes = Column(Text, nullable=True)
    
    # Relationships
    incident = relationship("Incident", back_populates="assigned_units")
    unit = relationship("Unit")
    dispatcher = relationship("User", foreign_keys=[dispatched_by]) 