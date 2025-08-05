#!/bin/bash

# Update system
apt-get update -y
apt-get upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
usermod -aG docker ubuntu

# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Start Ollama service
systemctl start ollama
systemctl enable ollama

# Install NVIDIA drivers for GPU support
ubuntu-drivers autoinstall

# Pull base models
ollama pull bert-base
ollama pull distilbert

# Configure firewall
ufw allow 11434
ufw allow 22
ufw --force enable

# Create systemd service for custom setup
cat > /etc/systemd/system/ollama-setup.service << EOF
[Unit]
Description=Ollama Custom Setup
After=ollama.service

[Service]
Type=oneshot
ExecStart=/usr/local/bin/setup-models.sh
RemainAfterExit=yes

[Install]
WantedBy=multi-user.target
EOF

# Create setup script
cat > /usr/local/bin/setup-models.sh << 'EOF'
#!/bin/bash
# Wait for Ollama to be ready
sleep 30

# Pull required models
ollama pull bert-base
ollama pull distilbert

# Create custom classification model
cat > /tmp/bert-classifier-modelfile << 'MODELFILE'
FROM bert-base

PARAMETER temperature 0.1
PARAMETER top_k 40
PARAMETER top_p 0.9

SYSTEM "You are a text classifier using a fine-tuned BERT model. Classify text sentiment as positive (1) or negative (0)."

TEMPLATE "Text: {{ .Prompt }}\nClassification:"
MODELFILE

ollama create bert-classifier -f /tmp/bert-classifier-modelfile
EOF

chmod +x /usr/local/bin/setup-models.sh
systemctl enable ollama-setup.service
systemctl start ollama-setup.service

# Log completion
echo "Ollama installation completed at $(date)" >> /var/log/ollama-install.log
