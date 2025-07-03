# CommandFlex - Real-Time Dispatch Management System

A comprehensive incident management and unit dispatch platform designed for emergency response operations.

## Features

- **Incident Management**: Create, track, and manage emergency incidents with priority levels
- **Unit Dispatch**: Assign available units to incidents with real-time status tracking
- **Geospatial Visualization**: Interactive map showing incidents, units, and routing
- **Real-time Updates**: Live status updates and notifications via WebSocket
- **Role-based Access**: Dispatcher, responder, and supervisor roles
- **AAR Reporting**: After-action review and reporting capabilities

## Tech Stack

- **Frontend**: Next.js 14 + TypeScript + Tailwind CSS
- **Backend**: Python FastAPI + PostgreSQL
- **Maps**: Google Maps API
- **Real-time**: WebSocket connections
- **Authentication**: JWT-based auth system
- **Database**: PostgreSQL with SQLAlchemy ORM

## Quick Start

### Prerequisites
- Docker and Docker Compose
- Node.js 18+
- Python 3.11+

### Development Setup

1. **Clone and setup**:
```bash
git clone <repository>
cd stratos-dispatch
```

2. **Environment Setup**:
```bash
cp .env.example .env
# Edit .env with your Google Maps API key and database credentials
```

3. **Start with Docker**:
```bash
docker-compose up -d
```

4. **Or run locally**:
```bash
# Backend
cd backend
pip install -r requirements.txt
uvicorn main:app --reload

# Frontend
cd frontend
npm install
npm run dev
```

## System Architecture

```
stratos-dispatch/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── api/            # API routes
│   │   ├── models/         # Database models
│   │   ├── services/       # Business logic
│   │   └── websocket/      # Real-time connections
│   └── requirements.txt
├── frontend/               # Next.js frontend
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── pages/          # Next.js pages
│   │   ├── hooks/          # Custom hooks
│   │   └── styles/         # Tailwind styles
│   └── package.json
├── docker-compose.yml      # Development environment
└── README.md
```

## API Documentation

Once running, visit:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## License

MIT License - see LICENSE file for details. 