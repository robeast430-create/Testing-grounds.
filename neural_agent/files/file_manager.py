import os
import json
import csv
import shutil
import mimetypes

class FileManager:
    def __init__(self, agent):
        self.agent = agent
        self.allowed_extensions = {
            ".txt", ".md", ".json", ".yaml", ".yml", ".csv", ".xml",
            ".py", ".js", ".html", ".css", ".json", ".log", ".cfg",
            ".ini", ".toml", ".env", ".sh", ".bat", ".cmd"
        }
        self.workdir = os.getcwd()

    def set_workdir(self, path):
        if os.path.isdir(path):
            self.workdir = path
            return f"Working directory set to: {path}"
        return f"Directory not found: {path}"

    def read(self, filepath):
        full_path = self._resolve_path(filepath)
        
        if not os.path.exists(full_path):
            return f"File not found: {filepath}"
        
        ext = os.path.splitext(full_path)[1].lower()
        if ext not in self.allowed_extensions:
            return f"File type not allowed: {ext}"
        
        try:
            with open(full_path, "r", encoding="utf-8") as f:
                content = f.read()
            return content
        except Exception as e:
            return f"Error reading {filepath}: {e}"

    def write(self, filepath, content):
        full_path = self._resolve_path(filepath)
        
        ext = os.path.splitext(full_path)[1].lower()
        if ext not in self.allowed_extensions:
            return f"File type not allowed: {ext}"
        
        try:
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            with open(full_path, "w", encoding="utf-8") as f:
                f.write(content)
            return f"Written to: {filepath}"
        except Exception as e:
            return f"Error writing {filepath}: {e}"

    def append(self, filepath, content):
        full_path = self._resolve_path(filepath)
        
        try:
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            with open(full_path, "a", encoding="utf-8") as f:
                f.write(content)
            return f"Appended to: {filepath}"
        except Exception as e:
            return f"Error appending to {filepath}: {e}"

    def list(self, directory="."):
        full_path = self._resolve_path(directory)
        
        if not os.path.isdir(full_path):
            return f"Directory not found: {directory}"
        
        try:
            items = []
            for item in os.listdir(full_path):
                item_path = os.path.join(full_path, item)
                if os.path.isdir(item_path):
                    items.append(f"{item}/")
                else:
                    items.append(item)
            return "\n".join(items) or "Empty directory"
        except Exception as e:
            return f"Error listing {directory}: {e}"

    def info(self, filepath):
        full_path = self._resolve_path(filepath)
        
        if not os.path.exists(full_path):
            return f"File not found: {filepath}"
        
        stat = os.stat(full_path)
        return f"Path: {full_path}\nSize: {stat.st_size} bytes\nModified: {stat.st_mtime}"

    def delete(self, filepath):
        full_path = self._resolve_path(filepath)
        
        if not os.path.exists(full_path):
            return f"File not found: {filepath}"
        
        try:
            if os.path.isdir(full_path):
                shutil.rmtree(full_path)
            else:
                os.remove(full_path)
            return f"Deleted: {filepath}"
        except Exception as e:
            return f"Error deleting {filepath}: {e}"

    def copy(self, source, dest):
        src = self._resolve_path(source)
        dst = self._resolve_path(dest)
        
        if not os.path.exists(src):
            return f"Source not found: {source}"
        
        try:
            if os.path.isdir(src):
                shutil.copytree(src, dst)
            else:
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                shutil.copy2(src, dst)
            return f"Copied: {source} -> {dest}"
        except Exception as e:
            return f"Error copying: {e}"

    def move(self, source, dest):
        src = self._resolve_path(source)
        dst = self._resolve_path(dest)
        
        if not os.path.exists(src):
            return f"Source not found: {source}"
        
        try:
            shutil.move(src, dst)
            return f"Moved: {source} -> {dest}"
        except Exception as e:
            return f"Error moving: {e}"

    def exists(self, filepath):
        full_path = self._resolve_path(filepath)
        return os.path.exists(full_path)

    def _resolve_path(self, filepath):
        if os.path.isabs(filepath):
            return filepath
        return os.path.join(self.workdir, filepath)

    def read_json(self, filepath):
        content = self.read(filepath)
        if content.startswith("Error"):
            return content
        try:
            return json.dumps(json.loads(content), indent=2)
        except Exception as e:
            return f"Error parsing JSON: {e}"

    def read_csv(self, filepath):
        content = self.read(filepath)
        if content.startswith("Error"):
            return content
        try:
            import io
            reader = csv.DictReader(io.StringIO(content))
            return "\n".join(str(row) for row in reader)
        except Exception as e:
            return f"Error parsing CSV: {e}"

    def read_lines(self, filepath, start=1, end=None):
        full_path = self._resolve_path(filepath)
        
        if not os.path.exists(full_path):
            return f"File not found: {filepath}"
        
        try:
            with open(full_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
            
            if end is None:
                end = len(lines)
            
            return "".join(lines[start-1:end])
        except Exception as e:
            return f"Error reading {filepath}: {e}"