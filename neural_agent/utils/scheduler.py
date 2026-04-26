import threading
import time
import queue
from datetime import datetime, timedelta
import json
import os

class Scheduler:
    def __init__(self, agent):
        self.agent = agent
        self.tasks = []
        self.running = True
        self.task_id = 0
        self._lock = threading.Lock()
        self._worker = threading.Thread(target=self._run_loop, daemon=True)
        self._worker.start()
    
    def _run_loop(self):
        while self.running:
            self._check_scheduled()
            time.sleep(1)
    
    def _check_scheduled(self):
        with self._lock:
            now = datetime.now()
            due_tasks = [t for t in self.tasks if self._is_due(t, now)]
            
            for task in due_tasks:
                self._execute_task(task)
                if task.get("repeat"):
                    self._reschedule(task)
                else:
                    self.tasks.remove(task)
    
    def _is_due(self, task, now):
        if task["next_run"] is None:
            return False
        return now >= task["next_run"]
    
    def _execute_task(self, task):
        print(f"[Scheduler] Running scheduled task: {task['description']}")
        try:
            result = self.agent.tasks.execute(task["action"])
            task["last_result"] = str(result)
            task["last_run"] = datetime.now().isoformat()
            task["status"] = "success"
        except Exception as e:
            task["last_result"] = str(e)
            task["status"] = "failed"
    
    def _reschedule(self, task):
        repeat = task["repeat"]
        if repeat == "hourly":
            task["next_run"] = task["last_run"] + timedelta(hours=1)
        elif repeat == "daily":
            task["next_run"] = task["last_run"] + timedelta(days=1)
        elif repeat == "weekly":
            task["next_run"] = task["last_run"] + timedelta(weeks=1)
    
    def schedule(self, action, when=None, repeat=None, description=None):
        self.task_id += 1
        task = {
            "id": self.task_id,
            "action": action,
            "description": description or action,
            "when": when,
            "repeat": repeat,
            "next_run": self._parse_time(when) if when else datetime.now(),
            "last_run": None,
            "last_result": None,
            "status": "pending"
        }
        with self._lock:
            self.tasks.append(task)
        print(f"[Scheduler] Scheduled task {self.task_id}: {action} ({repeat or 'once'})")
        return self.task_id
    
    def _parse_time(self, when):
        now = datetime.now()
        if when == "now":
            return now
        elif when == "1min":
            return now + timedelta(minutes=1)
        elif when == "5min":
            return now + timedelta(minutes=5)
        elif when == "1hour":
            return now + timedelta(hours=1)
        elif when == "1day":
            return now + timedelta(days=1)
        try:
            return datetime.strptime(when, "%Y-%m-%d %H:%M:%S")
        except:
            return now
    
    def list(self):
        with self._lock:
            return [{
                "id": t["id"],
                "description": t["description"],
                "next_run": t["next_run"].isoformat() if t["next_run"] else None,
                "repeat": t["repeat"],
                "status": t["status"]
            } for t in self.tasks]
    
    def cancel(self, task_id):
        with self._lock:
            for task in self.tasks:
                if task["id"] == task_id:
                    self.tasks.remove(task)
                    print(f"[Scheduler] Cancelled task {task_id}")
                    return True
        return False
    
    def stop(self):
        self.running = False