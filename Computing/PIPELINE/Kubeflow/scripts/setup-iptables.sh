#!/bin/bash

# iptables Configuration Script for BERT Kubeflow Pipeline
# Configures local firewall rules for development environment

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root/sudo
check_privileges() {
    if [[ $EUID -eq 0 ]]; then
        log_warning "Running as root. This is acceptable for iptables configuration."
    else
        log_error "This script requires sudo privileges to configure iptables."
        echo "Please run: sudo $0"
        exit 1
    fi
}

# Backup existing iptables rules
backup_iptables() {
    log_info "Backing up existing iptables rules..."
    
    local backup_dir="/etc/iptables/backup"
    mkdir -p "$backup_dir"
    
    local timestamp=$(date +%Y%m%d_%H%M%S)
    iptables-save > "$backup_dir/iptables_backup_$timestamp.rules"
    
    log_success "Backup saved to: $backup_dir/iptables_backup_$timestamp.rules"
}

# Configure basic firewall rules
configure_basic_rules() {
    log_info "Configuring basic iptables rules..."
    
    # Allow loopback traffic
    iptables -A INPUT -i lo -j ACCEPT
    iptables -A OUTPUT -o lo -j ACCEPT
    
    # Allow established and related connections
    iptables -A INPUT -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT
    
    # Allow outgoing connections
    iptables -A OUTPUT -j ACCEPT
    
    log_success "Basic rules configured"
}

# Configure application-specific rules
configure_app_rules() {
    log_info "Configuring application-specific rules..."
    
    # FastAPI server (port 8000)
    iptables -A INPUT -p tcp --dport 8000 -j ACCEPT
    log_info "Allowed incoming traffic on port 8000 (FastAPI)"
    
    # Kubeflow UI (port 8080)
    iptables -A INPUT -p tcp --dport 8080 -j ACCEPT
    log_info "Allowed incoming traffic on port 8080 (Kubeflow UI)"
    
    # Additional services (port 3000)
    iptables -A INPUT -p tcp --dport 3000 -j ACCEPT
    log_info "Allowed incoming traffic on port 3000 (Additional services)"
    
    # Jupyter notebooks (port 8888)
    iptables -A INPUT -p tcp --dport 8888 -j ACCEPT
    log_info "Allowed incoming traffic on port 8888 (Jupyter)"
    
    # Grafana monitoring (port 3000)
    iptables -A INPUT -p tcp --dport 3001 -j ACCEPT
    log_info "Allowed incoming traffic on port 3001 (Grafana)"
    
    # SSH access (port 22)
    iptables -A INPUT -p tcp --dport 22 -j ACCEPT
    log_info "Allowed incoming traffic on port 22 (SSH)"
    
    log_success "Application rules configured"
}

# Configure Docker-specific rules
configure_docker_rules() {
    log_info "Configuring Docker-specific rules..."
    
    # Allow Docker bridge network
    iptables -A INPUT -i docker0 -j ACCEPT
    iptables -A FORWARD -i docker0 -o docker0 -j ACCEPT
    log_info "Allowed Docker bridge network traffic"
    
    # Allow communication between Docker containers and host
    iptables -A FORWARD -i docker0 -o eth0 -j ACCEPT
    iptables -A FORWARD -i eth0 -o docker0 -j ACCEPT
    
    # Allow Docker daemon communication
    iptables -A INPUT -p tcp --dport 2375 -s 127.0.0.1 -j ACCEPT
    iptables -A INPUT -p tcp --dport 2376 -s 127.0.0.1 -j ACCEPT
    
    log_success "Docker rules configured"
}

# Configure Kubernetes-specific rules
configure_k8s_rules() {
    log_info "Configuring Kubernetes-specific rules..."
    
    # Kubernetes API server
    iptables -A INPUT -p tcp --dport 6443 -j ACCEPT
    
    # etcd server client API
    iptables -A INPUT -p tcp --dport 2379:2380 -j ACCEPT
    
    # Kubelet API
    iptables -A INPUT -p tcp --dport 10250 -j ACCEPT
    
    # kube-scheduler
    iptables -A INPUT -p tcp --dport 10251 -j ACCEPT
    
    # kube-controller-manager
    iptables -A INPUT -p tcp --dport 10252 -j ACCEPT
    
    # NodePort Services
    iptables -A INPUT -p tcp --dport 30000:32767 -j ACCEPT
    
    # Minikube VM specific
    if command -v minikube &> /dev/null; then
        # Allow traffic from Minikube
        local minikube_ip=$(minikube ip 2>/dev/null || echo "192.168.49.0/24")
        if [[ $minikube_ip != "192.168.49.0/24" ]]; then
            iptables -A INPUT -s "$minikube_ip" -j ACCEPT
            log_info "Allowed traffic from Minikube IP: $minikube_ip"
        else
            iptables -A INPUT -s 192.168.49.0/24 -j ACCEPT
            log_info "Allowed traffic from Minikube subnet: 192.168.49.0/24"
        fi
    fi
    
    log_success "Kubernetes rules configured"
}

# Configure AWS-specific rules
configure_aws_rules() {
    log_info "Configuring AWS-specific rules..."
    
    # Allow HTTPS for AWS API calls
    iptables -A OUTPUT -p tcp --dport 443 -j ACCEPT
    
    # Allow DNS resolution
    iptables -A OUTPUT -p udp --dport 53 -j ACCEPT
    iptables -A OUTPUT -p tcp --dport 53 -j ACCEPT
    
    # Allow NTP for time synchronization
    iptables -A OUTPUT -p udp --dport 123 -j ACCEPT
    
    log_success "AWS rules configured"
}

# Set default policies
set_default_policies() {
    log_info "Setting default policies..."
    
    # Set default policies (be careful with this in production)
    iptables -P INPUT DROP
    iptables -P FORWARD DROP
    iptables -P OUTPUT ACCEPT
    
    log_warning "Default INPUT policy set to DROP"
    log_warning "Default FORWARD policy set to DROP"
    log_info "Default OUTPUT policy set to ACCEPT"
}

# Save iptables rules
save_rules() {
    log_info "Saving iptables rules..."
    
    # Create iptables directory if it doesn't exist
    mkdir -p /etc/iptables
    
    # Save current rules
    iptables-save > /etc/iptables/rules.v4
    
    # Create systemd service to restore rules on boot
    create_systemd_service
    
    log_success "Rules saved to /etc/iptables/rules.v4"
}

# Create systemd service for iptables restoration
create_systemd_service() {
    log_info "Creating systemd service for iptables restoration..."
    
    cat > /etc/systemd/system/iptables-restore.service << 'EOF'
[Unit]
Description=Restore iptables rules
Before=network.target

[Service]
Type=oneshot
ExecStart=/sbin/iptables-restore /etc/iptables/rules.v4
RemainAfterExit=yes

[Install]
WantedBy=multi-user.target
EOF
    
    # Enable the service
    systemctl enable iptables-restore.service
    
    log_success "Systemd service created and enabled"
}

# Display current rules
show_rules() {
    log_info "Current iptables rules:"
    echo ""
    iptables -L -n -v --line-numbers
    echo ""
    log_info "NAT rules:"
    iptables -t nat -L -n -v --line-numbers
}

# Restore from backup
restore_backup() {
    local backup_file="$1"
    
    if [[ -z "$backup_file" ]]; then
        log_error "Please specify backup file path"
        echo "Usage: $0 restore /path/to/backup.rules"
        exit 1
    fi
    
    if [[ ! -f "$backup_file" ]]; then
        log_error "Backup file not found: $backup_file"
        exit 1
    fi
    
    log_info "Restoring iptables from: $backup_file"
    iptables-restore < "$backup_file"
    log_success "Rules restored from backup"
}

# Reset all rules
reset_rules() {
    log_warning "Resetting all iptables rules..."
    
    # Flush all rules
    iptables -F
    iptables -t nat -F
    iptables -t mangle -F
    iptables -t raw -F
    
    # Delete all chains
    iptables -X
    iptables -t nat -X
    iptables -t mangle -X
    iptables -t raw -X
    
    # Set default policies to ACCEPT
    iptables -P INPUT ACCEPT
    iptables -P FORWARD ACCEPT
    iptables -P OUTPUT ACCEPT
    
    log_success "All rules reset to default"
}

# Main configuration function
main() {
    log_info "Starting iptables configuration for BERT Kubeflow Pipeline..."
    
    # Check privileges
    check_privileges
    
    # Backup existing rules
    backup_iptables
    
    # Reset rules first
    reset_rules
    
    # Configure rules
    configure_basic_rules
    configure_app_rules
    configure_docker_rules
    configure_k8s_rules
    configure_aws_rules
    
    # Set default policies (comment out for less restrictive setup)
    # set_default_policies
    
    # Save rules
    save_rules
    
    # Show current rules
    show_rules
    
    log_success "iptables configuration completed!"
    
    echo ""
    echo "📝 SUMMARY:"
    echo "  ✅ Port 8000: FastAPI server"
    echo "  ✅ Port 8080: Kubeflow UI"
    echo "  ✅ Port 3000: Additional services"
    echo "  ✅ Port 8888: Jupyter notebooks"
    echo "  ✅ Port 22: SSH access"
    echo "  ✅ Docker bridge network"
    echo "  ✅ Kubernetes ports"
    echo "  ✅ AWS API access"
    echo ""
    echo "🔧 MANAGEMENT COMMANDS:"
    echo "  sudo $0 show     # Display current rules"
    echo "  sudo $0 reset    # Reset all rules"
    echo "  sudo $0 restore <backup_file> # Restore from backup"
    echo ""
}

# Script options
case "${1:-}" in
    "show")
        check_privileges
        show_rules
        ;;
    "reset")
        check_privileges
        reset_rules
        log_success "iptables rules reset"
        ;;
    "restore")
        check_privileges
        restore_backup "$2"
        ;;
    "backup")
        check_privileges
        backup_iptables
        ;;
    "help"|"-h"|"--help")
        echo "Usage: sudo $0 [show|reset|restore|backup|help]"
        echo ""
        echo "Options:"
        echo "  show               Display current iptables rules"
        echo "  reset              Reset all rules to default (ACCEPT all)"
        echo "  restore <file>     Restore rules from backup file"
        echo "  backup             Create backup of current rules"
        echo "  help               Show this help message"
        echo ""
        echo "Run without arguments to configure iptables for BERT pipeline"
        ;;
    *)
        main
        ;;
esac
