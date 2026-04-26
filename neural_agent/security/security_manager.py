import time
import threading
from collections import defaultdict

class SecurityManager:
    def __init__(self):
        self.rate_limits = defaultdict(lambda: {"count": 0, "reset_at": time.time() + 60})
        self.rate_limit_window = 60
        self.rate_limit_max = 100
        self.lock = threading.Lock()
        self.blocked_ips = {}
        self.blocked_users = {}
        self.max_failed_attempts = 5
        self.block_duration = 300
    
    def check_rate_limit(self, key):
        now = time.time()
        
        with self.lock:
            if key in self.blocked_users or key in self.blocked_ips:
                return False, "Rate limited or blocked"
            
            record = self.rate_limits[key]
            
            if now > record["reset_at"]:
                record["count"] = 0
                record["reset_at"] = now + self.rate_limit_window
            
            record["count"] += 1
            
            if record["count"] > self.rate_limit_max:
                return False, f"Rate limit exceeded ({record['count']}/{self.rate_limit_max})"
            
            return True, "OK"
    
    def record_failed_attempt(self, key):
        with self.lock:
            if key not in self.blocked_users:
                self.blocked_users[key] = {"attempts": 0, "blocked_until": None}
            
            self.blocked_users[key]["attempts"] += 1
            
            if self.blocked_users[key]["attempts"] >= self.max_failed_attempts:
                self.blocked_users[key]["blocked_until"] = time.time() + self.block_duration
    
    def is_blocked(self, key):
        now = time.time()
        with self.lock:
            if key in self.blocked_users:
                blocked = self.blocked_users[key]
                if blocked["blocked_until"] and now < blocked["blocked_until"]:
                    return True
                elif now >= blocked["blocked_until"]:
                    del self.blocked_users[key]
            return False
    
    def unblock(self, key):
        with self.lock:
            if key in self.blocked_users:
                del self.blocked_users[key]
            if key in self.blocked_ips:
                del self.blocked_ips[key]
        return True
    
    def set_rate_limit(self, max_requests, window_seconds):
        with self.lock:
            self.rate_limit_max = max_requests
            self.rate_limit_window = window_seconds
    
    def get_status(self):
        with self.lock:
            return {
                "rate_limit_max": self.rate_limit_max,
                "rate_limit_window": self.rate_limit_window,
                "blocked_users": len(self.blocked_users),
                "active_keys": len(self.rate_limits)
            }