#!/bin/bash

echo "🚨 CommandFlex - Emergency Dispatch System"
echo "=========================================="
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

echo "✅ Docker and Docker Compose are available"
echo ""

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file..."
    cat > .env << EOF
# Database Configuration
DATABASE_URL=postgresql://commandflex:commandflex123@localhost:5432/commandflex

# Security
SECRET_KEY=your-super-secret-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Google Maps API (optional for now)
GOOGLE_MAPS_API_KEY=your-google-maps-api-key-here

# Frontend Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_GOOGLE_MAPS_API_KEY=your-google-maps-api-key-here

# WebSocket Configuration
WEBSOCKET_HOST=0.0.0.0
WEBSOCKET_PORT=8001

# Logging
LOG_LEVEL=INFO
EOF
    echo "✅ Created .env file"
    echo "⚠️  Please update the Google Maps API key in .env if you want map functionality"
    echo ""
fi

# Start the services
echo "🚀 Starting CommandFlex services..."
docker-compose up -d

# Wait for services to be ready
echo "⏳ Waiting for services to start..."
sleep 10

# Check if services are running
echo "🔍 Checking service status..."
if docker-compose ps | grep -q "Up"; then
    echo "✅ Services are running"
else
    echo "❌ Some services failed to start"
    docker-compose logs
    exit 1
fi

# Seed the database
echo "🌱 Seeding database with initial data..."
docker-compose exec backend python seed_data.py

echo ""
echo "🎉 CommandFlex is ready!"
echo ""
echo "📱 Access the application:"
echo "   Frontend: http://localhost:3000"
echo "   Backend API: http://localhost:8000"
echo "   API Documentation: http://localhost:8000/docs"
echo ""
echo "🔑 Demo Credentials:"
echo "   Dispatcher: dispatcher / password123"
echo "   Responder: responder / password123"
echo "   Supervisor: supervisor / password123"
echo "   Admin: admin / password123"
echo ""
echo "🛑 To stop the services:"
echo "   docker-compose down"
echo ""
echo "📊 To view logs:"
echo "   docker-compose logs -f" 