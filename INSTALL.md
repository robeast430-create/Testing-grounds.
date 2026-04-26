# Neural Agent - Installation & Usage Guide

## Install with one command:

```bash
curl -fsSL https://raw.githubusercontent.com/robeast430-create/Testing-grounds./main/install.sh | bash
```

---

## Quick Install (Alternative Methods)

### Method 2: Python
```bash
curl -fsSL https://raw.githubusercontent.com/robeast430-create/Testing-grounds./main/install.py | python3
```

### Method 3: Manual Install
```bash
git clone https://github.com/robeast430-create/Testing-grounds..git
cd Testing-grounds.
pip3 install -r requirements.txt
chmod +x neural_agent/cli.py
```

---

## System Requirements

### Required Dependencies
| Package | Minimum Version | Install Command |
|---------|-----------------|------------------|
| Python | 3.8+ | `apt install python3` |
| pip | 20.0+ | `apt install python3-pip` |
| git | 2.0+ | `apt install git` |

### Optional Dependencies
| Package | Purpose | Install Command |
|---------|---------|------------------|
| Java JDK 11+ | APK building | `apt install openjdk-11-jdk` |
| Android SDK | APK building | See Android docs |
| Blender | 3D simulation export | `snap install blender` |
| sox | Voice/audio | `apt install sox` |
| portaudio | Voice input | `apt install portaudio19-dev` |
| libasound2-dev | Audio playback | `apt install libasound2-dev` |
| bluez | Bluetooth | `apt install bluez` |

---

## Installation Per OS

### Ubuntu/Debian
```bash
sudo apt update
sudo apt install python3 python3-pip git
curl -fsSL https://.../install.sh | bash
```

### Fedora
```bash
sudo dnf install python3 python3-pip git
curl -fsSL https://.../install.sh | bash
```

### Arch Linux
```bash
sudo pacman -Sy python python-pip git
curl -fsSL https://.../install.sh | bash
```

### Alpine
```bash
apk add python3 py3-pip git
curl -fsSL https://.../install.sh | bash
```

### Android (Termux)
```bash
pkg update
pkg install python git
curl -fsSL https://.../install.sh | bash
```

---

## Post-Installation Commands

### First Time Setup
```bash
# Create admin user
neural-agent user add admin password

# Start interactive mode
neural-agent start

# Start with web dashboard
neural-agent --web

# Start on custom port
neural-agent --web --port 9000
```

### Running Neural Agent

```bash
# Interactive CLI
neural-agent start

# With web interface
neural-agent --web

# Skip authentication
neural-agent --no-auth start

# User management
neural-agent user add username password
neural-agent user list
neural-agent user delete username
```

---

## 2D/3D/4D Simulations

```bash
# Create simulations
neural-agent sim create mysim 2d
neural-agent sim create mysim 3d
neural-agent sim create mysim 4d

# List simulations
neural-agent sim list

# Add particles
neural-agent sim add-particle mysim

# Step simulation
neural-agent sim step mysim

# Render to HTML
neural-agent sim render mysim output.html

# Export to Blender (requires Blender installed)
neural-agent sim blender mysim
```

---

## APK Build Commands

```bash
# Check dependencies
neural-agent apk check

# Setup build environment
neural-agent apk setup

# Build debug APK
neural-agent apk build

# Build with ALL features
neural-agent apk full

# Build release APK
neural-agent apk release

# Run ALL steps automatically
neural-agent apk all
```

---

## LinuxAI Terminal UI

Start the interactive TUI:
```bash
linai
```

### linai Commands
```
/help           Show help
/chat <msg>     Chat with AI
/search <q>     Web search
/learn <text>   Add to memory
/recall <q>     Search memory
/tasks          List tasks
/task <cmd>     Execute task
/kill           Trigger kill switch
/sim <cmd>      Simulation commands
/web            Start web dashboard
/status         System status
/sysinfo        System info
/exit           Exit
```

### linai Keyboard Shortcuts
```
Ctrl+C          Interrupt/Cancel
Ctrl+L          Clear screen
Ctrl+Q          Quit
Tab             Auto-complete
Up/Down         Command history
Ctrl+R          Search history
```

---

## API Server Endpoints

Start web server: `neural-agent web`

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/chat` | POST | Chat with AI |
| `/learn` | POST | Learn content |
| `/recall` | POST | Search memories |
| `/do` | POST | Execute task |
| `/search` | POST | Web search |
| `/fetch` | POST | Fetch URL |
| `/run` | POST | Run command |
| `/kill` | POST | Kill switch |
| `/status` | GET | Status |
| `/stats` | GET | Statistics |
| `/sysinfo` | GET | System info |
| `/tasks` | GET | Task list |
| `/sim/list` | GET | Simulations |
| `/sim/create` | POST | Create simulation |
| `/sim/step` | POST | Step simulation |
| `/sim/render` | POST | Render simulation |
| `/sim/blender` | POST | Export to Blender |

---

## Configuration

Edit `config.json`:
```json
{
    "agent_name": "Neural Agent",
    "memory_enabled": true,
    "simulation_enabled": true,
    "api": {
        "host": "0.0.0.0",
        "port": 8080
    }
}
```

---

## Troubleshooting

### Module not found errors
```bash
pip3 install -r requirements.txt
```

### Permission denied
```bash
sudo chmod +x /usr/local/bin/neural-agent
```

### Uninstall
```bash
rm -rf ~/.neural-agent
sudo rm /usr/local/bin/neural-agent
```

---

## Quick Reference

| Command | Description |
|---------|-------------|
| `neural-agent start` | Start agent |
| `neural-agent --web` | Start with web UI |
| `linai` | Terminal UI |
| `neural-agent sim *` | Simulations |
| `neural-agent apk *` | APK builder |
| `neural-agent user *` | User management |

---

For more help, see the full documentation or run `neural-agent --help`