import os
import json
from datetime import datetime

class CommandHistory:
    def __init__(self, data_dir="./auth_data"):
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
        self.history_file = os.path.join(data_dir, "command_history.json")
        self.history = self._load()
        self.max_history = 1000
    
    def _load(self):
        if os.path.exists(self.history_file):
            with open(self.history_file, "r") as f:
                return json.load(f)
        return {}
    
    def _save(self):
        with open(self.history_file, "w") as f:
            json.dump(self.history, f, indent=2)
    
    def add(self, username, command, result_preview=""):
        if username not in self.history:
            self.history[username] = []
        
        entry = {
            "timestamp": datetime.now().isoformat(),
            "command": command,
            "result_preview": result_preview[:200] if result_preview else ""
        }
        
        self.history[username].insert(0, entry)
        
        if len(self.history[username]) > self.max_history:
            self.history[username] = self.history[username][:self.max_history]
        
        self._save()
    
    def get(self, username, limit=50):
        if username in self.history:
            return self.history[username][:limit]
        return []
    
    def search(self, username, query):
        if username not in self.history:
            return []
        query_lower = query.lower()
        return [e for e in self.history[username] if query_lower in e["command"].lower()]
    
    def clear(self, username):
        if username in self.history:
            self.history[username] = []
            self._save()
        return True
    
    def get_recent_commands(self, username, count=10):
        return [e["command"] for e in self.get(username, count)]