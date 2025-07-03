from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import uuid

from backend.app.core.database import get_db
from backend.app.core.auth import get_current_active_user, require_role
from backend.app.models.user import User, UserRole
from backend.app.models.incident import Incident, IncidentStatus, IncidentType, IncidentPriority
from backend.app.models.unit import Unit, UnitStatus
from backend.app.models.log import Log, LogType
from backend.app.schemas.incident import IncidentCreate, IncidentUpdate, IncidentResponse, IncidentList, IncidentResolve
from backend.app.schemas.unit import UnitAssignment
from backend.app.schemas.log import LogCreate, TimelineEntry
from backend.app.services.logging import create_log

router = APIRouter(prefix="/incidents", tags=["incidents"])

def generate_incident_number() -> str:
    """Generate a unique incident number"""
    timestamp = datetime.now().strftime("%Y%m%d")
    unique_id = str(uuid.uuid4())[:8].upper()
    return f"INC-{timestamp}-{unique_id}"

@router.post("/", response_model=IncidentResponse)
async def create_incident(
    incident: IncidentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.dispatcher]))
):
    """Create a new incident (Dispatcher only)"""
    db_incident = Incident(
        type=incident.type,
        priority=incident.priority,
        location=incident.location,
        latitude=incident.latitude,
        longitude=incident.longitude,
        description=incident.description,
        status=IncidentStatus.new
    )
    db.add(db_incident)
    db.commit()
    db.refresh(db_incident)
    
    # Create initial log entry
    log = Log(
        incident_id=db_incident.id,
        type=LogType.status,
        message=f"Incident created: {incident.type} at {incident.location}"
    )
    db.add(log)
    db.commit()
    
    return db_incident

@router.get("/", response_model=List[IncidentList])
async def list_incidents(
    status: Optional[IncidentStatus] = None,
    priority: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """List incidents with optional filtering"""
    query = db.query(Incident)
    
    if status:
        query = query.filter(Incident.status == status)
    if priority:
        query = query.filter(Incident.priority == priority)
    
    incidents = query.order_by(Incident.created_at.desc()).all()
    return incidents

@router.get("/{incident_id}", response_model=IncidentResponse)
async def get_incident(
    incident_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get incident details"""
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    return incident

@router.patch("/{incident_id}", response_model=IncidentResponse)
async def update_incident(
    incident_id: int,
    incident_update: IncidentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.dispatcher]))
):
    """Update incident details (Dispatcher only)"""
    db_incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not db_incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    
    update_data = incident_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_incident, field, value)
    
    db_incident.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_incident)
    
    return db_incident

@router.post("/{incident_id}/assign", response_model=IncidentResponse)
async def assign_unit(
    incident_id: int,
    assignment: UnitAssignment,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.dispatcher]))
):
    """Assign a unit to an incident (Dispatcher only)"""
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    
    unit = db.query(Unit).filter(Unit.id == assignment.incident_id).first()
    if not unit:
        raise HTTPException(status_code=404, detail="Unit not found")
    
    if unit.status != UnitStatus.available:
        raise HTTPException(status_code=400, detail="Unit is not available")
    
    # Update unit assignment
    unit.incident_id = incident_id
    unit.status = UnitStatus.en_route
    unit.updated_at = datetime.utcnow()
    
    # Update incident status
    incident.status = IncidentStatus.dispatched
    incident.updated_at = datetime.utcnow()
    
    # Create log entries
    dispatch_log = Log(
        incident_id=incident_id,
        unit_id=unit.id,
        type=LogType.dispatch,
        message=f"Unit {unit.name} dispatched to incident"
    )
    db.add(dispatch_log)
    
    if assignment.notes:
        note_log = Log(
            incident_id=incident_id,
            unit_id=unit.id,
            type=LogType.note,
            message=f"Dispatch notes: {assignment.notes}"
        )
        db.add(note_log)
    
    db.commit()
    db.refresh(incident)
    
    return incident

@router.post("/{incident_id}/resolve", response_model=IncidentResponse)
async def resolve_incident(
    incident_id: int,
    resolution: IncidentResolve,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.dispatcher]))
):
    """Mark incident as resolved (Dispatcher only)"""
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    
    incident.status = IncidentStatus.resolved
    incident.resolved_summary = resolution.summary
    incident.updated_at = datetime.utcnow()
    
    # Free up assigned units
    for unit in incident.units:
        unit.incident_id = None
        unit.status = UnitStatus.available
        unit.updated_at = datetime.utcnow()
    
    # Create resolution log
    resolution_log = Log(
        incident_id=incident_id,
        type=LogType.resolution,
        message=f"Incident resolved: {resolution.summary}"
    )
    db.add(resolution_log)
    
    db.commit()
    db.refresh(incident)
    
    return incident

@router.get("/{incident_id}/timeline", response_model=List[TimelineEntry])
async def get_incident_timeline(
    incident_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get incident timeline/logs"""
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    
    logs = db.query(Log).filter(Log.incident_id == incident_id).order_by(Log.timestamp).all()
    
    timeline = []
    for log in logs:
        unit_name = None
        if log.unit_id:
            unit = db.query(Unit).filter(Unit.id == log.unit_id).first()
            unit_name = unit.name if unit else None
        
        timeline.append(TimelineEntry(
            id=log.id,
            type=log.type,
            message=log.message,
            timestamp=log.timestamp,
            unit_name=unit_name
        ))
    
    return timeline

@router.post("/{incident_id}/notes")
async def add_incident_note(
    incident_id: int,
    note: LogCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Add a note to an incident"""
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    
    log = Log(
        incident_id=incident_id,
        unit_id=note.unit_id,
        type=LogType.note,
        message=note.message
    )
    db.add(log)
    db.commit()
    
    return {"message": "Note added successfully"}

@router.delete("/{incident_id}")
async def delete_incident(
    incident_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete an incident (soft delete by setting status to cancelled)"""
    db_incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not db_incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    
    # Soft delete by setting status to cancelled
    db_incident.status = IncidentStatus.CANCELLED
    db.commit()
    
    # Log the cancellation
    await create_log(
        db=db,
        log_type="incident_updated",
        message=f"Incident {db_incident.incident_number} cancelled by {current_user.username}",
        user_id=current_user.id,
        incident_id=db_incident.id,
        details={"status": "cancelled"}
    )
    
    return {"message": "Incident cancelled successfully"} 