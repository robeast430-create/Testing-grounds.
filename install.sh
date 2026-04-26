#!/bin/bash
#
# Neural Agent Installer for Linux
# Install with: curl -fsSL https://raw.githubusercontent.com/robeast430-create/Testing-grounds./main/install.sh | bash
#

set -e

INSTALL_DIR="${NEURAL_AGENT_HOME:-$HOME/.neural-agent}"
PREFIX="/usr/local"
MODEL_MARKER="# Neural Agent"

parse_args() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            --dir)
                INSTALL_DIR="$2"
                shift 2
                ;;
            --uninstall)
                uninstall
                exit 0
                ;;
            --help)
                show_help
                exit 0
                ;;
            *)
                shift
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
    --dir DIR        Installation directory (default: ~/.neural-agent)
    --uninstall      Remove Neural Agent
    --help           Show this help

Install:
    curl -fsSL https://.../install.sh | bash
EOF
}

check_deps() {
    echo "[1/8] Checking dependencies..."
    
    local missing=()
    
    for cmd in python3 git pip3 curl; do
        if command -v "$cmd" &> /dev/null; then
            echo "  [OK] $cmd"
        else
            echo "  [MISSING] $cmd"
            missing+=("$cmd")
        fi
    done
    
    if [ ${#missing[@]} -gt 0 ]; then
        echo ""
        echo "  Installing missing dependencies..."
        install_system_deps
    fi
    
    echo "  [OK] Dependencies satisfied"
}

install_system_deps() {
    if command -v apt-get &> /dev/null; then
        echo "  Using apt..."
        sudo apt-get update
        sudo apt-get install -y python3 python3-pip git curl wget
        
    elif command -v dnf &> /dev/null; then
        echo "  Using dnf..."
        sudo dnf install -y python3 python3-pip git curl wget
        
    elif command -v pacman &> /dev/null; then
        echo "  Using pacman..."
        sudo pacman -Sy --noconfirm python python-pip git curl wget
        
    elif command -v apk &> /dev/null; then
        echo "  Using apk..."
        sudo apk add --no-cache python3 py3-pip git curl
        
    elif command -v zypper &> /dev/null; then
        echo "  Using zypper..."
        sudo zypper install -y python3 python3-pip git curl
        
    elif command -v yum &> /dev/null; then
        echo "  Using yum..."
        sudo yum install -y python3 python3-pip git curl
        
    else
        echo "  ERROR: Cannot detect package manager"
        echo "  Please install: python3, python3-pip, git, curl manually"
        exit 1
    fi
}

download_source() {
    echo "[2/8] Downloading Neural Agent..."
    
    mkdir -p "$INSTALL_DIR"
    cd "$INSTALL_DIR"
    
    REPO_URL="https://github.com/robeast430-create/Testing-grounds..git"
    
    if [ -d ".git" ]; then
        echo "  Pulling latest..."
        git pull origin main 2>/dev/null || git pull origin master 2>/dev/null
    else
        echo "  Cloning repository..."
        if ! git clone --depth 1 "$REPO_URL" . 2>/dev/null; then
            echo "  Git clone failed, trying tarball..."
            curl -fsSL "https://github.com/robeast430-create/Testing-grounds./archive/main.tar.gz" -o /tmp/neural.tar.gz
            tar -xzf /tmp/neural.tar.gz -C "$INSTALL_DIR" --strip-components=1
            rm -f /tmp/neural.tar.gz
        fi
    fi
    
    echo "  [OK] Source downloaded"
    echo "  Files installed:"
    find . -name "*.py" -type f | head -20 | while read f; do echo "    $f"; done
    py_count=$(find . -name "*.py" -type f | wc -l)
    echo "    ... and $py_count more Python files"
}

install_python_deps() {
    echo "[3/8] Installing Python dependencies..."
    
    echo "  Upgrading pip..."
    python3 -m pip install --upgrade pip setuptools wheel 2>/dev/null || true
    
    if [ -f "requirements.txt" ]; then
        echo "  Installing from requirements.txt..."
        python3 -m pip install -r requirements.txt 2>/dev/null || true
        echo "  [OK] requirements.txt"
    fi
    
    echo "  Installing additional packages..."
    
    CORE_DEPS=(
        numpy scipy requests beautifulsoup4 lxml
        sqlalchemy chromadb sentence-transformers
        transformers torch fastapi uvicorn
        jinja2 pyyaml cryptography pillow
        opencv-python pyttsx3 SpeechRecognition gtts
        flask flask-socketio psutil schedule
        apscheduler watchdog python-dotenv pydantic
        aiohttp websockets httpx scrapy
        pandas matplotlib networkx scikit-learn
        nltk spacy textblob openai anthropic
        qrcode pytz rich click prompt-toolkit
        colorama readline langchain huggingface-hub
        faiss-cpu tqdm accelerate safetensors
        tokenizers pyglet pyopengl trimesh moderngl
    )
    
    for dep in "${CORE_DEPS[@]}"; do
        echo -n "    $dep... "
        if python3 -m pip install "$dep" --quiet 2>/dev/null; then
            echo "OK"
        else
            echo "SKIP"
        fi
    done
    
    echo "  [OK] Python dependencies installed"
}

install_files() {
    echo "[4/8] Installing binaries..."
    
    mkdir -p "$INSTALL_DIR/auth_data" "$INSTALL_DIR/memory_db" "$INSTALL_DIR/logs"
    
    BIN_DIR="$PREFIX/bin"
    mkdir -p "$BIN_DIR"
    
    cat > "$BIN_DIR/neural-agent" << 'EOF'
#!/bin/bash
INSTALL_DIR="$(dirname "$(readlink -f "${BASH_SOURCE[0]}")")/../../.."
cd "$INSTALL_DIR"
exec python3 neural_agent/cli.py "$@"
EOF
    
    chmod +x "$BIN_DIR/neural-agent"
    echo "  [OK] $BIN_DIR/neural-agent"
    
    cat > "$BIN_DIR/linai" << 'EOF'
#!/bin/bash
INSTALL_DIR="$(dirname "$(readlink -f "${BASH_SOURCE[0]}")")/../../.."
cd "$INSTALL_DIR"
exec python3 linai.py "$@"
EOF
    
    chmod +x "$BIN_DIR/linai"
    echo "  [OK] $BIN_DIR/linai"
    
    echo "  All files installed:"
    echo "    neural_agent/ (full package)"
    echo "    linai.py"
    echo "    install.py / install.sh"
    echo "    requirements.txt"
    echo "    docs/"
    echo "    examples/"
}

configure() {
    echo "[5/8] Configuring..."
    
    if [ ! -f "config.json" ]; then
        cat > config.json << 'EOF'
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
EOF
        echo "  [OK] Created config.json"
    fi
    
    if [ -f "$HOME/.bashrc" ] && ! grep -q "$MODEL_MARKER" "$HOME/.bashrc"; then
        cat >> "$HOME/.bashrc" << EOF

$MODEL_MARKER
export NEURAL_AGENT_HOME="$INSTALL_DIR"
export PYTHONPATH="$INSTALL_DIR:\$PYTHONPATH"
alias neural-agent="$INSTALL_DIR/neural_agent/cli.py"
alias linai="$INSTALL_DIR/linai.py"
EOF
        echo "  [OK] Added to .bashrc"
    fi
    
    echo "  [OK] Configuration complete"
}

install_apk_deps() {
    echo "[6/8] Installing APK build dependencies (optional)..."
    
    for dep in kivy buildozer python-for-android; do
        echo -n "  $dep... "
        if python3 -m pip install "$dep" --quiet 2>/dev/null; then
            echo "OK"
        else
            echo "SKIP"
        fi
    done
    
    echo "  [OK] APK dependencies complete"
}

install_sim_deps() {
    echo "[7/8] Installing simulation dependencies..."
    
    for dep in pyglet pyopengl trimesh moderngl; do
        echo -n "  $dep... "
        if python3 -m pip install "$dep" --quiet 2>/dev/null; then
            echo "OK"
        else
            echo "SKIP"
        fi
    done
    
    echo "  [OK] Simulation dependencies complete"
}

finish() {
    echo "[8/8] Finalizing..."
    
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
    echo "  linai"
    echo ""
    echo "Simulations:"
    echo "  neural-agent sim create mysim 3d"
    echo "  neural-agent sim render mysim"
    echo ""
    echo "APK Build:"
    echo "  neural-agent apk all"
    echo ""
    echo "All Files Installed:"
    echo "  neural_agent/ (entire package)"
    echo "  linai.py"
    echo "  install.py / install.sh"
    echo "  requirements.txt"
    echo "  docs/"
    echo "  examples/"
    echo ""
    echo "=========================================="
}

uninstall() {
    echo "Uninstalling Neural Agent..."
    rm -rf "$INSTALL_DIR"
    rm -f "$PREFIX/bin/neural-agent"
    rm -f "$PREFIX/bin/linai"
    sed -i "/$MODEL_MARKER/,/alias linai/d" "$HOME/.bashrc" 2>/dev/null || true
    echo "Uninstalled!"
}

main() {
    parse_args "$@"
    
    echo "=========================================="
    echo "  Neural Agent Installer"
    echo "=========================================="
    echo ""
    
    check_deps
    download_source
    install_python_deps
    install_files
    configure
    install_apk_deps
    install_sim_deps
    finish
}

main "$@"