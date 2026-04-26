import threading
import time
import queue
from datetime import datetime

class Notification:
    def __init__(self, message, level="info", source="system"):
        self.message = message
        self.level = level
        self.source = source
        self.timestamp = datetime.now()
        self.read = False

class NotificationManager:
    def __init__(self, agent):
        self.agent = agent
        self.notifications = queue.Queue()
        self.history = []
        self.max_history = 500
        self.listeners = []
        self._worker = threading.Thread(target=self._process_notifications, daemon=True)
        self._worker.start()
        self.muted = set()
    
    def _process_notifications(self):
        while self.agent.can_run():
            try:
                notification = self.notifications.get(timeout=1)
                self._handle_notification(notification)
            except queue.Empty:
                continue
    
    def _handle_notification(self, notification):
        self.history.append(notification)
        if len(self.history) > self.max_history:
            self.history.pop(0)
        
        for listener in self.listeners:
            try:
                listener(notification)
            except:
                pass
    
    def notify(self, message, level="info", source="system"):
        if source in self.muted:
            return
        
        notification = Notification(message, level, source)
        self.notifications.put(notification)
        print(f"[{level.upper()}] {message}")
    
    def info(self, message, source="system"):
        self.notify(message, "info", source)
    
    def warning(self, message, source="system"):
        self.notify(message, "warning", source)
    
    def error(self, message, source="system"):
        self.notify(message, "error", source)
    
    def success(self, message, source="system"):
        self.notify(message, "success", source)
    
    def subscribe(self, listener):
        self.listeners.append(listener)
    
    def unsubscribe(self, listener):
        if listener in self.listeners:
            self.listeners.remove(listener)
    
    def get_unread(self, limit=50):
        unread = [n for n in self.history if not n.read]
        return unread[-limit:]
    
    def mark_read(self, index=None):
        if index is None:
            for n in self.history:
                n.read = True
        elif 0 <= index < len(self.history):
            self.history[index].read = True
    
    def mute(self, source):
        self.muted.add(source)
    
    def unmute(self, source):
        self.muted.discard(source)
    
    def get_history(self, limit=100):
        return self.history[-limit:]
    
    def clear_history(self):
        self.history.clear()
    
    def get_stats(self):
        unread = len([n for n in self.history if not n.read])
        by_level = {}
        for n in self.history:
            by_level[n.level] = by_level.get(n.level, 0) + 1
        return {
            "total": len(self.history),
            "unread": unread,
            "by_level": by_level,
            "muted": list(self.muted)
        }