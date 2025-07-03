from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta

from backend.app.core.database import get_db
from backend.app.core.auth import get_current_user, require_role
from backend.app.models.user import User, UserRole
from backend.app.models.log import Log, LogType
from backend.app.models.incident import Incident, IncidentStatus
from backend.app.models.unit import Unit, UnitStatus
from backend.app.schemas.log import LogResponse, TimelineEntry

router = APIRouter(prefix="/logs", tags=["logs"])

@router.get("/", response_model=List[LogResponse])
async def get_logs(
    incident_id: Optional[int] = None,
    unit_id: Optional[int] = None,
    log_type: Optional[LogType] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get logs with optional filtering"""
    query = db.query(Log)
    
    if incident_id:
        query = query.filter(Log.incident_id == incident_id)
    if unit_id:
        query = query.filter(Log.unit_id == unit_id)
    if log_type:
        query = query.filter(Log.type == log_type)
    if start_date:
        query = query.filter(Log.timestamp >= start_date)
    if end_date:
        query = query.filter(Log.timestamp <= end_date)
    
    logs = query.order_by(Log.timestamp.desc()).all()
    return logs

@router.get("/reports/incidents")
async def get_incident_report(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    priority: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.dispatcher]))
):
    """Get incident report statistics (Dispatcher only)"""
    query = db.query(Incident)
    
    if start_date:
        query = query.filter(Incident.created_at >= start_date)
    if end_date:
        query = query.filter(Incident.created_at <= end_date)
    if priority:
        query = query.filter(Incident.priority == priority)
    
    incidents = query.all()
    
    # Calculate statistics
    total_incidents = len(incidents)
    resolved_incidents = len([i for i in incidents if i.status == IncidentStatus.resolved])
    avg_response_time = None  # TODO: Calculate from logs
    
    return {
        "total_incidents": total_incidents,
        "resolved_incidents": resolved_incidents,
        "resolution_rate": (resolved_incidents / total_incidents * 100) if total_incidents > 0 else 0,
        "avg_response_time": avg_response_time
    }

@router.get("/reports/units")
async def get_unit_report(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.dispatcher]))
):
    """Get unit performance report (Dispatcher only)"""
    query = db.query(Unit)
    units = query.all()
    
    unit_stats = []
    for unit in units:
        # Count incidents assigned to this unit
        incident_count = len(unit.incident.units) if unit.incident else 0
        
        unit_stats.append({
            "unit_id": unit.id,
            "unit_name": unit.name,
            "incident_count": incident_count,
            "current_status": unit.status,
            "last_updated": unit.updated_at
        })
    
    return {
        "units": unit_stats,
        "total_units": len(units),
        "available_units": len([u for u in units if u.status == UnitStatus.available])
    }

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