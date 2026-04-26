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
from .auth import AuthManager, LoginInterface
from .auth.command_history import CommandHistory
from .plugins import PluginManager
from .database import Database
from .notifications import NotificationManager
from .conversation import ConversationManager
from .tools import APIKeyManager, ExportImportManager, FileWatcher
from .prompts import PromptManager
from .bluetooth import BluetoothManager
from .voice import VoiceManager
from .utils.system_utils import SystemUtils, BackupManager
from .coding import CodeAnalyzer, CodeGenerator, Linter, DependencyManager, TestGenerator
from .coding import GitManager, BuildManager, ContainerManager
import threading
import time

class NeuralAgent:
    def __init__(self, config_file=None, data_dir="./auth_data"):
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
        self.auth = AuthManager(data_dir)
        self.history = CommandHistory(data_dir)
        self.db = Database()
        self.notifications = NotificationManager(self)
        self.conversations = ConversationManager(self, self.db)
        self.api_keys = APIKeyManager(data_dir)
        self.export_import = ExportImportManager(self)
        self.file_watcher = FileWatcher(self)
        self.prompts = PromptManager(self)
        self.plugins = PluginManager(self)
        self.bluetooth = BluetoothManager(self)
        self.voice = VoiceManager(self)
        self.backup = BackupManager(self)
        self.utils = SystemUtils(self)
        self.code_analyzer = CodeAnalyzer(self)
        self.code_generator = CodeGenerator(self)
        self.linter = Linter(self)
        self.deps = DependencyManager(self)
        self.test_gen = TestGenerator(self)
        self.git = GitManager(self)
        self.build = BuildManager(self)
        self.containers = ContainerManager(self)
        self.current_user = None
        self.session_token = None
        self.running = True
        self.lock = threading.Lock()

    def start(self):
        print("[Neural Agent] Initializing...")
        self.memory.load()
        self.core.initialize()
        self.monitor.increment("queries", -self.monitor._stats["queries"])
        self.notifications.info("Neural Agent started", "system")
        print("[Neural Agent] Ready.")
        self.interface.start()

    def shutdown(self):
        with self.lock:
            self.running = False
        print("[Neural Agent] Shutting down...")
        self.scheduler.stop()
        self.file_watcher.stop()
        self.memory.save()
        self.config.save()
        self.db.close()
        self.logger.info("Agent shutdown complete")
        self.notifications.info("Neural Agent stopped", "system")
        print("[Neural Agent] Terminated.")

    def can_run(self):
        with self.lock:
            return self.running and not self.kill_switch.engaged