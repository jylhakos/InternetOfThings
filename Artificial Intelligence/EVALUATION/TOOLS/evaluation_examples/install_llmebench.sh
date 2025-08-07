
# Clone LLMeBench repository
git clone https://github.com/qcri/LLMeBench.git
cd LLMeBench

# Install dependencies
pip install -r requirements.txt

# Install LLMeBench package
pip install -e .

# Verify installation
python -c "import llmebench; print('LLMeBench installed successfully')"
