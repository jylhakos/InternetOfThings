#!/bin/bash
# OpenClaw Monitoring Script
# Monitors OpenClaw container health, resource usage, and logs for security events

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

CONTAINER_NAME="openclaw_secure"
LOG_FILE="logs/openclaw.log"

echo -e "${BLUE}================================${NC}"
echo -e "${BLUE}OpenClaw Monitoring Dashboard${NC}"
echo -e "${BLUE}================================${NC}"
echo

# Check if container is running
if ! docker ps --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
    echo -e "${RED}Error: Container '${CONTAINER_NAME}' is not running${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Container is running${NC}"
echo

# Container health status
echo -e "${YELLOW}Container Health:${NC}"
docker inspect --format='{{.State.Health.Status}}' $CONTAINER_NAME 2>/dev/null || echo "No health check configured"
echo

# Resource usage
echo -e "${YELLOW}Resource Usage:${NC}"
docker stats $CONTAINER_NAME --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}\t{{.BlockIO}}"
echo

# Uptime
echo -e "${YELLOW}Uptime:${NC}"
docker inspect --format='{{.State.StartedAt}}' $CONTAINER_NAME | xargs -I {} date -d {} "+Started: %Y-%m-%d %H:%M:%S"
echo

# Recent errors in logs
echo -e "${YELLOW}Recent Errors (last 10):${NC}"
if [ -f "$LOG_FILE" ]; then
    tail -n 100 "$LOG_FILE" | grep -i "error" | tail -n 10 || echo "No errors found"
else
    docker logs $CONTAINER_NAME 2>&1 | grep -i "error" | tail -n 10 || echo "No errors found"
fi
echo

# Security events
echo -e "${YELLOW}Security Events (last 5):${NC}"
if [ -f "$LOG_FILE" ]; then
    tail -n 100 "$LOG_FILE" | grep -iE "(unauthorized|failed|denied|security|blocked)" | tail -n 5 || echo "No security events"
else
    docker logs $CONTAINER_NAME 2>&1 | grep -iE "(unauthorized|failed|denied|security|blocked)" | tail -n 5 || echo "No security events"
fi
echo

# Network connections
echo -e "${YELLOW}Active Network Connections:${NC}"
docker exec $CONTAINER_NAME netstat -tuln 2>/dev/null | grep LISTEN || echo "netstat not available in container"
echo

# Process list inside container
echo -e "${YELLOW}Running Processes:${NC}"
docker top $CONTAINER_NAME
echo

# Disk usage
echo -e "${YELLOW}Disk Usage:${NC}"
docker exec $CONTAINER_NAME df -h 2>/dev/null | head -n 2 || echo "df not available in container"
echo

# Recent API calls (if accessible)
echo -e "${YELLOW}Recent Activity:${NC}"
if [ -f "$LOG_FILE" ]; then
    tail -n 20 "$LOG_FILE" | grep -iE "(request|task|action)" | tail -n 5 || echo "No recent activity logged"
fi
echo

# Optional: Check for updates
echo -e "${YELLOW}Image Information:${NC}"
docker images openclaw/openclaw:latest --format "table {{.Repository}}\t{{.Tag}}\t{{.CreatedAt}}\t{{.Size}}"
echo

echo -e "${GREEN}================================${NC}"
echo -e "${GREEN}Monitoring Complete${NC}"
echo -e "${GREEN}================================${NC}"
echo
echo "For continuous monitoring, run:"
echo "  docker logs -f $CONTAINER_NAME"
echo "  docker stats $CONTAINER_NAME"
echo
echo "To check container details:"
echo "  docker inspect $CONTAINER_NAME"
