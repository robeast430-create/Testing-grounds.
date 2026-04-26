import threading
import time
from functools import wraps

def timeout(seconds):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = [None]
            exception = [None]
            
            def target():
                try:
                    result[0] = func(*args, **kwargs)
                except Exception as e:
                    exception[0] = e
            
            thread = threading.Thread(target=target)
            thread.daemon = True
            thread.start()
            thread.join(timeout=seconds)
            
            if thread.is_alive():
                raise TimeoutError(f"{func.__name__} exceeded {seconds}s timeout")
            
            if exception[0]:
                raise exception[0]
            
            return result[0]
        return wrapper
    return decorator

class TimeoutManager:
    def __init__(self):
        self.timeouts = {
            "think": 60,
            "fetch": 30,
            "crawl": 300,
            "search": 30,
            "task": 300,
            "chat": 10
        }
        self._lock = threading.Lock()
    
    def set(self, operation, seconds):
        with self._lock:
            self.timeouts[operation] = seconds
    
    def get(self, operation):
        with self._lock:
            return self.timeouts.get(operation, 60)
    
    def run_with_timeout(self, operation, func, *args, **kwargs):
        timeout_sec = self.get(operation)
        result = [None]
        error = [None]
        
        def target():
            try:
                result[0] = func(*args, **kwargs)
            except Exception as e:
                error[0] = e
        
        thread = threading.Thread(target=target)
        thread.daemon = True
        thread.start()
        thread.join(timeout=timeout_sec)
        
        if thread.is_alive():
            raise TimeoutError(f"{operation} exceeded {timeout_sec}s timeout")
        
        if error[0]:
            raise error[0]
        
        return result[0]

    def set_all(self, defaults):
        for op, secs in defaults.items():
            self.set(op, secs)
    
    def reset(self):
        with self._lock:
            self.timeouts = {
                "think": 60,
                "fetch": 30,
                "crawl": 300,
                "search": 30,
                "task": 300,
                "chat": 10
            }
    
    def list_timeouts(self):
        return dict(self.timeouts)