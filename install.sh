#!/bin/bash
#
# Neural Agent Installer for Linux
# Install with: curl -fsSL https://raw.githubusercontent.com/robeast430-create/Testing-grounds./main/install.sh | bash
# Or for a specific version: curl -fsSL https://raw.githubusercontent.com/robeast430-create/Testing-grounds./main/install.sh | bash -s -- --version 1.0.0
#

set -e

VERSION="latest"
INSTALL_DIR="$HOME/.neural-agent"
PREFIX="/usr/local"
NEURAL_USER="${NEURAL_USER:-$USER}"

parse_args() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            --version)
                VERSION="$2"
                shift 2
                ;;
            --dir)
                INSTALL_DIR="$2"
                shift 2
                ;;
            --prefix)
                PREFIX="$2"
                shift 2
                ;;
            --help)
                show_help
                exit 0
                ;;
            --uninstall)
                uninstall
                exit 0
                ;;
            --update)
                update
                exit 0
                ;;
            *)
                echo "Unknown option: $1"
                show_help
                exit 1
                ;;
        esac
    done
}

show_help() {
    cat << EOF
Neural Agent Installer

Usage: curl -fsSL <url> | bash [options]
   Or: bash install.sh [options]

Options:
    --version VERSION    Install specific version (default: latest)
    --dir DIR            Installation directory (default: ~/.neural-agent)
    --prefix PREFIX      Binary prefix (default: /usr/local)
    --update             Update to latest version
    --uninstall          Remove Neural Agent
    --help               Show this help message

Examples:
    curl -fsSL https://.../install.sh | bash
    curl -fsSL https://.../install.sh | bash -s -- --version 1.0.0
EOF
}

check_deps() {
    echo "[1/6] Checking dependencies..."
    
    MISSING_DEPS=()
    
    if ! command -v python3 &> /dev/null; then
        MISSING_DEPS+=("python3")
    fi
    
    if ! command -v git &> /dev/null; then
        MISSING_DEPS+=("git")
    fi
    
    if ! command -v pip3 &> /dev/null; then
        MISSING_DEPS+=("pip3")
    fi
    
    if [ ${#MISSING_DEPS[@]} -gt 0 ]; then
        echo "Missing dependencies: ${MISSING_DEPS[*]}"
        
        if command -v apt-get &> /dev/null; then
            echo "Installing dependencies via apt..."
            sudo apt-get update && sudo apt-get install -y "${MISSING_DEPS[@]}"
        elif command -v dnf &> /dev/null; then
            echo "Installing dependencies via dnf..."
            sudo dnf install -y "${MISSING_DEPS[@]}"
        elif command -v pacman &> /dev/null; then
            echo "Installing dependencies via pacman..."
            sudo pacman -Sy --noconfirm "${MISSING_DEPS[@]}"
        elif command -v apk &> /dev/null; then
            echo "Installing dependencies via apk..."
            sudo apk add --no-cache "${MISSING_DEPS[@]}"
        else
            echo "Please install the missing dependencies manually."
            exit 1
        fi
    fi
    
    echo "  [OK] Dependencies satisfied"
}

install_deps() {
    echo "[2/6] Installing Python dependencies..."
    
    pip3 install --upgrade pip setuptools wheel 2>/dev/null || true
    
    CORE_DEPS=(
        "numpy>=1.21.0"
        "scipy>=1.7.0"
        "requests>=2.25.0"
        "beautifulsoup4>=4.9.0"
        "sqlalchemy>=1.4.0"
        "chromadb>=0.4.0"
        "sentence-transformers>=2.2.0"
        "transformers>=4.20.0"
        "torch>=2.0.0"
        "fastapi>=0.100.0"
        "uvicorn>=0.23.0"
        "jinja2>=3.1.0"
        "pyyaml>=6.0"
        "cryptography>=41.0.0"
        "pillow>=10.0.0"
        "opencv-python>=4.8.0"
        "pyttsx3>=2.90"
        "SpeechRecognition>=3.8.0"
        "gtts>=2.3.0"
        "pybluez>=0.23"
        "dbus-python>=1.3.0"
        "python-xlib>=0.33"
        "tkinter-tooltip>=2.1.0"
        "flask>=3.0.0"
        "flask-socketio>=5.3.0"
        "psutil>=5.9.0"
        "schedule>=1.2.0"
        "apscheduler>=3.10.0"
        "watchdog>=3.0.0"
        "watchfiles>=0.21.0"
        "python-dotenv>=1.0.0"
        "pydantic>=2.0.0"
        "aiohttp>=3.8.0"
        "websockets>=11.0.0"
        "httpx>=0.25.0"
        "scrapy>=2.11.0"
        "pandas>=2.0.0"
        "matplotlib>=3.7.0"
        "networkx>=3.0"
        "scikit-learn>=1.3.0"
        "nltk>=3.8.0"
        "spacy>=3.6.0"
        "textblob>=0.17.0"
    )
    
    for dep in "${CORE_DEPS[@]}"; do
        echo -n "  Installing ${dep}... "
        pip3 install --quiet "$dep" 2>/dev/null || echo "SKIP"
    done
    
    echo "  [OK] Python dependencies installed"
}

download_source() {
    echo "[3/6] Downloading Neural Agent..."
    
    mkdir -p "$INSTALL_DIR"
    cd "$INSTALL_DIR"
    
    REPO_URL="https://github.com/robeast430-create/Testing-grounds..git"
    
    if [ -d ".git" ]; then
        echo "  Repository exists, pulling latest..."
        git pull origin main 2>/dev/null || git pull origin master 2>/dev/null
    else
        echo "  Cloning repository..."
        git clone --depth 1 "$REPO_URL" . 2>/dev/null || {
            echo "  Git clone failed, trying alternative..."
            curl -fsSL "https://github.com/robeast430-create/Testing-grounds./archive/main.tar.gz" -o /tmp/neural.tar.gz
            tar -xzf /tmp/neural.tar.gz -C "$INSTALL_DIR" --strip-components=1 2>/dev/null || {
                echo "  Download failed. Please check your internet connection."
                exit 1
            }
            rm -f /tmp/neural.tar.gz
        }
    fi
    
    echo "  [OK] Source downloaded"
}

install_files() {
    echo "[4/6] Installing files..."
    
    cd "$INSTALL_DIR"
    
    mkdir -p "$INSTALL_DIR/auth_data"
    mkdir -p "$INSTALL_DIR/memory_db"
    mkdir -p "$INSTALL_DIR/logs"
    
    if [ -f "requirements.txt" ]; then
        echo "  Installing from requirements.txt..."
        pip3 install -r requirements.txt --quiet 2>/dev/null || true
    fi
    
    chmod +x neural_agent/cli.py 2>/dev/null || true
    chmod +x neural_agent/main.py 2>/dev/null || true
    
    BIN_DIR="$PREFIX/bin"
    mkdir -p "$BIN_DIR"
    
    cat > "$BIN_DIR/neural-agent" << 'INSTALL_EOF'
#!/bin/bash
cd "$(dirname "$(readlink -f "$0")/..")"
cd "$(dirname "$0")/../../../neural_agent"
exec python3 -m cli "$@"
INSTALL_EOF
    
    chmod +x "$BIN_DIR/neural-agent"
    
    cat > "$BIN_DIR/linai" << 'LINAI_EOF'
#!/bin/bash
cd "$(dirname "$(readlink -f "$0")/..")"
cd "$(dirname "$0")/../../../"
exec python3 linai.py "$@"
LINAI_EOF
    
    chmod +x "$BIN_DIR/linai"
    
    echo "  [OK] Binary installed to $BIN_DIR/neural-agent"
    echo "  [OK] linai installed to $BIN_DIR/linai"
}

configure() {
    echo "[5/6] Configuring..."
    
    cd "$INSTALL_DIR"
    
    if [ ! -f "config.json" ]; then
        cat > config.json << 'CONFIG_EOF'
{
    "agent_name": "Neural Agent",
    "version": "1.0.0",
    "memory_enabled": true,
    "web_enabled": true,
    "voice_enabled": true,
    "bluetooth_enabled": true,
    "simulation_enabled": true,
    "max_concurrent_tasks": 5,
    "log_level": "INFO",
    "api": {
        "host": "0.0.0.0",
        "port": 8080,
        "cors_enabled": true
    },
    "security": {
        "require_auth": true,
        "session_timeout": 3600
    }
}
CONFIG_EOF
    fi
    
    export PYTHONPATH="$INSTALL_DIR:$PYTHONPATH"
    
    cat >> ~/.bashrc << 'BASHRC_EOF'

# Neural Agent
export NEURAL_AGENT_HOME="$HOME/.neural-agent"
export PYTHONPATH="$NEURAL_AGENT_HOME:$PYTHONPATH"
alias neural-agent="$HOME/.neural-agent/neural_agent/cli.py"
BASHRC_EOF
    
    echo "  [OK] Configuration complete"
}

finish() {
    echo "[6/6] Finalizing..."
    
    cd "$INSTALL_DIR"
    
    echo ""
    echo "=========================================="
    echo "  Neural Agent Installation Complete!"
    echo "=========================================="
    echo ""
    echo "  Installation directory: $INSTALL_DIR"
    echo "  Binary location: $PREFIX/bin/neural-agent"
    echo ""
    echo "Quick Start:"
    echo "  neural-agent --help"
    echo "  neural-agent user add admin password"
    echo "  neural-agent start"
    echo "  neural-agent --web"
    echo ""
    echo "APK Build (requires Android SDK):"
    echo "  neural-agent apk all"
    echo ""
    echo "Simulation:"
    echo "  neural-agent sim create mysim 3d"
    echo "  neural-agent sim render mysim"
    echo ""
    echo "=========================================="
    
    export PATH="$PREFIX/bin:$PATH"
}

uninstall() {
    echo "Uninstalling Neural Agent..."
    rm -rf "$INSTALL_DIR"
    rm -f "$PREFIX/bin/neural-agent"
    sed -i '/Neural Agent/d' ~/.bashrc 2>/dev/null || true
    sed -i '/NEURAL_AGENT_HOME/d' ~/.bashrc 2>/dev/null || true
    echo "Uninstalled!"
}

update() {
    echo "Updating Neural Agent..."
    cd "$INSTALL_DIR"
    git pull 2>/dev/null || echo "Update failed"
    pip3 install -r requirements.txt --upgrade 2>/dev/null || true
    echo "Updated!"
}

main() {
    parse_args "$@"
    
    echo "=========================================="
    echo "  Neural Agent Installer"
    echo "  Version: $VERSION"
    echo "=========================================="
    echo ""
    
    check_deps
    install_deps
    download_source
    install_files
    configure
    finish
}

main "$@"