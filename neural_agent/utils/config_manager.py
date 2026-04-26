import json
import os

class ConfigManager:
    def __init__(self, agent, config_file="config.json"):
        self.agent = agent
        self.config_file = config_file
        self.config = self._default_config()
        self.load()
    
    def _default_config(self):
        return {
            "agent": {
                "name": "NeuralAgent",
                "version": "1.0.0",
                "max_memory": 10000
            },
            "timeouts": {
                "think": 60,
                "fetch": 30,
                "crawl": 300,
                "search": 30,
                "task": 300,
                "chat": 10
            },
            "web": {
                "user_agent": "Mozilla/5.0 (NeuralAgent/1.0)",
                "max_depth": 3,
                "max_pages": 10,
                "timeout": 30
            },
            "memory": {
                "persist": True,
                "db_path": "./memory_db",
                "top_k": 5
            },
            "logging": {
                "level": "INFO",
                "file": "agent.log",
                "console": True
            },
            "security": {
                "allowed_file_extensions": [
                    ".txt", ".md", ".json", ".yaml", ".yml", ".csv", ".xml",
                    ".py", ".js", ".html", ".css", ".log", ".cfg", ".ini", ".toml", ".env", ".sh", ".bat", ".cmd"
                ],
                "workdir": "."
            }
        }
    
    def load(self):
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, "r") as f:
                    loaded = json.load(f)
                self._merge_config(loaded)
                print(f"[Config] Loaded from {self.config_file}")
            except Exception as e:
                print(f"[Config] Error loading config: {e}")
        else:
            print(f"[Config] No config file found, using defaults")
    
    def _merge_config(self, loaded):
        for section, values in loaded.items():
            if section in self.config:
                if isinstance(values, dict):
                    self.config[section].update(values)
                else:
                    self.config[section] = values
            else:
                self.config[section] = values
    
    def save(self):
        try:
            with open(self.config_file, "w") as f:
                json.dump(self.config, f, indent=2)
            print(f"[Config] Saved to {self.config_file}")
        except Exception as e:
            print(f"[Config] Error saving config: {e}")
    
    def get(self, key, default=None):
        keys = key.split(".")
        value = self.config
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value
    
    def set(self, key, value):
        keys = key.split(".")
        config = self.config
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        config[keys[-1]] = value
        print(f"[Config] Set {key} = {value}")
    
    def reset(self):
        self.config = self._default_config()
        print("[Config] Reset to defaults")
    
    def export(self):
        return json.dumps(self.config, indent=2)