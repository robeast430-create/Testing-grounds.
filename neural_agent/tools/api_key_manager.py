import os
import json
import hashlib

class APIKeyManager:
    def __init__(self, data_dir="./auth_data"):
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
        self.keys_file = os.path.join(data_dir, "api_keys.json")
        self.env_file = os.path.join(data_dir, ".env")
        self.keys = self._load_keys()
    
    def _load_keys(self):
        if os.path.exists(self.keys_file):
            with open(self.keys_file, "r") as f:
                return json.load(f)
        return {}
    
    def _save_keys(self):
        with open(self.keys_file, "w") as f:
            json.dump(self.keys, f, indent=2)
    
    def _hash_key(self, key):
        return hashlib.sha256(key.encode()).hexdigest()[:16]
    
    def add_key(self, service, key, name=None):
        if not name:
            name = f"{service}_key"
        
        key_hash = self._hash_key(key)
        
        self.keys[service] = {
            "name": name,
            "hash": key_hash,
            "added_at": str(hashlib.md5(str(os.urandom(32)).encode()).hexdigest()[:8]),
            "active": True
        }
        
        self._save_keys()
        self._update_env_file()
        
        return f"API key for {service} added (hashed: {key_hash})"
    
    def get_key(self, service):
        return self.keys.get(service, {}).get("hash")
    
    def has_key(self, service):
        return service in self.keys and self.keys[service].get("active", False)
    
    def remove_key(self, service):
        if service in self.keys:
            del self.keys[service]
            self._save_keys()
            self._update_env_file()
            return f"API key for {service} removed"
        return f"No API key for {service}"
    
    def list_services(self):
        return [{
            "service": service,
            "name": data.get("name"),
            "active": data.get("active", True),
            "added_at": data.get("added_at")
        } for service, data in self.keys.items()]
    
    def toggle_key(self, service, active=True):
        if service in self.keys:
            self.keys[service]["active"] = active
            self._save_keys()
            return f"API key for {service} {'enabled' if active else 'disabled'}"
        return f"No API key for {service}"
    
    def _update_env_file(self):
        with open(self.env_file, "w") as f:
            for service, data in self.keys.items():
                if data.get("active"):
                    f.write(f"{service.upper()}_API_KEY={data.get('hash', '')}\n")
    
    def export_keys_info(self):
        return json.dumps(self.list_services(), indent=2)
    
    def clear_all(self):
        self.keys = {}
        self._save_keys()
        if os.path.exists(self.env_file):
            os.remove(self.env_file)
        return "All API keys cleared"


class ExportImportManager:
    def __init__(self, agent):
        self.agent = agent
    
    def export_all(self, directory="./exports"):
        import shutil
        import zipfile
        from datetime import datetime
        
        os.makedirs(directory, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        export_file = os.path.join(directory, f"neural_agent_export_{timestamp}.zip")
        
        with zipfile.ZipFile(export_file, 'w', zipfile.ZIP_DEFLATED) as zf:
            if os.path.exists("./auth_data"):
                for f in os.listdir("./auth_data"):
                    if os.path.isfile(os.path.join("./auth_data", f)):
                        zf.write(os.path.join("./auth_data", f), f"auth_data/{f}")
            
            if os.path.exists("./memory_db"):
                for root, dirs, files in os.walk("./memory_db"):
                    for file in files:
                        filepath = os.path.join(root, file)
                        arcname = filepath.replace("./", "")
                        zf.write(filepath, arcname)
            
            if os.path.exists("./config.json"):
                zf.write("./config.json", "config.json")
        
        return export_file
    
    def import_all(self, zip_file):
        import zipfile
        import tempfile
        
        if not os.path.exists(zip_file):
            return f"File not found: {zip_file}"
        
        temp_dir = tempfile.mkdtemp()
        
        try:
            with zipfile.ZipFile(zip_file, 'r') as zf:
                zf.extractall(temp_dir)
            
            import shutil
            
            if os.path.exists(os.path.join(temp_dir, "auth_data")):
                shutil.copytree(
                    os.path.join(temp_dir, "auth_data"),
                    "./auth_data",
                    dirs_exist_ok=True
                )
            
            if os.path.exists(os.path.join(temp_dir, "memory_db")):
                shutil.copytree(
                    os.path.join(temp_dir, "memory_db"),
                    "./memory_db",
                    dirs_exist_ok=True
                )
            
            if os.path.exists(os.path.join(temp_dir, "config.json")):
                shutil.copy2(
                    os.path.join(temp_dir, "config.json"),
                    "./config.json"
                )
            
            shutil.rmtree(temp_dir)
            return "Import complete. Restart the agent to apply changes."
        except Exception as e:
            shutil.rmtree(temp_dir, ignore_errors=True)
            return f"Import failed: {e}"
    
    def export_memories(self, filepath="memories_export.json"):
        memories = self.agent.memory.metadata["memories"]
        
        export_data = {
            "exported_at": str(__import__('datetime').datetime.now()),
            "count": len(memories),
            "memories": memories
        }
        
        with open(filepath, "w") as f:
            json.dump(export_data, f, indent=2)
        
        return f"Exported {len(memories)} memories to {filepath}"
    
    def import_memories(self, filepath):
        if not os.path.exists(filepath):
            return f"File not found: {filepath}"
        
        with open(filepath, "r") as f:
            data = json.load(f)
        
        memories = data.get("memories", [])
        imported = 0
        
        for mem in memories:
            self.agent.memory.add(
                mem.get("content", ""),
                mem.get("type", "imported")
            )
            imported += 1
        
        return f"Imported {imported} memories from {filepath}"