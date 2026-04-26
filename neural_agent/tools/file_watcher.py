import os
import threading
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class FileWatcherHandler(FileSystemEventHandler):
    def __init__(self, agent, callbacks):
        self.agent = agent
        self.callbacks = callbacks or {}
    
    def on_created(self, event):
        if not event.is_directory:
            self._notify("created", event.src_path)
    
    def on_modified(self, event):
        if not event.is_directory:
            self._notify("modified", event.src_path)
    
    def on_deleted(self, event):
        if not event.is_directory:
            self._notify("deleted", event.src_path)
    
    def on_moved(self, event):
        if not event.is_directory:
            self._notify("moved", f"{event.src_path} -> {event.dest_path}")
    
    def _notify(self, event_type, filepath):
        callback = self.callbacks.get(event_type)
        if callback:
            try:
                callback(filepath)
            except Exception as e:
                print(f"[FileWatcher] Callback error: {e}")
        else:
            print(f"[FileWatcher] {event_type}: {filepath}")

class FileWatcher:
    def __init__(self, agent):
        self.agent = agent
        self.observer = Observer()
        self.watched_paths = {}
        self.callbacks = {}
    
    def watch(self, path, recursive=True, callbacks=None):
        if not os.path.exists(path):
            return f"Path does not exist: {path}"
        
        if path in self.watched_paths:
            return f"Already watching: {path}"
        
        handler = FileWatcherHandler(self.agent, callbacks or {})
        
        self.observer.schedule(handler, path, recursive=recursive)
        self.observer.start()
        
        self.watched_paths[path] = {"recursive": recursive, "callbacks": callbacks or {}}
        
        return f"Watching: {path} (recursive: {recursive})"
    
    def unwatch(self, path):
        if path in self.watched_paths:
            del self.watched_paths[path]
            self.observer = Observer()
            for p, info in self.watched_paths.items():
                handler = FileWatcherHandler(self.agent, info["callbacks"])
                self.observer.schedule(handler, p, recursive=info["recursive"])
            self.observer.start()
            return f"Stopped watching: {path}"
        return f"Not watching: {path}"
    
    def list_watched(self):
        return [{
            "path": path,
            "recursive": info["recursive"]
        } for path, info in self.watched_paths.items()]
    
    def stop(self):
        self.observer.stop()
        self.observer.join()
    
    def watch_file_changes(self, filepath, on_change_callback):
        if not os.path.exists(filepath):
            return f"File not found: {filepath}"
        
        last_modified = os.path.getmtime(filepath)
        
        def check_changes():
            while os.path.exists(filepath):
                try:
                    current_modified = os.path.getmtime(filepath)
                    if current_modified != last_modified:
                        last_modified = current_modified
                        on_change_callback(filepath)
                except:
                    break
                time.sleep(1)
        
        thread = threading.Thread(target=check_changes, daemon=True)
        thread.start()
        
        return f"Watching file changes: {filepath}"