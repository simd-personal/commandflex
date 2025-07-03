from sqlalchemy.orm import Session
from backend.app.models.log import Log, LogType
from typing import Optional, Dict, Any

async def create_log(
    db: Session,
    log_type: str,
    message: str,
    user_id: Optional[int] = None,
    incident_id: Optional[int] = None,
    unit_id: Optional[int] = None,
    details: Optional[Dict[str, Any]] = None
):
    """Create a new log entry"""
    try:
        log = Log(
            type=LogType(log_type),
            message=message,
            user_id=user_id,
            incident_id=incident_id,
            unit_id=unit_id,
            details=details
        )
        db.add(log)
        db.commit()
        db.refresh(log)
        return log
    except Exception as e:
        db.rollback()
        raise e 