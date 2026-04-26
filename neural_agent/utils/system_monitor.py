import psutil
import os
import time
import threading
from datetime import datetime

class SystemMonitor:
    def __init__(self, agent):
        self.agent = agent
        self.start_time = time.time()
        self.start_datetime = datetime.now()
        self._stats = {
            "queries": 0,
            "tasks_completed": 0,
            "tasks_failed": 0,
            "web_requests": 0,
            "memories_added": 0,
            "files_read": 0,
            "files_written": 0
        }
        self._lock = threading.Lock()
    
    def increment(self, stat, value=1):
        with self._lock:
            if stat in self._stats:
                self._stats[stat] += value
    
    def get_stats(self):
        with self._lock:
            uptime = time.time() - self.start_time
            stats = dict(self._stats)
            stats["uptime_seconds"] = uptime
            stats["uptime_str"] = self._format_uptime(uptime)
            return stats
    
    def _format_uptime(self, seconds):
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        return f"{hours}h {minutes}m {secs}s"
    
    def get_system_info(self):
        return {
            "cpu_percent": psutil.cpu_percent(interval=0.1),
            "cpu_count": psutil.cpu_count(),
            "memory_percent": psutil.virtual_memory().percent,
            "memory_used_mb": psutil.virtual_memory().used // (1024 * 1024),
            "memory_total_mb": psutil.virtual_memory().total // (1024 * 1024),
            "disk_percent": psutil.disk_usage('/').percent,
            "pid": os.getpid()
        }
    
    def full_report(self):
        stats = self.get_stats()
        sys = self.get_system_info()
        
        report = f"""
=== System Report ===
Uptime: {stats['uptime_str']}
PID: {sys['pid']}

--- Performance ---
CPU: {sys['cpu_percent']}% ({sys['cpu_count']} cores)
Memory: {sys['memory_percent']}% ({sys['memory_used_mb']}/{sys['memory_total_mb']} MB)
Disk: {sys['disk_percent']}%

--- Agent Stats ---
Queries: {stats['queries']}
Tasks Completed: {stats['tasks_completed']}
Tasks Failed: {stats['tasks_failed']}
Web Requests: {stats['web_requests']}
Memories Added: {stats['memories_added']}
Files Read: {stats['files_read']}
Files Written: {stats['files_written']}
Memory Count: {self.agent.memory.count()}
==================
"""
        return report
    
    def reset_stats(self):
        with self._lock:
            for key in self._stats:
                self._stats[key] = 0
        print("[SystemMonitor] Stats reset")