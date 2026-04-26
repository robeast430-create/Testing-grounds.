import json
import os
import time
import threading
from datetime import datetime

class Alert:
    def __init__(self, name, condition, threshold, message):
        self.name = name
        self.condition = condition
        self.threshold = threshold
        self.message = message
        self.triggered = False
        self.triggered_at = None
    
    def check(self, value):
        triggered = False
        
        if self.condition == "gt" and value > self.threshold:
            triggered = True
        elif self.condition == "lt" and value < self.threshold:
            triggered = True
        elif self.condition == "eq" and value == self.threshold:
            triggered = True
        elif self.condition == "gte" and value >= self.threshold:
            triggered = True
        elif self.condition == "lte" and value <= self.threshold:
            triggered = True
        
        if triggered and not self.triggered:
            self.triggered = True
            self.triggered_at = datetime.now().isoformat()
            return True
        
        if not triggered:
            self.triggered = False
        
        return False


class AlertManager:
    def __init__(self, agent):
        self.agent = agent
        self.alerts = []
        self.history = []
        self.running = False
        self.monitor_thread = None
    
    def add_alert(self, name, condition, threshold, message):
        alert = Alert(name, condition, threshold, message)
        self.alerts.append(alert)
        return alert
    
    def remove_alert(self, name):
        self.alerts = [a for a in self.alerts if a.name != name]
        return "Alert removed" if name not in [a.name for a in self.alerts] else "Alert not found"
    
    def check_cpu(self, threshold=80):
        import psutil
        return self._check_metric("cpu", psutil.cpu_percent(), threshold)
    
    def check_memory(self, threshold=80):
        import psutil
        return self._check_metric("memory", psutil.virtual_memory().percent, threshold)
    
    def check_disk(self, threshold=90, path="/"):
        import psutil
        return self._check_metric("disk", psutil.disk_usage(path).percent, threshold)
    
    def _check_metric(self, name, value, threshold):
        for alert in self.alerts:
            if name in alert.name.lower():
                if alert.check(value):
                    self.history.append({
                        "alert": alert.name,
                        "value": value,
                        "threshold": alert.threshold,
                        "at": datetime.now().isoformat()
                    })
                    self.agent.notifications.warning(alert.message, "alert")
                    return f"ALERT: {alert.message}"
        return None
    
    def list_alerts(self):
        return [{
            "name": a.name,
            "condition": f"{a.condition} {a.threshold}",
            "message": a.message,
            "triggered": a.triggered
        } for a in self.alerts]
    
    def get_history(self, limit=50):
        return self.history[-limit:]
    
    def clear_history(self):
        self.history = []
        return "Alert history cleared"


class MetricsCollector:
    def __init__(self):
        self.metrics = {}
        self.history = []
    
    def collect(self, name, value):
        self.metrics[name] = {
            "value": value,
            "timestamp": datetime.now().isoformat()
        }
        self.history.append({
            "name": name,
            "value": value,
            "timestamp": datetime.now().isoformat()
        })
        
        if len(self.history) > 10000:
            self.history = self.history[-5000:]
    
    def get(self, name):
        return self.metrics.get(name)
    
    def get_history(self, name, limit=100):
        return [m for m in self.history if m["name"] == name][-limit:]
    
    def get_all(self):
        return self.metrics
    
    def clear(self):
        self.metrics = {}
        self.history = []


class UptimeMonitor:
    def __init__(self, urls=None, interval=60):
        self.urls = urls or []
        self.interval = interval
        self.results = []
        self.running = False
        self.monitor_thread = None
    
    def add_url(self, url):
        self.urls.append(url)
        return f"Added {url} to monitoring"
    
    def remove_url(self, url):
        if url in self.urls:
            self.urls.remove(url)
            return f"Removed {url}"
        return "URL not in monitoring list"
    
    def check(self, url):
        import requests
        try:
            start = time.time()
            response = requests.get(url, timeout=10)
            latency = (time.time() - start) * 1000
            
            self.results.append({
                "url": url,
                "status": response.status_code,
                "latency_ms": round(latency, 2),
                "timestamp": datetime.now().isoformat(),
                "up": response.status_code < 400
            })
            
            return {
                "url": url,
                "status": response.status_code,
                "latency_ms": round(latency, 2),
                "up": response.status_code < 400
            }
        except Exception as e:
            self.results.append({
                "url": url,
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
                "up": False
            })
            return {"url": url, "error": str(e), "up": False}
    
    def check_all(self):
        return [self.check(url) for url in self.urls]
    
    def start_monitoring(self):
        self.running = True
        
        def monitor_loop():
            while self.running:
                self.check_all()
                time.sleep(self.interval)
        
        self.monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
        self.monitor_thread.start()
        return "Monitoring started"
    
    def stop_monitoring(self):
        self.running = False
        return "Monitoring stopped"
    
    def get_stats(self):
        if not self.results:
            return "No results yet"
        
        total = len(self.results)
        uptime_count = sum(1 for r in self.results if r.get("up", False))
        
        latencies = [r.get("latency_ms") for r in self.results if "latency_ms" in r]
        avg_latency = sum(latencies) / len(latencies) if latencies else 0
        
        return {
            "total_checks": total,
            "uptime_percent": round((uptime_count / total) * 100, 2),
            "avg_latency_ms": round(avg_latency, 2),
            "last_check": self.results[-1] if self.results else None
        }


class CronScheduler:
    def __init__(self, agent):
        self.agent = agent
        self.jobs = []
        self.running = False
        self.worker = None
    
    def add_job(self, name, schedule, func, *args, **kwargs):
        self.jobs.append({
            "name": name,
            "schedule": schedule,
            "func": func,
            "args": args,
            "kwargs": kwargs,
            "last_run": None,
            "enabled": True
        })
        return f"Job '{name}' added"
    
    def remove_job(self, name):
        self.jobs = [j for j in self.jobs if j["name"] != name]
        return f"Job '{name}' removed" if name not in [j["name"] for j in self.jobs] else "Job not found"
    
    def enable_job(self, name):
        for job in self.jobs:
            if job["name"] == name:
                job["enabled"] = True
                return f"Job '{name}' enabled"
        return "Job not found"
    
    def disable_job(self, name):
        for job in self.jobs:
            if job["name"] == name:
                job["enabled"] = False
                return f"Job '{name}' disabled"
        return "Job not found"
    
    def list_jobs(self):
        return [{
            "name": j["name"],
            "schedule": j["schedule"],
            "enabled": j["enabled"],
            "last_run": j["last_run"]
        } for j in self.jobs]
    
    def start(self):
        self.running = True
        
        def worker():
            while self.running:
                now = datetime.now()
                for job in self.jobs:
                    if not job["enabled"]:
                        continue
                    
                    should_run = self._should_run(now, job["schedule"])
                    
                    if should_run:
                        try:
                            job["func"](*job["args"], **job["kwargs"])
                            job["last_run"] = now.isoformat()
                        except Exception as e:
                            print(f"Job error: {e}")
                
                time.sleep(60)
        
        self.worker = threading.Thread(target=worker, daemon=True)
        self.worker.start()
        return "Cron scheduler started"
    
    def stop(self):
        self.running = False
        return "Cron scheduler stopped"
    
    def _should_run(self, now, schedule):
        if schedule == "@hourly":
            return now.minute == 0
        elif schedule == "@daily":
            return now.hour == 0 and now.minute == 0
        elif schedule == "@weekly":
            return now.weekday() == 0 and now.hour == 0 and now.minute == 0
        elif schedule.startswith("*"):
            parts = schedule.split(":")
            if len(parts) == 2:
                minute = int(parts[0].replace("*", "0"))
                hour = int(parts[1].replace("*", "0"))
                return now.minute == minute and now.hour == hour
        return False


class HealthCheck:
    def __init__(self, agent):
        self.agent = agent
        self.checks = {}
    
    def register_check(self, name, check_func):
        self.checks[name] = check_func
        return f"Check '{name}' registered"
    
    def run_check(self, name):
        if name not in self.checks:
            return "Check not found"
        
        try:
            result = self.checks[name]()
            return {"name": name, "status": "pass", "result": result}
        except Exception as e:
            return {"name": name, "status": "fail", "error": str(e)}
    
    def run_all(self):
        results = []
        for name in self.checks:
            results.append(self.run_check(name))
        return results
    
    def status(self):
        results = self.run_all()
        passed = sum(1 for r in results if r["status"] == "pass")
        failed = sum(1 for r in results if r["status"] == "fail")
        
        return {
            "total": len(results),
            "passed": passed,
            "failed": failed,
            "healthy": failed == 0,
            "results": results
        }