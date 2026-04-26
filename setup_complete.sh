#!/bin/bash

# Neural Agent Setup Script
# This script sets up the complete environment

set -e

echo "=========================================="
echo "  Neural Agent Setup Script"
echo "=========================================="
echo ""

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Check if running as root
check_root() {
    if [ "$EUID" -eq 0 ]; then
        echo -e "${YELLOW}Warning: Running as root${NC}"
    fi
}

# Check system requirements
check_system() {
    echo "[1/7] Checking system requirements..."
    
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
        echo "  Python: $PYTHON_VERSION"
    else
        echo -e "${RED}Error: Python 3 not found${NC}"
        exit 1
    fi
    
    if command -v git &> /dev/null; then
        echo "  Git: installed"
    fi
    
    echo "  System check: OK"
}

# Install system dependencies
install_system_deps() {
    echo ""
    echo "[2/7] Installing system dependencies..."
    
    if [ -f /etc/debian_version ]; then
        sudo apt-get update
        sudo apt-get install -y python3-dev python3-pip build-essential \
            libssl-dev libffi-dev libpq-dev \
            bluetooth bluez libbluetooth-dev \
            libasound2-dev portaudio19-dev \
            ffmpeg espeak
    elif [ -f /etc/redhat-release ]; then
        sudo yum groupinstall -y "Development Tools"
        sudo yum install -y python3-devel python3-pip \
            openssl-devel ffi-devel postgresql-devel \
            bluez-libs-devel alsa-lib-devel portaudio-devel \
            ffmpeg espeak
    elif [ -f /etc/arch-release ]; then
        sudo pacman -Sy
        sudo pacman -S --noconfirm python python-pip \
            base-devel openssl ffi postgresql-libs \
            bluez libpulse alsa-lib \
            ffmpeg espeak
    else
        echo "  Unknown distribution - please install manually"
    fi
    
    echo "  System dependencies: OK"
}

# Create virtual environment
create_venv() {
    echo ""
    echo "[3/7] Creating virtual environment..."
    
    if [ -d "venv" ]; then
        echo "  Removing existing venv..."
        rm -rf venv
    fi
    
    python3 -m venv venv
    source venv/bin/activate
    
    echo "  Virtual environment: OK"
}

# Install Python dependencies
install_python_deps() {
    echo ""
    echo "[4/7] Installing Python dependencies..."
    
    pip install --upgrade pip
    pip install wheel setuptools
    
    pip install -r requirements.txt
    
    echo "  Python dependencies: OK"
}

# Install the package
install_package() {
    echo ""
    echo "[5/7] Installing Neural Agent package..."
    
    pip install -e .
    
    echo "  Package installed: OK"
}

# Create directories
create_dirs() {
    echo ""
    echo "[6/7] Creating directories..."
    
    mkdir -p auth_data
    mkdir -p memory_db
    mkdir -p data
    mkdir -p cache
    mkdir -p backups
    mkdir -p exports
    mkdir -p logs
    mkdir -p plugins
    mkdir -p migrations
    
    echo "  Directories created: OK"
}

# Final setup
final_setup() {
    echo ""
    echo "[7/7] Final setup..."
    
    if [ ! -f "config.json" ]; then
        cp config.json config.json.bak 2>/dev/null || true
    fi
    
    chmod +x install.sh
    chmod +x neural_agent/cli.py 2>/dev/null || true
    
    echo "  Final setup: OK"
}

# Print success message
print_success() {
    echo ""
    echo -e "${GREEN}=========================================="
    echo "  Installation Complete!"
    echo "==========================================${NC}"
    echo ""
    echo "Quick Start:"
    echo "  source venv/bin/activate"
    echo "  neural-agent"
    echo ""
    echo "Or with web dashboard:"
    echo "  source venv/bin/activate"
    echo "  neural-agent --web"
    echo ""
    echo "=========================================="
}

# Main
main() {
    check_root
    check_system
    install_system_deps
    create_venv
    install_python_deps
    install_package
    create_dirs
    final_setup
    print_success
}

main "$@"