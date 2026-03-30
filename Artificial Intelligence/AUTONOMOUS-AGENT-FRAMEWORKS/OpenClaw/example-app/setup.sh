#!/bin/bash
# OpenClaw Secure Setup Script
# This script helps set up OpenClaw with security best practices

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}================================${NC}"
echo -e "${GREEN}OpenClaw Secure Setup${NC}"
echo -e "${GREEN}================================${NC}"
echo

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   echo -e "${RED}Error: Do not run this script as root${NC}"
   echo "Run as your regular user. Sudo will be requested when needed."
   exit 1
fi

# Check prerequisites
echo -e "${YELLOW}Checking prerequisites...${NC}"

command -v docker >/dev/null 2>&1 || {
    echo -e "${RED}Error: Docker is not installed${NC}"
    echo "Install Docker: https://docs.docker.com/engine/install/"
    exit 1
}

command -v docker-compose >/dev/null 2>&1 || command -v docker compose >/dev/null 2>&1 || {
    echo -e "${RED}Error: Docker Compose is not installed${NC}"
    echo "Install Docker Compose: https://docs.docker.com/compose/install/"
    exit 1
}

echo -e "${GREEN}✓ Prerequisites met${NC}"
echo

# Create directory structure
echo -e "${YELLOW}Creating directory structure...${NC}"
mkdir -p workspace config logs
chmod 700 workspace  # Owner only
chmod 755 config
chmod 755 logs

echo -e "${GREEN}✓ Directories created${NC}"
echo

# Check if .env exists
if [ ! -f .env ]; then
    echo -e "${YELLOW}Creating .env file from template...${NC}"
    if [ -f .env.example ]; then
        cp .env.example .env
        echo -e "${GREEN}✓ .env file created${NC}"
        echo -e "${YELLOW}⚠ Please edit .env and add your API keys${NC}"
        read -p "Press Enter to open .env in your default editor..." -r
        ${EDITOR:-nano} .env
    else
        echo -e "${RED}Error: .env.example not found${NC}"
        exit 1
    fi
else
    echo -e "${GREEN}✓ .env file exists${NC}"
fi
echo

# Set proper ownership
echo -e "${YELLOW}Setting file ownership...${NC}"
USER_UID=$(id -u)
USER_GID=$(id -g)

# Update .env with correct UID/GID
if grep -q "RUN_AS_UID=" .env; then
    sed -i "s/RUN_AS_UID=.*/RUN_AS_UID=$USER_UID/" .env
    sed -i "s/RUN_AS_GID=.*/RUN_AS_GID=$USER_GID/" .env
else
    echo "RUN_AS_UID=$USER_UID" >> .env
    echo "RUN_AS_GID=$USER_GID" >> .env
fi

echo -e "${GREEN}✓ Ownership configured (UID: $USER_UID, GID: $USER_GID)${NC}"
echo

# Create temp directory for container
echo -e "${YELLOW}Creating temporary directory...${NC}"
sudo mkdir -p /tmp/openclaw
sudo chown -R $USER_UID:$USER_GID /tmp/openclaw
sudo chmod 755 /tmp/openclaw
echo -e "${GREEN}✓ Temporary directory created${NC}"
echo

# Verify .gitignore
if [ -f .gitignore ]; then
    if ! grep -q ".env" .gitignore; then
        echo ".env" >> .gitignore
        echo -e "${YELLOW}⚠ Added .env to .gitignore${NC}"
    fi
else
    echo ".env" > .gitignore
    echo -e "${YELLOW}⚠ Created .gitignore with .env${NC}"
fi
echo

# Security check
echo -e "${YELLOW}Running security checks...${NC}"

# Check .env permissions
ENV_PERMS=$(stat -c %a .env 2>/dev/null || stat -f %Lp .env)
if [ "$ENV_PERMS" != "600" ]; then
    chmod 600 .env
    echo -e "${YELLOW}⚠ Fixed .env permissions (set to 600)${NC}"
fi

# Check if API keys are set
if grep -q "your-.*-key-here" .env; then
    echo -e "${RED}⚠ WARNING: Placeholder API keys detected in .env${NC}"
    echo "Remember to replace them with real keys before running."
fi

echo -e "${GREEN}✓ Security checks complete${NC}"
echo

# Option to pull/build image
echo -e "${YELLOW}Docker Image Setup${NC}"
echo "1) Pull official OpenClaw image (recommended)"
echo "2) Build from source (requires cloned openclaw repository)"
echo "3) Skip (I'll do it manually)"
read -p "Select an option [1-3]: " -r IMAGE_OPTION

case $IMAGE_OPTION in
    1)
        echo -e "${YELLOW}Pulling OpenClaw image...${NC}"
        docker pull openclaw/openclaw:latest || {
            echo -e "${YELLOW}⚠ Official image not found, you may need to build from source${NC}"
        }
        ;;
    2)
        if [ ! -d "openclaw" ]; then
            echo -e "${YELLOW}Cloning OpenClaw repository...${NC}"
            git clone https://github.com/openclaw/openclaw.git
        fi
        echo -e "${YELLOW}Building OpenClaw image...${NC}"
        cd openclaw
        docker build -t openclaw/openclaw:latest .
        cd ..
        echo -e "${GREEN}✓ Image built${NC}"
        ;;
    3)
        echo -e "${YELLOW}Skipping image setup${NC}"
        ;;
    *)
        echo -e "${RED}Invalid option${NC}"
        ;;
esac
echo

# Summary
echo -e "${GREEN}================================${NC}"
echo -e "${GREEN}Setup Complete!${NC}"
echo -e "${GREEN}================================${NC}"
echo
echo "Next steps:"
echo "1. Verify your .env file has correct API keys"
echo "2. Run: docker compose -f docker-compose.secure.yml up -d"
echo "3. Check logs: docker compose -f docker-compose.secure.yml logs -f"
echo "4. Access OpenClaw at: http://127.0.0.1:18789"
echo
echo "Security reminders:"
echo "- Gateway is only accessible from localhost (127.0.0.1)"
echo "- Container runs as non-root user"
echo "- .env file is protected (600 permissions)"
echo "- For remote access, set up the Nginx reverse proxy"
echo
echo -e "${YELLOW}Read the README.md for detailed instructions and security best practices.${NC}"
