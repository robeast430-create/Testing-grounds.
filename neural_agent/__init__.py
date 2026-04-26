from .core.neural_core import NeuralCore
from .memory.memory_bank import MemoryBank
from .tasks.task_engine import TaskEngine
from .interface.chat_interface import ChatInterface
from .kill_switch import KillSwitch
from .web.web_crawler import WebCrawler
import threading
import time

class NeuralAgent:
    def __init__(self):
        self.memory = MemoryBank()
        self.core = NeuralCore(self.memory)
        self.tasks = TaskEngine(self)
        self.interface = ChatInterface(self)
        self.kill_switch = KillSwitch(self)
        self.web = WebCrawler(self)
        self.running = True
        self.lock = threading.Lock()

    def start(self):
        print("[Neural Agent] Initializing...")
        self.memory.load()
        self.core.initialize()
        print("[Neural Agent] Ready.")
        self.interface.start()

    def shutdown(self):
        with self.lock:
            self.running = False
        print("[Neural Agent] Shutting down...")
        self.memory.save()
        print("[Neural Agent] Terminated.")

    def can_run(self):
        with self.lock:
            return self.running and not self.kill_switch.engaged