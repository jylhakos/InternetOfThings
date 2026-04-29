## GPU/CUDA Testing for RNN+LSTM Project

### STATUS

We fix the PyTorch installation.

```bash
# 1. Uninstall problematic PyTorch version
pip uninstall torch torchvision torchaudio

# 2. Install stable PyTorch with CUDA 12.4 support
pip install torch==2.4.1 torchvision==0.19.1 torchaudio==2.4.1 --index-url https://download.pytorch.org/whl/cu124

# 3. Alternative: Use conda for better compatibility
# conda install pytorch torchvision torchaudio pytorch-cuda=12.4 -c pytorch -c nvidia
```
---

**NEXT STEPS**: Run the PyTorch reinstallation commands above.

```python
import torch
print(f"CUDA available: {torch.cuda.is_available()}")
```
