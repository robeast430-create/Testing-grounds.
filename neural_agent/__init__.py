from .core.neural_core import NeuralCore
from .memory.memory_bank import MemoryBank
from .tasks.task_engine import TaskEngine
from .interface.chat_interface import ChatInterface
from .kill_switch import KillSwitch
from .web.web_crawler import WebCrawler
from .files.file_manager import FileManager
from .utils.timeout_manager import TimeoutManager
from .utils.scheduler import Scheduler
from .utils.system_monitor import SystemMonitor
from .utils.config_manager import ConfigManager
from .utils.logger import AgentLogger
from .utils.process_manager import ProcessManager
import threading
import time

class NeuralAgent:
    def __init__(self, config_file=None):
        self.memory = MemoryBank()
        self.core = NeuralCore(self.memory)
        self.tasks = TaskEngine(self)
        self.interface = ChatInterface(self)
        self.kill_switch = KillSwitch(self)
        self.web = WebCrawler(self)
        self.files = FileManager(self)
        self.timeouts = TimeoutManager()
        self.scheduler = Scheduler(self)
        self.monitor = SystemMonitor(self)
        self.config = ConfigManager(self, config_file or "config.json")
        self.logger = AgentLogger()
        self.processes = ProcessManager(self)
        self.running = True
        self.lock = threading.Lock()

    def start(self):
        print("[Neural Agent] Initializing...")
        self.memory.load()
        self.core.initialize()
        self.monitor.increment("queries", -self.monitor._stats["queries"])
        print("[Neural Agent] Ready.")
        self.interface.start()

    def shutdown(self):
        with self.lock:
            self.running = False
        print("[Neural Agent] Shutting down...")
        self.scheduler.stop()
        self.memory.save()
        self.config.save()
        self.logger.info("Agent shutdown complete")
        print("[Neural Agent] Terminated.")

    def can_run(self):
        with self.lock:
            return self.running and not self.kill_switch.engaged