#!/usr/bin/env python3
"""
Neural Agent Installer - Full Installation
curl -fsSL https://raw.githubusercontent.com/robeast430-create/Testing-grounds./main/install.py | python3
"""

import os
import sys
import subprocess
from pathlib import Path


def print_status(msg, ok=True):
    status = "[OK]" if ok else "[FAIL]"
    print(f"  {status} {msg}")


def run_cmd(cmd, show_error=True, timeout=300):
    """Run command and return success status"""
    try:
        result = subprocess.run(
            cmd if isinstance(cmd, list) else cmd.split(),
            capture_output=True,
            text=True,
            timeout=timeout
        )
        return result.returncode == 0, result
    except subprocess.TimeoutExpired:
        return False, None
    except Exception as e:
        if show_error:
            print(f"    Error: {e}")
        return False, None


def check_deps():
    """Check system dependencies"""
    print("[1/8] Checking dependencies...")
    
    for cmd in ['python3', 'git', 'pip3', 'curl']:
        success, _ = run_cmd([cmd, '--version'], show_error=False)
        print_status(f"{cmd}: installed" if success else f"{cmd}: MISSING")
        
        if not success and cmd in ['python3', 'git', 'pip3']:
            install_system_deps()
            break


def install_system_deps():
    """Install system packages"""
    print("\n  Installing system packages...")
    
    pkg_managers = [
        ('apt', ['sudo', 'apt-get', 'update']),
        ('apt', ['sudo', 'apt-get', 'install', '-y', 
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
    )
    
    for manager, install_cmd in pkg_managers:
        if Path(f'/usr/bin/{manager}').exists():
            print(f"  Using {manager}...")
            success, _ = run_cmd(install_cmd, timeout=300)
            if success:
                print_status("System packages installed")
                return
            break
    
    print_status("Could not install system packages automatically", False)


def download_source(install_dir):
    """Download Neural Agent"""
    print("\n[2/8] Downloading Neural Agent...")
    
    install_dir = Path(install_dir)
    install_dir.mkdir(parents=True, exist_ok=True)
    os.chdir(install_dir)
    
    if (install_dir / '.git').exists():
        print_status("Pulling latest...")
        run_cmd(['git', 'pull', 'origin', 'main'], show_error=False)
    else:
        print_status("Cloning repository...")
        success, result = run_cmd([
            'git', 'clone', '--depth', '1',
            'https://github.com/robeast430-create/Testing-grounds..git', '.'
        ], timeout=120)
        
        if not success:
            print_status("Git clone failed, trying tarball...", False)
            run_cmd([
                'curl', '-fsSL',
                'https://github.com/robeast430-create/Testing-grounds./archive/main.tar.gz',
                '-o', '/tmp/neural.tar.gz'
            ], timeout=60)
            run_cmd([
                'tar', '-xzf', '/tmp/neural.tar.gz',
                '-C', str(install_dir), '--strip-components=1'
            ], timeout=60)
    
    file_count = len(list(install_dir.rglob('*')))
    print_status(f"Source downloaded ({file_count} files)")
    
    dirs = [d.name for d in install_dir.iterdir() if d.is_dir()][:10]
    for d in dirs:
        print(f"    - {d}/")


def install_python_deps(install_dir):
    """Install ALL Python dependencies"""
    print("\n[3/8] Installing Python dependencies...")
    
    install_dir = Path(install_dir)
    
    print("  Upgrading pip...")
    run_cmd([sys.executable, '-m', 'pip', 'install', '--upgrade', 'pip', 'setuptools', 'wheel'])
    
    success_count = 0
    fail_count = 0
    
    if (install_dir / 'requirements.txt').exists():
        print("\n  Installing from requirements.txt...")
        success, result = run_cmd([
            sys.executable, '-m', 'pip', 'install', '-r', str(install_dir / 'requirements.txt')
        ], timeout=600)
        
        if success:
            print_status("requirements.txt installed")
            success_count += 1
        else:
            print_status("requirements.txt failed", False)
            
            print("  Installing packages individually...")
            with open(install_dir / 'requirements.txt') as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                    success, _ = run_cmd([sys.executable, '-m', 'pip', 'install', line], timeout=120)
                    if success:
                        success_count += 1
                    else:
                        fail_count += 1
    
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
        success, _ = run_cmd([sys.executable, '-m', 'pip', 'install', pkg], timeout=180)
        if success:
            print_status(pkg)
            success_count += 1
        else:
            print_status(f"{pkg}: skipped", False)
            fail_count += 1
    
    print(f"\n  Installed: {success_count}, Skipped: {fail_count}")
    print_status("Python dependencies complete")


def install_files(install_dir):
    """Install binaries"""
    print("\n[4/8] Installing binaries...")
    
    install_dir = Path(install_dir)
    
    for subdir in ['auth_data', 'memory_db', 'logs']:
        (install_dir / subdir).mkdir(exist_ok=True)
    
    bin_dir = Path('/usr/local/bin')
    bin_dir.mkdir(parents=True, exist_ok=True)
    
    neural_script = f'''#!/bin/bash
SCRIPT_DIR="$(cd "$(dirname "${{BASH_SOURCE[0]}}")" && pwd)"
INSTALL_DIR="$(dirname "$SCRIPT_DIR")/../.."
cd "$INSTALL_DIR"
exec python3 neural_agent/cli.py "$@"
'''
    
    linai_script = f'''#!/bin/bash
SCRIPT_DIR="$(cd "$(dirname "${{BASH_SOURCE[0]}}")" && pwd)"
INSTALL_DIR="$(dirname "$SCRIPT_DIR")/../.."
cd "$INSTALL_DIR"
exec python3 linai.py "$@"
'''
    
    (bin_dir / 'neural-agent').write_text(neural_script)
    (bin_dir / 'neural-agent').chmod(0o755)
    print_status("/usr/local/bin/neural-agent")
    
    (bin_dir / 'linai').write_text(linai_script)
    (bin_dir / 'linai').chmod(0o755)
    print_status("/usr/local/bin/linai")


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
        print_status("config.json created")
    
    print_status("Configuration complete")


def install_apk_deps():
    """APK build dependencies"""
    print("\n[6/8] Installing APK dependencies...")
    
    for pkg in ['kivy', 'buildozer', 'python-for-android']:
        success, _ = run_cmd([sys.executable, '-m', 'pip', 'install', pkg], timeout=300)
        print_status(pkg if success else f"{pkg}: skipped")
    
    print_status("APK dependencies complete")


def install_sim_deps():
    """Simulation dependencies"""
    print("\n[7/8] Installing simulation dependencies...")
    
    for pkg in ['pyglet', 'pyopengl', 'trimesh', 'moderngl', 'moderngl-glew']:
        success, _ = run_cmd([sys.executable, '-m', 'pip', 'install', pkg], timeout=180)
        print_status(pkg if success else f"{pkg}: skipped")
    
    print_status("Simulation dependencies complete")


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