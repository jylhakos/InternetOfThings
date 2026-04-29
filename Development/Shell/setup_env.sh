#!/usr/bin/env bash
# setup_env.sh
#
# Description:
#   Sets up the Python virtual environment for the IoT development project,
#   installs dependencies from Python/requirements.txt, and prints
#   instructions for running the IoT publisher script.
#
# Run from the Development directory:
#   cd /home/laptop/EXERCISES/IOT/InternetOfThings/Development
#   bash Shell/setup_env.sh
#
# After this script completes, the virtual environment is active in the
# current terminal session. Open a new terminal and activate manually with:
#   source .venv/bin/activate

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
VENV_DIR="$PROJECT_ROOT/.venv"
REQUIREMENTS="$PROJECT_ROOT/Python/requirements.txt"

echo "Project root : $PROJECT_ROOT"
echo "Virtual env  : $VENV_DIR"
echo ""

# ---------------------------------------------------------------------------
# Step 1: Ensure python3-venv is available
# ---------------------------------------------------------------------------
if ! python3 -c "import venv" 2>/dev/null; then
    echo "[1/4] Installing python3-venv ..."
    sudo apt-get update -q
    sudo apt-get install -y python3-venv
else
    echo "[1/4] python3-venv is available."
fi

# ---------------------------------------------------------------------------
# Step 2: Create the virtual environment
# ---------------------------------------------------------------------------
if [ ! -d "$VENV_DIR" ]; then
    echo "[2/4] Creating virtual environment at $VENV_DIR ..."
    python3 -m venv "$VENV_DIR"
else
    echo "[2/4] Virtual environment already exists."
fi

# ---------------------------------------------------------------------------
# Step 3: Activate virtual environment and upgrade pip
# ---------------------------------------------------------------------------
echo "[3/4] Activating virtual environment and upgrading pip ..."
# shellcheck disable=SC1091
source "$VENV_DIR/bin/activate"
pip install --upgrade pip --quiet

# ---------------------------------------------------------------------------
# Step 4: Install project dependencies
# ---------------------------------------------------------------------------
if [ -f "$REQUIREMENTS" ]; then
    echo "[4/4] Installing dependencies from $(basename "$REQUIREMENTS") ..."
    pip install -r "$REQUIREMENTS"
else
    echo "[4/4] WARNING: requirements.txt not found at $REQUIREMENTS"
fi

echo ""
echo "Setup complete. The virtual environment is active in this shell session."
echo ""
echo "Next steps:"
echo ""
echo "  Set AWS IoT environment variables:"
echo "    export AWS_IOT_ENDPOINT=\"your-endpoint.iot.us-east-1.amazonaws.com\""
echo "    export AWS_IOT_CERT=\"/home/pi/certs/certificate.pem.crt\""
echo "    export AWS_IOT_KEY=\"/home/pi/certs/private.pem.key\""
echo "    export AWS_IOT_ROOT_CA=\"/home/pi/certs/rootCA.pem\""
echo ""
echo "  Run the IoT publisher:"
echo "    python3 $PROJECT_ROOT/Python/aws_iot_publisher.py"
echo ""
echo "  Stop the publisher cleanly with Ctrl+C."
echo ""
echo "  Deactivate the virtual environment when finished:"
echo "    deactivate"
echo ""
echo "  To re-activate in a new terminal:"
echo "    source $VENV_DIR/bin/activate"
