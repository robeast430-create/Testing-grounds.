import os
import shutil
import json
import hashlib
from datetime import datetime

class BackupManager:
    def __init__(self, agent):
        self.agent = agent
        self.backup_dir = "./backups"
        os.makedirs(self.backup_dir, exist_ok=True)
    
    def create_backup(self, name=None):
        if name is None:
            name = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        backup_path = os.path.join(self.backup_dir, name)
        os.makedirs(backup_path, exist_ok=True)
        
        items = [
            ("auth_data", "./auth_data"),
            ("memory_db", "./memory_db"),
            ("config.json", "./config.json"),
        ]
        
        backed_up = []
        
        for dest_name, src_path in items:
            if os.path.exists(src_path):
                dest_path = os.path.join(backup_path, dest_name)
                if os.path.isdir(src_path):
                    shutil.copytree(src_path, dest_path, dirs_exist_ok=True)
                else:
                    shutil.copy2(src_path, dest_path)
                backed_up.append(dest_name)
        
        manifest = {
            "name": name,
            "created_at": datetime.now().isoformat(),
            "items": backed_up,
            "checksum": self._calculate_checksum(backup_path)
        }
        
        with open(os.path.join(backup_path, "manifest.json"), "w") as f:
            json.dump(manifest, f, indent=2)
        
        return backup_path
    
    def _calculate_checksum(self, path):
        hash_md5 = hashlib.md5()
        for root, dirs, files in os.walk(path):
            for file in files:
                if file == "manifest.json":
                    continue
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, "rb") as f:
                        for chunk in iter(lambda: f.read(4096), b""):
                            hash_md5.update(chunk)
                except:
                    pass
        return hash_md5.hexdigest()
    
    def list_backups(self):
        if not os.path.exists(self.backup_dir):
            return "No backups found"
        
        backups = []
        for name in os.listdir(self.backup_dir):
            backup_path = os.path.join(self.backup_dir, name)
            if os.path.isdir(backup_path):
                manifest_path = os.path.join(backup_path, "manifest.json")
                created = datetime.now()
                if os.path.exists(manifest_path):
                    with open(manifest_path, "r") as f:
                        manifest = json.load(f)
                        created = manifest.get("created_at", "")
                
                backups.append({
                    "name": name,
                    "path": backup_path,
                    "created": created
                })
        
        if backups:
            output = "Available backups:\n"
            for b in sorted(backups, key=lambda x: x["created"], reverse=True):
                output += f"  {b['name']} - {b['created'][:19]}\n"
            return output.strip()
        return "No backups found"
    
    def restore(self, name):
        backup_path = os.path.join(self.backup_dir, name)
        
        if not os.path.exists(backup_path):
            return f"Backup not found: {name}"
        
        manifest_path = os.path.join(backup_path, "manifest.json")
        if os.path.exists(manifest_path):
            with open(manifest_path, "r") as f:
                manifest = json.load(f)
            
            checksum = self._calculate_checksum(backup_path)
            if checksum != manifest.get("checksum"):
                return "Backup checksum mismatch. May be corrupted."
        
        for item in os.listdir(backup_path):
            if item == "manifest.json":
                continue
            
            src = os.path.join(backup_path, item)
            dest = os.path.join(".", item)
            
            if item == "config.json":
                shutil.copy2(src, dest)
            else:
                if os.path.exists(dest):
                    if os.path.isdir(dest):
                        shutil.rmtree(dest)
                    else:
                        os.remove(dest)
                shutil.copytree(src, dest)
        
        return f"Restored from backup: {name}"
    
    def delete_backup(self, name):
        backup_path = os.path.join(self.backup_dir, name)
        
        if not os.path.exists(backup_path):
            return f"Backup not found: {name}"
        
        shutil.rmtree(backup_path)
        return f"Deleted backup: {name}"
    
    def clean_old_backups(self, keep=5):
        if not os.path.exists(self.backup_dir):
            return "No backups to clean"
        
        backups = []
        for name in os.listdir(self.backup_dir):
            backup_path = os.path.join(self.backup_dir, name)
            if os.path.isdir(backup_path):
                created = os.path.getmtime(backup_path)
                backups.append((created, name))
        
        backups.sort()
        
        deleted = 0
        while len(backups) > keep:
            created, name = backups.pop(0)
            backup_path = os.path.join(self.backup_dir, name)
            shutil.rmtree(backup_path)
            deleted += 1
        
        return f"Deleted {deleted} old backups"


class SystemUtils:
    def __init__(self, agent):
        self.agent = agent
    
    def uptime(self):
        import uptime
        try:
            return f"System uptime: {uptime.uptime()}"
        except:
            return "Uptime not available"
    
    def hostname(self):
        import socket
        return f"Hostname: {socket.gethostname()}"
    
    def ip_address(self):
        import socket
        hostname = socket.gethostname()
        try:
            ip = socket.gethostbyname(hostname)
            return f"IP Address: {ip}"
        except:
            return "IP Address: unknown"
    
    def disk_usage(self, path="/"):
        import shutil
        usage = shutil.disk_usage(path)
        return (f"Disk usage ({path}):\n"
                f"  Total: {usage.total // (1024**3)} GB\n"
                f"  Used: {usage.used // (1024**3)} GB\n"
                f"  Free: {usage.free // (1024**3)} GB")
    
    def network_status(self):
        import socket
        try:
            socket.create_connection(("8.8.8.8", 53), timeout=3)
            return "Network: Connected"
        except OSError:
            return "Network: Disconnected"
    
    def processes(self, limit=10):
        import psutil
        procs = []
        for proc in psutil.process_iter(["pid", "name", "cpu_percent", "memory_percent"]):
            try:
                procs.append(proc.info)
            except:
                pass
        
        procs.sort(key=lambda x: x.get("cpu_percent", 0), reverse=True)
        
        output = "Top processes:\n"
        for p in procs[:limit]:
            output += f"  [{p['pid']}] {p['name']} - CPU: {p['cpu_percent']:.1f}%, MEM: {p['memory_percent']:.1f}%\n"
        return output.strip()
    
    def battery(self):
        import psutil
        try:
            battery = psutil.sensors_battery()
            if battery:
                plugged = "Plugged in" if battery.power_plugged else "On battery"
                return (f"Battery: {battery.percent}% ({plugged})\n"
                        f"Time remaining: {battery.secsleft // 60} minutes")
            return "No battery"
        except:
            return "Battery info not available"
    
    def temperature(self):
        import psutil
        temps = []
        try:
            for name, temp in psutil.sensors_temperatures().items():
                temps.append(f"{name}: {temp.current}°C")
            
            if temps:
                return "Temperatures:\n  " + "\n  ".join(temps)
            return "No temperature sensors found"
        except:
            return "Temperature info not available"