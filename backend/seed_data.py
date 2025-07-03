#!/usr/bin/env python3
"""
Seed script to populate the database with initial data for CommandFlex
"""

import asyncio
from sqlalchemy.orm import Session
from app.core.database import SessionLocal, engine
from app.models import Base, User, Incident, Unit
from app.models.user import UserRole
from app.models.incident import IncidentType, IncidentPriority, IncidentStatus
from app.models.unit import UnitType, UnitStatus
from app.core.auth import get_password_hash
from datetime import datetime, timedelta
import random

def create_users(db: Session):
    """Create initial users"""
    users_data = [
        {
            "username": "dispatcher",
            "email": "dispatcher@commandflex.com",
            "full_name": "John Dispatcher",
            "password": "password123",
            "role": UserRole.DISPATCHER
        },
        {
            "username": "responder",
            "email": "responder@commandflex.com",
            "full_name": "Sarah Responder",
            "password": "password123",
            "role": UserRole.RESPONDER
        },
        {
            "username": "supervisor",
            "email": "supervisor@commandflex.com",
            "full_name": "Mike Supervisor",
            "password": "password123",
            "role": UserRole.SUPERVISOR
        },
        {
            "username": "admin",
            "email": "admin@commandflex.com",
            "full_name": "Admin User",
            "password": "password123",
            "role": UserRole.ADMIN
        }
    ]
    
    for user_data in users_data:
        # Check if user already exists
        existing_user = db.query(User).filter(User.username == user_data["username"]).first()
        if not existing_user:
            hashed_password = get_password_hash(user_data["password"])
            user = User(
                username=user_data["username"],
                email=user_data["email"],
                full_name=user_data["full_name"],
                hashed_password=hashed_password,
                role=user_data["role"]
            )
            db.add(user)
            print(f"Created user: {user_data['username']}")
    
    db.commit()

def create_units(db: Session):
    """Create sample units"""
    units_data = [
        {"unit_number": "P-101", "type": UnitType.POLICE, "description": "Patrol Car 1"},
        {"unit_number": "P-102", "type": UnitType.POLICE, "description": "Patrol Car 2"},
        {"unit_number": "P-103", "type": UnitType.POLICE, "description": "Patrol Car 3"},
        {"unit_number": "F-201", "type": UnitType.FIRE, "description": "Fire Engine 1"},
        {"unit_number": "F-202", "type": UnitType.FIRE, "description": "Fire Engine 2"},
        {"unit_number": "E-301", "type": UnitType.EMS, "description": "Ambulance 1"},
        {"unit_number": "E-302", "type": UnitType.EMS, "description": "Ambulance 2"},
        {"unit_number": "S-401", "type": UnitType.SPECIAL, "description": "SWAT Team"},
    ]
    
    for unit_data in units_data:
        # Check if unit already exists
        existing_unit = db.query(Unit).filter(Unit.unit_number == unit_data["unit_number"]).first()
        if not existing_unit:
            unit = Unit(
                unit_number=unit_data["unit_number"],
                type=unit_data["type"],
                description=unit_data["description"],
                status=UnitStatus.AVAILABLE
            )
            db.add(unit)
            print(f"Created unit: {unit_data['unit_number']}")
    
    db.commit()

def create_incidents(db: Session):
    """Create sample incidents"""
    dispatcher = db.query(User).filter(User.role == UserRole.DISPATCHER).first()
    if not dispatcher:
        print("No dispatcher found, skipping incidents creation")
        return
    
    incidents_data = [
        {
            "incident_number": "INC-20241201-001",
            "type": IncidentType.POLICE,
            "priority": IncidentPriority.HIGH,
            "status": IncidentStatus.DISPATCHED,
            "address": "123 Main St, Downtown",
            "description": "Domestic disturbance reported",
            "caller_name": "Jane Doe",
            "caller_phone": "555-0101"
        },
        {
            "incident_number": "INC-20241201-002",
            "type": IncidentType.FIRE,
            "priority": IncidentPriority.CRITICAL,
            "status": IncidentStatus.NEW,
            "address": "456 Oak Ave, Industrial District",
            "description": "Structure fire at warehouse",
            "caller_name": "John Smith",
            "caller_phone": "555-0102"
        },
        {
            "incident_number": "INC-20241201-003",
            "type": IncidentType.MEDICAL,
            "priority": IncidentPriority.MODERATE,
            "status": IncidentStatus.EN_ROUTE,
            "address": "789 Pine Rd, Residential Area",
            "description": "Chest pain, possible heart attack",
            "caller_name": "Bob Wilson",
            "caller_phone": "555-0103"
        },
        {
            "incident_number": "INC-20241201-004",
            "type": IncidentType.TRAFFIC,
            "priority": IncidentPriority.LOW,
            "status": IncidentStatus.RESOLVED,
            "address": "321 Elm St, Highway Exit",
            "description": "Minor traffic accident, no injuries",
            "caller_name": "Alice Johnson",
            "caller_phone": "555-0104"
        }
    ]
    
    for incident_data in incidents_data:
        # Check if incident already exists
        existing_incident = db.query(Incident).filter(Incident.incident_number == incident_data["incident_number"]).first()
        if not existing_incident:
            incident = Incident(
                incident_number=incident_data["incident_number"],
                type=incident_data["type"],
                priority=incident_data["priority"],
                status=incident_data["status"],
                address=incident_data["address"],
                description=incident_data["description"],
                caller_name=incident_data["caller_name"],
                caller_phone=incident_data["caller_phone"],
                created_by=dispatcher.id
            )
            db.add(incident)
            print(f"Created incident: {incident_data['incident_number']}")
    
    db.commit()

def main():
    """Main seeding function"""
    print("Starting database seeding...")
    
    # Create database tables
    Base.metadata.create_all(bind=engine)
    
    # Get database session
    db = SessionLocal()
    
    try:
        # Create users
        print("\nCreating users...")
        create_users(db)
        
        # Create units
        print("\nCreating units...")
        create_units(db)
        
        # Create incidents
        print("\nCreating incidents...")
        create_incidents(db)
        
        print("\nDatabase seeding completed successfully!")
        
    except Exception as e:
        print(f"Error during seeding: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    main() 