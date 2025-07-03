from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import uuid

from app.core.database import get_db
from app.core.auth import get_current_active_user
from app.models.user import User
from app.models.incident import Incident, IncidentStatus, IncidentType, IncidentPriority
from app.schemas.incident import IncidentCreate, IncidentUpdate, IncidentResponse, IncidentList
from app.services.logging import create_log

router = APIRouter()

def generate_incident_number() -> str:
    """Generate a unique incident number"""
    timestamp = datetime.now().strftime("%Y%m%d")
    unique_id = str(uuid.uuid4())[:8].upper()
    return f"INC-{timestamp}-{unique_id}"

@router.post("/", response_model=IncidentResponse)
async def create_incident(
    incident: IncidentCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new incident"""
    incident_number = generate_incident_number()
    
    db_incident = Incident(
        incident_number=incident_number,
        type=incident.type,
        priority=incident.priority,
        address=incident.address,
        description=incident.description,
        caller_name=incident.caller_name,
        caller_phone=incident.caller_phone,
        latitude=incident.latitude,
        longitude=incident.longitude,
        created_by=current_user.id
    )
    
    db.add(db_incident)
    db.commit()
    db.refresh(db_incident)
    
    # Log the incident creation
    await create_log(
        db=db,
        log_type="incident_created",
        message=f"Incident {incident_number} created by {current_user.username}",
        user_id=current_user.id,
        incident_id=db_incident.id,
        details={
            "incident_number": incident_number,
            "type": incident.type.value,
            "priority": incident.priority.value,
            "address": incident.address
        }
    )
    
    return IncidentResponse.from_orm(db_incident)

@router.get("/", response_model=IncidentList)
async def get_incidents(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[IncidentStatus] = None,
    type: Optional[IncidentType] = None,
    priority: Optional[IncidentPriority] = None,
    db: Session = Depends(get_db)
):
    """Get list of incidents with optional filtering"""
    query = db.query(Incident)
    
    if status:
        query = query.filter(Incident.status == status)
    if type:
        query = query.filter(Incident.type == type)
    if priority:
        query = query.filter(Incident.priority == priority)
    
    total = query.count()
    incidents = query.offset(skip).limit(limit).all()
    
    return IncidentList(
        incidents=[IncidentResponse.from_orm(incident) for incident in incidents],
        total=total,
        page=skip // limit + 1,
        size=limit
    )

@router.get("/{incident_id}", response_model=IncidentResponse)
async def get_incident(
    incident_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific incident by ID"""
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    
    return IncidentResponse.from_orm(incident)

@router.patch("/{incident_id}", response_model=IncidentResponse)
async def update_incident(
    incident_id: int,
    incident_update: IncidentUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update an incident"""
    db_incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not db_incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    
    # Update fields
    update_data = incident_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_incident, field, value)
    
    # Set resolved timestamp if status is resolved
    if incident_update.status == IncidentStatus.RESOLVED:
        db_incident.resolved_at = datetime.utcnow()
    
    db.commit()
    db.refresh(db_incident)
    
    # Log the update
    await create_log(
        db=db,
        log_type="incident_updated",
        message=f"Incident {db_incident.incident_number} updated by {current_user.username}",
        user_id=current_user.id,
        incident_id=db_incident.id,
        details=update_data
    )
    
    return IncidentResponse.from_orm(db_incident)

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