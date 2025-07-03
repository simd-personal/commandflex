from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.core.database import get_db
from app.core.auth import get_current_active_user
from app.models.user import User
from app.models.unit import Unit, UnitStatus, UnitType
from app.schemas.unit import UnitCreate, UnitUpdate, UnitResponse, UnitList, UnitStatusUpdate
from app.services.logging import create_log

router = APIRouter()

@router.post("/", response_model=UnitResponse)
async def create_unit(
    unit: UnitCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new unit"""
    # Check if unit number already exists
    existing_unit = db.query(Unit).filter(Unit.unit_number == unit.unit_number).first()
    if existing_unit:
        raise HTTPException(status_code=400, detail="Unit number already exists")
    
    db_unit = Unit(
        unit_number=unit.unit_number,
        type=unit.type,
        description=unit.description
    )
    
    db.add(db_unit)
    db.commit()
    db.refresh(db_unit)
    
    # Log the unit creation
    await create_log(
        db=db,
        log_type="system_event",
        message=f"Unit {unit.unit_number} created by {current_user.username}",
        user_id=current_user.id,
        unit_id=db_unit.id,
        details={
            "unit_number": unit.unit_number,
            "type": unit.type.value,
            "description": unit.description
        }
    )
    
    return UnitResponse.from_orm(db_unit)

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
    type: Optional[UnitType] = None,
    db: Session = Depends(get_db)
):
    """Get list of available units for dispatch"""
    query = db.query(Unit).filter(Unit.status == UnitStatus.AVAILABLE, Unit.is_active == True)
    
    if type:
        query = query.filter(Unit.type == type)
    
    units = query.all()
    return [UnitResponse.from_orm(unit) for unit in units]

@router.get("/{unit_id}", response_model=UnitResponse)
async def get_unit(
    unit_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific unit by ID"""
    unit = db.query(Unit).filter(Unit.id == unit_id).first()
    if not unit:
        raise HTTPException(status_code=404, detail="Unit not found")
    
    return UnitResponse.from_orm(unit)

@router.patch("/{unit_id}", response_model=UnitResponse)
async def update_unit(
    unit_id: int,
    unit_update: UnitUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update a unit"""
    db_unit = db.query(Unit).filter(Unit.id == unit_id).first()
    if not db_unit:
        raise HTTPException(status_code=404, detail="Unit not found")
    
    # Update fields
    update_data = unit_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_unit, field, value)
    
    db.commit()
    db.refresh(db_unit)
    
    # Log the update
    await create_log(
        db=db,
        log_type="system_event",
        message=f"Unit {db_unit.unit_number} updated by {current_user.username}",
        user_id=current_user.id,
        unit_id=db_unit.id,
        details=update_data
    )
    
    return UnitResponse.from_orm(db_unit)

@router.patch("/{unit_id}/status", response_model=UnitResponse)
async def update_unit_status(
    unit_id: int,
    status_update: UnitStatusUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update unit status and location"""
    db_unit = db.query(Unit).filter(Unit.id == unit_id).first()
    if not db_unit:
        raise HTTPException(status_code=404, detail="Unit not found")
    
    # Update status and location
    db_unit.status = status_update.status
    if status_update.latitude is not None:
        db_unit.current_latitude = status_update.latitude
    if status_update.longitude is not None:
        db_unit.current_longitude = status_update.longitude
    
    db_unit.last_location_update = datetime.utcnow()
    db.commit()
    db.refresh(db_unit)
    
    # Log the status change
    await create_log(
        db=db,
        log_type="unit_status_changed",
        message=f"Unit {db_unit.unit_number} status changed to {status_update.status.value} by {current_user.username}",
        user_id=current_user.id,
        unit_id=db_unit.id,
        details={
            "status": status_update.status.value,
            "latitude": status_update.latitude,
            "longitude": status_update.longitude
        }
    )
    
    return UnitResponse.from_orm(db_unit)

@router.delete("/{unit_id}")
async def delete_unit(
    unit_id: int,
    current_user: User = Depends(get_current_active_user),
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
        message=f"Unit {db_unit.unit_number} deactivated by {current_user.username}",
        user_id=current_user.id,
        unit_id=db_unit.id
    )
    
    return {"message": "Unit deactivated successfully"} 