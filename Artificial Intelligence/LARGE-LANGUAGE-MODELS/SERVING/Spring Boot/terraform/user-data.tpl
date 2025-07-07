#!/bin/bash

# User data script for EC2 instance setup
yum update -y

# Install CloudWatch agent
yum install -y amazon-cloudwatch-agent

# Install Java 17
yum install -y java-17-amazon-corretto-devel

# Install Docker
yum install -y docker
systemctl start docker
systemctl enable docker
usermod -a -G docker ec2-user

# Install Docker Compose
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Configure Ollama service
cat > /etc/systemd/system/ollama.service << 'EOF'
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
Environment="OLLAMA_ORIGINS=*"

[Install]
WantedBy=default.target
EOF

# Start and enable Ollama
systemctl daemon-reload
systemctl enable ollama
systemctl start ollama

# Wait for Ollama to be ready
sleep 15

# Pull Llama-3 model as ec2-user
sudo -u ec2-user bash -c 'ollama pull llama3'

# Create application directory
mkdir -p /opt/llm-chat
chown ec2-user:ec2-user /opt/llm-chat

# Install Maven
cd /opt
wget https://dlcdn.apache.org/maven/maven-3/3.9.6/binaries/apache-maven-3.9.6-bin.tar.gz
tar xzf apache-maven-3.9.6-bin.tar.gz
ln -s apache-maven-3.9.6 maven
echo 'export PATH=/opt/maven/bin:$PATH' >> /home/ec2-user/.bashrc

# Configure CloudWatch agent
cat > /opt/aws/amazon-cloudwatch-agent/etc/amazon-cloudwatch-agent.json << 'EOF'
{
  "logs": {
    "logs_collected": {
      "files": {
        "collect_list": [
          {
            "file_path": "/var/log/messages",
            "log_group_name": "/aws/ec2/llm-chat-service",
            "log_stream_name": "system-logs"
          },
          {
            "file_path": "/opt/llm-chat/app.log",
            "log_group_name": "/aws/ec2/llm-chat-service",
            "log_stream_name": "application-logs"
          }
        ]
      }
    }
  },
  "metrics": {
    "namespace": "LLM-Chat-Service",
    "metrics_collected": {
      "cpu": {
        "measurement": [
          "cpu_usage_idle",
          "cpu_usage_iowait",
          "cpu_usage_user",
          "cpu_usage_system"
        ],
        "metrics_collection_interval": 60
      },
      "disk": {
        "measurement": [
          "used_percent"
        ],
        "metrics_collection_interval": 60,
        "resources": [
          "*"
        ]
      },
      "mem": {
        "measurement": [
          "mem_used_percent"
        ],
        "metrics_collection_interval": 60
      }
    }
  }
}
EOF

# Start CloudWatch agent
/opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl \
  -a fetch-config \
  -m ec2 \
  -c file:/opt/aws/amazon-cloudwatch-agent/etc/amazon-cloudwatch-agent.json \
  -s

# Create application startup script
cat > /home/ec2-user/start-app.sh << 'EOF'
#!/bin/bash
cd /opt/llm-chat

# Ensure Ollama is running
if ! systemctl is-active --quiet ollama; then
    sudo systemctl start ollama
    sleep 10
fi

# Set environment variables
export PATH=/opt/maven/bin:$PATH
export JAVA_HOME=/usr/lib/jvm/java-17-amazon-corretto
export SPRING_PROFILES_ACTIVE=production

# Build application if source exists
if [ -f "pom.xml" ]; then
    mvn clean package -DskipTests
fi

# Start application
nohup java -jar target/llm-chat-service-1.0.0.jar > app.log 2>&1 &
echo $! > app.pid

echo "Application started successfully"
EOF

chmod +x /home/ec2-user/start-app.sh
chown ec2-user:ec2-user /home/ec2-user/start-app.sh

# Create systemd service for the application
cat > /etc/systemd/system/llm-chat-service.service << 'EOF'
[Unit]
Description=LLM Chat Service
After=ollama.service
Requires=ollama.service

[Service]
Type=forking
User=ec2-user
Group=ec2-user
WorkingDirectory=/opt/llm-chat
ExecStart=/home/ec2-user/start-app.sh
ExecStop=/bin/kill $(cat /opt/llm-chat/app.pid)
PIDFile=/opt/llm-chat/app.pid
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable llm-chat-service

# Log completion
echo "$(date): User data script completed successfully" >> /var/log/user-data.log
