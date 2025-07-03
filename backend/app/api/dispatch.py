from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from backend.app.core.database import get_db
from backend.app.core.auth import get_current_active_user
from backend.app.models.user import User
from backend.app.models.incident import Incident, IncidentStatus
from backend.app.models.unit import Unit, UnitStatus
from backend.app.models.dispatch import Dispatch, DispatchStatus
from backend.app.schemas.dispatch import DispatchCreate, DispatchUpdate, DispatchResponse
from backend.app.services.logging import create_log

router = APIRouter()

@router.post("/", response_model=DispatchResponse)
async def create_dispatch(
    dispatch: DispatchCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Dispatch a unit to an incident"""
    # Check if incident exists
    incident = db.query(Incident).filter(Incident.id == dispatch.incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    
    # Check if unit exists and is available
    unit = db.query(Unit).filter(Unit.id == dispatch.unit_id).first()
    if not unit:
        raise HTTPException(status_code=404, detail="Unit not found")
    
    if unit.status != UnitStatus.AVAILABLE:
        raise HTTPException(status_code=400, detail="Unit is not available for dispatch")
    
    # Check if unit is already dispatched to this incident
    existing_dispatch = db.query(Dispatch).filter(
        Dispatch.incident_id == dispatch.incident_id,
        Dispatch.unit_id == dispatch.unit_id,
        Dispatch.status.in_([DispatchStatus.DISPATCHED, DispatchStatus.EN_ROUTE, DispatchStatus.ON_SCENE])
    ).first()
    
    if existing_dispatch:
        raise HTTPException(status_code=400, detail="Unit is already dispatched to this incident")
    
    # Create dispatch record
    db_dispatch = Dispatch(
        incident_id=dispatch.incident_id,
        unit_id=dispatch.unit_id,
        dispatched_by=current_user.id,
        dispatch_notes=dispatch.dispatch_notes
    )
    
    # Update unit status and assignment
    unit.status = UnitStatus.EN_ROUTE
    unit.assigned_incident_id = dispatch.incident_id
    
    # Update incident status
    if incident.status == IncidentStatus.NEW:
        incident.status = IncidentStatus.DISPATCHED
    
    db.add(db_dispatch)
    db.commit()
    db.refresh(db_dispatch)
    
    # Log the dispatch
    await create_log(
        db=db,
        log_type="unit_dispatched",
        message=f"Unit {unit.unit_number} dispatched to incident {incident.incident_number} by {current_user.username}",
        user_id=current_user.id,
        incident_id=incident.id,
        unit_id=unit.id,
        details={
            "incident_number": incident.incident_number,
            "unit_number": unit.unit_number,
            "dispatch_notes": dispatch.dispatch_notes
        }
    )
    
    return DispatchResponse.from_orm(db_dispatch)

@router.get("/incident/{incident_id}", response_model=List[DispatchResponse])
async def get_incident_dispatches(
    incident_id: int,
    db: Session = Depends(get_db)
):
    """Get all dispatches for a specific incident"""
    dispatches = db.query(Dispatch).filter(Dispatch.incident_id == incident_id).all()
    return [DispatchResponse.from_orm(dispatch) for dispatch in dispatches]

@router.get("/unit/{unit_id}", response_model=List[DispatchResponse])
async def get_unit_dispatches(
    unit_id: int,
    db: Session = Depends(get_db)
):
    """Get all dispatches for a specific unit"""
    dispatches = db.query(Dispatch).filter(Dispatch.unit_id == unit_id).all()
    return [DispatchResponse.from_orm(dispatch) for dispatch in dispatches]

@router.patch("/{dispatch_id}", response_model=DispatchResponse)
async def update_dispatch(
    dispatch_id: int,
    dispatch_update: DispatchUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update dispatch status"""
    db_dispatch = db.query(Dispatch).filter(Dispatch.id == dispatch_id).first()
    if not db_dispatch:
        raise HTTPException(status_code=404, detail="Dispatch not found")
    
    # Get related records
    unit = db.query(Unit).filter(Unit.id == db_dispatch.unit_id).first()
    incident = db.query(Incident).filter(Incident.id == db_dispatch.incident_id).first()
    
    # Update dispatch status and timestamps
    if dispatch_update.status:
        old_status = db_dispatch.status
        db_dispatch.status = dispatch_update.status
        
        # Update timestamps based on status
        if dispatch_update.status == DispatchStatus.EN_ROUTE and not db_dispatch.en_route_time:
            db_dispatch.en_route_time = datetime.utcnow()
        elif dispatch_update.status == DispatchStatus.ON_SCENE and not db_dispatch.on_scene_time:
            db_dispatch.on_scene_time = datetime.utcnow()
        elif dispatch_update.status == DispatchStatus.CLEARED and not db_dispatch.cleared_time:
            db_dispatch.cleared_time = datetime.utcnow()
            
            # Update unit status to available
            if unit:
                unit.status = UnitStatus.AVAILABLE
                unit.assigned_incident_id = None
    
    # Update notes
    if dispatch_update.arrival_notes:
        db_dispatch.arrival_notes = dispatch_update.arrival_notes
    if dispatch_update.clearance_notes:
        db_dispatch.clearance_notes = dispatch_update.clearance_notes
    
    db.commit()
    db.refresh(db_dispatch)
    
    # Log the status update
    if dispatch_update.status:
        await create_log(
            db=db,
            log_type="unit_status_changed",
            message=f"Dispatch status changed from {old_status.value} to {dispatch_update.status.value} by {current_user.username}",
            user_id=current_user.id,
            incident_id=incident.id if incident else None,
            unit_id=unit.id if unit else None,
            details={
                "old_status": old_status.value,
                "new_status": dispatch_update.status.value,
                "dispatch_id": dispatch_id
            }
        )
    
    return DispatchResponse.from_orm(db_dispatch)

@router.delete("/{dispatch_id}")
async def cancel_dispatch(
    dispatch_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Cancel a dispatch"""
    db_dispatch = db.query(Dispatch).filter(Dispatch.id == dispatch_id).first()
    if not db_dispatch:
        raise HTTPException(status_code=404, detail="Dispatch not found")
    
    # Get related records
    unit = db.query(Unit).filter(Unit.id == db_dispatch.unit_id).first()
    incident = db.query(Incident).filter(Incident.id == db_dispatch.incident_id).first()
    
    # Cancel dispatch
    db_dispatch.status = DispatchStatus.CANCELLED
    
    # Update unit status if it was assigned to this incident
    if unit and unit.assigned_incident_id == db_dispatch.incident_id:
        unit.status = UnitStatus.AVAILABLE
        unit.assigned_incident_id = None
    
    db.commit()
    
    # Log the cancellation
    await create_log(
        db=db,
        log_type="unit_dispatched",
        message=f"Dispatch cancelled by {current_user.username}",
        user_id=current_user.id,
        incident_id=incident.id if incident else None,
        unit_id=unit.id if unit else None,
        details={
            "dispatch_id": dispatch_id,
            "action": "cancelled"
        }
    )
    
    return {"message": "Dispatch cancelled successfully"} 