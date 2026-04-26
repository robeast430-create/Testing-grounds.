#!/bin/bash
#
# Neural Agent Installer for Linux
# Install: curl -fsSL https://raw.githubusercontent.com/robeast430-create/Testing-grounds./main/install.sh | bash
#

set -e

INSTALL_DIR="${NEURAL_AGENT_HOME:-$HOME/.neural-agent}"
PREFIX="/usr/local"

echo "=========================================="
echo "  Neural Agent Installer v1.0"
echo "=========================================="
echo ""

check_deps() {
    echo "[1/8] Checking dependencies..."
    
    for cmd in python3 git pip3 curl; do
        if command -v "$cmd" &> /dev/null; then
            echo "  [OK] $cmd"
        else
            echo "  [MISSING] $cmd - installing..."
            MISSING=1
        fi
    done
    
    if [ -n "$MISSING" ]; then
        install_system_deps
    fi
}

install_system_deps() {
    echo "  Installing system packages..."
    
    if command -v apt-get &> /dev/null; then
        sudo apt-get update
        sudo apt-get install -y python3 python3-pip git curl wget python3-dev build-essential
        
    elif command -v dnf &> /dev/null; then
        sudo dnf install -y python3 python3-pip git curl wget python3-devel gcc
        
    elif command -v pacman &> /dev/null; then
        sudo pacman -Sy --noconfirm python python-pip git curl wget base-devel
        
    elif command -v apk &> /dev/null; then
        sudo apk add --no-cache python3 py3-pip git curl wget python3-dev musl-dev gcc
        
    elif command -v zypper &> /dev/null; then
        sudo zypper install -y python3 python3-pip git curl wget python3-devel gcc
        
    elif command -v yum &> /dev/null; then
        sudo yum install -y python3 python3-pip git curl wget python3-devel gcc
        
    else
        echo "  ERROR: Cannot find package manager"
        exit 1
    fi
    
    echo "  [OK] System packages installed"
}

download_source() {
    echo "[2/8] Downloading Neural Agent..."
    
    mkdir -p "$INSTALL_DIR"
    cd "$INSTALL_DIR"
    
    if [ -d ".git" ]; then
        echo "  Pulling latest..."
        git pull origin main 2>/dev/null || git pull origin master 2>/dev/null || true
    else
        echo "  Cloning repository..."
        if ! git clone --depth 1 "https://github.com/robeast430-create/Testing-grounds..git" .; then
            echo "  Git failed, downloading tarball..."
            curl -fsSL "https://github.com/robeast430-create/Testing-grounds./archive/main.tar.gz" -o /tmp/neural.tar.gz
            tar -xzf /tmp/neural.tar.gz -C "$INSTALL_DIR" --strip-components=1
            rm -f /tmp/neural.tar.gz
        fi
    fi
    
    echo "  [OK] Source downloaded"
    
    FILE_COUNT=$(find . -type f | wc -l)
    echo "  Files installed: $FILE_COUNT"
    echo "  Key directories:"
    ls -d */ 2>/dev/null | head -10 | sed 's/^/    /'
}

install_python_deps() {
    echo "[3/8] Installing Python dependencies..."
    
    echo "  Upgrading pip..."
    python3 -m pip install --upgrade pip setuptools wheel --quiet || \
    python3 -m pip install --upgrade pip setuptools wheel || true
    
    if [ -f "requirements.txt" ]; then
        echo "  Installing from requirements.txt..."
        python3 -m pip install -r requirements.txt || {
            echo "  requirements.txt failed, installing individually..."
            while IFS= read -r line; do
                [[ "$line" =~ ^# ]] && continue
                [[ -z "$line" ]] && continue
                echo "    Installing: $line"
                python3 -m pip install "$line" || true
            done < requirements.txt
        }
    fi
    
    echo "  Installing core packages..."
    
    PACKAGES=(
        numpy scipy requests beautifulsoup4 lxml html5lib
        sqlalchemy chromadb sentence-transformers
        transformers torch fastapi uvicorn
        jinja2 pyyaml cryptography pillow
        opencv-python opencv-contrib-python
        flask flask-socketio flask-cors
        psutil schedule apscheduler
        watchdog python-dotenv pydantic
        aiohttp websockets httpx scrapy
        pandas matplotlib networkx scikit-learn
        nltk spacy textblob
        openai anthropic
        qrcode pytz rich click prompt-toolkit colorama
        readline langchain huggingface-hub
        faiss-cpu faiss-gpu tqdm accelerate safetensors
        tokenizers pyglet pyopengl trimesh moderngl
        kivy buildozer python-for-android
        pyttsx3 gtts
        SpeechRecognition
    )
    
    FAILED=()
    
    for pkg in "${PACKAGES[@]}"; do
        echo -n "    $pkg... "
        if python3 -m pip install "$pkg" 2>/dev/null; then
            echo "OK"
        else
            echo "FAIL"
            FAILED+=("$pkg")
        fi
    done
    
    if [ ${#FAILED[@]} -gt 0 ]; then
        echo ""
        echo "  Failed packages: ${FAILED[*]}"
        echo "  (These may require system dependencies or be optional)"
    fi
    
    echo "  [OK] Python packages complete"
}

install_files() {
    echo "[4/8] Installing binaries..."
    
    mkdir -p "$INSTALL_DIR/auth_data" "$INSTALL_DIR/memory_db" "$INSTALL_DIR/logs"
    
    BIN_DIR="$PREFIX/bin"
    mkdir -p "$BIN_DIR"
    
    cat > "$BIN_DIR/neural-agent" << 'NEOF'
#!/bin/bash
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INSTALL_DIR="$(dirname "$SCRIPT_DIR")/../.."
cd "$INSTALL_DIR"
exec python3 neural_agent/cli.py "$@"
NEOF
    chmod +x "$BIN_DIR/neural-agent"
    echo "  [OK] $BIN_DIR/neural-agent"
    
    cat > "$BIN_DIR/linai" << 'LEOF'
#!/bin/bash
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INSTALL_DIR="$(dirname "$SCRIPT_DIR")/../.."
cd "$INSTALL_DIR"
exec python3 linai.py "$@"
LEOF
    chmod +x "$BIN_DIR/linai"
    echo "  [OK] $BIN_DIR/linai"
}

configure() {
    echo "[5/8] Configuring..."
    
    if [ ! -f "config.json" ]; then
        cat > config.json << 'CEOF'
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
    "api": {"host": "0.0.0.0", "port": 8080, "cors_enabled": true},
    "security": {"require_auth": true, "session_timeout": 3600}
}
CEOF
        echo "  [OK] config.json created"
    fi
    
    echo "  [OK] Configuration complete"
}

install_apk_deps() {
    echo "[6/8] Installing APK build dependencies..."
    
    for pkg in kivy buildozer python-for-android; do
        echo -n "  $pkg... "
        python3 -m pip install "$pkg" 2>/dev/null && echo "OK" || echo "SKIP"
    done
    
    echo "  [OK] APK dependencies complete"
}

install_sim_deps() {
    echo "[7/8] Installing simulation dependencies..."
    
    for pkg in pyglet pyopengl trimesh moderngl moderngl-glew; do
        echo -n "  $pkg... "
        python3 -m pip install "$pkg" 2>/dev/null && echo "OK" || echo "SKIP"
    done
    
    echo "  [OK] Simulation dependencies complete"
}

finish() {
    echo "[8/8] Complete!"
    
    echo ""
    echo "=========================================="
    echo "  Neural Agent Installed!"
    echo "=========================================="
    echo ""
    echo "  Directory: $INSTALL_DIR"
    echo "  Command: /usr/local/bin/neural-agent"
    echo ""
    echo "  Usage:"
    echo "    neural-agent --help"
    echo "    neural-agent user add admin password"
    echo "    neural-agent start"
    echo "    neural-agent --web"
    echo "    linai"
    echo ""
    echo "=========================================="
}

main() {
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