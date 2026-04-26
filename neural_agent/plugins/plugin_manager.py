import os
import importlib
import inspect
from abc import ABC, abstractmethod

class PluginBase(ABC):
    name = "plugin"
    version = "1.0.0"
    description = ""
    
    @abstractmethod
    def initialize(self, agent):
        pass
    
    @abstractmethod
    def execute(self, *args, **kwargs):
        pass
    
    def shutdown(self):
        pass

class PluginManager:
    def __init__(self, agent):
        self.agent = agent
        self.plugins = {}
        self.plugin_dir = "./plugins"
        self._load_builtin_plugins()
    
    def _load_builtin_plugins(self):
        builtin = {
            "math": MathPlugin,
            "date": DateTimePlugin,
            "weather": WeatherPlugin,
            "translate": TranslatePlugin,
            "code": CodePlugin,
            "reminder": ReminderPlugin,
            "calculator": CalculatorPlugin,
            "url_shortener": URLShortenerPlugin,
            "qrcode": QRCodePlugin,
            "screenshot": ScreenshotPlugin,
        }
        
        for name, plugin_class in builtin.items():
            try:
                self.load_plugin_class(name, plugin_class)
            except Exception as e:
                print(f"[PluginManager] Failed to load {name}: {e}")
    
    def load_plugin_class(self, name, plugin_class):
        plugin = plugin_class()
        plugin.initialize(self.agent)
        self.plugins[name] = plugin
        print(f"[PluginManager] Loaded: {name} v{plugin.version}")
        return plugin
    
    def load_plugin_file(self, filepath):
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Plugin file not found: {filepath}")
        
        directory = os.path.dirname(filepath)
        filename = os.path.basename(filepath)
        module_name = filename[:-3]
        
        if directory not in os.sys.path:
            os.sys.path.insert(0, directory)
        
        try:
            module = importlib.import_module(module_name)
            
            for name, obj in inspect.getmembers(module):
                if inspect.isclass(obj) and issubclass(obj, PluginBase) and obj != PluginBase:
                    plugin_name = getattr(obj, 'name', module_name)
                    return self.load_plugin_class(plugin_name, obj)
        except Exception as e:
            raise Exception(f"Failed to load plugin {filepath}: {e}")
    
    def load_plugin_directory(self):
        if not os.path.exists(self.plugin_dir):
            os.makedirs(self.plugin_dir)
            return
        
        for filename in os.listdir(self.plugin_dir):
            if filename.endswith(".py") and not filename.startswith("_"):
                filepath = os.path.join(self.plugin_dir, filename)
                try:
                    self.load_plugin_file(filepath)
                except Exception as e:
                    print(f"[PluginManager] Error loading {filename}: {e}")
    
    def execute_plugin(self, name, *args, **kwargs):
        if name not in self.plugins:
            return f"Plugin '{name}' not found"
        
        plugin = self.plugins[name]
        try:
            return plugin.execute(*args, **kwargs)
        except Exception as e:
            return f"Plugin error: {e}"
    
    def unload_plugin(self, name):
        if name in self.plugins:
            self.plugins[name].shutdown()
            del self.plugins[name]
            print(f"[PluginManager] Unloaded: {name}")
            return True
        return False
    
    def list_plugins(self):
        return [{
            "name": name,
            "version": plugin.version,
            "description": plugin.description
        } for name, plugin in self.plugins.items()]
    
    def get_plugin(self, name):
        return self.plugins.get(name)


class MathPlugin(PluginBase):
    name = "math"
    version = "1.0.0"
    description = "Mathematical operations"
    
    def initialize(self, agent):
        self.agent = agent
    
    def execute(self, expression):
        try:
            import ast
            import operator
            
            ops = {
                ast.Add: operator.add, ast.Sub: operator.sub,
                ast.Mult: operator.mul, ast.Div: operator.truediv,
                ast.Pow: operator.pow, ast.Mod: operator.mod,
                ast.USub: operator.neg
            }
            
            def eval_expr(node):
                if isinstance(node, ast.Num):
                    return node.n
                elif isinstance(node, ast.BinOp):
                    left = eval_expr(node.left)
                    right = eval_expr(node.right)
                    return ops[type(node.op)](left, right)
                elif isinstance(node, ast.UnaryOp):
                    return ops[type(node.op)](eval_expr(node.operand))
                else:
                    raise ValueError(f"Unsupported: {ast.dump(node)}")
            
            tree = ast.parse(expression, mode='eval')
            result = eval_expr(tree.body)
            return f"Result: {result}"
        except Exception as e:
            return f"Math error: {e}"


class DateTimePlugin(PluginBase):
    name = "date"
    version = "1.0.0"
    description = "Date and time utilities"
    
    def initialize(self, agent):
        self.agent = agent
    
    def execute(self, action="now"):
        from datetime import datetime
        
        if action == "now":
            return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        elif action == "today":
            return datetime.now().strftime("%Y-%m-%d")
        elif action == "time":
            return datetime.now().strftime("%H:%M:%S")
        elif action == "iso":
            return datetime.now().isoformat()
        elif action.startswith("format "):
            fmt = action[7:]
            return datetime.now().strftime(fmt)
        else:
            return f"Unknown action: {action}"


class WeatherPlugin(PluginBase):
    name = "weather"
    version = "1.0.0"
    description = "Weather information (uses wttr.in)"
    
    def initialize(self, agent):
        self.agent = agent
    
    def execute(self, location="auto"):
        try:
            import urllib.request
            url = f"https://wttr.in/{location}?format=j1"
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=10) as response:
                data = response.json()
            
            current = data["current_condition"][0]
            return (f"Weather in {location}:\n"
                   f"Temperature: {current['temp_C']}°C\n"
                   f"Condition: {current['weatherDesc'][0]['value']}\n"
                   f"Humidity: {current['humidity']}%\n"
                   f"Wind: {current['windspeedKmph']} km/h")
        except Exception as e:
            return f"Weather unavailable: {e}"


class TranslatePlugin(PluginBase):
    name = "translate"
    version = "1.0.0"
    description = "Language translation"
    
    def initialize(self, agent):
        self.agent = agent
    
    def execute(self, text, target_lang="en"):
        try:
            import urllib.parse
            import urllib.request
            
            params = urllib.parse.urlencode({
                "client": "gtx",
                "sl": "auto",
                "tl": target_lang,
                "dt": "t",
                "q": text
            })
            
            url = f"https://translate.googleapis.com/translate_a/single?{params}"
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            
            with urllib.request.urlopen(req, timeout=10) as response:
                data = response.json()
            
            translated = ''.join([item[0] for item in data[0]])
            return translated
        except Exception as e:
            return f"Translation error: {e}"


class CodePlugin(PluginBase):
    name = "code"
    version = "1.0.0"
    description = "Code execution and utilities"
    
    def initialize(self, agent):
        self.agent = agent
    
    def execute(self, code, language="python"):
        if language.lower() == "python":
            try:
                result = {}
                exec(code, {"__builtins__": __builtins__}, result)
                return str(result.get("_", result)) if result else "Code executed"
            except Exception as e:
                return f"Error: {e}"
        else:
            return f"Language '{language}' not supported"


class ReminderPlugin(PluginBase):
    name = "reminder"
    version = "1.0.0"
    description = "Set reminders"
    
    def __init__(self):
        super().__init__()
        self.reminders = []
    
    def initialize(self, agent):
        self.agent = agent
    
    def execute(self, message, seconds=60):
        import time
        import threading
        
        def remind():
            time.sleep(seconds)
            if self.agent.can_run():
                print(f"[Reminder] {message}")
        
        thread = threading.Thread(target=remind, daemon=True)
        thread.start()
        return f"Reminder set for {seconds} seconds"


class CalculatorPlugin(PluginBase):
    name = "calculator"
    version = "1.0.0"
    description = "Basic calculator"
    
    def initialize(self, agent):
        self.agent = agent
    
    def execute(self, operation, a, b):
        ops = {
            "add": lambda x, y: x + y,
            "subtract": lambda x, y: x - y,
            "multiply": lambda x, y: x * y,
            "divide": lambda x, y: x / y if y != 0 else "Error: Division by zero",
            "power": lambda x, y: x ** y,
            "mod": lambda x, y: x % y
        }
        
        if operation in ops:
            try:
                result = ops[operation](float(a), float(b))
                return f"Result: {result}"
            except Exception as e:
                return f"Error: {e}"
        return f"Unknown operation: {operation}"


class URLShortenerPlugin(PluginBase):
    name = "url_shortener"
    version = "1.0.0"
    description = "Shorten URLs"
    
    def initialize(self, agent):
        self.agent = agent
    
    def execute(self, url):
        try:
            import urllib.parse
            import urllib.request
            
            data = urllib.parse.urlencode({"url": url}).encode()
            req = urllib.request.Request("https://is.gd/create.php", data=data)
            
            with urllib.request.urlopen(req, timeout=10) as response:
                result = response.read().decode()
                
            import re
            match = re.search(r'value="(https?://[^"]+)"', result)
            if match:
                return f"Short URL: {match.group(1)}"
            return "Could not shorten URL"
        except Exception as e:
            return f"URL shortening error: {e}"


class QRCodePlugin(PluginBase):
    name = "qrcode"
    version = "1.0.0"
    description = "Generate QR codes"
    
    def initialize(self, agent):
        self.agent = agent
    
    def execute(self, data, output="qrcode.png"):
        try:
            import qrcode
            img = qrcode.make(data)
            img.save(output)
            return f"QR code saved to {output}"
        except Exception as e:
            return f"QR code error: {e}"


class ScreenshotPlugin(PluginBase):
    name = "screenshot"
    version = "1.0.0"
    description = "Take screenshots"
    
    def initialize(self, agent):
        self.agent = agent
    
    def execute(self, output="screenshot.png"):
        try:
            from PIL import ImageGrab
            img = ImageGrab.grab()
            img.save(output)
            return f"Screenshot saved to {output}"
        except Exception as e:
            return f"Screenshot error: {e}"