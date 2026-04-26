import subprocess
import os
import json
from pathlib import Path

class BuildManager:
    def __init__(self, agent):
        self.agent = agent
        self.build_history = []
    
    def detect_project_type(self):
        if os.path.exists("package.json"):
            return "node"
        elif os.path.exists("requirements.txt") or os.path.exists("setup.py"):
            return "python"
        elif os.path.exists("Cargo.toml"):
            return "rust"
        elif os.path.exists("go.mod"):
            return "go"
        elif os.path.exists("pom.xml"):
            return "java"
        elif os.path.exists("build.gradle"):
            return "java-gradle"
        elif os.path.exists("Makefile"):
            return "make"
        elif os.path.exists("CMakeLists.txt"):
            return "cmake"
        elif os.path.exists("Dockerfile"):
            return "docker"
        else:
            return "unknown"
    
    def build(self, project_type=None, target=None):
        if project_type is None:
            project_type = self.detect_project_type()
        
        builders = {
            "node": self._build_node,
            "python": self._build_python,
            "rust": self._build_rust,
            "go": self._build_go,
            "java": self._build_java,
            "java-gradle": self._build_gradle,
            "make": self._build_make,
            "cmake": self._build_cmake,
            "docker": self._build_docker,
        }
        
        builder = builders.get(project_type)
        if not builder:
            return f"No builder for project type: {project_type}"
        
        result = builder(target)
        self.build_history.append({
            "type": project_type,
            "target": target,
            "result": result,
            "success": "Error" not in result
        })
        return result
    
    def _build_node(self, target=None):
        if not os.path.exists("package.json"):
            return "package.json not found"
        
        try:
            if target == "install":
                result = subprocess.run(["npm", "install"], capture_output=True, text=True, timeout=300)
            elif target == "test":
                result = subprocess.run(["npm", "test"], capture_output=True, text=True, timeout=120)
            elif target == "lint":
                result = subprocess.run(["npm", "run", "lint"], capture_output=True, text=True, timeout=60)
            elif target == "build":
                result = subprocess.run(["npm", "run", "build"], capture_output=True, text=True, timeout=300)
            else:
                result = subprocess.run(["npm", "install"], capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                return f"npm {target or 'install'} completed successfully"
            else:
                return f"Error: {result.stderr[:500]}"
        except subprocess.TimeoutExpired:
            return "Build timed out"
        except Exception as e:
            return f"Error: {e}"
    
    def _build_python(self, target=None):
        if not os.path.exists("requirements.txt") and not os.path.exists("setup.py"):
            return "No Python build files found"
        
        try:
            if target == "install":
                result = subprocess.run(["pip", "install", "-r", "requirements.txt"], capture_output=True, text=True, timeout=300)
            elif target == "dev":
                result = subprocess.run(["pip", "install", "-e", "."], capture_output=True, text=True, timeout=300)
            elif target == "test":
                result = subprocess.run(["pytest"], capture_output=True, text=True, timeout=120)
            elif target == "package":
                result = subprocess.run(["python", "setup.py", "sdist"], capture_output=True, text=True, timeout=300)
            else:
                result = subprocess.run(["pip", "install", "-e", "."], capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                return f"Python build completed"
            else:
                return f"Error: {result.stderr[:500]}"
        except subprocess.TimeoutExpired:
            return "Build timed out"
        except Exception as e:
            return f"Error: {e}"
    
    def _build_rust(self, target=None):
        if not os.path.exists("Cargo.toml"):
            return "Cargo.toml not found"
        
        try:
            if target == "build":
                result = subprocess.run(["cargo", "build"], capture_output=True, text=True, timeout=300)
            elif target == "release":
                result = subprocess.run(["cargo", "build", "--release"], capture_output=True, text=True, timeout=600)
            elif target == "test":
                result = subprocess.run(["cargo", "test"], capture_output=True, text=True, timeout=300)
            elif target == "check":
                result = subprocess.run(["cargo", "check"], capture_output=True, text=True, timeout=120)
            else:
                result = subprocess.run(["cargo", "build"], capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                return f"Rust build completed"
            else:
                return f"Error: {result.stderr[:500]}"
        except subprocess.TimeoutExpired:
            return "Build timed out"
        except Exception as e:
            return f"Error: {e}"
    
    def _build_go(self, target=None):
        if not os.path.exists("go.mod"):
            return "go.mod not found"
        
        try:
            if target == "build":
                result = subprocess.run(["go", "build", "./..."], capture_output=True, text=True, timeout=300)
            elif target == "test":
                result = subprocess.run(["go", "test", "./..."], capture_output=True, text=True, timeout=300)
            elif target == "install":
                result = subprocess.run(["go", "install", "./..."], capture_output=True, text=True, timeout=300)
            else:
                result = subprocess.run(["go", "build", "./..."], capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                return f"Go build completed"
            else:
                return f"Error: {result.stderr[:500]}"
        except subprocess.TimeoutExpired:
            return "Build timed out"
        except Exception as e:
            return f"Error: {e}"
    
    def _build_java(self, target=None):
        try:
            if target == "build":
                result = subprocess.run(["mvn", "package"], capture_output=True, text=True, timeout=300)
            elif target == "test":
                result = subprocess.run(["mvn", "test"], capture_output=True, text=True, timeout=300)
            elif target == "clean":
                result = subprocess.run(["mvn", "clean"], capture_output=True, text=True, timeout=60)
            else:
                result = subprocess.run(["mvn", "package"], capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                return f"Maven build completed"
            else:
                return f"Error: {result.stderr[:500]}"
        except subprocess.TimeoutExpired:
            return "Build timed out"
        except Exception as e:
            return f"Error: {e}"
    
    def _build_gradle(self, target=None):
        try:
            if target == "build":
                result = subprocess.run(["./gradlew", "build"], capture_output=True, text=True, timeout=300)
            elif target == "test":
                result = subprocess.run(["./gradlew", "test"], capture_output=True, text=True, timeout=300)
            elif target == "clean":
                result = subprocess.run(["./gradlew", "clean"], capture_output=True, text=True, timeout=60)
            else:
                result = subprocess.run(["./gradlew", "build"], capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                return f"Gradle build completed"
            else:
                return f"Error: {result.stderr[:500]}"
        except subprocess.TimeoutExpired:
            return "Build timed out"
        except Exception as e:
            return f"Error: {e}"
    
    def _build_make(self, target=None):
        try:
            cmd = ["make"]
            if target:
                cmd.append(target)
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                return f"Make build completed"
            else:
                return f"Error: {result.stderr[:500]}"
        except subprocess.TimeoutExpired:
            return "Build timed out"
        except Exception as e:
            return f"Error: {e}"
    
    def _build_cmake(self, target=None):
        build_dir = "build"
        
        try:
            if not os.path.exists(build_dir):
                os.makedirs(build_dir)
                result = subprocess.run(["cmake", ".."], cwd=build_dir, capture_output=True, text=True, timeout=60)
                if result.returncode != 0:
                    return f"CMake configuration failed: {result.stderr}"
            
            result = subprocess.run(["cmake", "--build", "."], cwd=build_dir, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                return f"CMake build completed"
            else:
                return f"Error: {result.stderr[:500]}"
        except subprocess.TimeoutExpired:
            return "Build timed out"
        except Exception as e:
            return f"Error: {e}"
    
    def _build_docker(self, target=None):
        if not os.path.exists("Dockerfile"):
            return "Dockerfile not found"
        
        try:
            if target == "build":
                result = subprocess.run(
                    ["docker", "build", "-t", "myapp:latest", "."],
                    capture_output=True,
                    text=True,
                    timeout=600
                )
            elif target == "run":
                result = subprocess.run(
                    ["docker", "run", "--rm", "myapp:latest"],
                    capture_output=True,
                    text=True,
                    timeout=60
                )
            elif target == "stop":
                subprocess.run(["docker", "ps", "-a", "-q"], capture_output=True)
                result = subprocess.run(["docker", "container", "stop", "myapp"], capture_output=True, text=True)
            else:
                result = subprocess.run(
                    ["docker", "build", "-t", "myapp:latest", "."],
                    capture_output=True,
                    text=True,
                    timeout=600
                )
            
            if result.returncode == 0:
                return f"Docker {target or 'build'} completed"
            else:
                return f"Error: {result.stderr[:500]}"
        except subprocess.TimeoutExpired:
            return "Build timed out"
        except Exception as e:
            return f"Error: {e}"
    
    def run_tests(self, project_type=None):
        return self.build(project_type, "test")
    
    def clean(self, project_type=None):
        if project_type is None:
            project_type = self.detect_project_type()
        
        import shutil
        
        targets = {
            "node": ["node_modules"],
            "python": ["build", "dist", "*.egg-info", "__pycache__"],
            "rust": ["target"],
            "go": [],
            "java": ["target"],
            "java-gradle": ["build", ".gradle"],
            "make": [],
            "cmake": ["build"],
            "docker": []
        }
        
        patterns = targets.get(project_type, [])
        removed = []
        
        for pattern in patterns:
            if "*" in pattern:
                import glob
                for item in glob.glob(pattern):
                    if os.path.isdir(item):
                        shutil.rmtree(item)
                    else:
                        os.remove(item)
                    removed.append(item)
            elif os.path.exists(pattern):
                if os.path.isdir(pattern):
                    shutil.rmtree(pattern)
                else:
                    os.remove(pattern)
                removed.append(pattern)
        
        return f"Cleaned: {', '.join(removed) if removed else 'nothing'}"
    
    def get_project_info(self):
        project_type = self.detect_project_type()
        
        info = {
            "type": project_type,
            "files": []
        }
        
        if project_type == "node":
            with open("package.json", "r") as f:
                data = json.load(f)
                info["name"] = data.get("name")
                info["version"] = data.get("version")
                info["scripts"] = list(data.get("scripts", {}).keys())
        
        elif project_type == "python":
            if os.path.exists("setup.py"):
                info["name"] = "Python package"
            elif os.path.exists("requirements.txt"):
                with open("requirements.txt", "r") as f:
                    info["dependencies"] = len(f.readlines())
        
        return info


class ContainerManager:
    def __init__(self, agent):
        self.agent = agent
    
    def is_docker_available(self):
        try:
            result = subprocess.run(["docker", "--version"], capture_output=True)
            return result.returncode == 0
        except:
            return False
    
    def list_containers(self, all=False):
        if not self.is_docker_available():
            return "Docker not available"
        
        try:
            cmd = ["docker", "ps"]
            if all:
                cmd.append("-a")
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            return result.stdout or "No containers"
        except Exception as e:
            return f"Error: {e}"
    
    def list_images(self):
        if not self.is_docker_available():
            return "Docker not available"
        
        try:
            result = subprocess.run(["docker", "images"], capture_output=True, text=True)
            return result.stdout or "No images"
        except Exception as e:
            return f"Error: {e}"
    
    def start_container(self, name):
        if not self.is_docker_available():
            return "Docker not available"
        
        try:
            result = subprocess.run(["docker", "start", name], capture_output=True, text=True)
            return f"Started {name}" if result.returncode == 0 else f"Error: {result.stderr}"
        except Exception as e:
            return f"Error: {e}"
    
    def stop_container(self, name):
        if not self.is_docker_available():
            return "Docker not available"
        
        try:
            result = subprocess.run(["docker", "stop", name], capture_output=True, text=True)
            return f"Stopped {name}" if result.returncode == 0 else f"Error: {result.stderr}"
        except Exception as e:
            return f"Error: {e}"
    
    def remove_container(self, name, force=False):
        if not self.is_docker_available():
            return "Docker not available"
        
        try:
            cmd = ["docker", "rm"]
            if force:
                cmd.append("-f")
            cmd.append(name)
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            return f"Removed {name}" if result.returncode == 0 else f"Error: {result.stderr}"
        except Exception as e:
            return f"Error: {e}"
    
    def pull_image(self, image):
        if not self.is_docker_available():
            return "Docker not available"
        
        try:
            result = subprocess.run(["docker", "pull", image], capture_output=True, text=True, timeout=300)
            return f"Pulled {image}" if result.returncode == 0 else f"Error: {result.stderr}"
        except subprocess.TimeoutExpired:
            return "Pull timed out"
        except Exception as e:
            return f"Error: {e}"