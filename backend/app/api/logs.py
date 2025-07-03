from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta

from app.core.database import get_db
from app.core.auth import get_current_active_user
from app.models.user import User
from app.models.log import Log, LogType
from app.schemas.log import LogResponse, LogList

router = APIRouter()

@router.get("/", response_model=LogList)
async def get_logs(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    log_type: Optional[LogType] = None,
    user_id: Optional[int] = None,
    incident_id: Optional[int] = None,
    unit_id: Optional[int] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db)
):
    """Get activity logs with optional filtering"""
    query = db.query(Log)
    
    if log_type:
        query = query.filter(Log.type == log_type)
    if user_id:
        query = query.filter(Log.user_id == user_id)
    if incident_id:
        query = query.filter(Log.incident_id == incident_id)
    if unit_id:
        query = query.filter(Log.unit_id == unit_id)
    if start_date:
        query = query.filter(Log.created_at >= start_date)
    if end_date:
        query = query.filter(Log.created_at <= end_date)
    
    # Order by most recent first
    query = query.order_by(Log.created_at.desc())
    
    total = query.count()
    logs = query.offset(skip).limit(limit).all()
    
    return LogList(
        logs=[LogResponse.from_orm(log) for log in logs],
        total=total,
        page=skip // limit + 1,
        size=limit
    )

@router.get("/incident/{incident_id}", response_model=List[LogResponse])
async def get_incident_logs(
    incident_id: int,
    db: Session = Depends(get_db)
):
    """Get all logs for a specific incident (for AAR reporting)"""
    logs = db.query(Log).filter(
        Log.incident_id == incident_id
    ).order_by(Log.created_at.asc()).all()
    
    return [LogResponse.from_orm(log) for log in logs]

@router.get("/unit/{unit_id}", response_model=List[LogResponse])
async def get_unit_logs(
    unit_id: int,
    db: Session = Depends(get_db)
):
    """Get all logs for a specific unit"""
    logs = db.query(Log).filter(
        Log.unit_id == unit_id
    ).order_by(Log.created_at.desc()).all()
    
    return [LogResponse.from_orm(log) for log in logs]

@router.get("/user/{user_id}", response_model=List[LogResponse])
async def get_user_logs(
    user_id: int,
    db: Session = Depends(get_db)
):
    """Get all logs for a specific user"""
    logs = db.query(Log).filter(
        Log.user_id == user_id
    ).order_by(Log.created_at.desc()).all()
    
    return [LogResponse.from_orm(log) for log in logs]

@router.get("/recent", response_model=List[LogResponse])
async def get_recent_logs(
    hours: int = Query(24, ge=1, le=168),  # Default to 24 hours, max 1 week
    db: Session = Depends(get_db)
):
    """Get recent logs within specified hours"""
    cutoff_time = datetime.utcnow() - timedelta(hours=hours)
    
    logs = db.query(Log).filter(
        Log.created_at >= cutoff_time
    ).order_by(Log.created_at.desc()).limit(100).all()
    
    return [LogResponse.from_orm(log) for log in logs]

@router.get("/summary")
async def get_log_summary(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db)
):
    """Get summary statistics for logs (useful for AAR reports)"""
    query = db.query(Log)
    
    if start_date:
        query = query.filter(Log.created_at >= start_date)
    if end_date:
        query = query.filter(Log.created_at <= end_date)
    
    # Get total count
    total_logs = query.count()
    
    # Get counts by type
    type_counts = {}
    for log_type in LogType:
        count = query.filter(Log.type == log_type).count()
        type_counts[log_type.value] = count
    
    # Get most active users
    user_activity = db.query(Log.user_id, db.func.count(Log.id).label('count')).filter(
        Log.user_id.isnot(None)
    ).group_by(Log.user_id).order_by(db.func.count(Log.id).desc()).limit(10).all()
    
    return {
        "total_logs": total_logs,
        "type_counts": type_counts,
        "most_active_users": [{"user_id": user_id, "count": count} for user_id, count in user_activity],
        "date_range": {
            "start_date": start_date.isoformat() if start_date else None,
            "end_date": end_date.isoformat() if end_date else None
        }
    } 