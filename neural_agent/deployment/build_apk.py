"""
APK Builder for Neural Agent
Packages the application as an Android APK using Kivy/Buildozer
"""

import os
import sys
import json
import subprocess
import shutil
from pathlib import Path


class APKBuilder:
    def __init__(self, project_dir: str = "."):
        self.project_dir = Path(project_dir)
        self.build_dir = self.project_dir / ".apk_build"
        self.spec_file = self.build_dir / "neural_agent.spec"
        self.buildozer_yaml = self.build_dir / "buildozer.yaml"
    
    def check_dependencies(self) -> dict:
        """Check if required tools are available"""
        results = {}
        
        results["python"] = self._check_command("python3 --version")
        results["pip"] = self._check_command("pip3 --version")
        results["java"] = self._check_command("java -version")
        results["android_sdk"] = self._check_android_sdk()
        results["buildozer"] = self._check_command("buildozer --version")
        
        return results
    
    def _check_command(self, cmd: str) -> bool:
        try:
            subprocess.run(cmd, shell=True, capture_output=True, timeout=10)
            return True
        except:
            return False
    
    def _check_android_sdk(self) -> bool:
        sdk_paths = [
            os.environ.get("ANDROIDSDK", ""),
            os.environ.get("ANDROID_HOME", ""),
            os.path.expanduser("~/Android/Sdk"),
            "/usr/lib/android-sdk"
        ]
        for path in sdk_paths:
            if path and Path(path).exists():
                return True
        return False
    
    def setup_environment(self) -> bool:
        """Install required dependencies"""
        print("[APK Builder] Setting up environment...")
        
        deps = [
            "kivy",
            "buildozer",
            "python-for-android"
        ]
        
        for dep in deps:
            print(f"  Installing {dep}...")
            result = subprocess.run(
                ["pip3", "install", dep],
                capture_output=True,
                text=True
            )
            if result.returncode != 0:
                print(f"  Warning: {dep} install may have issues: {result.stderr[:200]}")
        
        return True
    
    def create_spec_file(self, app_name: str = "NeuralAgent",
                         app_id: str = "com.neuralagent.app",
                         version: str = "1.0.0") -> str:
        """Create Buildozer spec file"""
        content = f'''[app]

title = {app_name}
package.name = {app_name.lower().replace(" ", "_")}
package.domain = com.neuralagent

version = {version}

source.include_exts = py,png,jpg,kv,atlas,json,yml,txt,md,html,css,js,toml

version.filename = {version}

fullscreen = 0

android.permissions = INTERNET,BLUETOOTH,BLUETOOTH_ADMIN,Bluetooth,BLUETOOTH_CONNECT,BLUETOOTH_SCAN,RECORD_AUDIO,VIBRATE,WAKE_LOCK,CAMERA,READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE,ACCESS_NETWORK_STATE,ACCESS_WIFI_STATE,CHANGE_WIFI_STATE

android.archs = arm64-v8a, armeabi-v7a

android.minapi = 21
android.api = 33

android.allow_backup = True

android.accept_sdk_license = True

orientation = all

p4abootstrap_whitelist_cv = True

ios.kivy_ios_url = https://github.com/kivy/kivy-ios
ios.kivy_ios_branch = master
ios.ios_deploy_url = https://github.com/phonegap/ios-deploy
ios.ios_deploy_branch = 1.10.0

log_level = 2

warn_on_root = 1

[buildozer]

log_level = 2

warn_on_root = 1

build_dir = ./.buildozer

bin_dir = ./bin
'''
        self.spec_file.write_text(content)
        return str(self.spec_file)
    
    def create_kivy_app(self) -> str:
        """Create main Kivy app file"""
        kivy_dir = self.build_dir / "kivy_app"
        kivy_dir.mkdir(exist_ok=True)
        
        main_py = '''#!/usr/bin/env python3
"""
Neural Agent - Android App
"""

import kivy
kivy.require('2.2.0')

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.core.window import Window
from kivy.clock import Clock
import threading
import time

try:
    from neural_agent import NeuralAgent
    NEURAL_AVAILABLE = True
except:
    NEURAL_AVAILABLE = False


class ChatScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.setup_ui()
        if NEURAL_AVAILABLE:
            self.init_agent()
    
    def setup_ui(self):
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        self.chat_display = ScrollView(size_hint=(1, 0.7))
        self.chat_label = Label(
            text='', size_hint_y=None, text_size=(self.width, None),
            valign='top', halign='left'
        )
        self.chat_display.add_widget(self.chat_label)
        layout.add_widget(self.chat_display)
        
        input_layout = BoxLayout(size_hint_y=0.1, spacing=5)
        self.input_field = TextInput(hint_text='Type message...', multiline=False)
        input_layout.add_widget(self.input_field)
        
        send_btn = Button(text='Send', on_press=self.send_message)
        input_layout.add_widget(send_btn)
        layout.add_widget(input_layout)
        
        self.add_widget(layout)
    
    def init_agent(self):
        try:
            self.agent = NeuralAgent()
            self.add_message("System", "Neural Agent initialized!")
        except Exception as e:
            self.add_message("System", f"Error: {e}")
    
    def add_message(self, sender, message):
        current = self.chat_label.text
        self.chat_label.text = f"{current}{sender}: {message}\\n\\n"
        self.chat_label.text_size = (self.width - 20, None)
        self.chat_label.height = self.chat_label.texture_update()[1][1]
        self.chat_display.scroll_y = 0
    
    def send_message(self, instance):
        msg = self.input_field.text.strip()
        if not msg:
            return
        self.add_message("You", msg)
        self.input_field.text = ""
        
        if NEURAL_AVAILABLE and hasattr(self, 'agent'):
            threading.Thread(target=self.process_message, args=(msg,)).start()
    
    def process_message(self, msg):
        try:
            response = self.agent.core.query(msg)
            Clock.schedule_once(lambda dt: self.add_message("Agent", response))
        except Exception as e:
            Clock.schedule_once(lambda dt: self.add_message("Error", str(e)))


class SimScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.setup_ui()
    
    def setup_ui(self):
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        layout.add_widget(Label(text='2D/3D/4D Simulation Dashboard', size_hint_y=0.1))
        
        sim_layout = BoxLayout(size_hint_y=0.3, spacing=10)
        
        for dim in ['2D', '3D', '4D']:
            btn = Button(text=f'Launch {dim} Sim', on_press=lambda x, d=dim: self.launch_sim(d))
            sim_layout.add_widget(btn)
        
        layout.add_widget(sim_layout)
        
        self.sim_display = ScrollView(size_hint_y=0.5)
        self.sim_label = Label(text='No simulations running', valign='top')
        self.sim_display.add_widget(self.sim_label)
        layout.add_widget(self.sim_display)
        
        self.add_widget(layout)
    
    def launch_sim(self, dim):
        self.sim_label.text = f"Launching {dim}D simulation..."


class ToolsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.setup_ui()
    
    def setup_ui(self):
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        tools = [
            ('Web Search', self.do_search),
            ('File Manager', self.do_files),
            ('Database', self.do_db),
            ('Voice', self.do_voice),
            ('Bluetooth', self.do_bluetooth),
            ('Code Analysis', self.do_code),
            ('Network Tools', self.do_network),
            ('Security', self.do_security),
        ]
        
        for tool_name, callback in tools:
            btn = Button(text=tool_name, size_hint_y=0.1, on_press=callback)
            layout.add_widget(btn)
        
        self.output = ScrollView(size_hint_y=0.3)
        self.output_label = Label(text='Tool output will appear here', valign='top')
        self.output.add_widget(self.output_label)
        layout.add_widget(self.output)
        
        self.add_widget(layout)
    
    def update_output(self, text):
        self.output_label.text = text
    
    def do_search(self, x): self.update_output("Web search triggered")
    def do_files(self, x): self.update_output("File manager triggered")
    def do_db(self, x): self.update_output("Database triggered")
    def do_voice(self, x): self.update_output("Voice triggered")
    def do_bluetooth(self, x): self.update_output("Bluetooth triggered")
    def do_code(self, x): self.update_output("Code analysis triggered")
    def do_network(self, x): self.update_output("Network tools triggered")
    def do_security(self, x): self.update_output("Security tools triggered")


class SettingsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.setup_ui()
    
    def setup_ui(self):
        layout = BoxLayout(orientation='vertical', padding=10)
        layout.add_widget(Label(text='Settings', font_size='24sp'))
        layout.add_widget(Label(text='Kill Switch: Available'))
        layout.add_widget(Label(text='Memory: Active'))
        layout.add_widget(Label(text='Tasks: Queued'))
        self.add_widget(layout)
    
    def trigger_kill_switch(self):
        if hasattr(self.agent, 'kill_switch'):
            self.agent.kill_switch.trigger()


class NeuralAgentApp(App):
    def build(self):
        self.title = 'Neural Agent'
        Window.softinput_mode = 'below_target'
        
        sm = ScreenManager()
        sm.add_widget(ChatScreen(name='chat'))
        sm.add_widget(SimScreen(name='sim'))
        sm.add_widget(ToolsScreen(name='tools'))
        sm.add_widget(SettingsScreen(name='settings'))
        
        nav = BoxLayout(size_hint_y=0.1, spacing=5)
        for name in ['chat', 'sim', 'tools', 'settings']:
            nav.add_widget(Button(text=name.title(), on_press=lambda x, s=sm, n=name: setattr(s, 'current', n)))
        sm.add_widget(nav)
        
        return sm


if __name__ == '__main__':
    NeuralAgentApp().run()
'''
        
        return str(kivy_dir / "main.py")
    
    def prepare_source(self) -> bool:
        """Prepare source files for APK build"""
        print("[APK Builder] Preparing source files...")
        
        self.build_dir.mkdir(exist_ok=True)
        
        (self.build_dir / "src").mkdir(exist_ok=True)
        (self.build_dir / "src" / "kivy_app").mkdir(exist_ok=True)
        
        kivy_main = '''#!/usr/bin/env python3
import kivy
kivy.require('2.2.0')

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.core.window import Window
from kivy.clock import Clock
import threading

class NeuralAgentMobile(App):
    def build(self):
        Window.clearcolor = (0.1, 0.1, 0.15, 1)
        sm = ScreenManager()
        sm.add_widget(MainScreen(name='main'))
        sm.add_widget(SimulationScreen(name='sim'))
        sm.add_widget(ToolsScreen(name='tools'))
        return sm

class MainScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.agent = None
        self.setup_ui()
        self.init_agent()
    
    def setup_ui(self):
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        layout.add_widget(Label(text='Neural Agent AI', font_size='24', size_hint_y=0.1))
        
        self.output = ScrollView(size_hint_y=0.6)
        self.output_label = Label(text='Initializing...', size_hint_y=None, valign='top')
        self.output.add_widget(self.output_label)
        layout.add_widget(self.output)
        
        input_box = BoxLayout(size_hint_y=0.1)
        self.input_field = TextInput(hint_text='Enter command...', multiline=False)
        input_box.add_widget(self.input_field)
        
        btn = Button(text='Send', on_press=self.send_cmd)
        input_box.add_widget(btn)
        layout.add_widget(input_box)
        
        nav = BoxLayout(size_hint_y=0.1, spacing=5)
        for name in ['main', 'sim', 'tools']:
            nav.add_widget(Button(text=name.upper(), on_press=lambda x, s=self.manager, n=name: setattr(s, 'current', n)))
        layout.add_widget(nav)
        
        self.add_widget(layout)
    
    def init_agent(self):
        try:
            from neural_agent import NeuralAgent
            self.agent = NeuralAgent()
            self.output_label.text = '[b]Neural Agent Ready![/b]\\n\\n'
            self.output_label.text += 'Commands: search, learn, recall, task, kill\\n'
        except Exception as e:
            self.output_label.text = f'[color=ff0000]Error: {e}[/color]\\n'
            self.output_label.text += 'Running in demo mode'
    
    def send_cmd(self, instance):
        msg = self.input_field.text.strip()
        if not msg:
            return
        self.input_field.text = ''
        self.output_label.text += f'[color=00ff00]You:[/color] {msg}\\n'
        
        if self.agent:
            threading.Thread(target=self.process_cmd, args=(msg,)).start()
        else:
            self.output_label.text += f'[color=ffff00]Demo:[/color] {msg} - acknowledged\\n'
    
    def process_cmd(self, msg):
        try:
            if msg.startswith('search '):
                result = self.agent.web.search(msg[7:])
                Clock.schedule_once(lambda dt: setattr(self.output_label, 'text', self.output_label.text + f'Results: {len(result)} found\\n'))
            elif msg.startswith('learn '):
                self.agent.memory.add(msg[6:])
                Clock.schedule_once(lambda dt: setattr(self.output_label, 'text', self.output_label.text + 'Learned!\\n'))
            elif msg.startswith('recall '):
                results = self.agent.memory.recall(msg[6:])
                Clock.schedule_once(lambda dt: setattr(self.output_label, 'text', self.output_label.text + f'Found {len(results)} memories\\n'))
            elif msg == 'kill':
                self.agent.kill_switch.trigger()
                Clock.schedule_once(lambda dt: setattr(self.output_label, 'text', self.output_label.text + 'Kill switch engaged!\\n'))
            else:
                response = self.agent.core.query(msg)
                Clock.schedule_once(lambda dt: setattr(self.output_label, 'text', self.output_label.text + f'[color=00ffff]Agent:[/color] {response}\\n'))
        except Exception as e:
            Clock.schedule_once(lambda dt: setattr(self.output_label, 'text', self.output_label.text + f'Error: {e}\\n'))

class SimulationScreen(Screen):
    def setup_ui(self):
        layout = BoxLayout(orientation='vertical', padding=10)
        layout.add_widget(Label(text='2D/3D/4D Simulations', font_size='24'))
        
        btns = BoxLayout(size_hint_y=0.2)
        for dim in ['2D', '3D', '4D']:
            btns.add_widget(Button(text=f'Launch {dim}', on_press=lambda x, d=dim: self.launch_sim(d)))
        layout.add_widget(btns)
        
        self.sim_output = Label(text='Select a simulation')
        layout.add_widget(self.sim_output)
        
        self.add_widget(layout)
    
    def launch_sim(self, dim):
        self.sim_output.text = f'Loading {dim}D simulation engine...'
        try:
            from neural_agent.simulation import SimulationManager, Dimension
            manager = SimulationManager()
            dim_map = {'2D': Dimension.DIM_2D, '3D': Dimension.DIM_3D, '4D': Dimension.DIM_4D}
            sim = manager.create_simulation(f'mobile_{dim}', dim_map[dim])
            self.sim_output.text = f'{dim}D simulation ready!\\nParticles: {len(getattr(sim, "hyperparticles", [])) + len(getattr(sim, "particles", []))}'
        except Exception as e:
            self.sim_output.text = f'Simulation error: {e}'
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.setup_ui()

class ToolsScreen(Screen):
    def setup_ui(self):
        layout = BoxLayout(orientation='vertical', padding=10)
        layout.add_widget(Label(text='Tools & Utilities', font_size='24'))
        
        tools = ['Web Search', 'File Manager', 'Database', 'Voice', 'Bluetooth', 'Code', 'Network', 'Security']
        for tool in tools:
            layout.add_widget(Button(text=tool, size_hint_y=0.1, on_press=lambda x, t=tool: self.show_tool(t)))
        
        self.tool_output = Label(text='Select a tool')
        layout.add_widget(self.tool_output)
        
        self.add_widget(layout)
    
    def show_tool(self, tool):
        self.tool_output.text = f'{tool} - Ready'
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.setup_ui()

if __name__ == '__main__':
    NeuralAgentMobile().run()
'''
        
        (self.build_dir / "src" / "kivy_app" / "main.py").write_text(main_spec)
        
        with open(self.project_dir / "requirements.txt", "r") as f:
            reqs = f.read()
        
        new_reqs = reqs.strip() + "\nkivy\nbuildozer\npython-for-android\n"
        (self.build_dir / "requirements.txt").write_text(new_reqs)
        
        return True
    
    def build_apk(self, debug: bool = True) -> str:
        """Build the APK"""
        print("[APK Builder] Building APK...")
        print("  This may take 10-30 minutes on first run...")
        
        os.chdir(self.build_dir)
        
        cmd = ["buildozer", "android", "debug"] if debug else ["buildozer", "android", "release"]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=3600)
            
            bin_dir = self.build_dir / "bin"
            if bin_dir.exists():
                apks = list(bin_dir.glob("*.apk"))
                if apks:
                    latest = max(apks, key=lambda p: p.stat().st_mtime)
                    dest = self.project_dir / f"neural_agent_{'debug' if debug else 'release'}.apk"
                    shutil.copy(latest, dest)
                    print(f"[APK Builder] APK built: {dest}")
                    return str(dest)
            
            print("Build output:", result.stdout[-1000:] if result.stdout else "")
            print("Build errors:", result.stderr[-1000:] if result.stderr else "")
            return None
        except subprocess.TimeoutExpired:
            print("[APK Builder] Build timed out (took > 1 hour)")
            return None
        except Exception as e:
            print(f"[APK Builder] Build error: {e}")
            return None
    
    def build_flexible_apk(self) -> str:
        """Build APK with all features included"""
        print("[APK Builder] Building FULL APK with all features...")
        
        self.create_spec_file()
        self.prepare_source()
        
        self.spec_file.write_text(self.spec_file.read_text().replace(
            'source.include_exts = py,png,jpg,kv,atlas',
            'source.include_exts = py,png,jpg,kv,atlas,json,yml,txt,md,html,css,js,toml,csv,xml'
        ))
        
        return self.build_apk(debug=True)


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Build Neural Agent APK")
    parser.add_argument("--check", action="store_true", help="Check dependencies")
    parser.add_argument("--setup", action="store_true", help="Setup environment")
    parser.add_argument("--build", action="store_true", help="Build APK")
    parser.add_argument("--full", action="store_true", help="Full build with all features")
    parser.add_argument("--release", action="store_true", help="Build release APK")
    parser.add_argument("--dir", default=".", help="Project directory")
    
    args = parser.parse_args()
    
    builder = APKBuilder(args.dir)
    
    if args.check:
        deps = builder.check_dependencies()
        print("\\nDependency Status:")
        for name, available in deps.items():
            status = "✓" if available else "✗"
            print(f"  {status} {name}: {'Available' if available else 'Missing'}")
        
        if not all(deps.values()):
            print("\\nMissing dependencies. Run with --setup to install.")
            return 1
        return 0
    
    if args.setup:
        builder.setup_environment()
        return 0
    
    if args.full:
        return builder.build_flexible_apk() is not None
    
    if args.build or args.release:
        if args.release:
            return builder.build_apk(debug=False) is not None
        return builder.build_apk(debug=True) is not None
    
    print("Neural Agent APK Builder")
    print("Usage:")
    print("  --check   Check dependencies")
    print("  --setup   Install build dependencies")
    print("  --build   Build debug APK")
    print("  --full    Build full APK with all features")
    print("  --release Build release APK")
    return 0


if __name__ == "__main__":
    sys.exit(main())