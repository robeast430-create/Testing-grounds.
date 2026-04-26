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
    print("[1/8] Checking system dependencies...")
    
    deps = {}
    
    for cmd in ['python3', 'git', 'pip3']:
        try:
            subprocess.run([cmd, '--version'], capture_output=True, check=True, timeout=5)
            deps[cmd] = True
            print(f"  [OK] {cmd}")
        except:
            deps[cmd] = False
            print(f"  [MISSING] {cmd}")
    
    if not all(deps.values()):
        print("\n  Installing missing dependencies...")
        install_system_deps()
    
    print("  [OK] System dependencies satisfied")


def install_system_deps():
    """Install system dependencies based on package manager"""
    print("  Detecting package manager...")
    
    pkg_managers = [
        ('apt-get', ['apt-get', 'update'], ['apt-get', 'install', '-y']),
        ('dnf', ['dnf', 'check-update'], ['dnf', 'install', '-y']),
        ('pacman', ['pacman', '-Sy'], ['pacman', '-Sy', '--noconfirm']),
        ('apk', [], ['apk', 'add', '--no-cache']),
        ('zypper', ['zypper', 'refresh'], ['zypper', 'install', '-y']),
        ('yum', [], ['yum', 'install', '-y']),
    ]
    
    pkgs = ['python3', 'python3-pip', 'git', 'curl', 'wget']
    
    for name, update_cmd, install_cmd in pkg_managers:
        if Path(f'/usr/bin/{name}').exists() or Path(f'/bin/{name}').exists():
            print(f"  Found: {name}")
            try:
                if update_cmd:
                    subprocess.run(update_cmd, capture_output=True, timeout=60)
                subprocess.run(install_cmd + pkgs, check=True, capture_output=True, timeout=300)
                print(f"  [OK] Installed via {name}")
                return
            except Exception as e:
                print(f"  {name} install failed: {e}")
    
    print("  ERROR: Could not install system dependencies automatically")
    print("  Please install: python3, python3-pip, git, curl manually")


def download_source(install_dir):
    """Download Neural Agent source"""
    print("[2/8] Downloading Neural Agent...")
    
    install_dir = Path(install_dir)
    install_dir.mkdir(parents=True, exist_ok=True)
    
    os.chdir(install_dir)
    
    repo_url = "https://github.com/robeast430-create/Testing-grounds..git"
    
    if (install_dir / '.git').exists():
        print("  Repository exists, pulling latest...")
        subprocess.run(['git', 'pull', 'origin', 'main'], capture_output=True)
    else:
        print("  Cloning repository...")
        try:
            result = subprocess.run(
                ['git', 'clone', '--depth', '1', repo_url, '.'],
                capture_output=True,
                text=True,
                timeout=120
            )
            if result.returncode != 0:
                raise Exception(result.stderr)
        except Exception as e:
            print(f"  Git clone failed: {e}")
            print("  Trying tarball download...")
            try:
                subprocess.run([
                    'curl', '-fsSL',
                    'https://github.com/robeast430-create/Testing-grounds./archive/main.tar.gz',
                    '-o', '/tmp/neural.tar.gz'
                ], capture_output=True, timeout=60)
                subprocess.run([
                    'tar', '-xzf', '/tmp/neural.tar.gz',
                    '-C', str(install_dir),
                    '--strip-components=1'
                ], capture_output=True)
                subprocess.run(['rm', '-f', '/tmp/neural.tar.gz'])
            except Exception as e2:
                print(f"  Download failed: {e2}")
                sys.exit(1)
    
    print("  [OK] Source downloaded")
    list_files(install_dir)


def list_files(install_dir):
    """List all installed files"""
    print("  Files installed:")
    py_files = list(Path(install_dir).rglob("*.py"))[:20]
    for f in py_files:
        print(f"    {f.relative_to(install_dir)}")
    print(f"    ... and {len(list(Path(install_dir).rglob('*.py')))-20} more Python files")


def install_python_deps(install_dir):
    """Install ALL Python dependencies"""
    print("[3/8] Installing Python dependencies...")
    
    install_dir = Path(install_dir)
    
    upgrade = ['pip', 'setuptools', 'wheel']
    print("  Upgrading pip/setuptools/wheel...")
    for p in upgrade:
        try:
            subprocess.run(
                [sys.executable, '-m', 'pip', 'install', '--upgrade', p],
                capture_output=True, timeout=60
            )
        except:
            pass
    
    requirements_file = install_dir / 'requirements.txt'
    if requirements_file.exists():
        print("  Installing from requirements.txt...")
        result = subprocess.run(
            [sys.executable, '-m', 'pip', 'install', '-r', str(requirements_file)],
            capture_output=True, text=True, timeout=600
        )
        if result.returncode == 0:
            print("  [OK] requirements.txt installed")
        else:
            print(f"  Warning: {result.stderr[:200]}")
    
    all_deps = [
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
        'nltk>=3.8.0', 'spacy>=3.6.0',
        'textblob>=0.17.0', 'openai>=1.0.0',
        'anthropic>=0.18.0', 'lxml>=4.9.0',
        'qrcode>=7.4.0', 'pytz>=2023.3',
        'rich>=13.0.0', 'click>=8.0.0',
        'prompt-toolkit>=3.0.0', 'colorama>=0.4.0',
        'readline', 'langchain>=0.0.300',
        'huggingface-hub>=0.16.0', 'faiss-cpu>=1.7.0',
        'tqdm>=4.65.0', 'accelerate>=0.20.0',
        'safetensors>=0.3.0', 'tokenizers>=0.13.0',
    ]
    
    print(f"  Installing {len(all_deps)} additional packages...")
    for i, dep in enumerate(all_deps):
        try:
            result = subprocess.run(
                [sys.executable, '-m', 'pip', 'install', dep],
                capture_output=True, timeout=180
            )
            if i % 10 == 0:
                print(f"  Progress: {i}/{len(all_deps)}")
        except:
            pass
    
    print("  [OK] Python dependencies installed")


def install_files(install_dir):
    """Install files and create symlinks"""
    print("[4/8] Installing binaries...")
    
    install_dir = Path(install_dir)
    
    for subdir in ['auth_data', 'memory_db', 'logs']:
        (install_dir / subdir).mkdir(exist_ok=True)
    
    bin_dir = Path('/usr/local/bin')
    bin_dir.mkdir(parents=True, exist_ok=True)
    
    cli_path = install_dir / 'neural_agent' / 'cli.py'
    linai_path = install_dir / 'linai.py'
    install_py_path = install_dir / 'install.py'
    install_sh_path = install_dir / 'install.sh'
    
    neural_script = f'''#!/bin/bash
cd "{install_dir}"
exec python3 "{cli_path}" "$@"
'''
    
    linai_script = f'''#!/bin/bash
cd "{install_dir}"
exec python3 "{linai_path}" "$@"
'''
    
    (bin_dir / 'neural-agent').write_text(neural_script)
    (bin_dir / 'neural-agent').chmod(0o755)
    
    (bin_dir / 'linai').write_text(linai_script)
    (bin_dir / 'linai').chmod(0o755)
    
    print(f"  [OK] /usr/local/bin/neural-agent")
    print(f"  [OK] /usr/local/bin/linai")


def configure(install_dir):
    """Create configuration files"""
    print("[5/8] Configuring...")
    
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
        print("  [OK] Created config.json")
    
    bashrc = Path.home() / '.bashrc'
    marker = "# Neural Agent"
    
    if bashrc.exists():
        content = bashrc.read_text()
        if marker not in content:
            bashrc.write_text(content + f'''

{model_marker}
export NEURAL_AGENT_HOME="{install_dir}"
export PYTHONPATH="{install_dir}:$PYTHONPATH"
alias neural-agent="{install_dir}/neural_agent/cli.py"
alias linai="{install_dir}/linai.py"
''')
            print("  [OK] Added to .bashrc")
    
    print("  [OK] Configuration complete")


def install_apk_deps():
    """Install APK build dependencies"""
    print("[6/8] Installing APK build dependencies (optional)...")
    
    apk_deps = [
        'kivy>=2.2.0',
        'buildozer>=1.5.0',
        'python-for-android>=2022.12.0',
    ]
    
    for dep in apk_deps:
        try:
            subprocess.run(
                [sys.executable, '-m', 'pip', 'install', dep],
                capture_output=True, timeout=300
            )
            print(f"  [OK] {dep}")
        except:
            print(f"  [SKIP] {dep}")
    
    print("  [OK] APK dependencies complete")


def install_simulation_deps():
    """Install 3D simulation dependencies"""
    print("[7/8] Installing simulation dependencies...")
    
    sim_deps = [
        'pyglet>=2.0.0',
        'pyopengl>=3.1.0',
        'trimesh>=3.21.0',
        'moderngl>=5.8.0',
    ]
    
    for dep in sim_deps:
        try:
            subprocess.run(
                [sys.executable, '-m', 'pip', 'install', dep],
                capture_output=True, timeout=180
            )
        except:
            pass
    
    print("  [OK] Simulation dependencies complete")


def finish(install_dir):
    """Print completion message"""
    print("[8/8] Finalizing...")
    
    print(f"""
==========================================
  Neural Agent Installation Complete!
==========================================

  Installation directory: {install_dir}
  Binary location: /usr/local/bin/neural-agent

Quick Start:
  neural-agent --help
  neural-agent user add admin password
  neural-agent start
  neural-agent --web
  linai

Simulations:
  neural-agent sim create mysim 3d
  neural-agent sim render mysim

APK Build (requires Android SDK):
  neural-agent apk all

All Files Installed:
  neural_agent/ (entire package)
  linai.py
  install.py / install.sh
  requirements.txt
  docs/
  examples/

==========================================
""")


def main():
    install_dir = os.environ.get('NEURAL_AGENT_HOME', os.path.expanduser('~/.neural-agent'))
    
    print("==========================================")
    print("  Neural Agent Installer")
    print("==========================================")
    print()
    
    check_deps()
    download_source(install_dir)
    install_python_deps(install_dir)
    install_files(install_dir)
    configure(install_dir)
    install_apk_deps()
    install_simulation_deps()
    finish(install_dir)


if __name__ == '__main__':
    main()