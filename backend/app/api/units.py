from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.core.database import get_db
from app.core.auth import get_current_user, require_role
from app.models.user import User, UserRole
from app.models.unit import Unit, UnitStatus, UnitType
from app.models.log import Log, LogType
from app.schemas.unit import UnitCreate, UnitUpdate, UnitResponse, UnitList, UnitStatusUpdate
from app.schemas.log import LogCreate
from app.services.logging import create_log

router = APIRouter(prefix="/units", tags=["units"])

@router.post("/", response_model=UnitResponse)
async def create_unit(
    unit: UnitCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.dispatcher]))
):
    """Create a new unit (Dispatcher only)"""
    # Check if unit name already exists
    existing_unit = db.query(Unit).filter(Unit.name == unit.name).first()
    if existing_unit:
        raise HTTPException(status_code=400, detail="Unit name already exists")
    
    db_unit = Unit(
        name=unit.name,
        responder_id=unit.responder_id,
        status=UnitStatus.available
    )
    db.add(db_unit)
    db.commit()
    db.refresh(db_unit)
    
    return db_unit

@router.get("/", response_model=UnitList)
async def get_units(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[UnitStatus] = None,
    type: Optional[UnitType] = None,
    db: Session = Depends(get_db)
):
    """Get list of units with optional filtering"""
    query = db.query(Unit)
    
    if status:
        query = query.filter(Unit.status == status)
    if type:
        query = query.filter(Unit.type == type)
    
    total = query.count()
    units = query.offset(skip).limit(limit).all()
    
    return UnitList(
        units=[UnitResponse.from_orm(unit) for unit in units],
        total=total,
        page=skip // limit + 1,
        size=limit
    )

@router.get("/available", response_model=List[UnitResponse])
async def get_available_units(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.dispatcher]))
):
    """Get all available units (Dispatcher only)"""
    units = db.query(Unit).filter(Unit.status == UnitStatus.available).order_by(Unit.name).all()
    return units

@router.get("/{unit_id}", response_model=UnitResponse)
async def get_unit(
    unit_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get unit details"""
    unit = db.query(Unit).filter(Unit.id == unit_id).first()
    if not unit:
        raise HTTPException(status_code=404, detail="Unit not found")
    return unit

@router.patch("/{unit_id}", response_model=UnitResponse)
async def update_unit(
    unit_id: int,
    unit_update: UnitUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.dispatcher]))
):
    """Update unit details (Dispatcher only)"""
    unit = db.query(Unit).filter(Unit.id == unit_id).first()
    if not unit:
        raise HTTPException(status_code=404, detail="Unit not found")
    
    update_data = unit_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(unit, field, value)
    
    unit.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(unit)
    
    return unit

@router.patch("/{unit_id}/status", response_model=UnitResponse)
async def update_unit_status(
    unit_id: int,
    status_update: UnitStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.responder]))
):
    """Update unit status (Responder only)"""
    unit = db.query(Unit).filter(Unit.id == unit_id).first()
    if not unit:
        raise HTTPException(status_code=404, detail="Unit not found")
    
    # Verify the user is assigned to this unit
    if unit.responder_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this unit")
    
    old_status = unit.status
    unit.status = status_update.status
    unit.updated_at = datetime.utcnow()
    
    # Create status change log
    status_log = Log(
        incident_id=unit.incident_id,
        unit_id=unit.id,
        type=LogType.status,
        message=f"Unit {unit.name} status changed from {old_status} to {status_update.status}"
    )
    db.add(status_log)
    
    # Add notes if provided
    if status_update.notes:
        note_log = Log(
            incident_id=unit.incident_id,
            unit_id=unit.id,
            type=LogType.note,
            message=f"Status update notes: {status_update.notes}"
        )
        db.add(note_log)
    
    db.commit()
    db.refresh(unit)
    
    return unit

@router.post("/{unit_id}/arrive", response_model=UnitResponse)
async def unit_arrive_on_scene(
    unit_id: int,
    notes: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.responder]))
):
    """Mark unit as arrived on scene (Responder only)"""
    unit = db.query(Unit).filter(Unit.id == unit_id).first()
    if not unit:
        raise HTTPException(status_code=404, detail="Unit not found")
    
    if unit.responder_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this unit")
    
    if not unit.incident_id:
        raise HTTPException(status_code=400, detail="Unit is not assigned to an incident")
    
    unit.status = UnitStatus.on_scene
    unit.updated_at = datetime.utcnow()
    
    # Create arrival log
    arrival_log = Log(
        incident_id=unit.incident_id,
        unit_id=unit.id,
        type=LogType.arrival,
        message=f"Unit {unit.name} arrived on scene"
    )
    db.add(arrival_log)
    
    # Add notes if provided
    if notes:
        note_log = Log(
            incident_id=unit.incident_id,
            unit_id=unit.id,
            type=LogType.note,
            message=f"Arrival notes: {notes}"
        )
        db.add(note_log)
    
    db.commit()
    db.refresh(unit)
    
    return unit

@router.post("/{unit_id}/clear", response_model=UnitResponse)
async def unit_clear_scene(
    unit_id: int,
    resolution_code: str,
    notes: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.responder]))
):
    """Mark unit as cleared from scene (Responder only)"""
    unit = db.query(Unit).filter(Unit.id == unit_id).first()
    if not unit:
        raise HTTPException(status_code=404, detail="Unit not found")
    
    if unit.responder_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this unit")
    
    if not unit.incident_id:
        raise HTTPException(status_code=400, detail="Unit is not assigned to an incident")
    
    unit.status = UnitStatus.available
    unit.incident_id = None
    unit.updated_at = datetime.utcnow()
    
    # Create clear log
    clear_log = Log(
        incident_id=unit.incident_id,
        unit_id=unit.id,
        type=LogType.status,
        message=f"Unit {unit.name} cleared scene - Resolution: {resolution_code}"
    )
    db.add(clear_log)
    
    # Add notes if provided
    if notes:
        note_log = Log(
            incident_id=unit.incident_id,
            unit_id=unit.id,
            type=LogType.note,
            message=f"Clear notes: {notes}"
        )
        db.add(note_log)
    
    db.commit()
    db.refresh(unit)
    
    return unit

@router.delete("/{unit_id}")
async def delete_unit(
    unit_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a unit (soft delete by setting is_active to False)"""
    db_unit = db.query(Unit).filter(Unit.id == unit_id).first()
    if not db_unit:
        raise HTTPException(status_code=404, detail="Unit not found")
    
    # Soft delete
    db_unit.is_active = False
    db.commit()
    
    # Log the deletion
    await create_log(
        db=db,
        log_type="system_event",
        message=f"Unit {db_unit.name} deactivated by {current_user.username}",
        user_id=current_user.id,
        unit_id=db_unit.id
    )
    
    return {"message": "Unit deactivated successfully"} 