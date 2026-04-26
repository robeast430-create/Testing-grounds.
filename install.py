#!/usr/bin/env python3
"""
Neural Agent Installer
Install on Linux: curl -fsSL https://raw.githubusercontent.com/robeast430-create/Testing-grounds./main/install.py | python3
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path


def check_deps():
    """Check for required dependencies"""
    print("[1/7] Checking dependencies...")
    
    deps = {}
    
    for cmd in ['python3', 'git', 'pip3']:
        try:
            subprocess.run([cmd, '--version'], capture_output=True, check=True)
            deps[cmd] = True
        except:
            deps[cmd] = False
    
    if not all(deps.values()):
        print("  Missing: " + ", ".join(k for k, v in deps.items() if not v))
        install_system_deps()
    
    print("  [OK] Dependencies satisfied")


def install_system_deps():
    """Install system dependencies based on package manager"""
    print("  Installing system dependencies...")
    
    pkg_managers = [
        ('apt-get', ['sudo', 'apt-get', 'update'] + ['sudo', 'apt-get', 'install', '-y']),
        ('dnf', ['sudo', 'dnf', 'install', '-y']),
        ('pacman', ['sudo', 'pacman', '-Sy', '--noconfirm']),
        ('apk', ['sudo', 'apk', 'add', '--no-cache']),
    ]
    
    pkgs = ['python3', 'python3-pip', 'git']
    
    for name, install_cmd in pkg_managers:
        if Path(f'/usr/bin/{name}').exists() or Path(f'/bin/{name}').exists():
            try:
                subprocess.run(install_cmd + pkgs, check=True, capture_output=True)
                print(f"  Installed via {name}")
                return
            except:
                pass
    
    print("  Please install python3, pip3, and git manually")


def install_python_deps():
    """Install Python dependencies"""
    print("[2/7] Installing Python dependencies...")
    
    upgrade = ['pip', 'setuptools', 'wheel']
    for p in upgrade:
        subprocess.run([sys.executable, '-m', 'pip', 'install', '--upgrade', p], 
                      capture_output=True)
    
    core_deps = [
        'numpy>=1.21.0', 'scipy>=1.7.0', 'requests>=2.25.0',
        'beautifulsoup4>=4.9.0', 'sqlalchemy>=1.4.0',
        'chromadb>=0.4.0', 'sentence-transformers>=2.2.0',
        'transformers>=4.20.0', 'torch', 'fastapi>=0.100.0',
        'uvicorn>=0.23.0', 'jinja2>=3.1.0', 'pyyaml>=6.0',
        'cryptography>=41.0.0', 'pillow>=10.0.0',
        'opencv-python>=4.8.0', 'pyttsx3>=2.90',
        'SpeechRecognition>=3.8.0', 'gtts>=2.3.0',
        'flask>=3.0.0', 'flask-socketio>=5.3.0',
        'psutil>=5.9.0', 'schedule>=1.2.0',
        'apscheduler>=3.10.0', 'watchdog>=3.0.0',
        'python-dotenv>=1.0.0', 'pydantic>=2.0.0',
        'aiohttp>=3.8.0', 'websockets>=11.0.0',
        'httpx>=0.25.0', 'scrapy>=2.11.0',
        'pandas>=2.0.0', 'matplotlib>=3.7.0',
        'networkx>=3.0', 'scikit-learn>=1.3.0',
    ]
    
    for dep in core_deps:
        try:
            subprocess.run([sys.executable, '-m', 'pip', 'install', dep], 
                          capture_output=True, timeout=120)
        except:
            pass
    
    print("  [OK] Python dependencies installed")


def download_source(install_dir):
    """Download Neural Agent source"""
    print("[3/7] Downloading Neural Agent...")
    
    install_dir = Path(install_dir)
    install_dir.mkdir(parents=True, exist_ok=True)
    
    os.chdir(install_dir)
    
    repo_url = "https://github.com/robeast430-create/Testing-grounds..git"
    
    if (install_dir / '.git').exists():
        print("  Pulling latest...")
        subprocess.run(['git', 'pull', 'origin', 'main'], capture_output=True)
    else:
        print("  Cloning repository...")
        try:
            subprocess.run(['git', 'clone', '--depth', '1', repo_url, '.'], 
                          capture_output=True, check=True)
        except:
            print("  Git clone failed, trying tarball...")
            try:
                subprocess.run([
                    'curl', '-fsSL', 
                    'https://github.com/robeast430-create/Testing-grounds./archive/main.tar.gz',
                    '-o', '/tmp/neural.tar.gz'
                ], capture_output=True)
                subprocess.run([
                    'tar', '-xzf', '/tmp/neural.tar.gz', '-C', str(install_dir), 
                    '--strip-components=1'
                ], capture_output=True)
            except:
                print("  Download failed. Please check your connection.")
                sys.exit(1)
    
    print("  [OK] Source downloaded")


def install_files(install_dir):
    """Install files and create symlinks"""
    print("[4/7] Installing files...")
    
    install_dir = Path(install_dir)
    
    for subdir in ['auth_data', 'memory_db', 'logs']:
        (install_dir / subdir).mkdir(exist_ok=True)
    
    bin_path = Path('/usr/local/bin/neural-agent')
    bin_path.parent.mkdir(parents=True, exist_ok=True)
    
    cli_path = install_dir / 'neural_agent' / 'cli.py'
    
    neural_script = f'''#!/bin/bash
cd "{install_dir}"
exec python3 "{cli_path}" "$@"
'''
    
    bin_path.write_text(neural_script)
    bin_path.chmod(0o755)
    
    linai_path = install_dir / 'linai.py'
    linai_bin_path = Path('/usr/local/bin/linai')
    linai_bin_path.write_text(neural_script.replace('cli.py', 'linai.py'))
    linai_bin_path.chmod(0o755)
    
    print(f"  [OK] Binary installed to {bin_path}")
    print(f"  [OK] linai installed to {linai_bin_path}")


def configure(install_dir):
    """Create configuration files"""
    print("[5/7] Configuring...")
    
    install_dir = Path(install_dir)
    
    config = install_dir / 'config.json'
    if not config.exists():
        config.write_text('''{
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
''')
    
    bashrc = Path.home() / '.bashrc'
    if bashrc.exists():
        content = bashrc.read_text()
        if 'NEURAL_AGENT_HOME' not in content:
            bashrc.write_text(content + f'''

# Neural Agent
export NEURAL_AGENT_HOME="{install_dir}"
export PYTHONPATH="{install_dir}:$PYTHONPATH"
alias neural-agent="{install_dir}/neural_agent/cli.py"
''')
    
    print("  [OK] Configuration complete")


def install_apk_deps():
    """Install APK build dependencies"""
    print("[6/7] Installing APK build dependencies...")
    
    apk_deps = ['kivy', 'buildozer', 'python-for-android']
    
    for dep in apk_deps:
        try:
            subprocess.run([sys.executable, '-m', 'pip', 'install', dep], 
                          capture_output=True, timeout=300)
        except:
            pass
    
    print("  [OK] APK dependencies installed (optional)")


def finish(install_dir):
    """Print completion message"""
    print("[7/7] Finalizing...")
    
    print("""
==========================================
  Neural Agent Installation Complete!
==========================================

  Installation directory: {dir}
  Binary location: /usr/local/bin/neural-agent

Quick Start:
  neural-agent --help
  neural-agent user add admin password
  neural-agent start
  neural-agent --web

APK Build (requires Android SDK):
  neural-agent apk all

Simulation:
  neural-agent sim create mysim 3d
  neural-agent sim render mysim

==========================================
""".format(dir=install_dir))


def main():
    install_dir = os.environ.get('NEURAL_AGENT_HOME', os.path.expanduser('~/.neural-agent'))
    
    print("==========================================")
    print("  Neural Agent Installer")
    print("==========================================")
    print()
    
    check_deps()
    install_python_deps()
    download_source(install_dir)
    install_files(install_dir)
    configure(install_dir)
    install_apk_deps()
    finish(install_dir)


if __name__ == '__main__':
    main()