# Flutter SPA with Amazon AWS Backend Integration

A Flutter Single Page Application (SPA) with Amazon AWS backend services for user management, authentication, and data persistence.

## Platforms

- **Android**: Native mobile application
- **Chrome Tablet**: Progressive Web App (PWA)
- **Apple iPad iOS**: Native mobile application and PWA

## Project Structure

### Frontend (Flutter SPA)
```
lib/
├── main.dart                  App entry point with Riverpod & GoRouter
├── models/
│   ├── user.dart             User data model with JSON serialization
│   └── api_response.dart     Generic API response wrapper
├── services/
│   ├── auth_service.dart    Amazon AWS Cognito authentication service
│   ├── api_service.dart      HTTP client with JWT token handling
│   └── storage_service.dart  Secure local storage service
└── screens/
    ├── login_screen.dart     Material Design authentication UI
    ├── home_screen.dart      Dashboard with navigation drawer
    └── profile_screen.dart   User profile management screen

web/
├── index.html               Flutter web entry point
└── manifest.json            PWA manifest configuration

pubspec.yaml                 Flutter dependencies & AWS integration
```

### Backend (Node.js API)
```
backend/
├── src/
│   ├── server.js            Express server with CORS & middleware
│   ├── config/
│   │   └── database.js      MongoDB connection configuration
│   ├── models/
│   │   └── User.js          Mongoose user schema & validation
│   ├── middleware/
│   │   └── auth.js          JWT authentication middleware
│   └── routes/
│       ├── auth.js          Authentication routes (login/register)
│       └── users.js         User management routes (CRUD)
├── package.json             Node.js dependencies & scripts
├── Dockerfile               Container build configuration
└── .env.example             Environment variables template
```

### Infrastructure
```
├── docker-compose.yml       Multi-container orchestration
├── nginx.conf               Reverse proxy & load balancer
├── .gitignore               Git exclusions for all components
├── scripts/
│   ├── setup-dev.sh         Development environment automation
│   ├── deploy.sh            Amazon AWS deployment automation
│   └── test-api.sh          API testing & validation
└── .env.example             Environment configuration template
```

## Flutter SPA + Frontend + Backend Architecture

### Complete System Architecture
```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                                   CLIENT TIER                                       │
├─────────────────────────────────────────────────────────────────────────────────────┤
│     Android App           Chrome Tablet PWA               iPad iOS App              │
│  ┌─────────────────┐    ┌─────────────────────┐     ┌─────────────────────┐         │
│  │ Flutter Mobile  │    │ Flutter Web (SPA)   │     │ Flutter Mobile/PWA  │         │
│  │ - Native UI     │    │ - Progressive Web   │     │ - Native/Web Hybrid │         │
│  │ - Local Storage │    │ - Browser Storage   │     │ - Local Storage     │         │
│  │ - Push Notif.   │    │ - Service Workers   │     │ - Push Notifications│         │
│  └─────────────────┘    └─────────────────────┘     └─────────────────────┘         │
│            │                        │                           │                   │
│            └────────────────────────┼───────────────────────────┘                   │
└─────────────────────────────────────┼───────────────────────────────────────────────┘
                                      │
                               HTTPS/WebSocket
                                      │
┌─────────────────────────────────────┼────────────────────────────────────────────────┐
│                              PRESENTATION TIER                                       │
├─────────────────────────────────────┼────────────────────────────────────────────────┤
│                    🌐 NGINX Reverse Proxy + Load Balancer                            │
│  ┌─────────────────────────────────────────────────────────────────────────────────┐ │
│  │  SSL Termination       Rate Limiting         Static Assets Serving              │ │
│  │  CORS Configuration    Request Routing       Gzip Compression                   │ │
│  │  Security Headers      Load Balancing        Caching Strategies                 │ │
│  └─────────────────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────┼────────────────────────────────────────────────┘
                                      │
                                 HTTP/REST API
                                      │
┌─────────────────────────────────────┼────────────────────────────────────────────────┐
│                              APPLICATION TIER                                        │
├─────────────────────────────────────┼────────────────────────────────────────────────┤
│                           Node.js Express API Server                                 │
│  ┌─────────────────────────────────────────────────────────────────────────────────┐ │
│  │                           📂 Server Architecture                                │ │
│  │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────────────────────┐  │ │
│  │  │   Middleware    │  │     Routes      │  │        Business Logic           │  │ │
│  │  │                 │  │                 │  │                                 │  │ │
│  │  │  CORS Setup     │  │   /auth/*       │  │  User Management                │  │ │
│  │  │  JWT Auth       │  │   /api/users/*  │  │  Authentication Logic           │  │ │
│  │  │  Rate Limit     │  │  /api/profile   │  │  Data Validation                │  │ │
│  │  │  Error Handle   │  │  /health        │  │  Password Hashing               │  │ │
│  │  │  Logging        │  │  /api/admin/*   │  │  Token Management               │  │ │
│  │  └─────────────────┘  └─────────────────┘  └─────────────────────────────────┘  │ │
│  └─────────────────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────┼────────────────────────────────────────────────┘
                                      │
                                 MongoDB Driver
                                      │
┌─────────────────────────────────────┼────────────────────────────────────────────────┐
│                                DATA TIER                                             │
├─────────────────────────────────────┼────────────────────────────────────────────────┤
│                             MongoDB Database                                         │
│  ┌─────────────────────────────────────────────────────────────────────────────────┐ │
│  │                            Database Schema                                      │ │
│  │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────────────────────┐  │ │
│  │  │   Users Model   │  │   Sessions      │  │        Application Data         │  │ │
│  │  │                 │  │                 │  │                                 │  │ │
│  │  │  User Schema    │  │  JWT Tokens     │  │  Audit Logs                     │  │ │
│  │  │  Validation     │  │  Refresh        │  │  User Preferences               │  │ │
│  │  │  Indexing       │  │  Expiration     │  │  Application Settings           │  │ │
│  │  │  Relationships  │  │  Blacklist      │  │  Performance Metrics            │  │ │
│  │  └─────────────────┘  └─────────────────┘  └─────────────────────────────────┘  │ │
│  └─────────────────────────────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────────────────────────┘
```

### AWS Integration Architecture
```
┌──────────────────────────────────────────────────────────────────────────────────────┐
│                                   Amazon AWS CLOUD                                   │
├──────────────────────────────────────────────────────────────────────────────────────┤
│  🔐 AWS Cognito             API Gateway             S3 Bucket                        │
│  ┌─────────────────┐    ┌─────────────────┐      ┌─────────────────────────────────┐ │
│  │ User Pool       │    │ REST Endpoints  │      │ Static Assets + Files           │ │
│  │ - Registration  │    │ - Rate Limiting │      │ - Flutter Web Build             │ │
│  │ - Authentication│    │ - CORS Setup    │      │ - User Uploads                  │ │
│  │ - JWT Tokens    │    │ - Request Routing│     │ - Backups                       │ │
│  │ - MFA Support   │    │ - Logging       │      │ - CDN Distribution              │ │
│  └─────────────────┘    └─────────────────┘      └─────────────────────────────────┘ │
│            │                        │                           │                    │
│            └────────────────────────┼───────────────────────────┘                    │
│                                     │                                                │
│  🐳 ECS Fargate                CloudWatch              🔧 Systems Manager            │
│  ┌─────────────────┐    ┌──────────────────────┐    ┌─────────────────────────────┐  │
│  │ Container Tasks │    │ Monitoring & Logs    │    │ Configuration Management    │  │
│  │ - Flutter Web   │    │ - Application Logs   │    │ - Environment Variables     │  │
│  │ - Node.js API   │    │ - Performance Metrics│    │ - Secrets Management        │  │
│  │ - NGINX Proxy   │    │ - Custom Dashboards  │    │ - Parameter Store           │  │
│  │ - Auto Scaling  │    │ - Alarms & Alerts    │    │ - Configuration Updates     │  │
│  └─────────────────┘    └──────────────────────┘    └─────────────────────────────┘  │
└──────────────────────────────────────────────────────────────────────────────────────┘
```

## Data Flow Architecture

### Authentication Flow
```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│Flutter SPA  │───▶│AWS Cognito  │───▶│Node.js API  │───▶│MongoDB      │
│Login Screen │    │User Pool    │    │Auth Service │    │User Store   │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
       │                   │                   │                   │
       ▼                   ▼                   ▼                   ▼
1. User enters          2. Cognito          3. API validates    4. User data
   credentials             validates           JWT token           retrieved
   (phone/email +          and issues         and processes       from database
   password)               JWT token          request
```

### API Request Flow
```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│Flutter SPA  │───▶│NGINX Proxy  │───▶│Node.js API  │───▶│MongoDB      │
│HTTP Client  │    │Load Balance │    │Express      │    │Database     │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
       │                   │                   │                   │
       ▼                   ▼                   ▼                   ▼
1. API call with        2. Route request    3. Process business  4. Execute
   JWT token in           to available        logic with data     database
   Authorization          backend server      validation          operations
   header
```

### Real-time Updates Flow
```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│Flutter SPA  │◀──▶│WebSocket    │◀──▶│Node.js API  │◀──▶│MongoDB      │
│State Mgmt   │    │Connection   │    │Socket.IO    │    │Change       │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
       │                   │                   │                   │
       ▼                   ▼                   ▼                   ▼
1. Subscribe to         2. Maintain         3. Broadcast        4. Database
   real-time events       bidirectional       changes to          change events
   (user updates,         WebSocket           connected           trigger
   notifications)         connection          clients             notifications
```

### Client-Server Workflow Details

#### 1. **User Authentication**:
- User enters credentials (username/phone, password)
- Flutter app sends authentication request to AWS Cognito
- Cognito validates credentials and returns JWT token
- Token stored locally for subsequent API calls

#### 2. **Data Retrieval**:
- Flutter app makes authenticated API calls to NGINX proxy
- NGINX forwards requests to available Node.js backend instance
- Backend validates JWT token and processes request
- Backend queries MongoDB for user data
- Response sent back through the chain to Flutter UI

#### 3. **Real-time Updates**:
- WebSocket connections for live data updates
- Push notifications through AWS SNS
- Offline data synchronization capabilities
- State management updates across all connected clients

### Files

```bash
# Flutter SPA Frontend
lib/main.dart                    # 87 lines - App entry point
lib/models/user.dart             # 45 lines - User model
lib/models/api_response.dart     # 25 lines - API wrapper
lib/services/auth_service.dart   # 120 lines - AWS Cognito auth
lib/services/api_service.dart    # 95 lines - HTTP client
lib/services/storage_service.dart # 60 lines - Secure storage
lib/screens/login_screen.dart    # 180 lines - Login UI
lib/screens/home_screen.dart     # 140 lines - Dashboard
lib/screens/profile_screen.dart  # 160 lines - Profile UI
web/index.html                   # HTML5 entry point
web/manifest.json                # PWA configuration

# Configuration
pubspec.yaml                     # Flutter dependencies
.gitignore                       # Git exclusions
docker-compose.yml               # Container orchestration
nginx.conf                       # Reverse proxy config

# Backend API
backend/src/server.js            # Express server
backend/src/models/User.js       # MongoDB model
backend/src/middleware/auth.js   # JWT middleware
backend/src/routes/auth.js       # Auth routes
backend/src/routes/users.js      # User routes

# Deployment Scripts
scripts/setup-dev.sh             # Development setup
scripts/deploy.sh                # AWS deployment
scripts/test-api.sh              # API testing
```

### Cross-Platform Compatibility
- **Android**: Flutter native support
- **Chrome Tablet**: Web responsive design
- **iPad iOS**: PWA with native feel
- **Desktop**: Flutter desktop support

## 🛠️ Prerequisites

### Development Environment

#### Flutter Installation
```bash
# Install Flutter SDK
git clone https://github.com/flutter/flutter.git -b stable
export PATH="$PATH:`pwd`/flutter/bin"

# Verify installation
flutter doctor

# Enable web support
flutter config --enable-web
```

#### AWS CLI Setup
```bash
# Install AWS CLI
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

# Configure AWS credentials
aws configure
```

#### AWS Amplify CLI
```bash
# Install Amplify CLI
npm install -g @aws-amplify/cli

# Configure Amplify
amplify configure
```

#### Node.js and MongoDB
```bash
# Install Node.js (using nvm)
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
nvm install --lts
nvm use --lts
```

#### Docker
```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

## MongoDB Setup

### Local Development MongoDB

#### Option 1: MongoDB Community Server (Local Installation)
```bash
# Ubuntu/Debian Installation
# Import MongoDB public GPG key
wget -qO - https://www.mongodb.org/static/pgp/server-7.0.asc | sudo apt-key add -

# Add MongoDB repository
echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu focal/mongodb-org/7.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-7.0.list

# Update package list and install
sudo apt-get update
sudo apt-get install -y mongodb-org

# Start MongoDB service
sudo systemctl start mongod
sudo systemctl enable mongod

# Verify installation
sudo systemctl status mongod
mongo --version
```

#### Option 2: MongoDB via Docker (Recommended for Development)
```bash
# Pull MongoDB Docker image
docker pull mongo:7.0

# Run MongoDB container
docker run --name mongodb-dev \
  -p 27017:27017 \
  -e MONGO_INITDB_ROOT_USERNAME=admin \
  -e MONGO_INITDB_ROOT_PASSWORD=password123 \
  -e MONGO_INITDB_DATABASE=flutter_spa \
  -v mongodb_data:/data/db \
  -d mongo:7.0

# Check if MongoDB is running
docker ps | grep mongodb-dev

# Connect to MongoDB shell
docker exec -it mongodb-dev mongosh -u admin -p password123
```

#### Local MongoDB Configuration
```bash
# Create application database and user
mongosh "mongodb://admin:password123@localhost:27017"

# In MongoDB shell:
use flutter_spa
db.createUser({
  user: "app_user",
  pwd: "app_password",
  roles: [
    { role: "readWrite", db: "flutter_spa" },
    { role: "dbAdmin", db: "flutter_spa" }
  ]
})

# Test connection
db.users.insertOne({name: "Test User", email: "test@example.com"})
db.users.find()
```

### AWS MongoDB Deployment Options

#### Option 1: MongoDB Atlas (Cloud Service) - Recommended
```bash
# 1. Create MongoDB Atlas Account
# Visit: https://cloud.mongodb.com/

# 2. Create New Cluster
# - Choose AWS as cloud provider
# - Select region (us-east-1 recommended)
# - Choose M0 (Free tier) or M2+ for production

# 3. Configure Network Access
# Add IP addresses or use 0.0.0.0/0 for development
# For production: Add specific VPC CIDR blocks

# 4. Create Database User
# Username: flutter_app
# Password: Generate secure password

# 5. Get Connection String
# Format: mongodb+srv://flutter_app:<password>@cluster0.xxxxx.mongodb.net/flutter_spa?retryWrites=true&w=majority
```

#### Option 2: Self-Managed MongoDB on AWS EC2
```bash
# Launch EC2 Instance (Ubuntu 20.04 LTS)
aws ec2 run-instances \
  --image-id ami-0c02fb55956c7d316 \
  --count 1 \
  --instance-type t3.medium \
  --key-name your-key-pair \
  --security-groups mongodb-sg \
  --user-data '#!/bin/bash
    # Update system
    apt-get update -y
    
    # Install MongoDB
    wget -qO - https://www.mongodb.org/static/pgp/server-7.0.asc | apt-key add -
    echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu focal/mongodb-org/7.0 multiverse" | tee /etc/apt/sources.list.d/mongodb-org-7.0.list
    apt-get update -y
    apt-get install -y mongodb-org
    
    # Configure MongoDB
    sed -i "s/127.0.0.1/0.0.0.0/" /etc/mongod.conf
    
    # Start MongoDB
    systemctl start mongod
    systemctl enable mongod
    
    # Create admin user
    mongosh --eval "
      db.getSiblingDB(\"admin\").createUser({
        user: \"admin\",
        pwd: \"SecurePassword123!\",
        roles: [\"userAdminAnyDatabase\", \"dbAdminAnyDatabase\", \"readWriteAnyDatabase\"]
      })
    "'

# Create Security Group for MongoDB
aws ec2 create-security-group \
  --group-name mongodb-sg \
  --description "MongoDB Security Group"

# Allow MongoDB port (27017) from your application servers
aws ec2 authorize-security-group-ingress \
  --group-name mongodb-sg \
  --protocol tcp \
  --port 27017 \
  --source-group your-app-security-group
```

#### Option 3: MongoDB on AWS DocumentDB (AWS Managed)
```bash
# Create DocumentDB Cluster
aws docdb create-db-cluster \
  --db-cluster-identifier flutter-spa-docdb \
  --engine docdb \
  --master-username admin \
  --master-user-password SecurePassword123! \
  --vpc-security-group-ids sg-xxxxxxxxx \
  --db-subnet-group-name default

# Create DocumentDB Instance
aws docdb create-db-instance \
  --db-instance-identifier flutter-spa-docdb-instance \
  --db-instance-class db.t3.medium \
  --engine docdb \
  --db-cluster-identifier flutter-spa-docdb

# Get connection endpoint
aws docdb describe-db-clusters \
  --db-cluster-identifier flutter-spa-docdb \
  --query 'DBClusters[0].Endpoint'
```

### MongoDB Connection Configuration

#### Environment Variables Setup
```bash
# Local Development (.env)
MONGODB_URI=mongodb://app_user:app_password@localhost:27017/flutter_spa
MONGODB_DATABASE=flutter_spa

# Production with MongoDB Atlas (.env.production)
MONGODB_URI=mongodb+srv://flutter_app:<password>@cluster0.xxxxx.mongodb.net/flutter_spa?retryWrites=true&w=majority
MONGODB_DATABASE=flutter_spa

# Production with AWS DocumentDB (.env.production)
MONGODB_URI=mongodb://admin:SecurePassword123!@flutter-spa-docdb.cluster-xxxxxxxxx.us-east-1.docdb.amazonaws.com:27017/flutter_spa?tls=true&replicaSet=rs0&readPreference=secondaryPreferred&retryWrites=false
MONGODB_DATABASE=flutter_spa
```

#### Node.js Connection Code
```javascript
// backend/src/config/database.js
const mongoose = require('mongoose');

const connectDB = async () => {
  try {
    const conn = await mongoose.connect(process.env.MONGODB_URI, {
      useNewUrlParser: true,
      useUnifiedTopology: true,
      // For AWS DocumentDB
      ...(process.env.NODE_ENV === 'production' && {
        ssl: true,
        sslValidate: false,
        sslCA: require('fs').readFileSync('./rds-combined-ca-bundle.pem')
      })
    });

    console.log(`MongoDB Connected: ${conn.connection.host}`);
    
    // Create indexes
    await createIndexes();
    
  } catch (error) {
    console.error('Database connection error:', error);
    process.exit(1);
  }
};

const createIndexes = async () => {
  try {
    const db = mongoose.connection.db;
    
    // Create indexes for users collection
    await db.collection('users').createIndex({ email: 1 }, { unique: true });
    await db.collection('users').createIndex({ phone: 1 }, { unique: true });
    await db.collection('users').createIndex({ createdAt: 1 });
    
    console.log('Database indexes created successfully');
  } catch (error) {
    console.error('Error creating indexes:', error);
  }
};

module.exports = connectDB;
```

### MongoDB DevOps Scripts

#### Development Scripts
```bash
# scripts/mongodb-dev.sh
#!/bin/bash

start_mongodb() {
    echo "Starting MongoDB for development..."
    
    # Check if MongoDB container exists
    if docker ps -a | grep -q "mongodb-dev"; then
        echo " Starting existing MongoDB container..."
        docker start mongodb-dev
    else
        echo " Creating new MongoDB container..."
        docker run --name mongodb-dev \
            -p 27017:27017 \
            -e MONGO_INITDB_ROOT_USERNAME=admin \
            -e MONGO_INITDB_ROOT_PASSWORD=password123 \
            -e MONGO_INITDB_DATABASE=flutter_spa \
            -v mongodb_data:/data/db \
            -d mongo:7.0
    fi
    
    # Wait for MongoDB to be ready
    echo " Waiting for MongoDB to be ready..."
    sleep 10
    
    # Create application user if not exists
    docker exec mongodb-dev mongosh --quiet --eval "
        use flutter_spa
        try {
            db.createUser({
                user: 'app_user',
                pwd: 'app_password',
                roles: [
                    { role: 'readWrite', db: 'flutter_spa' },
                    { role: 'dbAdmin', db: 'flutter_spa' }
                ]
            })
            print(' Application user created')
        } catch(e) {
            print('ℹ️  Application user already exists')
        }
    " 2>/dev/null || true
    
    echo " MongoDB development server is ready!"
    echo "🔗 Connection: mongodb://app_user:app_password@localhost:27017/flutter_spa"
}

stop_mongodb() {
    echo " Stopping MongoDB development server..."
    docker stop mongodb-dev
    echo " MongoDB stopped"
}

reset_mongodb() {
    echo " Resetting MongoDB development database..."
    docker stop mongodb-dev 2>/dev/null || true
    docker rm mongodb-dev 2>/dev/null || true
    docker volume rm mongodb_data 2>/dev/null || true
    start_mongodb
    echo " MongoDB reset complete"
}

case "$1" in
    start)
        start_mongodb
        ;;
    stop)
        stop_mongodb
        ;;
    reset)
        reset_mongodb
        ;;
    *)
        echo "Usage: $0 {start|stop|reset}"
        exit 1
        ;;
esac
```

#### AWS Deployment Script
```bash
# scripts/deploy-mongodb-aws.sh
#!/bin/bash

deploy_atlas() {
    echo "🌩️  Setting up MongoDB Atlas cluster..."
    
    # Install MongoDB Atlas CLI (if not installed)
    if ! command -v atlas &> /dev/null; then
        echo " Installing MongoDB Atlas CLI..."
        curl -fLo atlas-linux-x86_64.deb https://fastdl.mongodb.org/mongocli/atlas-cli_1.0.0_linux_x86_64.deb
        sudo dpkg -i atlas-cli_1.0.0_linux_x86_64.deb
        rm atlas-cli_1.0.0_linux_x86_64.deb
    fi
    
    # Login to Atlas (requires manual authentication)
    echo "🔐 Please complete Atlas authentication..."
    atlas auth login
    
    # Create project
    PROJECT_NAME="Flutter-SPA-Project"
    atlas projects create "$PROJECT_NAME"
    
    # Create cluster
    CLUSTER_NAME="flutter-spa-cluster"
    atlas clusters create "$CLUSTER_NAME" \
        --provider AWS \
        --region US_EAST_1 \
        --tier M2 \
        --diskSizeGB 10
    
    # Create database user
    atlas dbusers create atlasAdmin \
        --username flutter_app \
        --password "$(openssl rand -base64 32)" \
        --role readWriteAnyDatabase
    
    # Configure network access
    atlas accesslists create \
        --type cidrBlock \
        --cidrBlock "0.0.0.0/0" \
        --comment "Development access"
    
    echo " MongoDB Atlas cluster deployed!"
    echo " Get connection string from Atlas UI"
}

deploy_documentdb() {
    echo "🌩️  Deploying MongoDB on AWS DocumentDB..."
    
    # Create DocumentDB subnet group
    aws docdb create-db-subnet-group \
        --db-subnet-group-name flutter-spa-subnet-group \
        --db-subnet-group-description "Flutter SPA DocumentDB Subnet Group" \
        --subnet-ids subnet-xxxxxx subnet-yyyyyy
    
    # Create security group
    VPC_ID=$(aws ec2 describe-vpcs --filters "Name=is-default,Values=true" --query 'Vpcs[0].VpcId' --output text)
    SG_ID=$(aws ec2 create-security-group \
        --group-name flutter-spa-docdb-sg \
        --description "Flutter SPA DocumentDB Security Group" \
        --vpc-id $VPC_ID \
        --query 'GroupId' --output text)
    
    # Allow DocumentDB port from application security group
    aws ec2 authorize-security-group-ingress \
        --group-id $SG_ID \
        --protocol tcp \
        --port 27017 \
        --source-group $APP_SECURITY_GROUP_ID
    
    # Create DocumentDB cluster
    aws docdb create-db-cluster \
        --db-cluster-identifier flutter-spa-docdb \
        --engine docdb \
        --master-username admin \
        --master-user-password "$(openssl rand -base64 32)" \
        --vpc-security-group-ids $SG_ID \
        --db-subnet-group-name flutter-spa-subnet-group
    
    # Create DocumentDB instance
    aws docdb create-db-instance \
        --db-instance-identifier flutter-spa-docdb-primary \
        --db-instance-class db.t3.medium \
        --engine docdb \
        --db-cluster-identifier flutter-spa-docdb
    
    echo " AWS DocumentDB cluster deployed!"
    echo " Cluster will be available in 10-15 minutes"
}

case "$1" in
    atlas)
        deploy_atlas
        ;;
    documentdb)
        deploy_documentdb
        ;;
    *)
        echo "Usage: $0 {atlas|documentdb}"
        echo "  atlas     - Deploy MongoDB Atlas cluster"
        echo "  documentdb - Deploy AWS DocumentDB cluster"
        exit 1
        ;;
esac
```

### MongoDB Monitoring & Maintenance

#### Health Check Script
```bash
# scripts/mongodb-health.sh
#!/bin/bash

check_local() {
    echo " Checking local MongoDB..."
    if docker exec mongodb-dev mongosh --quiet --eval "db.adminCommand('ping')" 2>/dev/null; then
        echo " Local MongoDB is healthy"
        docker exec mongodb-dev mongosh --quiet --eval "
            use flutter_spa
            print(' Collections: ' + db.getCollectionNames().length)
            print('👥 Users: ' + db.users.countDocuments())
        "
    else
        echo "❌ Local MongoDB is not responding"
        return 1
    fi
}

check_atlas() {
    echo " Checking MongoDB Atlas..."
    if mongosh "$MONGODB_URI" --quiet --eval "db.adminCommand('ping')" 2>/dev/null; then
        echo " MongoDB Atlas is healthy"
        mongosh "$MONGODB_URI" --quiet --eval "
            use $MONGODB_DATABASE
            print(' Collections: ' + db.getCollectionNames().length)
            print('👥 Users: ' + db.users.countDocuments())
        "
    else
        echo "❌ MongoDB Atlas is not responding"
        return 1
    fi
}

backup_database() {
    echo " Creating database backup..."
    BACKUP_DIR="./backups/mongodb/$(date +%Y%m%d_%H%M%S)"
    mkdir -p "$BACKUP_DIR"
    
    if [ "$1" = "local" ]; then
        docker exec mongodb-dev mongodump --db flutter_spa --out /tmp/backup
        docker cp mongodb-dev:/tmp/backup/flutter_spa "$BACKUP_DIR/"
    else
        mongodump --uri "$MONGODB_URI" --out "$BACKUP_DIR"
    fi
    
    echo " Backup created: $BACKUP_DIR"
}

case "$1" in
    local)
        check_local
        ;;
    atlas)
        check_atlas
        ;;
    backup)
        backup_database $2
        ;;
    *)
        echo "Usage: $0 {local|atlas|backup [local|atlas]}"
        exit 1
        ;;
esac
```

## Quick Start

### Development Setup

1. **Clone and Setup**:
```bash
# Navigate to the project directory
cd /path/to/flutter-spa-aws

# Run the setup script (includes MongoDB setup)
./scripts/setup-dev.sh setup
```

2. **Start MongoDB**:
```bash
# Option 1: Start MongoDB with Docker (recommended)
./scripts/mongodb-dev.sh start

# Option 2: Start local MongoDB service
sudo systemctl start mongod

# Verify MongoDB is running
./scripts/mongodb-health.sh local
```

3. **Start Development Servers**:
```bash
# Option 1: Development mode (recommended for development)
./scripts/setup-dev.sh start

# Option 2: Docker Compose (full stack with MongoDB)
./scripts/setup-dev.sh docker
```

4. **Access the Application**:
- **Frontend**: http://localhost:8080
- **Backend API**: http://localhost:3000
- **API Health Check**: http://localhost:3000/health

### Testing

```bash
# Run all tests
./scripts/setup-dev.sh test

# Test API endpoints
./scripts/test-api.sh basic

# Run performance tests
./scripts/test-api.sh performance
```

### Deployment

```bash
# Deploy to AWS
./scripts/deploy.sh full

# Deploy specific components
./scripts/deploy.sh amplify    # Deploy with Amplify
./scripts/deploy.sh ecs       # Deploy with ECS
```

### Verification Commands

```bash
# Verify Flutter project structure
ls -la lib/                    # Check Dart files
flutter pub get               # Install dependencies
flutter doctor                # Verify Flutter setup

# Verify backend structure
ls -la backend/src/           # Check Node.js files
cd backend && npm install     # Install dependencies

# Verify Docker setup
docker-compose config         # Validate compose file
docker-compose build          # Build images

# Full project verification
./scripts/setup-dev.sh verify # Complete health check
```

### 1. Create Flutter Project
```bash
# Create new Flutter project with web and mobile support
flutter create flutter_spa_aws --platforms=web,android,ios
cd flutter_spa_aws

# Add AWS Amplify dependencies
flutter pub add amplify_flutter amplify_auth_cognito amplify_api amplify_storage_s3
flutter pub add http dio shared_preferences
```

### 2. Initialize AWS Amplify Backend
```bash
# Initialize Amplify project
amplify init

# Add authentication with Cognito
amplify add auth

# Add API with GraphQL or REST
amplify add api

# Add storage with S3
amplify add storage

# Deploy backend resources
amplify push
```

### 3. Setup Node.js Backend
```bash
# Create backend directory
mkdir backend && cd backend

# Initialize Node.js project
npm init -y

# Install dependencies
npm install express mongoose cors dotenv jsonwebtoken bcryptjs
npm install -D nodemon
```

### 4. Configure MongoDB
```bash
# Start local MongoDB
sudo systemctl start mongod

# Or configure MongoDB Atlas connection string
# mongodb+srv://<username>:<password>@cluster.mongodb.net/flutter_spa
```

## 🔐 Authentication Setup

### AWS Cognito Configuration

1. **User Pool Creation**:
```bash
# Using AWS CLI
aws cognito-idp create-user-pool \
  --pool-name "FlutterSPAUserPool" \
  --auto-verified-attributes email phone_number
```

2. **User Pool Client**:
```bash
# Create app client
aws cognito-idp create-user-pool-client \
  --user-pool-id us-east-1_XXXXXXXXX \
  --client-name "FlutterSPAClient"
```

### JWT Token Validation
Backend middleware validates JWT tokens from Cognito for secure API access.

## API Gateway Setup

### REST API Endpoints

```bash
# Create API Gateway
aws apigateway create-rest-api --name "FlutterSPAAPI"

# Configure CORS
aws apigateway put-gateway-response \
  --rest-api-id <api-id> \
  --response-type DEFAULT_4XX \
  --response-parameters gatewayresponse.header.Access-Control-Allow-Origin="'*'"
```

### API Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/auth/login` | User authentication | No |
| POST | `/auth/register` | User registration | No |
| GET | `/api/user/profile` | Get user profile | Yes |
| PUT | `/api/user/profile` | Update user profile | Yes |
| GET | `/api/users` | List all users | Yes |
| POST | `/api/users` | Create new user | Yes |

## Testing

### CURL Test Cases

#### Authentication
```bash
# User Login
curl -X POST https://your-api-gateway.amazonaws.com/prod/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "+1234567890",
    "password": "SecurePassword123!"
  }'
```

#### Get User Profile
```bash
# Get authenticated user profile
curl -X GET https://your-api-gateway.amazonaws.com/prod/api/user/profile \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

#### Create User
```bash
# Create new user (admin endpoint)
curl -X POST https://your-api-gateway.amazonaws.com/prod/api/users \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -d '{
    "name": "John Doe",
    "phone": "+1234567890",
    "email": "john.doe@example.com"
  }'
```

#### Update User Profile
```bash
# Update user profile
curl -X PUT https://your-api-gateway.amazonaws.com/prod/api/user/profile \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -d '{
    "name": "John Smith",
    "phone": "+1234567891"
  }'
```

## 🐳 Docker Configuration

### Development Environment
```bash
# Start local development environment
docker-compose up -d

# This starts:
# - MongoDB database
# - Node.js API server
# - NGINX reverse proxy
# - Flutter web development server
```

### Production Build
```bash
# Build Flutter web app
flutter build web --release

# Build and push Docker images
docker build -t flutter-spa:latest ./frontend
docker build -t flutter-api:latest ./backend

# Push to AWS ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account>.dkr.ecr.us-east-1.amazonaws.com
docker tag flutter-spa:latest <account>.dkr.ecr.us-east-1.amazonaws.com/flutter-spa:latest
docker push <account>.dkr.ecr.us-east-1.amazonaws.com/flutter-spa:latest
```

## ☁️ Amazon AWS Deployment

### Using AWS Amplify Hosting
```bash
# Deploy frontend to Amplify
amplify add hosting
amplify publish

# Custom domain configuration
amplify add custom-domain
```

### Using ECS with Fargate
```bash
# Deploy containerized applications
aws ecs create-cluster --cluster-name flutter-spa-cluster

# Create task definitions and services
aws ecs create-task-definition --cli-input-json file://task-definition.json
aws ecs create-service --cluster flutter-spa-cluster --service-name flutter-spa-service
```

### Infrastructure as Code

#### CloudFormation
```bash
# Deploy infrastructure
aws cloudformation create-stack \
  --stack-name flutter-spa-infrastructure \
  --template-body file://infrastructure/cloudformation/template.yaml \
  --capabilities CAPABILITY_IAM
```

#### Terraform
```bash
# Initialize Terraform
terraform init

# Plan deployment
terraform plan

# Apply infrastructure changes
terraform apply
```

## Load Balancing & Scaling

### NGINX Configuration
- Reverse proxy for API requests
- Static file serving for Flutter web assets
- SSL termination
- Rate limiting and security headers

### Amazon AWS Application Load Balancer (ALB)
- Health checks for backend services
- Auto-scaling based on CPU/memory metrics
- Multi-AZ deployment for high availability

**What is an Application Load Balancer?**

A load balancer serves as the single point of contact for clients. The load balancer distributes incoming application traffic across multiple targets, such as EC2 instances, in multiple Availability Zones.

![alt text](https://github.com/jylhakos/InternetOfThings/blob/main/Frameworks/Frontend/Flutter/load_balancer.png?raw=true)

*Figure: Application Load Balancer*

## 🔒 Security

1. **Authentication & Authorization**:
   - JWT tokens with short expiration
   - Refresh token rotation
   - Role-based access control (RBAC)

2. **API Security**:
   - Input validation and sanitization
   - Rate limiting per user/IP
   - CORS configuration
   - SQL injection prevention

3. **Infrastructure Security**:
   - VPC with private subnets
   - Security groups with minimal access
   - IAM roles with least privilege
   - AWS Secrets Manager for credentials

## Monitoring & Logging

### AWS CloudWatch
- Application logs aggregation
- Custom metrics and alarms
- Performance monitoring dashboards

### Error Tracking
- AWS X-Ray for distributed tracing
- Application error logging
- User interaction analytics

## CI/CD Pipeline

### GitHub Actions
```yaml
# Automated testing, building, and deployment
# Triggered on push to main branch
# Deploys to staging first, then production after approval
```

### Deployment Stages
1. **Development**: Local development with hot reload
2. **Staging**: AWS staging environment for testing
3. **Production**: Full AWS production deployment

## Resources

- [AWS Amplify Flutter Documentation](https://docs.amplify.aws/gen1/flutter/)
- [Flutter Web Deployment Guide](https://docs.flutter.dev/deployment/web)
- [AWS API Gateway Documentation](https://docs.aws.amazon.com/apigateway/)
- [MongoDB Atlas Documentation](https://docs.atlas.mongodb.com/)
- [AWS Cognito Integration Guide](https://docs.aws.amazon.com/cognito/latest/developerguide/)


## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.
