from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn

from app.api import incidents, units, dispatch, auth, logs, websocket
from app.core.config import settings
from app.core.database import engine
from app.models import Base

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="CommandFlex API",
    description="Real-time dispatch management system for emergency response operations",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "http://127.0.0.1:3000", "http://127.0.0.1:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(incidents.router, prefix="/api/incidents", tags=["Incidents"])
app.include_router(units.router, prefix="/api/units", tags=["Units"])
app.include_router(dispatch.router, prefix="/api/dispatch", tags=["Dispatch"])
app.include_router(logs.router, prefix="/api/logs", tags=["Logs"])
app.include_router(websocket.router, tags=["WebSocket"])

@app.get("/")
async def root():
    return {"message": "CommandFlex API - Emergency Dispatch System"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "CommandFlex API"}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    ) 