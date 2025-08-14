#!/bin/bash

# MongoDB Development Server Management Script
# Usage: ./scripts/mongodb-dev.sh {start|stop|reset|logs|shell}

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
CONTAINER_NAME="mongodb-dev"
MONGODB_PORT="27017"
MONGODB_ROOT_USERNAME="admin"
MONGODB_ROOT_PASSWORD="password123"
MONGODB_DATABASE="flutter_spa"
MONGODB_APP_USER="app_user"
MONGODB_APP_PASSWORD="app_password"
VOLUME_NAME="mongodb_data"

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_docker() {
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    if ! docker info &> /dev/null; then
        print_error "Docker is not running. Please start Docker first."
        exit 1
    fi
}

wait_for_mongodb() {
    print_status "Waiting for MongoDB to be ready..."
    local max_attempts=30
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if docker exec $CONTAINER_NAME mongosh --quiet --eval "db.adminCommand('ping')" &>/dev/null; then
            print_success "MongoDB is ready!"
            return 0
        fi
        
        print_status "Attempt $attempt/$max_attempts - MongoDB not ready yet..."
        sleep 2
        ((attempt++))
    done
    
    print_error "MongoDB failed to start after $max_attempts attempts"
    return 1
}

create_app_user() {
    print_status "Creating application user..."
    
    docker exec $CONTAINER_NAME mongosh --quiet --eval "
        use $MONGODB_DATABASE
        try {
            db.createUser({
                user: '$MONGODB_APP_USER',
                pwd: '$MONGODB_APP_PASSWORD',
                roles: [
                    { role: 'readWrite', db: '$MONGODB_DATABASE' },
                    { role: 'dbAdmin', db: '$MONGODB_DATABASE' }
                ]
            })
            print('✅ Application user created successfully')
        } catch(e) {
            if (e.code === 11000) {
                print('ℹ️  Application user already exists')
            } else {
                print('❌ Error creating user: ' + e.message)
            }
        }
    " 2>/dev/null || print_warning "Could not create application user"
}

create_indexes() {
    print_status "Creating database indexes..."
    
    docker exec $CONTAINER_NAME mongosh --quiet --eval "
        use $MONGODB_DATABASE
        try {
            db.users.createIndex({ 'email': 1 }, { unique: true })
            db.users.createIndex({ 'phone': 1 }, { unique: true })
            db.users.createIndex({ 'createdAt': 1 })
            db.users.createIndex({ 'updatedAt': 1 })
            print('✅ Database indexes created successfully')
        } catch(e) {
            print('ℹ️  Indexes may already exist: ' + e.message)
        }
    " 2>/dev/null || print_warning "Could not create indexes"
}

start_mongodb() {
    check_docker
    
    print_status "Starting MongoDB development server..."
    
    # Check if container exists
    if docker ps -a --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
        # Container exists, check if it's running
        if docker ps --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
            print_success "MongoDB container is already running!"
            show_connection_info
            return 0
        else
            print_status "Starting existing MongoDB container..."
            docker start $CONTAINER_NAME
        fi
    else
        print_status "Creating new MongoDB container..."
        docker run --name $CONTAINER_NAME \
            -p $MONGODB_PORT:27017 \
            -e MONGO_INITDB_ROOT_USERNAME=$MONGODB_ROOT_USERNAME \
            -e MONGO_INITDB_ROOT_PASSWORD=$MONGODB_ROOT_PASSWORD \
            -e MONGO_INITDB_DATABASE=$MONGODB_DATABASE \
            -v $VOLUME_NAME:/data/db \
            -d mongo:7.0 \
            --auth
        
        if [ $? -ne 0 ]; then
            print_error "Failed to create MongoDB container"
            exit 1
        fi
    fi
    
    # Wait for MongoDB to be ready
    if wait_for_mongodb; then
        create_app_user
        create_indexes
        print_success "MongoDB development server is ready!"
        show_connection_info
    else
        print_error "Failed to start MongoDB"
        exit 1
    fi
}

stop_mongodb() {
    print_status "Stopping MongoDB development server..."
    
    if docker ps --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
        docker stop $CONTAINER_NAME
        print_success "MongoDB container stopped"
    else
        print_warning "MongoDB container is not running"
    fi
}

restart_mongodb() {
    print_status "Restarting MongoDB development server..."
    stop_mongodb
    sleep 2
    start_mongodb
}

reset_mongodb() {
    print_warning "This will destroy all data in the MongoDB development database!"
    read -p "Are you sure you want to continue? (y/N): " -n 1 -r
    echo
    
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_status "Reset cancelled"
        return 0
    fi
    
    print_status "Resetting MongoDB development database..."
    
    # Stop and remove container
    docker stop $CONTAINER_NAME 2>/dev/null || true
    docker rm $CONTAINER_NAME 2>/dev/null || true
    
    # Remove volume
    docker volume rm $VOLUME_NAME 2>/dev/null || true
    
    print_success "MongoDB reset complete"
    start_mongodb
}

show_logs() {
    print_status "Showing MongoDB logs (press Ctrl+C to exit)..."
    docker logs -f $CONTAINER_NAME
}

open_shell() {
    if ! docker ps --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
        print_error "MongoDB container is not running. Start it first with: $0 start"
        exit 1
    fi
    
    print_status "Opening MongoDB shell..."
    print_status "Connecting as: $MONGODB_APP_USER"
    print_status "Database: $MONGODB_DATABASE"
    print_status "Type 'exit' or press Ctrl+D to exit the shell"
    echo
    
    docker exec -it $CONTAINER_NAME mongosh \
        "mongodb://$MONGODB_APP_USER:$MONGODB_APP_PASSWORD@localhost:27017/$MONGODB_DATABASE"
}

show_status() {
    print_status "MongoDB Development Server Status:"
    echo
    
    if docker ps --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
        print_success "Container Status: Running ✅"
        
        # Get container info
        CONTAINER_ID=$(docker ps -q --filter name=$CONTAINER_NAME)
        CREATED=$(docker inspect --format='{{.Created}}' $CONTAINER_ID | cut -d'T' -f1)
        UPTIME=$(docker inspect --format='{{.State.StartedAt}}' $CONTAINER_ID)
        
        echo "  📦 Container ID: $CONTAINER_ID"
        echo "  📅 Created: $CREATED"
        echo "  ⏰ Started: $(echo $UPTIME | cut -d'T' -f1-2 | tr 'T' ' ' | cut -d'.' -f1)"
        
        # Test connection
        if docker exec $CONTAINER_NAME mongosh --quiet --eval "db.adminCommand('ping')" &>/dev/null; then
            print_success "Database Status: Healthy ✅"
            
            # Get database stats
            STATS=$(docker exec $CONTAINER_NAME mongosh --quiet --eval "
                use $MONGODB_DATABASE
                print('Collections: ' + db.getCollectionNames().length)
                print('Users: ' + (db.users ? db.users.countDocuments() : 0))
            " 2>/dev/null)
            
            echo "  📊 Database Stats:"
            echo "$STATS" | while read line; do
                echo "     $line"
            done
        else
            print_warning "Database Status: Not responding ⚠️"
        fi
        
        show_connection_info
        
    elif docker ps -a --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
        print_warning "Container Status: Stopped ⚠️"
        echo "  Use '$0 start' to start the container"
    else
        print_warning "Container Status: Not created ⚠️"
        echo "  Use '$0 start' to create and start the container"
    fi
}

show_connection_info() {
    echo
    print_success "📡 Connection Information:"
    echo "  🔗 Application URL: mongodb://$MONGODB_APP_USER:$MONGODB_APP_PASSWORD@localhost:$MONGODB_PORT/$MONGODB_DATABASE"
    echo "  🔗 Admin URL: mongodb://$MONGODB_ROOT_USERNAME:$MONGODB_ROOT_PASSWORD@localhost:$MONGODB_PORT/admin"
    echo "  🌐 Host: localhost"
    echo "  🔌 Port: $MONGODB_PORT"
    echo "  🗃️  Database: $MONGODB_DATABASE"
    echo "  👤 App User: $MONGODB_APP_USER"
    echo
    print_status "Environment variable for your .env file:"
    echo "  MONGODB_URI=mongodb://$MONGODB_APP_USER:$MONGODB_APP_PASSWORD@localhost:$MONGODB_PORT/$MONGODB_DATABASE"
}

show_help() {
    echo "MongoDB Development Server Management"
    echo
    echo "Usage: $0 {start|stop|restart|reset|logs|shell|status|help}"
    echo
    echo "Commands:"
    echo "  start    - Start MongoDB development server"
    echo "  stop     - Stop MongoDB development server" 
    echo "  restart  - Restart MongoDB development server"
    echo "  reset    - Reset MongoDB (destroys all data)"
    echo "  logs     - Show MongoDB logs"
    echo "  shell    - Open MongoDB shell"
    echo "  status   - Show server status and connection info"
    echo "  help     - Show this help message"
    echo
    echo "Examples:"
    echo "  $0 start                 # Start MongoDB"
    echo "  $0 shell                 # Open MongoDB shell"
    echo "  $0 logs                  # View logs"
    echo "  $0 reset                 # Reset database (with confirmation)"
}

# Main script logic
case "$1" in
    start)
        start_mongodb
        ;;
    stop)
        stop_mongodb
        ;;
    restart)
        restart_mongodb
        ;;
    reset)
        reset_mongodb
        ;;
    logs)
        show_logs
        ;;
    shell)
        open_shell
        ;;
    status)
        show_status
        ;;
    help)
        show_help
        ;;
    *)
        print_error "Unknown command: $1"
        echo
        show_help
        exit 1
        ;;
esac
