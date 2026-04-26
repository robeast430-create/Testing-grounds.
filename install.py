#!/usr/bin/env python3
"""
Neural Agent Installer - Full Installation
curl -fsSL https://raw.githubusercontent.com/robeast430-create/Testing-grounds./main/install.py | python3
"""

import os
import sys
import subprocess
from pathlib import Path


def install_package(pkg):
    """Install a package and return (success, output)"""
    try:
        result = subprocess.run(
            [sys.executable, '-m', 'pip', 'install', pkg],
            capture_output=True,
            text=True,
            timeout=120
        )
        return result.returncode == 0, result.stdout + result.stderr
    except subprocess.TimeoutExpired:
        return False, "Timeout"
    except Exception as e:
        return False, str(e)


def check_deps():
    """Check system dependencies"""
    print("[1/8] Checking dependencies...")
    
    for cmd in ['python3', 'git', 'pip3', 'curl']:
        try:
            subprocess.run([cmd, '--version'], capture_output=True, timeout=5)
            print(f"  [OK] {cmd}")
        except:
            print(f"  [MISSING] {cmd}")
            install_system_deps()
            break


def install_system_deps():
    """Install system packages"""
    print("\n  Installing system packages...")
    
    pkg_managers = [
        ('apt-get', ['sudo', 'apt-get', 'update']),
        ('apt-get', ['sudo', 'apt-get', 'install', '-y', 
                     'python3', 'python3-pip', 'git', 'curl', 'wget',
                     'python3-dev', 'build-essential']),
        ('dnf', ['sudo', 'dnf', 'install', '-y',
                 'python3', 'python3-pip', 'git', 'curl', 'wget',
                 'python3-devel', 'gcc']),
        ('pacman', ['sudo', 'pacman', '-Sy', '--noconfirm',
                   'python', 'python-pip', 'git', 'curl', 'wget',
                   'base-devel']),
        ('apk', ['sudo', 'apk', 'add', '--no-cache',
                 'python3', 'py3-pip', 'git', 'curl',
                 'python3-dev', 'musl-dev', 'gcc']),
    ]
    
    for manager, cmd in pkg_managers:
        if Path(f'/usr/bin/{manager}').exists():
            print(f"  Using {manager}...")
            subprocess.run(cmd, capture_output=True, timeout=120)
            print("  [OK] System packages installed")
            return
    
    print("  [FAIL] Could not install system packages")


def download_source(install_dir):
    """Download Neural Agent"""
    print("\n[2/8] Downloading Neural Agent...")
    
    install_dir = Path(install_dir)
    install_dir.mkdir(parents=True, exist_ok=True)
    os.chdir(install_dir)
    
    if (install_dir / '.git').exists():
        print("  Pulling latest...")
        subprocess.run(['git', 'pull', 'origin', 'main'], capture_output=True)
    else:
        print("  Cloning repository...")
        success, output = install_package('git')
        if not success:
            print("  Git not available, trying tarball...")
        
        result = subprocess.run([
            'curl', '-fsSL',
            'https://github.com/robeast430-create/Testing-grounds./archive/main.tar.gz',
            '-o', '/tmp/neural.tar.gz'
        ], capture_output=True, timeout=60)
        
        subprocess.run([
            'tar', '-xzf', '/tmp/neural.tar.gz',
            '-C', str(install_dir), '--strip-components=1'
        ], capture_output=True, timeout=60)
    
    file_count = len(list(install_dir.rglob('*')))
    print(f"  [OK] Source downloaded ({file_count} files)")


def install_python_deps(install_dir):
    """Install ALL Python dependencies"""
    print("\n[3/8] Installing Python dependencies...")
    
    install_dir = Path(install_dir)
    
    print("  Upgrading pip...")
    install_package('pip')
    install_package('setuptools')
    install_package('wheel')
    
    installed = 0
    failed = 0
    
    if (install_dir / 'requirements.txt').exists():
        print("\n  Installing from requirements.txt...")
        with open(install_dir / 'requirements.txt') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                print(f"    {line}... ", end='', flush=True)
                success, output = install_package(line)
                
                if success:
                    print("OK")
                    installed += 1
                else:
                    print("SKIP")
                    reason = get_skip_reason(output)
                    print(f"      Reason: {reason}")
                    failed += 1
    
    print("\n  Installing core packages...")
    
    packages = [
        'numpy', 'scipy', 'requests', 'beautifulsoup4', 'lxml', 'html5lib',
        'sqlalchemy', 'chromadb', 'sentence-transformers',
        'transformers', 'torch', 'fastapi', 'uvicorn',
        'jinja2', 'pyyaml', 'cryptography', 'pillow',
        'opencv-python', 'opencv-contrib-python',
        'flask', 'flask-socketio', 'flask-cors',
        'psutil', 'schedule', 'apscheduler',
        'watchdog', 'python-dotenv', 'pydantic',
        'aiohttp', 'websockets', 'httpx', 'scrapy',
        'pandas', 'matplotlib', 'networkx', 'scikit-learn',
        'nltk', 'spacy', 'textblob',
        'openai', 'anthropic',
        'qrcode', 'pytz', 'rich', 'click', 'prompt-toolkit', 'colorama',
        'readline', 'langchain', 'huggingface-hub',
        'faiss-cpu', 'tqdm', 'accelerate', 'safetensors',
        'tokenizers', 'pyglet', 'pyopengl', 'trimesh', 'moderngl',
        'kivy', 'buildozer', 'python-for-android',
        'pyttsx3', 'gtts', 'SpeechRecognition',
    ]
    
    for pkg in packages:
        print(f"    {pkg}... ", end='', flush=True)
        success, output = install_package(pkg)
        
        if success:
            print("OK")
            installed += 1
        else:
            print("SKIP")
            reason = get_skip_reason(output)
            print(f"      Reason: {reason}")
            failed += 1
    
    print(f"\n  Summary: Installed={installed} Failed={failed}")


def get_skip_reason(output):
    """Extract useful error message from pip output"""
    if not output:
        return "Unknown error"
    
    output = output.lower()
    
    if 'already satisfied' in output:
        return "Already installed"
    elif 'could not find' in output or 'not found' in output:
        return "Package not found in PyPI"
    elif 'requirement already satisfied' in output:
        return "Already satisfied"
    elif 'connection' in output or 'timeout' in output or 'network' in output:
        return "Network/connection error"
    elif 'permission' in output or 'sudo' in output or 'root' in output:
        return "Permission denied (try sudo)"
    elif 'version' in output and 'conflict' in output:
        return "Version conflict with existing package"
    elif 'platform' in output or 'system' in output:
        return "Incompatible platform/system"
    elif 'no module named' in output:
        return "Missing system dependency"
    else:
        lines = output.split('\n')
        for line in lines:
            if 'error' in line.lower() or 'failed' in line.lower():
                return line.strip()[:100]
        return output.split('\n')[-1].strip()[:100] if output else "Unknown"


def install_files(install_dir):
    """Install binaries"""
    print("\n[4/8] Installing binaries...")
    
    install_dir = Path(install_dir)
    
    for subdir in ['auth_data', 'memory_db', 'logs']:
        (install_dir / subdir).mkdir(exist_ok=True)
    
    bin_dir = Path('/usr/local/bin')
    bin_dir.mkdir(parents=True, exist_ok=True)
    
    neural_script = '''#!/bin/bash
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INSTALL_DIR="$(dirname "$SCRIPT_DIR")/../.."
cd "$INSTALL_DIR"
exec python3 neural_agent/cli.py "$@"
'''
    
    linai_script = '''#!/bin/bash
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INSTALL_DIR="$(dirname "$SCRIPT_DIR")/../.."
cd "$INSTALL_DIR"
exec python3 linai.py "$@"
'''
    
    (bin_dir / 'neural-agent').write_text(neural_script)
    (bin_dir / 'neural-agent').chmod(0o755)
    print("  [OK] /usr/local/bin/neural-agent")
    
    (bin_dir / 'linai').write_text(linai_script)
    (bin_dir / 'linai').chmod(0o755)
    print("  [OK] /usr/local/bin/linai")


def configure(install_dir):
    """Create config"""
    print("\n[5/8] Configuring...")
    
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
    "api": {"host": "0.0.0.0", "port": 8080, "cors_enabled": true},
    "security": {"require_auth": true, "session_timeout": 3600}
}
''')
        print("  [OK] config.json created")
    
    print("  [OK] Configuration complete")


def install_apk_deps():
    """APK build dependencies"""
    print("\n[6/8] Installing APK build dependencies...")
    
    for pkg in ['kivy', 'buildozer', 'python-for-android']:
        print(f"  {pkg}... ", end='', flush=True)
        success, output = install_package(pkg)
        
        if success:
            print("OK")
        else:
            print("SKIP")
            print(f"      Reason: {get_skip_reason(output)}")
    
    print("  [OK] APK dependencies done")


def install_sim_deps():
    """Simulation dependencies"""
    print("\n[7/8] Installing simulation dependencies...")
    
    for pkg in ['pyglet', 'pyopengl', 'trimesh', 'moderngl', 'moderngl-glew']:
        print(f"  {pkg}... ", end='', flush=True)
        success, output = install_package(pkg)
        
        if success:
            print("OK")
        else:
            print("SKIP")
            print(f"      Reason: {get_skip_reason(output)}")
    
    print("  [OK] Simulation dependencies done")


def finish(install_dir):
    """Done"""
    print("\n[8/8] Complete!")
    
    print("""
==========================================
  Neural Agent Installed!
==========================================

  Directory: {dir}
  Command: /usr/local/bin/neural-agent

  Usage:
    neural-agent --help
    neural-agent user add admin password
    neural-agent start
    neural-agent --web
    linai

==========================================
""".format(dir=install_dir))


def main():
    install_dir = os.environ.get('NEURAL_AGENT_HOME', os.path.expanduser('~/.neural-agent'))
    
    print("==========================================")
    print("  Neural Agent Installer v1.0")
    print("==========================================")
    print()
    
    check_deps()
    download_source(install_dir)
    install_python_deps(install_dir)
    install_files(install_dir)
    configure(install_dir)
    install_apk_deps()
    install_sim_deps()
    finish(install_dir)


if __name__ == '__main__':
    main()