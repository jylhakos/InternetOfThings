#!/bin/bash

# Network Configuration Guide for Fish Weight Prediction MLflow Pipeline
# This script helps determine if you need iptables or nginx configuration

echo "🔍 MLflow Pipeline Network Configuration Analysis"
echo "================================================"

# Check current network interfaces
echo "📡 Network Interfaces:"
ip addr show | grep -E "inet |interface" | head -10

# Check if services are running
echo -e "\n🔍 Checking if ML services are running:"

# Check MLflow UI (port 5000)
if netstat -tuln 2>/dev/null | grep -q ":5000 "; then
    echo "✅ MLflow UI is running on port 5000"
    MLFLOW_RUNNING=true
else
    echo "❌ MLflow UI not running on port 5000"
    MLFLOW_RUNNING=false
fi

# Check FastAPI (port 8000)
if netstat -tuln 2>/dev/null | grep -q ":8000 "; then
    echo "✅ FastAPI server is running on port 8000"
    API_RUNNING=true
else
    echo "❌ FastAPI server not running on port 8000"
    API_RUNNING=false
fi

# Check what's listening on these ports
echo -e "\n🔍 Port Analysis:"
echo "Port 5000 (MLflow UI):"
netstat -tuln 2>/dev/null | grep ":5000 " || echo "  No service listening"

echo "Port 8000 (FastAPI):"
netstat -tuln 2>/dev/null | grep ":8000 " || echo "  No service listening"

# Check if ports are bound to localhost vs all interfaces
echo -e "\n🔒 Security Analysis:"

if netstat -tuln 2>/dev/null | grep -q "127.0.0.1:5000\|localhost:5000"; then
    echo "✅ MLflow UI bound to localhost only (secure for local dev)"
    MLFLOW_LOCALHOST=true
elif netstat -tuln 2>/dev/null | grep -q "0.0.0.0:5000"; then
    echo "⚠️ MLflow UI bound to all interfaces (accessible from network)"
    MLFLOW_LOCALHOST=false
else
    MLFLOW_LOCALHOST="unknown"
fi

if netstat -tuln 2>/dev/null | grep -q "127.0.0.1:8000\|localhost:8000"; then
    echo "✅ FastAPI bound to localhost only (secure for local dev)"
    API_LOCALHOST=true
elif netstat -tuln 2>/dev/null | grep -q "0.0.0.0:8000"; then
    echo "⚠️ FastAPI bound to all interfaces (accessible from network)"
    API_LOCALHOST=false
else
    API_LOCALHOST="unknown"
fi

# Check firewall status
echo -e "\n🛡️ Firewall Status:"
if command -v ufw &> /dev/null; then
    ufw status | head -5
elif command -v firewall-cmd &> /dev/null; then
    firewall-cmd --state 2>/dev/null || echo "firewalld not running"
elif command -v iptables &> /dev/null; then
    echo "iptables available, checking rules:"
    iptables -L INPUT | head -5 2>/dev/null || echo "Cannot read iptables (may need sudo)"
else
    echo "No common firewall tools found"
fi

# Recommendations
echo -e "\n📋 RECOMMENDATIONS:"
echo "=================="

echo -e "\n🏠 For LOCAL DEVELOPMENT (current setup):"
echo "✅ No iptables configuration needed"
echo "✅ No nginx configuration needed"
echo "✅ Services should bind to localhost (127.0.0.1)"
echo "✅ Only you can access the services"

echo -e "\n🌐 For TEAM SHARING (if needed):"
echo "🔧 Configure services to bind to 0.0.0.0"
echo "🔧 Add firewall rules to allow specific ports"
echo "🔧 Consider nginx for reverse proxy"

echo -e "\n🏭 For PRODUCTION DEPLOYMENT:"
echo "🔧 Definitely need nginx for reverse proxy"
echo "🔧 Need iptables/firewall configuration"
echo "🔧 Need SSL/TLS termination"
echo "🔧 Need authentication and authorization"

# Check access from local machine
echo -e "\n🧪 Testing Local Access:"

if $API_RUNNING; then
    echo "Testing FastAPI health check:"
    curl -s http://localhost:8000/ | head -100 2>/dev/null || echo "❌ Cannot reach FastAPI"
else
    echo "⚠️ FastAPI not running - start with: make serve"
fi

if $MLFLOW_RUNNING; then
    echo "Testing MLflow UI:"
    curl -s http://localhost:5000/ | grep -q "MLflow" && echo "✅ MLflow UI accessible" || echo "❌ MLflow UI not responding"
else
    echo "⚠️ MLflow UI not running - start with: make ui"
fi

# Configuration templates
echo -e "\n📝 CONFIGURATION TEMPLATES:"
echo "=========================="

echo -e "\n1. 🏠 LOCAL DEVELOPMENT (recommended):"
cat << 'EOF'
# Current setup - no changes needed
# Services bind to localhost automatically
# Access via:
#   http://localhost:8000  (API)
#   http://localhost:5000  (MLflow UI)
EOF

echo -e "\n2. 🌐 TEAM SHARING (if needed):"
cat << 'EOF'
# Modify serve_api.py to bind to all interfaces:
uvicorn.run("serve_api:app", host="0.0.0.0", port=8000)

# Start MLflow UI for external access:
mlflow ui --host 0.0.0.0 --port 5000

# Add firewall rules (Ubuntu/Debian):
sudo ufw allow 8000/tcp
sudo ufw allow 5000/tcp

# Access via:
#   http://YOUR_IP:8000  (API)
#   http://YOUR_IP:5000  (MLflow UI)
EOF

echo -e "\n3. 🏭 PRODUCTION with nginx:"
cat << 'EOF'
# /etc/nginx/sites-available/mlflow-api
server {
    listen 80;
    server_name your-domain.com;
    
    location /api/ {
        proxy_pass http://127.0.0.1:8000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    location /mlflow/ {
        proxy_pass http://127.0.0.1:5000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}

# Enable site:
sudo ln -s /etc/nginx/sites-available/mlflow-api /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx
EOF

echo -e "\n4. 🛡️ Production iptables rules:"
cat << 'EOF'
# Basic iptables rules for production
sudo iptables -A INPUT -i lo -j ACCEPT
sudo iptables -A INPUT -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 22 -j ACCEPT   # SSH
sudo iptables -A INPUT -p tcp --dport 80 -j ACCEPT   # HTTP
sudo iptables -A INPUT -p tcp --dport 443 -j ACCEPT  # HTTPS
sudo iptables -A INPUT -j DROP                       # Drop all other

# Save rules:
sudo iptables-save > /etc/iptables/rules.v4
EOF

echo -e "\n💡 CONCLUSION:"
echo "============="
echo "For your current LOCAL ML PIPELINE setup:"
echo "❌ NO iptables configuration needed"
echo "❌ NO nginx configuration needed"
echo "✅ Default localhost binding is perfect"
echo "✅ Just run: make serve && make ui"
echo ""
echo "Only configure iptables/nginx if you plan to:"
echo "- Share with team members over network"
echo "- Deploy to production servers"
echo "- Need load balancing or SSL termination"
