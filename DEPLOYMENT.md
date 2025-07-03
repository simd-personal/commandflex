# CommandFlex Deployment Guide

## Quick Start

### Prerequisites
- Docker and Docker Compose
- At least 4GB RAM available
- Ports 3000, 8000, and 5432 available

### One-Command Setup
```bash
./start.sh
```

This script will:
1. Check Docker installation
2. Create environment configuration
3. Start all services
4. Seed the database with demo data
5. Provide access information

## Manual Setup

### 1. Environment Configuration
Create a `.env` file in the root directory:

```env
# Database Configuration
DATABASE_URL=postgresql://commandflex:commandflex123@localhost:5432/commandflex

# Security
SECRET_KEY=your-super-secret-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Google Maps API (optional)
GOOGLE_MAPS_API_KEY=your-google-maps-api-key-here

# Frontend Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_GOOGLE_MAPS_API_KEY=your-google-maps-api-key-here

# WebSocket Configuration
WEBSOCKET_HOST=0.0.0.0
WEBSOCKET_PORT=8001

# Logging
LOG_LEVEL=INFO
```

### 2. Start Services
```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### 3. Seed Database
```bash
# Run seed script
docker-compose exec backend python seed_data.py
```

## Access Information

### Web Interfaces
- **Frontend Application**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

### Demo Credentials
- **Dispatcher**: `dispatcher` / `password123`
- **Responder**: `responder` / `password123`
- **Supervisor**: `supervisor` / `password123`
- **Admin**: `admin` / `password123`

## Architecture

### Services
1. **PostgreSQL Database** (Port 5432)
   - Stores all application data
   - Persistent volume for data retention

2. **FastAPI Backend** (Port 8000)
   - REST API endpoints
   - WebSocket connections
   - Authentication and authorization
   - Business logic

3. **Next.js Frontend** (Port 3000)
   - React-based user interface
   - Real-time updates via WebSocket
   - Responsive design for multiple devices

### Data Flow
```
Frontend (React) ↔ WebSocket ↔ Backend (FastAPI) ↔ Database (PostgreSQL)
```

## API Endpoints

### Authentication
- `POST /api/auth/login` - User login
- `POST /api/auth/register` - User registration
- `GET /api/auth/me` - Get current user
- `POST /api/auth/logout` - User logout

### Incidents
- `GET /api/incidents` - List incidents
- `POST /api/incidents` - Create incident
- `GET /api/incidents/{id}` - Get incident details
- `PATCH /api/incidents/{id}` - Update incident
- `DELETE /api/incidents/{id}` - Cancel incident

### Units
- `GET /api/units` - List units
- `GET /api/units/available` - List available units
- `POST /api/units` - Create unit
- `PATCH /api/units/{id}` - Update unit
- `PATCH /api/units/{id}/status` - Update unit status

### Dispatch
- `POST /api/dispatch` - Dispatch unit to incident
- `GET /api/dispatch/incident/{id}` - Get incident dispatches
- `PATCH /api/dispatch/{id}` - Update dispatch status

### Logs
- `GET /api/logs` - List activity logs
- `GET /api/logs/incident/{id}` - Get incident logs
- `GET /api/logs/recent` - Get recent logs

## Development

### Backend Development
```bash
# Enter backend container
docker-compose exec backend bash

# Run tests
pytest

# Start development server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Development
```bash
# Enter frontend container
docker-compose exec frontend bash

# Install dependencies
npm install

# Start development server
npm run dev
```

### Database Management
```bash
# Access PostgreSQL
docker-compose exec postgres psql -U commandflex -d commandflex

# Backup database
docker-compose exec postgres pg_dump -U commandflex commandflex > backup.sql

# Restore database
docker-compose exec -T postgres psql -U commandflex -d commandflex < backup.sql
```

## Troubleshooting

### Common Issues

#### Services Won't Start
```bash
# Check Docker status
docker --version
docker-compose --version

# Check available ports
netstat -an | grep :3000
netstat -an | grep :8000
netstat -an | grep :5432

# View detailed logs
docker-compose logs
```

#### Database Connection Issues
```bash
# Check database status
docker-compose exec postgres pg_isready -U commandflex

# Reset database
docker-compose down -v
docker-compose up -d
docker-compose exec backend python seed_data.py
```

#### Frontend Build Issues
```bash
# Clear node modules and rebuild
docker-compose exec frontend rm -rf node_modules package-lock.json
docker-compose exec frontend npm install
docker-compose restart frontend
```

#### Authentication Issues
```bash
# Check JWT token
curl -H "Authorization: Bearer YOUR_TOKEN" http://localhost:8000/api/auth/me

# Reset user passwords
docker-compose exec backend python -c "
from app.core.database import SessionLocal
from app.models.user import User
from app.core.auth import get_password_hash
db = SessionLocal()
user = db.query(User).filter(User.username == 'dispatcher').first()
user.hashed_password = get_password_hash('password123')
db.commit()
db.close()
"
```

### Performance Optimization

#### Database
```sql
-- Add indexes for better performance
CREATE INDEX idx_incidents_status ON incidents(status);
CREATE INDEX idx_incidents_created_at ON incidents(created_at);
CREATE INDEX idx_units_status ON units(status);
CREATE INDEX idx_logs_created_at ON logs(created_at);
```

#### Frontend
- Enable gzip compression
- Use CDN for static assets
- Implement proper caching headers

#### Backend
- Enable connection pooling
- Implement request rate limiting
- Use background tasks for heavy operations

## Security Considerations

### Production Deployment
1. **Change default passwords**
2. **Use strong SECRET_KEY**
3. **Enable HTTPS**
4. **Configure firewall rules**
5. **Regular security updates**
6. **Database backups**
7. **Log monitoring**

### Environment Variables
```env
# Production settings
SECRET_KEY=your-very-long-random-secret-key
DATABASE_URL=postgresql://user:pass@host:port/db
LOG_LEVEL=WARNING
```

## Monitoring

### Health Checks
```bash
# API health
curl http://localhost:8000/health

# Database health
docker-compose exec postgres pg_isready -U commandflex

# Frontend health
curl http://localhost:3000
```

### Logs
```bash
# View all logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f postgres
```

### Metrics
- API response times
- Database query performance
- WebSocket connection count
- Error rates

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review application logs
3. Check API documentation at http://localhost:8000/docs
4. Create an issue in the project repository

## License

This project is licensed under the MIT License - see the LICENSE file for details. 