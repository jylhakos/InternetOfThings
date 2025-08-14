#!/bin/bash

# AWS MongoDB Deployment Script
# Usage: ./scripts/deploy-mongodb-aws.sh {atlas|documentdb|ec2|help}

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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

check_aws_cli() {
    if ! command -v aws &> /dev/null; then
        print_error "AWS CLI is not installed. Please install it first."
        echo "Installation: https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html"
        exit 1
    fi
    
    if ! aws sts get-caller-identity &>/dev/null; then
        print_error "AWS credentials are not configured. Please run 'aws configure'."
        exit 1
    fi
}

deploy_atlas() {
    print_status "🌩️  Setting up MongoDB Atlas cluster..."
    
    # Check if Atlas CLI is installed
    if ! command -v atlas &> /dev/null; then
        print_status "📦 Installing MongoDB Atlas CLI..."
        
        # Detect OS
        if [[ "$OSTYPE" == "linux-gnu"* ]]; then
            curl -fLo atlas-linux-x86_64.deb https://fastdl.mongodb.org/mongocli/atlas-cli_1.0.0_linux_x86_64.deb
            sudo dpkg -i atlas-cli_1.0.0_linux_x86_64.deb
            rm atlas-cli_1.0.0_linux_x86_64.deb
        elif [[ "$OSTYPE" == "darwin"* ]]; then
            brew install mongodb-atlas-cli
        else
            print_error "Unsupported OS for automatic Atlas CLI installation"
            print_status "Please install manually from: https://www.mongodb.com/docs/atlas/cli/stable/install-atlas-cli/"
            exit 1
        fi
        
        print_success "MongoDB Atlas CLI installed"
    fi
    
    # Check if already authenticated
    if ! atlas auth whoami &>/dev/null; then
        print_status "🔐 Authenticating with MongoDB Atlas..."
        print_status "This will open a browser window for authentication."
        read -p "Press Enter to continue..."
        atlas auth login
    fi
    
    # Get current user info
    USER_INFO=$(atlas auth whoami)
    print_success "Authenticated as: $USER_INFO"
    
    # Create or select project
    PROJECT_NAME="Flutter-SPA-AWS"
    print_status "📁 Creating/selecting project: $PROJECT_NAME"
    
    PROJECT_ID=$(atlas projects create "$PROJECT_NAME" --output json 2>/dev/null | jq -r '.id' || \
                 atlas projects list --output json | jq -r ".results[] | select(.name==\"$PROJECT_NAME\") | .id")
    
    if [ "$PROJECT_ID" = "null" ] || [ -z "$PROJECT_ID" ]; then
        print_error "Failed to create or find project"
        exit 1
    fi
    
    print_success "Project ID: $PROJECT_ID"
    
    # Set project context
    atlas config set project_id "$PROJECT_ID"
    
    # Create cluster
    CLUSTER_NAME="flutter-spa-cluster"
    print_status "🚀 Creating MongoDB Atlas cluster: $CLUSTER_NAME"
    
    # Check if cluster already exists
    if atlas clusters describe "$CLUSTER_NAME" &>/dev/null; then
        print_warning "Cluster $CLUSTER_NAME already exists"
    else
        atlas clusters create "$CLUSTER_NAME" \
            --provider AWS \
            --region US_EAST_1 \
            --tier M2 \
            --diskSizeGB 10 \
            --output json
        
        print_status "⏳ Waiting for cluster to be created (this may take 5-10 minutes)..."
        
        # Wait for cluster to be ready
        while true; do
            STATUS=$(atlas clusters describe "$CLUSTER_NAME" --output json | jq -r '.stateName')
            if [ "$STATUS" = "IDLE" ]; then
                print_success "Cluster is ready!"
                break
            elif [ "$STATUS" = "CREATING" ]; then
                print_status "Cluster status: $STATUS - waiting..."
                sleep 30
            else
                print_error "Unexpected cluster status: $STATUS"
                exit 1
            fi
        done
    fi
    
    # Create database user
    DB_USERNAME="flutter_app"
    DB_PASSWORD=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-25)
    
    print_status "👤 Creating database user: $DB_USERNAME"
    
    atlas dbusers create atlasAdmin \
        --username "$DB_USERNAME" \
        --password "$DB_PASSWORD" \
        --role readWriteAnyDatabase \
        --output json || print_warning "User may already exist"
    
    # Configure network access
    print_status "🌐 Configuring network access..."
    
    # Add current IP
    CURRENT_IP=$(curl -s ifconfig.me)
    atlas accesslists create \
        --type ipAddress \
        --ipAddress "$CURRENT_IP" \
        --comment "Development machine" \
        --output json || print_warning "IP may already be added"
    
    # Add common AWS regions (for production deployment)
    atlas accesslists create \
        --type cidrBlock \
        --cidrBlock "0.0.0.0/0" \
        --comment "All access (configure properly for production)" \
        --output json || print_warning "CIDR may already be added"
    
    # Get connection string
    CONNECTION_STRING=$(atlas clusters connectionStrings describe "$CLUSTER_NAME" --output json | jq -r '.standardSrv')
    CONNECTION_STRING=$(echo "$CONNECTION_STRING" | sed "s/<username>/$DB_USERNAME/" | sed "s/<password>/$DB_PASSWORD/")
    
    # Save configuration
    mkdir -p ./config
    cat > ./config/mongodb-atlas.env << EOF
# MongoDB Atlas Configuration
MONGODB_URI=$CONNECTION_STRING
MONGODB_DATABASE=flutter_spa
MONGODB_USERNAME=$DB_USERNAME
MONGODB_PASSWORD=$DB_PASSWORD
CLUSTER_NAME=$CLUSTER_NAME
PROJECT_ID=$PROJECT_ID
EOF
    
    print_success "🎉 MongoDB Atlas deployment complete!"
    echo
    print_success "📋 Configuration saved to: ./config/mongodb-atlas.env"
    print_success "🔗 Connection String: $CONNECTION_STRING"
    print_success "👤 Username: $DB_USERNAME"
    print_success "🔑 Password: $DB_PASSWORD"
    echo
    print_status "🌍 Atlas Dashboard: https://cloud.mongodb.com/v2/$PROJECT_ID#clusters"
    
    # Test connection
    print_status "🧪 Testing connection..."
    if command -v mongosh &> /dev/null; then
        timeout 10 mongosh "$CONNECTION_STRING/flutter_spa" --quiet --eval "db.adminCommand('ping')" && \
        print_success "✅ Connection test successful!" || \
        print_warning "⚠️  Connection test failed (may need time to propagate)"
    else
        print_warning "⚠️  Install mongosh to test the connection"
    fi
}

deploy_documentdb() {
    check_aws_cli
    
    print_status "🌩️  Deploying AWS DocumentDB cluster..."
    
    # Configuration
    CLUSTER_NAME="flutter-spa-docdb"
    INSTANCE_NAME="flutter-spa-docdb-primary"
    DB_USERNAME="admin"
    DB_PASSWORD=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-25)
    INSTANCE_CLASS="db.t3.medium"
    
    # Get VPC information
    print_status "🌐 Getting VPC information..."
    DEFAULT_VPC=$(aws ec2 describe-vpcs --filters "Name=is-default,Values=true" --query 'Vpcs[0].VpcId' --output text)
    
    if [ "$DEFAULT_VPC" = "None" ] || [ -z "$DEFAULT_VPC" ]; then
        print_error "No default VPC found. Please create a VPC first."
        exit 1
    fi
    
    print_success "Using VPC: $DEFAULT_VPC"
    
    # Get subnets
    SUBNETS=$(aws ec2 describe-subnets --filters "Name=vpc-id,Values=$DEFAULT_VPC" --query 'Subnets[*].SubnetId' --output text)
    SUBNET_ARRAY=($SUBNETS)
    
    if [ ${#SUBNET_ARRAY[@]} -lt 2 ]; then
        print_error "At least 2 subnets required in different AZs for DocumentDB"
        exit 1
    fi
    
    print_success "Using subnets: ${SUBNET_ARRAY[0]} ${SUBNET_ARRAY[1]}"
    
    # Create subnet group
    print_status "🏗️  Creating DocumentDB subnet group..."
    aws docdb create-db-subnet-group \
        --db-subnet-group-name "$CLUSTER_NAME-subnet-group" \
        --db-subnet-group-description "Flutter SPA DocumentDB Subnet Group" \
        --subnet-ids ${SUBNET_ARRAY[0]} ${SUBNET_ARRAY[1]} \
        --output json || print_warning "Subnet group may already exist"
    
    # Create security group
    print_status "🔒 Creating security group..."
    SG_ID=$(aws ec2 create-security-group \
        --group-name "$CLUSTER_NAME-sg" \
        --description "Flutter SPA DocumentDB Security Group" \
        --vpc-id "$DEFAULT_VPC" \
        --query 'GroupId' --output text) || {
        # Get existing security group
        SG_ID=$(aws ec2 describe-security-groups \
            --filters "Name=group-name,Values=$CLUSTER_NAME-sg" \
            --query 'SecurityGroups[0].GroupId' --output text)
        print_warning "Using existing security group: $SG_ID"
    }
    
    # Add rules to security group (allow DocumentDB port from anywhere - configure properly for production)
    aws ec2 authorize-security-group-ingress \
        --group-id "$SG_ID" \
        --protocol tcp \
        --port 27017 \
        --cidr 0.0.0.0/0 || print_warning "Security group rule may already exist"
    
    print_success "Security group: $SG_ID"
    
    # Create DocumentDB cluster
    print_status "🚀 Creating DocumentDB cluster..."
    aws docdb create-db-cluster \
        --db-cluster-identifier "$CLUSTER_NAME" \
        --engine docdb \
        --master-username "$DB_USERNAME" \
        --master-user-password "$DB_PASSWORD" \
        --vpc-security-group-ids "$SG_ID" \
        --db-subnet-group-name "$CLUSTER_NAME-subnet-group" \
        --port 27017 \
        --output json || print_warning "Cluster may already exist"
    
    print_status "⏳ Waiting for cluster to be available..."
    aws docdb wait db-cluster-available --db-cluster-identifier "$CLUSTER_NAME"
    
    # Create DocumentDB instance
    print_status "💾 Creating DocumentDB instance..."
    aws docdb create-db-instance \
        --db-instance-identifier "$INSTANCE_NAME" \
        --db-instance-class "$INSTANCE_CLASS" \
        --engine docdb \
        --db-cluster-identifier "$CLUSTER_NAME" \
        --output json || print_warning "Instance may already exist"
    
    print_status "⏳ Waiting for instance to be available..."
    aws docdb wait db-instance-available --db-instance-identifier "$INSTANCE_NAME"
    
    # Get cluster endpoint
    CLUSTER_ENDPOINT=$(aws docdb describe-db-clusters \
        --db-cluster-identifier "$CLUSTER_NAME" \
        --query 'DBClusters[0].Endpoint' --output text)
    
    CLUSTER_PORT=$(aws docdb describe-db-clusters \
        --db-cluster-identifier "$CLUSTER_NAME" \
        --query 'DBClusters[0].Port' --output text)
    
    # Download RDS CA certificate
    print_status "📄 Downloading RDS CA certificate..."
    mkdir -p ./certs
    curl -o ./certs/rds-combined-ca-bundle.pem https://truststore.pki.rds.amazonaws.com/global/global-bundle.pem
    
    # Create connection string
    CONNECTION_STRING="mongodb://$DB_USERNAME:$DB_PASSWORD@$CLUSTER_ENDPOINT:$CLUSTER_PORT/flutter_spa?tls=true&replicaSet=rs0&readPreference=secondaryPreferred&retryWrites=false"
    
    # Save configuration
    mkdir -p ./config
    cat > ./config/mongodb-documentdb.env << EOF
# AWS DocumentDB Configuration
MONGODB_URI=$CONNECTION_STRING
MONGODB_DATABASE=flutter_spa
MONGODB_USERNAME=$DB_USERNAME
MONGODB_PASSWORD=$DB_PASSWORD
MONGODB_HOST=$CLUSTER_ENDPOINT
MONGODB_PORT=$CLUSTER_PORT
CLUSTER_NAME=$CLUSTER_NAME
SECURITY_GROUP_ID=$SG_ID
TLS_CA_FILE=./certs/rds-combined-ca-bundle.pem
EOF
    
    print_success "🎉 AWS DocumentDB deployment complete!"
    echo
    print_success "📋 Configuration saved to: ./config/mongodb-documentdb.env"
    print_success "🔗 Connection String: $CONNECTION_STRING"
    print_success "🌍 Endpoint: $CLUSTER_ENDPOINT:$CLUSTER_PORT"
    print_success "👤 Username: $DB_USERNAME"
    print_success "🔑 Password: $DB_PASSWORD"
    echo
    print_warning "⚠️  Configure security group rules properly for production!"
    print_status "📊 AWS Console: https://console.aws.amazon.com/docdb/home"
}

deploy_ec2() {
    check_aws_cli
    
    print_status "🌩️  Deploying MongoDB on AWS EC2..."
    
    # Configuration
    INSTANCE_NAME="flutter-spa-mongodb"
    INSTANCE_TYPE="t3.medium"
    KEY_NAME="flutter-spa-key"
    SECURITY_GROUP_NAME="mongodb-sg"
    
    # Check if key pair exists
    if ! aws ec2 describe-key-pairs --key-names "$KEY_NAME" &>/dev/null; then
        print_status "🔑 Creating EC2 key pair..."
        aws ec2 create-key-pair --key-name "$KEY_NAME" --query 'KeyMaterial' --output text > "$KEY_NAME.pem"
        chmod 600 "$KEY_NAME.pem"
        print_success "Key pair created: $KEY_NAME.pem"
    fi
    
    # Get latest Ubuntu AMI
    AMI_ID=$(aws ec2 describe-images \
        --owners 099720109477 \
        --filters "Name=name,Values=ubuntu/images/hvm-ssd/ubuntu-focal-20.04-amd64-server-*" \
        --query 'Images | sort_by(@, &CreationDate) | [-1].ImageId' \
        --output text)
    
    print_success "Using AMI: $AMI_ID"
    
    # Create security group
    print_status "🔒 Creating security group..."
    VPC_ID=$(aws ec2 describe-vpcs --filters "Name=is-default,Values=true" --query 'Vpcs[0].VpcId' --output text)
    
    SG_ID=$(aws ec2 create-security-group \
        --group-name "$SECURITY_GROUP_NAME" \
        --description "MongoDB Security Group for Flutter SPA" \
        --vpc-id "$VPC_ID" \
        --query 'GroupId' --output text) || {
        SG_ID=$(aws ec2 describe-security-groups \
            --filters "Name=group-name,Values=$SECURITY_GROUP_NAME" \
            --query 'SecurityGroups[0].GroupId' --output text)
        print_warning "Using existing security group: $SG_ID"
    }
    
    # Add security group rules
    aws ec2 authorize-security-group-ingress \
        --group-id "$SG_ID" \
        --protocol tcp \
        --port 22 \
        --cidr 0.0.0.0/0 || true # SSH
    
    aws ec2 authorize-security-group-ingress \
        --group-id "$SG_ID" \
        --protocol tcp \
        --port 27017 \
        --cidr 0.0.0.0/0 || true # MongoDB
    
    # Create user data script
    USER_DATA_SCRIPT=$(cat << 'EOF'
#!/bin/bash
set -e

# Update system
apt-get update -y
apt-get upgrade -y

# Install MongoDB
wget -qO - https://www.mongodb.org/static/pgp/server-7.0.asc | apt-key add -
echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu focal/mongodb-org/7.0 multiverse" | tee /etc/apt/sources.list.d/mongodb-org-7.0.list
apt-get update -y
apt-get install -y mongodb-org

# Configure MongoDB to accept connections from anywhere (configure properly for production)
sed -i 's/127.0.0.1/0.0.0.0/' /etc/mongod.conf

# Enable authentication
echo 'security:' >> /etc/mongod.conf
echo '  authorization: enabled' >> /etc/mongod.conf

# Start MongoDB
systemctl start mongod
systemctl enable mongod

# Wait for MongoDB to start
sleep 10

# Create admin user
mongosh --eval "
db.getSiblingDB('admin').createUser({
  user: 'admin',
  pwd: 'SecurePassword123!',
  roles: ['userAdminAnyDatabase', 'dbAdminAnyDatabase', 'readWriteAnyDatabase']
})
"

# Create application user
mongosh -u admin -p SecurePassword123! --authenticationDatabase admin --eval "
db.getSiblingDB('flutter_spa').createUser({
  user: 'flutter_app',
  pwd: 'AppPassword123!',
  roles: [
    { role: 'readWrite', db: 'flutter_spa' },
    { role: 'dbAdmin', db: 'flutter_spa' }
  ]
})
"

# Create indexes
mongosh -u flutter_app -p AppPassword123! --authenticationDatabase flutter_spa --eval "
use flutter_spa
db.users.createIndex({ 'email': 1 }, { unique: true })
db.users.createIndex({ 'phone': 1 }, { unique: true })
db.users.createIndex({ 'createdAt': 1 })
"

echo "MongoDB setup complete!" > /var/log/mongodb-setup.log
EOF
)
    
    # Launch EC2 instance
    print_status "🚀 Launching EC2 instance..."
    INSTANCE_ID=$(aws ec2 run-instances \
        --image-id "$AMI_ID" \
        --count 1 \
        --instance-type "$INSTANCE_TYPE" \
        --key-name "$KEY_NAME" \
        --security-group-ids "$SG_ID" \
        --user-data "$USER_DATA_SCRIPT" \
        --tag-specifications "ResourceType=instance,Tags=[{Key=Name,Value=$INSTANCE_NAME}]" \
        --query 'Instances[0].InstanceId' \
        --output text)
    
    print_success "Instance launched: $INSTANCE_ID"
    print_status "⏳ Waiting for instance to be running..."
    aws ec2 wait instance-running --instance-ids "$INSTANCE_ID"
    
    # Get public IP
    PUBLIC_IP=$(aws ec2 describe-instances \
        --instance-ids "$INSTANCE_ID" \
        --query 'Reservations[0].Instances[0].PublicIpAddress' \
        --output text)
    
    print_success "Instance is running!"
    print_success "Public IP: $PUBLIC_IP"
    
    # Wait for MongoDB setup to complete
    print_status "⏳ Waiting for MongoDB setup to complete (this may take 5-10 minutes)..."
    sleep 300 # Wait 5 minutes for setup
    
    # Save configuration
    mkdir -p ./config
    cat > ./config/mongodb-ec2.env << EOF
# AWS EC2 MongoDB Configuration
MONGODB_URI=mongodb://flutter_app:AppPassword123!@$PUBLIC_IP:27017/flutter_spa
MONGODB_DATABASE=flutter_spa
MONGODB_HOST=$PUBLIC_IP
MONGODB_PORT=27017
MONGODB_USERNAME=flutter_app
MONGODB_PASSWORD=AppPassword123!
INSTANCE_ID=$INSTANCE_ID
SECURITY_GROUP_ID=$SG_ID
KEY_FILE=$KEY_NAME.pem
EOF
    
    print_success "🎉 MongoDB EC2 deployment complete!"
    echo
    print_success "📋 Configuration saved to: ./config/mongodb-ec2.env"
    print_success "🔗 Connection String: mongodb://flutter_app:AppPassword123!@$PUBLIC_IP:27017/flutter_spa"
    print_success "🌍 Public IP: $PUBLIC_IP"
    print_success "🔑 SSH Key: $KEY_NAME.pem"
    echo
    print_status "SSH Command: ssh -i $KEY_NAME.pem ubuntu@$PUBLIC_IP"
    print_warning "⚠️  Configure security groups properly for production!"
}

show_help() {
    echo "AWS MongoDB Deployment Script"
    echo
    echo "Usage: $0 {atlas|documentdb|ec2|help}"
    echo
    echo "Commands:"
    echo "  atlas      - Deploy MongoDB Atlas cluster (recommended)"
    echo "  documentdb - Deploy AWS DocumentDB cluster"
    echo "  ec2        - Deploy MongoDB on EC2 instance"
    echo "  help       - Show this help message"
    echo
    echo "Examples:"
    echo "  $0 atlas                # Deploy MongoDB Atlas"
    echo "  $0 documentdb           # Deploy AWS DocumentDB"
    echo "  $0 ec2                  # Deploy MongoDB on EC2"
    echo
    echo "Prerequisites:"
    echo "  - AWS CLI installed and configured"
    echo "  - Appropriate AWS permissions"
    echo "  - For Atlas: Internet connection for authentication"
}

# Main script logic
case "$1" in
    atlas)
        deploy_atlas
        ;;
    documentdb)
        deploy_documentdb
        ;;
    ec2)
        deploy_ec2
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
