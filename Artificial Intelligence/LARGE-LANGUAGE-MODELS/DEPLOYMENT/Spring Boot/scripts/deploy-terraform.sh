#!/bin/bash

# Terraform deployment script for AWS
set -e

echo "🏗️  Deploying LLM Chat Service with Terraform"

# Check prerequisites
command -v terraform >/dev/null 2>&1 || { echo "❌ Terraform is required but not installed."; exit 1; }
command -v aws >/dev/null 2>&1 || { echo "❌ AWS CLI is required but not installed."; exit 1; }

# Check AWS credentials
aws sts get-caller-identity >/dev/null 2>&1 || { echo "❌ AWS credentials not configured."; exit 1; }

cd terraform

# Initialize Terraform
echo "🔄 Initializing Terraform..."
terraform init

# Plan deployment
echo "📋 Planning deployment..."
terraform plan -out=tfplan

# Ask for confirmation
echo ""
read -p "Do you want to proceed with the deployment? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Deployment cancelled."
    exit 1
fi

# Apply configuration
echo "🚀 Applying Terraform configuration..."
terraform apply tfplan

# Get outputs
echo ""
echo "✅ Deployment completed!"
echo ""
echo "📊 Infrastructure Details:"
terraform output

# Create deployment script
echo ""
echo "📦 Creating application deployment script..."

INSTANCE_IP=$(terraform output -raw instance_public_ip)
ALB_DNS=$(terraform output -raw load_balancer_dns)

cat > deploy-application.sh << EOF
#!/bin/bash
set -e

echo "📦 Deploying application to infrastructure..."

# Wait for instance to be ready
echo "⏳ Waiting for instance to be ready..."
while ! ssh -o ConnectTimeout=5 -o StrictHostKeyChecking=no -i llm-chat-key.pem ec2-user@$INSTANCE_IP "echo 'ready'" 2>/dev/null; do
    sleep 10
done

echo "✅ Instance is ready"

# Copy application source
echo "📁 Copying application files..."
scp -o StrictHostKeyChecking=no -i llm-chat-key.pem -r ../pom.xml ../src ec2-user@$INSTANCE_IP:/opt/llm-chat/

# Build and start application
echo "🔨 Building and starting application..."
ssh -o StrictHostKeyChecking=no -i llm-chat-key.pem ec2-user@$INSTANCE_IP "
    cd /opt/llm-chat
    export PATH=/opt/maven/bin:\$PATH
    export JAVA_HOME=/usr/lib/jvm/java-17-amazon-corretto
    mvn clean package -DskipTests
    sudo systemctl start llm-chat-service
    sudo systemctl status llm-chat-service
"

echo "✅ Application deployed successfully!"
echo ""
echo "🎯 Access your application:"
echo "Direct IP: http://$INSTANCE_IP:8080"
echo "Load Balancer: http://$ALB_DNS"
echo ""
echo "🔗 SSH Access:"
echo "ssh -i llm-chat-key.pem ec2-user@$INSTANCE_IP"
EOF

chmod +x deploy-application.sh

echo ""
echo "🎯 Next Steps:"
echo "1. Ensure you have the SSH key 'llm-chat-key.pem' in this directory"
echo "2. Run './deploy-application.sh' to deploy the application"
echo "3. Wait for deployment to complete (may take 10-15 minutes)"
echo ""
echo "🗑️  To destroy infrastructure:"
echo "terraform destroy"
