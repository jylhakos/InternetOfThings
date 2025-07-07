#!/bin/bash

# AWS Deployment Script for LLM Chat Service
# This script deploys the Spring Boot application and Ollama to AWS

set -e

# Configuration
AWS_REGION="${AWS_REGION:-us-east-1}"
KEY_PAIR_NAME="${KEY_PAIR_NAME:-llm-chat-key}"
SECURITY_GROUP_NAME="llm-chat-security-group"
INSTANCE_TYPE="${INSTANCE_TYPE:-m5.xlarge}"  # Minimum for Ollama with Llama-3
AMI_ID="${AMI_ID:-ami-0c02fb55956c7d316}"  # Amazon Linux 2 AMI (update as needed)
INSTANCE_NAME="llm-chat-service"

echo "🚀 Deploying LLM Chat Service to AWS"
echo "Region: $AWS_REGION"
echo "Instance Type: $INSTANCE_TYPE"

# Check if AWS CLI is installed and configured
command -v aws >/dev/null 2>&1 || { echo "❌ AWS CLI is required but not installed. Aborting." >&2; exit 1; }

# Check AWS credentials
aws sts get-caller-identity >/dev/null 2>&1 || { echo "❌ AWS credentials not configured. Run 'aws configure' first." >&2; exit 1; }

echo "✅ AWS CLI configured"

# Create security group if it doesn't exist
echo "🔒 Setting up security group..."
if ! aws ec2 describe-security-groups --group-names "$SECURITY_GROUP_NAME" --region "$AWS_REGION" >/dev/null 2>&1; then
    echo "Creating security group: $SECURITY_GROUP_NAME"
    SECURITY_GROUP_ID=$(aws ec2 create-security-group \
        --group-name "$SECURITY_GROUP_NAME" \
        --description "Security group for LLM Chat Service" \
        --region "$AWS_REGION" \
        --query 'GroupId' --output text)
        
    # Add rules
    aws ec2 authorize-security-group-ingress \
        --group-id "$SECURITY_GROUP_ID" \
        --protocol tcp \
        --port 22 \
        --cidr 0.0.0.0/0 \
        --region "$AWS_REGION"
        
    aws ec2 authorize-security-group-ingress \
        --group-id "$SECURITY_GROUP_ID" \
        --protocol tcp \
        --port 8080 \
        --cidr 0.0.0.0/0 \
        --region "$AWS_REGION"
        
    aws ec2 authorize-security-group-ingress \
        --group-id "$SECURITY_GROUP_ID" \
        --protocol tcp \
        --port 11434 \
        --cidr 0.0.0.0/0 \
        --region "$AWS_REGION"
else
    SECURITY_GROUP_ID=$(aws ec2 describe-security-groups \
        --group-names "$SECURITY_GROUP_NAME" \
        --region "$AWS_REGION" \
        --query 'SecurityGroups[0].GroupId' --output text)
    echo "Using existing security group: $SECURITY_GROUP_ID"
fi

# Create key pair if it doesn't exist
echo "🔑 Setting up key pair..."
if ! aws ec2 describe-key-pairs --key-names "$KEY_PAIR_NAME" --region "$AWS_REGION" >/dev/null 2>&1; then
    echo "Creating key pair: $KEY_PAIR_NAME"
    aws ec2 create-key-pair \
        --key-name "$KEY_PAIR_NAME" \
        --region "$AWS_REGION" \
        --query 'KeyMaterial' --output text > "${KEY_PAIR_NAME}.pem"
    chmod 400 "${KEY_PAIR_NAME}.pem"
    echo "Key pair saved as ${KEY_PAIR_NAME}.pem"
else
    echo "Using existing key pair: $KEY_PAIR_NAME"
    if [ ! -f "${KEY_PAIR_NAME}.pem" ]; then
        echo "⚠️  Key file ${KEY_PAIR_NAME}.pem not found. You may need to provide it manually."
    fi
fi

# Create user data script
cat > user-data.sh << 'EOF'
#!/bin/bash
yum update -y

# Install Java 17
yum install -y java-17-amazon-corretto-devel

# Install Docker
yum install -y docker
systemctl start docker
systemctl enable docker
usermod -a -G docker ec2-user

# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Create systemd service for Ollama
cat > /etc/systemd/system/ollama.service << 'OLLAMA_SERVICE'
[Unit]
Description=Ollama Server
After=network-online.target

[Service]
ExecStart=/usr/local/bin/ollama serve
User=ec2-user
Group=ec2-user
Restart=always
RestartSec=3
Environment="OLLAMA_HOST=0.0.0.0"

[Install]
WantedBy=default.target
OLLAMA_SERVICE

systemctl daemon-reload
systemctl enable ollama
systemctl start ollama

# Wait for Ollama to start
sleep 10

# Pull Llama-3 model
sudo -u ec2-user ollama pull llama3

# Create application directory
mkdir -p /opt/llm-chat
chown ec2-user:ec2-user /opt/llm-chat

# Install Maven
cd /opt
wget https://dlcdn.apache.org/maven/maven-3/3.9.6/binaries/apache-maven-3.9.6-bin.tar.gz
tar xzf apache-maven-3.9.6-bin.tar.gz
ln -s apache-maven-3.9.6 maven
echo 'export PATH=/opt/maven/bin:$PATH' >> /home/ec2-user/.bashrc

# Create startup script
cat > /home/ec2-user/start-app.sh << 'START_SCRIPT'
#!/bin/bash
cd /opt/llm-chat

# Ensure Ollama is running
if ! systemctl is-active --quiet ollama; then
    sudo systemctl start ollama
    sleep 5
fi

# Start Spring Boot application
export PATH=/opt/maven/bin:$PATH
export JAVA_HOME=/usr/lib/jvm/java-17-amazon-corretto
nohup mvn spring-boot:run > app.log 2>&1 &
echo $! > app.pid
START_SCRIPT

chmod +x /home/ec2-user/start-app.sh
chown ec2-user:ec2-user /home/ec2-user/start-app.sh

echo "User data script completed" > /tmp/userdata.log
EOF

# Launch EC2 instance
echo "🖥️  Launching EC2 instance..."
INSTANCE_ID=$(aws ec2 run-instances \
    --image-id "$AMI_ID" \
    --count 1 \
    --instance-type "$INSTANCE_TYPE" \
    --key-name "$KEY_PAIR_NAME" \
    --security-group-ids "$SECURITY_GROUP_ID" \
    --user-data file://user-data.sh \
    --tag-specifications "ResourceType=instance,Tags=[{Key=Name,Value=$INSTANCE_NAME}]" \
    --region "$AWS_REGION" \
    --query 'Instances[0].InstanceId' --output text)

echo "✅ Instance launched: $INSTANCE_ID"

# Wait for instance to be running
echo "⏳ Waiting for instance to be running..."
aws ec2 wait instance-running --instance-ids "$INSTANCE_ID" --region "$AWS_REGION"

# Get public IP
PUBLIC_IP=$(aws ec2 describe-instances \
    --instance-ids "$INSTANCE_ID" \
    --region "$AWS_REGION" \
    --query 'Reservations[0].Instances[0].PublicIpAddress' --output text)

echo "✅ Instance is running at IP: $PUBLIC_IP"

# Create deployment script
cat > deploy-app.sh << EOF
#!/bin/bash
echo "📦 Deploying application to AWS instance..."

# Wait for instance to be ready
echo "⏳ Waiting for instance to be ready for SSH..."
while ! ssh -o ConnectTimeout=5 -o StrictHostKeyChecking=no -i "${KEY_PAIR_NAME}.pem" ec2-user@$PUBLIC_IP "echo 'ready'" 2>/dev/null; do
    sleep 10
done

echo "✅ Instance is ready for deployment"

# Copy application files
echo "📁 Copying application files..."
scp -o StrictHostKeyChecking=no -i "${KEY_PAIR_NAME}.pem" -r ../pom.xml ../src ec2-user@$PUBLIC_IP:/opt/llm-chat/

# Build and start application
echo "🔨 Building and starting application..."
ssh -o StrictHostKeyChecking=no -i "${KEY_PAIR_NAME}.pem" ec2-user@$PUBLIC_IP "
    cd /opt/llm-chat
    export PATH=/opt/maven/bin:\$PATH
    export JAVA_HOME=/usr/lib/jvm/java-17-amazon-corretto
    mvn clean package -DskipTests
    ./start-app.sh
"

echo "✅ Application deployed successfully!"
echo ""
echo "🎯 Access your application:"
echo "Web Interface: http://$PUBLIC_IP:8080"
echo "API Endpoint: http://$PUBLIC_IP:8080/api/v1/chat"
echo "Health Check: http://$PUBLIC_IP:8080/api/v1/chat/health"
echo ""
echo "🔗 SSH Access:"
echo "ssh -i ${KEY_PAIR_NAME}.pem ec2-user@$PUBLIC_IP"
EOF

chmod +x deploy-app.sh

echo "✅ AWS infrastructure deployed!"
echo ""
echo "🎯 Next steps:"
echo "1. Run './deploy-app.sh' to deploy the application"
echo "2. Wait for the deployment to complete (may take 10-15 minutes)"
echo "3. Access your application at http://$PUBLIC_IP:8080"
echo ""
echo "💡 Instance Details:"
echo "Instance ID: $INSTANCE_ID"
echo "Public IP: $PUBLIC_IP"
echo "Key File: ${KEY_PAIR_NAME}.pem"
echo ""
echo "🗑️  To clean up resources later:"
echo "aws ec2 terminate-instances --instance-ids $INSTANCE_ID --region $AWS_REGION"

# Clean up
rm -f user-data.sh
