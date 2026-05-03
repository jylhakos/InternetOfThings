#!/usr/bin/env bash
# -----------------------------------------------------------------------------
# setup_venv.sh
#
# Creates a Python virtual environment named "venv" in the current directory,
# activates it, and installs all dependencies required for the LLM pre-training
# pipeline.
#
# Usage:
#   bash scripts/setup_venv.sh
#
# After setup, activate the virtual environment in every new terminal session:
#   source venv/bin/activate
#
# VS Code integration:
#   1. Open Command Palette (Ctrl+Shift+P)
#   2. Select "Python: Select Interpreter"
#   3. Choose the interpreter at ./venv/bin/python
# -----------------------------------------------------------------------------

set -euo pipefail

VENV_DIR="venv"
PYTHON_BIN="${PYTHON_BIN:-python3}"
CUDA_VERSION="${CUDA_VERSION:-cu121}"   # Override for your CUDA version, e.g. cu118

# ---------------------------------------------------------------------------
# Step 1: Locate Python interpreter
# ---------------------------------------------------------------------------
if ! command -v "${PYTHON_BIN}" &>/dev/null; then
    echo "ERROR: '${PYTHON_BIN}' not found. Install Python 3.10+ and try again." >&2
    exit 1
fi

PY_VERSION=$("${PYTHON_BIN}" -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
echo "Python interpreter : ${PYTHON_BIN}  (${PY_VERSION})"

# ---------------------------------------------------------------------------
# Step 2: Create the virtual environment
# ---------------------------------------------------------------------------
if [[ -d "${VENV_DIR}" ]]; then
    echo "Virtual environment '${VENV_DIR}/' already exists. Skipping creation."
else
    echo "Creating virtual environment in ./${VENV_DIR}/ ..."
    "${PYTHON_BIN}" -m venv "${VENV_DIR}"
    echo "Virtual environment created."
fi

# ---------------------------------------------------------------------------
# Step 3: Activate
# ---------------------------------------------------------------------------
# shellcheck source=/dev/null
source "${VENV_DIR}/bin/activate"
echo "Activated: $(which python)"

# ---------------------------------------------------------------------------
# Step 4: Upgrade pip
# ---------------------------------------------------------------------------
echo ""
echo "Upgrading pip ..."
pip install --upgrade pip --quiet

# ---------------------------------------------------------------------------
# Step 5: Install PyTorch with CUDA support
# ---------------------------------------------------------------------------
echo ""
echo "Installing PyTorch (CUDA ${CUDA_VERSION}) ..."
pip install \
    torch \
    torchvision \
    torchaudio \
    --index-url "https://download.pytorch.org/whl/${CUDA_VERSION}" \
    --quiet

# ---------------------------------------------------------------------------
# Step 6: Install Hugging Face ecosystem
# ---------------------------------------------------------------------------
echo ""
echo "Installing Hugging Face libraries ..."
pip install \
    transformers \
    tokenizers \
    datasets \
    accelerate \
    peft \
    --quiet

# ---------------------------------------------------------------------------
# Step 7: Install training and monitoring utilities
# ---------------------------------------------------------------------------
echo ""
echo "Installing training utilities ..."
pip install \
    tqdm \
    wandb \
    --quiet

# ---------------------------------------------------------------------------
# Step 8: Verify key installations
# ---------------------------------------------------------------------------
echo ""
echo "Verifying installations ..."
python - <<'EOF'
import torch
print(f"  PyTorch version : {torch.__version__}")
print(f"  CUDA available  : {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"  GPU             : {torch.cuda.get_device_name(0)}")
    print(f"  VRAM            : {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f} GB")
import transformers
print(f"  Transformers    : {transformers.__version__}")
import tokenizers
print(f"  Tokenizers      : {tokenizers.__version__}")
import datasets
print(f"  Datasets        : {datasets.__version__}")
EOF

# ---------------------------------------------------------------------------
# Step 9: Print activation instructions
# ---------------------------------------------------------------------------
echo ""
echo "================================================================"
echo " Setup complete."
echo ""
echo " To activate the virtual environment in future terminal sessions:"
echo "   source ${VENV_DIR}/bin/activate"
echo ""
echo " To run the pipeline scripts:"
echo "   source ${VENV_DIR}/bin/activate"
echo "   python scripts/data_preparation.py"
echo "   python scripts/tokenizer_train.py"
echo "   python scripts/pretrain.py"
echo "================================================================"
