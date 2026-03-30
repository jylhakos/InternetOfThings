# OpenClaw Example Application: Secure Local Task Automation

This example demonstrates how to set up and run OpenClaw securely in a Docker container for local task automation. The application is configured with security best practices including privilege dropping, network isolation, and read-only filesystems.

## Overview

This example shows:
- Secure Docker-based deployment with hardened configuration
- Virtual environment setup for local development
- Proper secret management with .env files
- Network isolation and egress control
- Example task automation workflows
- Monitoring and logging configuration

## Prerequisites

- Docker and Docker Compose installed
- Linux system (Ubuntu/Debian recommended)
- Basic understanding of Docker and networking
- API keys for OpenAI and/or Anthropic (optional for local models)

## Quick Start

### 1. Clone OpenClaw

```bash
# Clone the official OpenClaw repository
git clone https://github.com/openclaw/openclaw.git
cd openclaw
```

### 2. Set Up the Example Configuration

```bash
# Copy this example configuration
cp -r /path/to/example-app/* .

# Create required directories
mkdir -p workspace config logs
chmod 700 workspace  # Restrict to owner only
```

### 3. Configure Environment Variables

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env with your API keys
nano .env  # or vim, code, etc.
```

Add your credentials:
```bash
OPENAI_API_KEY=sk-your-openai-key-here
ANTHROPIC_API_KEY=sk-ant-your-anthropic-key-here
GATEWAY_PORT=18789
GATEWAY_HOST=127.0.0.1
```

**Security Note**: Never commit `.env` to version control. It's included in `.gitignore`.

### 4. Build and Run Securely

```bash
# Build the Docker image
docker compose -f docker-compose.secure.yml build

# Start OpenClaw in detached mode
docker compose -f docker-compose.secure.yml up -d

# View logs
docker compose -f docker-compose.secure.yml logs -f
```

### 5. Access OpenClaw

```bash
# OpenClaw Gateway is accessible only on localhost
curl http://127.0.0.1:18789/health

# Or use the web interface (if enabled)
# Open browser to: http://127.0.0.1:18789
```

## Local Development (Virtual Environment)

If you want to run OpenClaw locally for development without Docker:

### Setup

```bash
# Create a Python virtual environment
python3 -m venv venv

# Activate the virtual environment
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows

# Install Node.js dependencies (OpenClaw uses pnpm)
npm install -g pnpm
pnpm install

# Install Python dependencies if needed
pip install -r requirements.txt

# Load environment variables
export $(cat .env | xargs)

# Run OpenClaw
pnpm start
```

### Deactivate Virtual Environment

```bash
deactivate
```

## Security Configuration Details

### Docker Compose Security Features

The `docker-compose.secure.yml` includes:

1. **Non-Root User**: Runs as UID 1000 instead of root
2. **Read-Only Filesystem**: Root filesystem is read-only to prevent tampering
3. **Dropped Capabilities**: All Linux capabilities dropped by default
4. **No Privilege Escalation**: Prevents setuid/setgid exploits
5. **Localhost Binding**: Gateway port only accessible from 127.0.0.1
6. **Volume Restrictions**: Only necessary directories mounted, with minimal permissions
7. **Resource Limits**: CPU and memory limits to prevent DoS
8. **Logging**: Structured logging with rotation

### Network Security

```bash
# Verify port is bound to localhost only
netstat -tuln | grep 18789
# Should show: 127.0.0.1:18789

# Check no external exposure
nmap -p 18789 localhost
```

### File Permissions

```bash
# Workspace permissions (owner only)
chmod 700 workspace

# Config permissions (read-only for container)
chmod 644 config/*

# .env permissions (owner read-only)
chmod 600 .env
```

## Example Task: Automated File Organization

This example demonstrates using OpenClaw to automatically organize files in the workspace.

### Task Definition

Create `workspace/organize-task.json`:

```json
{
  "task": "organize_files",
  "description": "Organize files in the workspace by type",
  "actions": [
    {
      "type": "scan_directory",
      "path": "/app/workspace"
    },
    {
      "type": "classify_files",
      "rules": {
        "documents": [".pdf", ".docx", ".txt"],
        "images": [".jpg", ".png", ".gif"],
        "code": [".py", ".js", ".java", ".go"]
      }
    },
    {
      "type": "create_folders",
      "folders": ["documents", "images", "code", "other"]
    },
    {
      "type": "move_files",
      "method": "copy",
      "preserve_originals": true
    }
  ],
  "constraints": {
    "max_files": 1000,
    "dry_run": false,
    "confirm_destructive": true
  }
}
```

### Run the Task

```bash
# Submit task to OpenClaw
curl -X POST http://127.0.0.1:18789/api/tasks \
  -H "Content-Type: application/json" \
  -d @workspace/organize-task.json

# Check task status
curl http://127.0.0.1:18789/api/tasks/status
```

## Monitoring and Logging

### View Live Logs

```bash
# All logs
docker compose -f docker-compose.secure.yml logs -f

# Specific service logs
docker logs -f openclaw_secure

# Filter for errors
docker logs openclaw_secure 2>&1 | grep -i error
```

### Log Files

Logs are stored in the `logs/` directory:
- `gateway.log` - Main gateway process logs
- `agent.log` - Agent execution logs
- `security.log` - Security events and alerts

### Resource Monitoring

```bash
# Real-time resource usage
docker stats openclaw_secure

# Historical usage (if cAdvisor installed)
docker run \
  --volume=/:/rootfs:ro \
  --volume=/var/run:/var/run:ro \
  --volume=/sys:/sys:ro \
  --publish=8080:8080 \
  --detach=true \
  --name=cadvisor \
  google/cadvisor:latest
```

## Advanced: Network Egress Filtering

To restrict OpenClaw to specific external APIs only:

### Using iptables (requires root)

```bash
# Allow specific API endpoints
sudo iptables -A OUTPUT -p tcp -d api.openai.com -j ACCEPT
sudo iptables -A OUTPUT -p tcp -d api.anthropic.com -j ACCEPT
sudo iptables -A OUTPUT -p tcp -d api.deepinfra.com -j ACCEPT

# Block all other outbound from the container
# (Requires identifying container's network namespace)
```

### Using Docker Network (recommended)

Create a custom network with restricted egress:

```yaml
# Add to docker-compose.secure.yml
networks:
  restricted:
    driver: bridge
    driver_opts:
      com.docker.network.bridge.name: br-openclaw
    ipam:
      config:
        - subnet: 172.28.0.0/16
```

Then use a sidecar proxy container to filter traffic.

## Reverse Proxy for Remote Access

If you need to access OpenClaw remotely, use a reverse proxy with TLS:

### Nginx Setup

```bash
# Install Nginx
sudo apt-get install nginx

# Install Certbot for Let's Encrypt
sudo apt-get install certbot python3-certbot-nginx

# Copy the Nginx configuration
sudo cp nginx-openclaw.conf /etc/nginx/sites-available/openclaw
sudo ln -s /etc/nginx/sites-available/openclaw /etc/nginx/sites-enabled/

# Get SSL certificate
sudo certbot --nginx -d openclaw.yourdomain.com

# Create htpasswd file for basic auth
sudo apt-get install apache2-utils
sudo htpasswd -c /etc/nginx/.htpasswd openclaw-user

# Test and reload Nginx
sudo nginx -t
sudo systemctl reload nginx
```

Now access via: `https://openclaw.yourdomain.com`

## Troubleshooting

### Container Won't Start

```bash
# Check logs for errors
docker compose -f docker-compose.secure.yml logs

# Verify user permissions
docker exec openclaw_secure id
# Should show: uid=1000 gid=1000

# Fix volume permissions
sudo chown -R 1000:1000 workspace config
```

### API Connection Errors

```bash
# Test API keys
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY"

# Check environment variables are loaded
docker exec openclaw_secure env | grep API_KEY
```

### Port Already in Use

```bash
# Find what's using port 18789
sudo lsof -i :18789

# Kill the process or change port in .env
kill -9 <PID>
```

### Permission Denied

```bash
# SELinux issues (Fedora/RHEL/CentOS)
sudo semanage fcontext -a -t container_file_t "/path/to/workspace(/.*)?"
sudo restorecon -Rv /path/to/workspace

# AppArmor issues (Ubuntu/Debian)
# Check AppArmor status
sudo aa-status
```

## Cleanup

```bash
# Stop and remove containers
docker compose -f docker-compose.secure.yml down

# Remove volumes (WARNING: deletes all data)
docker compose -f docker-compose.secure.yml down -v

# Clean up virtual environment
deactivate
rm -rf venv

# Remove logs
rm -rf logs/*
```

## Security Checklist

- [ ] `.env` file is not committed to version control
- [ ] Gateway port bound to 127.0.0.1 only
- [ ] Container runs as non-root user
- [ ] Read-only filesystem enabled
- [ ] All capabilities dropped
- [ ] Resource limits configured
- [ ] Sensitive directories not mounted
- [ ] TLS enabled for remote access
- [ ] Authentication enabled (basic auth minimum)
- [ ] Logging and monitoring configured
- [ ] Regular updates scheduled
- [ ] Backup strategy in place

## Next Steps

1. Review the [OpenClaw Documentation](https://docs.openclaw.ai/)
2. Explore available plugins and skills
3. Create custom workflows for your use cases
4. Set up monitoring and alerting
5. Implement automated backups
6. Consider VPN or mutual TLS for stronger authentication

## Contributing

Found a security issue or improvement? Please open an issue or PR in the main repository.

## License

This example is provided for educational purposes. Review and comply with OpenClaw's official license terms.
