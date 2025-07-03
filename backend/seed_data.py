#!/usr/bin/env python3
"""
Seed script to populate the database with initial data for CommandFlex
"""

import asyncio
from sqlalchemy.orm import Session
from backend.app.core.database import SessionLocal, engine
from backend.app.models import Base, User, Incident, Unit
from backend.app.models.user import UserRole
from backend.app.models.incident import IncidentType, IncidentPriority, IncidentStatus
from backend.app.models.unit import UnitType, UnitStatus
from backend.app.core.auth import get_password_hash
from datetime import datetime, timedelta
import random
from backend.app.models.log import Log, LogType

def create_users(db: Session):
    """Create initial users"""
    users_data = [
        {
            "username": "dispatcher@commandflex.com",
            "email": "dispatcher@commandflex.com",
            "full_name": "John Dispatcher",
            "password": "password123",
            "role": UserRole.dispatcher
        },
        {
            "username": "responder@commandflex.com",
            "email": "responder@commandflex.com",
            "full_name": "Sarah Responder",
            "password": "password123",
            "role": UserRole.responder
        }
    ]
    
    for user_data in users_data:
        # Check if user already exists
        existing_user = db.query(User).filter(User.username == user_data["username"]).first()
        if not existing_user:
            password_hash = get_password_hash(user_data["password"])
            user = User(
                username=user_data["username"],
                password_hash=password_hash,
                role=user_data["role"]
            )
            db.add(user)
            print(f"Created user: {user_data['username']}")
    
    db.commit()

def create_units(db: Session):
    """Create sample units"""
    units_data = [
        {"unit_number": "P-101", "type": UnitType.POLICE, "description": "Patrol Car 1", "status": UnitStatus.available},
        {"unit_number": "P-102", "type": UnitType.POLICE, "description": "Patrol Car 2", "status": UnitStatus.available},
        {"unit_number": "P-103", "type": UnitType.POLICE, "description": "Patrol Car 3", "status": UnitStatus.available},
        {"unit_number": "F-201", "type": UnitType.FIRE, "description": "Fire Engine 1", "status": UnitStatus.available},
        {"unit_number": "F-202", "type": UnitType.FIRE, "description": "Fire Engine 2", "status": UnitStatus.available},
        {"unit_number": "E-301", "type": UnitType.EMS, "description": "Ambulance 1", "status": UnitStatus.available},
        {"unit_number": "E-302", "type": UnitType.EMS, "description": "Ambulance 2", "status": UnitStatus.available},
        {"unit_number": "S-401", "type": UnitType.SPECIAL, "description": "SWAT Team", "status": UnitStatus.available},
    ]
    
    for unit_data in units_data:
        # Check if unit already exists
        existing_unit = db.query(Unit).filter(Unit.unit_number == unit_data["unit_number"]).first()
        if not existing_unit:
            unit = Unit(
                unit_number=unit_data["unit_number"],
                type=unit_data["type"],
                description=unit_data["description"],
                status=unit_data["status"]
            )
            db.add(unit)
            print(f"Created unit: {unit_data['unit_number']}")
    
    db.commit()

def create_incidents(db: Session):
    """Create sample incidents"""
    dispatcher = db.query(User).filter(User.role == UserRole.dispatcher).first()
    if not dispatcher:
        print("No dispatcher found, skipping incidents creation")
        return
    
    incidents_data = [
        {
            "incident_number": "INC-20240703-001",
            "type": IncidentType.POLICE,
            "priority": IncidentPriority.HIGH,
            "status": IncidentStatus.dispatched,
            "address": "123 Main St, Downtown",
            "description": "Domestic disturbance reported",
            "caller_name": "Jane Doe",
            "caller_phone": "555-0101"
        },
        {
            "incident_number": "INC-20240703-002",
            "type": IncidentType.FIRE,
            "priority": IncidentPriority.CRITICAL,
            "status": IncidentStatus.new,
            "address": "456 Oak Ave, Industrial District",
            "description": "Structure fire at warehouse",
            "caller_name": "John Smith",
            "caller_phone": "555-0102"
        },
        {
            "incident_number": "INC-20240703-003",
            "type": IncidentType.MEDICAL,
            "priority": IncidentPriority.MODERATE,
            "status": IncidentStatus.dispatched,
            "address": "789 Pine Rd, Residential Area",
            "description": "Chest pain, possible heart attack",
            "caller_name": "Bob Wilson",
            "caller_phone": "555-0103"
        },
        {
            "incident_number": "INC-20240703-004",
            "type": IncidentType.TRAFFIC,
            "priority": IncidentPriority.LOW,
            "status": IncidentStatus.resolved,
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
                created_by=dispatcher.id if dispatcher else None,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )
            db.add(incident)
            print(f"Created incident: {incident_data['incident_number']}")
    
    db.commit()

def create_seed_data():
    # Ensure tables are created
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    
    try:
        # Clear existing data
        db.query(Log).delete()
        db.query(Incident).delete()
        db.query(Unit).delete()
        db.query(User).delete()
        db.commit()
        
        print("Creating seed data for CommandFlex PD...")
        
        # Create users
        users_data = [
            {
                "username": "dispatcher@commandflex.com",
                "email": "dispatcher@commandflex.com",
                "full_name": "John Dispatcher",
                "password": "password123",
                "role": UserRole.dispatcher
            },
            {
                "username": "responder@commandflex.com",
                "email": "responder@commandflex.com",
                "full_name": "Sarah Responder",
                "password": "password123",
                "role": UserRole.responder
            }
        ]
        
        for user_data in users_data:
            # Check if user already exists
            existing_user = db.query(User).filter(User.username == user_data["username"]).first()
            if not existing_user:
                password_hash = get_password_hash(user_data["password"])
                user = User(
                    username=user_data["username"],
                    email=user_data["email"],
                    full_name=user_data["full_name"],
                    password_hash=password_hash,
                    role=user_data["role"]
                )
                db.add(user)
                print(f"Created user: {user_data['username']}")
        
        db.commit()
        
        # Create units
        units_data = [
            {"unit_number": "P-101", "type": UnitType.POLICE, "description": "Patrol Car 1", "status": UnitStatus.available},
            {"unit_number": "P-102", "type": UnitType.POLICE, "description": "Patrol Car 2", "status": UnitStatus.available},
            {"unit_number": "P-103", "type": UnitType.POLICE, "description": "Patrol Car 3", "status": UnitStatus.available},
            {"unit_number": "F-201", "type": UnitType.FIRE, "description": "Fire Engine 1", "status": UnitStatus.available},
            {"unit_number": "F-202", "type": UnitType.FIRE, "description": "Fire Engine 2", "status": UnitStatus.available},
            {"unit_number": "E-301", "type": UnitType.EMS, "description": "Ambulance 1", "status": UnitStatus.available},
            {"unit_number": "E-302", "type": UnitType.EMS, "description": "Ambulance 2", "status": UnitStatus.available},
            {"unit_number": "S-401", "type": UnitType.SPECIAL, "description": "SWAT Team", "status": UnitStatus.available},
        ]
        
        for unit_data in units_data:
            # Check if unit already exists
            existing_unit = db.query(Unit).filter(Unit.unit_number == unit_data["unit_number"]).first()
            if not existing_unit:
                unit = Unit(
                    unit_number=unit_data["unit_number"],
                    type=unit_data["type"],
                    description=unit_data["description"],
                    status=unit_data["status"]
                )
                db.add(unit)
                print(f"Created unit: {unit_data['unit_number']}")
        
        db.commit()
        
        # Create incidents with realistic scenarios
        incidents_data = [
            {
                "incident_number": "INC-20240703-001",
                "type": IncidentType.POLICE,
                "priority": IncidentPriority.HIGH,
                "status": IncidentStatus.dispatched,
                "address": "123 Main St, Downtown",
                "description": "Domestic disturbance reported",
                "caller_name": "Jane Doe",
                "caller_phone": "555-0101"
            },
            {
                "incident_number": "INC-20240703-002",
                "type": IncidentType.FIRE,
                "priority": IncidentPriority.CRITICAL,
                "status": IncidentStatus.new,
                "address": "456 Oak Ave, Industrial District",
                "description": "Structure fire at warehouse",
                "caller_name": "John Smith",
                "caller_phone": "555-0102"
            },
            {
                "incident_number": "INC-20240703-003",
                "type": IncidentType.MEDICAL,
                "priority": IncidentPriority.MODERATE,
                "status": IncidentStatus.dispatched,
                "address": "789 Pine Rd, Residential Area",
                "description": "Chest pain, possible heart attack",
                "caller_name": "Bob Wilson",
                "caller_phone": "555-0103"
            },
            {
                "incident_number": "INC-20240703-004",
                "type": IncidentType.TRAFFIC,
                "priority": IncidentPriority.LOW,
                "status": IncidentStatus.resolved,
                "address": "321 Elm St, Highway Exit",
                "description": "Minor traffic accident, no injuries",
                "caller_name": "Alice Johnson",
                "caller_phone": "555-0104"
            }
        ]
        
        dispatcher = db.query(User).filter(User.role == UserRole.dispatcher).first()
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
                    created_by=dispatcher.id if dispatcher else None,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow(),
                )
                db.add(incident)
                print(f"Created incident: {incident_data['incident_number']}")
        
        db.commit()
        
        # Assign units to incidents
        unit1 = db.query(Unit).filter(Unit.unit_number == "P-101").first()
        unit2 = db.query(Unit).filter(Unit.unit_number == "P-102").first()
        unit3 = db.query(Unit).filter(Unit.unit_number == "E-301").first()
        unit4 = db.query(Unit).filter(Unit.unit_number == "E-302").first()
        
        incident1 = db.query(Incident).filter(Incident.incident_number == "INC-20240703-001").first()
        incident2 = db.query(Incident).filter(Incident.incident_number == "INC-20240703-002").first()
        incident3 = db.query(Incident).filter(Incident.incident_number == "INC-20240703-003").first()
        incident4 = db.query(Incident).filter(Incident.incident_number == "INC-20240703-004").first()
        
        unit1.incident_id = incident1.id
        unit1.status = UnitStatus.en_route
        
        unit2.incident_id = incident2.id
        unit2.status = UnitStatus.on_scene
        
        unit3.incident_id = incident3.id
        unit3.status = UnitStatus.en_route
        
        unit4.incident_id = incident4.id
        unit4.status = UnitStatus.en_route
        
        db.commit()
        
        # Create timeline logs for each incident
        logs_data = [
            {
                "incident_id": incident1.id,
                "type": LogType.status,
                "message": "Incident created: Armed Robbery at 123 Main Street, Downtown",
                "timestamp": incident1.created_at
            },
            {
                "incident_id": incident1.id,
                "unit_id": unit1.id,
                "type": LogType.dispatch,
                "message": "Unit P-101 dispatched to incident",
                "timestamp": incident1.created_at + timedelta(minutes=2)
            },
            {
                "incident_id": incident1.id,
                "unit_id": unit1.id,
                "type": LogType.note,
                "message": "Dispatch notes: Suspect armed with handgun, 3 hostages inside store",
                "timestamp": incident1.created_at + timedelta(minutes=2)
            },
            {
                "incident_id": incident2.id,
                "type": LogType.status,
                "message": "Incident created: Traffic Accident at 456 Oak Avenue, Midtown",
                "timestamp": incident2.created_at
            },
            {
                "incident_id": incident2.id,
                "unit_id": unit2.id,
                "type": LogType.dispatch,
                "message": "Unit P-102 dispatched to incident",
                "timestamp": incident2.created_at + timedelta(minutes=1)
            },
            {
                "incident_id": incident2.id,
                "unit_id": unit2.id,
                "type": LogType.arrival,
                "message": "Unit P-102 arrived on scene",
                "timestamp": incident2.created_at + timedelta(minutes=8)
            },
            {
                "incident_id": incident2.id,
                "unit_id": unit2.id,
                "type": LogType.note,
                "message": "Scene notes: Two vehicles involved, one driver complaining of neck pain, ambulance requested",
                "timestamp": incident2.created_at + timedelta(minutes=10)
            },
            {
                "incident_id": incident3.id,
                "type": LogType.status,
                "message": "Incident created: Medical Emergency at 789 Pine Road, Residential Area",
                "timestamp": incident3.created_at
            },
            {
                "incident_id": incident3.id,
                "unit_id": unit3.id,
                "type": LogType.dispatch,
                "message": "Unit E-301 dispatched to incident",
                "timestamp": incident3.created_at + timedelta(minutes=1)
            },
            {
                "incident_id": incident3.id,
                "unit_id": unit3.id,
                "type": LogType.arrival,
                "message": "Unit E-301 arrived on scene",
                "timestamp": incident3.created_at + timedelta(minutes=6)
            },
            {
                "incident_id": incident3.id,
                "type": LogType.resolution,
                "message": "Incident resolved: Patient transported to hospital, condition stable",
                "timestamp": incident3.created_at + timedelta(minutes=25)
            },
            {
                "incident_id": incident4.id,
                "type": LogType.status,
                "message": "Incident created: Traffic Accident at 321 Elm Street, Highway Exit",
                "timestamp": incident4.created_at
            },
            {
                "incident_id": incident4.id,
                "unit_id": unit4.id,
                "type": LogType.dispatch,
                "message": "Unit E-302 dispatched to incident",
                "timestamp": incident4.created_at + timedelta(minutes=1)
            },
            {
                "incident_id": incident4.id,
                "type": LogType.arrival,
                "message": "Unit E-302 arrived on scene",
                "timestamp": incident4.created_at + timedelta(minutes=6)
            },
            {
                "incident_id": incident4.id,
                "type": LogType.resolution,
                "message": "Incident resolved: Patient transported to hospital, condition stable",
                "timestamp": incident4.created_at + timedelta(minutes=25)
            }
        ]
        
        for log_data in logs_data:
            log = Log(
                incident_id=log_data["incident_id"],
                unit_id=log_data.get("unit_id"),
                type=log_data["type"],
                message=log_data["message"],
                timestamp=log_data["timestamp"]
            )
            db.add(log)
        
        db.commit()
        
        print("✅ Seed data created successfully!")
        print(f"📊 Created {len(users_data)} users ({len([u for u in users_data if u['role'] == UserRole.dispatcher])} dispatchers, {len([u for u in users_data if u['role'] == UserRole.responder])} responders)")
        print(f"🚓 Created {len(units_data)} units")
        print(f"🚨 Created {len(incidents_data)} incidents")
        print(f"📝 Created {len(logs_data)} log entries")
        print("\n🔑 Login Credentials:")
        print("Dispatcher: dispatcher@commandflex.com / password123")
        print("Responder: responder@commandflex.com / password123")
        print("\n🎯 Demo Scenarios:")
        print("- Armed robbery in progress (Priority 1, dispatched)")
        print("- Traffic accident on scene (Priority 2, on scene)")
        print("- Medical emergency resolved (Priority 3, resolved)")
        print("- Traffic accident resolved (Priority 4, resolved)")
        
    except Exception as e:
        print(f"❌ Error creating seed data: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_seed_data() 