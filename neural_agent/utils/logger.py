import logging
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler

class AgentLogger:
    def __init__(self, name="NeuralAgent", log_file="agent.log", level="INFO"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, level.upper()))
        self.logger.handlers = []
        
        formatter = logging.Formatter(
            "%(asctime)s [%(levelname)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        
        console = logging.StreamHandler()
        console.setFormatter(formatter)
        self.logger.addHandler(console)
        
        if log_file:
            try:
                os.makedirs(os.path.dirname(log_file) if os.path.dirname(log_file) else ".", exist_ok=True)
                file_handler = RotatingFileHandler(
                    log_file, maxBytes=10 * 1024 * 1024, backupCount=5
                )
                file_handler.setFormatter(formatter)
                self.logger.addHandler(file_handler)
            except Exception as e:
                self.logger.warning(f"Could not create log file: {e}")
    
    def debug(self, msg):
        self.logger.debug(msg)
    
    def info(self, msg):
        self.logger.info(msg)
    
    def warning(self, msg):
        self.logger.warning(msg)
    
    def error(self, msg):
        self.logger.error(msg)
    
    def critical(self, msg):
        self.logger.critical(msg)
    
    def log_action(self, action, details=""):
        self.info(f"[ACTION] {action} {details}")
    
    def log_query(self, query):
        self.debug(f"[QUERY] {query}")
    
    def log_task(self, task_id, status, details=""):
        self.info(f"[TASK:{task_id}] {status} {details}")
    
    def log_error(self, source, error):
        self.error(f"[ERROR:{source}] {error}")
    
    def set_level(self, level):
        self.logger.setLevel(getattr(logging, level.upper()))