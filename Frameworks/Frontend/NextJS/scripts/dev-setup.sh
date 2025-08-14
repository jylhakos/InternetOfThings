#!/bin/bash

echo "🚀 Setting up development environment..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    echo "   Ubuntu/Debian: sudo apt-get install docker.io docker-compose"
    echo "   CentOS/RHEL: sudo yum install docker docker-compose"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 20+ first."
    exit 1
fi

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file..."
    cat > .env << EOL
# Database Configuration
DATABASE_URL="postgresql://webapp_user:webapp_password@localhost:5432/webapp_database"
DIRECT_URL="postgresql://webapp_user:webapp_password@localhost:5432/webapp_database"

# Redis Configuration
REDIS_URL="redis://localhost:6379"

# Application Configuration
NODE_ENV="development"
NEXT_PUBLIC_URL="http://localhost:3000"
API_URL="http://localhost:3000"

# Security
JWT_SECRET="development-jwt-secret-key"
NEXTAUTH_SECRET="development-nextauth-secret"
NEXTAUTH_URL="http://localhost:3000"
EOL
    echo "✅ Created .env file with default development settings"
fi

# Start PostgreSQL and Redis
echo "🐘 Starting PostgreSQL and Redis..."
docker-compose up -d

# Wait for PostgreSQL to be ready
echo "⏳ Waiting for PostgreSQL to be ready..."
until docker exec webapp_postgres pg_isready -U webapp_user -d webapp_database 2>/dev/null; do
    sleep 2
    printf "."
done
echo ""

# Install dependencies
echo "📦 Installing dependencies..."
npm install

# Generate Prisma client
echo "🔧 Generating Prisma client..."
npx prisma generate

# Run migrations
echo "🗄️ Running database migrations..."
npx prisma migrate dev --name init

# Seed database
echo "🌱 Seeding database..."
npx prisma db seed

echo ""
echo "✅ Development environment setup complete!"
echo "🌐 You can now run: npm run dev"
echo "📊 PostgreSQL is running on: localhost:5432"
echo "🔴 Redis is running on: localhost:6379"
echo "💾 Database GUI: npx prisma studio"
echo ""
echo "🔗 Useful commands:"
echo "   npm run dev          - Start development server"
echo "   npx prisma studio    - Open database GUI"
echo "   docker-compose logs  - View database logs"
echo "   docker-compose down  - Stop database services"
