#!/usr/bin/env python3
"""
LinuxAI - Terminal UI for Neural Agent
Run with: linai
"""

import os
import sys
import readline
import time
import threading
import subprocess
from pathlib import Path


try:
    from neural_agent import NeuralAgent
    NEURAL_AVAILABLE = True
except ImportError:
    NEURAL_AVAILABLE = False
    print("Warning: Neural Agent not installed. Running in demo mode.")


class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    RESET = '\033[0m'
    
    @classmethod
    def strip(cls, text):
        return cls.RED + text + cls.RESET


class LinuxAI:
    def __init__(self):
        self.agent = None
        self.running = True
        self.history = []
        self.max_history = 100
        self.history_file = Path.home() / ".linai_history"
        self.load_history()
        
        if NEURAL_AVAILABLE:
            self.init_agent()
    
    def init_agent(self):
        try:
            self.agent = NeuralAgent()
            self.agent.current_user = "linai_user"
        except Exception as e:
            print(f"Agent init error: {e}")
            self.agent = None
    
    def load_history(self):
        if self.history_file.exists():
            with open(self.history_file) as f:
                self.history = [line.strip() for line in f.readlines()[-100:]]
            readline.set_history_length(100)
    
    def save_history(self):
        with open(self.history_file, 'w') as f:
            f.write('\n'.join(self.history[-100:]))
    
    def print_banner(self):
        banner = f"""
{Colors.CYAN}╔═══════════════════════════════════════════════════════════╗
║  {Colors.BOLD}LinuxAI{Colors.RESET}{Colors.CYAN} - Neural Agent Terminal Interface            ║
║  {Colors.DIM}Advanced AI with memory, autonomy, and simulations{Colors.RESET}         {Colors.CYAN}║
╚═══════════════════════════════════════════════════════════╝{Colors.RESET}

"""
        print(banner)
    
    def print_help(self):
        help_text = f"""
{Colors.BOLD}COMMANDS:{Colors.RESET}
  {Colors.GREEN}/help{Colors.RESET}           Show this help
  {Colors.GREEN}/chat <msg>{Colors.RESET}     Chat with the AI
  {Colors.GREEN}/learn <text>{Colors.RESET}   Add information to memory
  {Colors.GREEN}/recall <q>{Colors.RESET}     Search memory
  {Colors.GREEN}/search <q>{Colors.RESET}     Web search
  {Colors.GREEN}/fetch <url>{Colors.RESET}    Fetch web page
  {Colors.GREEN}/tasks{Colors.RESET}          List pending tasks
  {Colors.GREEN}/task <cmd>{Colors.RESET}     Execute a task
  {Colors.GREEN}/run <cmd>{Colors.RESET}       Run shell command
  {Colors.GREEN}/kill{Colors.RESET}            Trigger kill switch

{Colors.BOLD}SIMULATION:{Colors.RESET}
  {Colors.GREEN}/sim create <n> <d>{Colors.RESET}  Create simulation (2d/3d/4d)
  {Colors.GREEN}/sim step <n>{Colors.RESET}        Step simulation
  {Colors.GREEN}/sim list{Colors.RESET}            List simulations
  {Colors.GREEN}/sim render <n>{Colors.RESET}       Render to HTML
  {Colors.GREEN}/sim blender <n>{Colors.RESET}      Export to Blender

{Colors.BOLD}APK BUILDING:{Colors.RESET}
  {Colors.GREEN}/apk check{Colors.RESET}      Check dependencies
  {Colors.GREEN}/apk setup{Colors.RESET}      Setup environment
  {Colors.GREEN}/apk build{Colors.RESET}      Build APK
  {Colors.GREEN}/apk all{Colors.RESET}        Full build
  {Colors.GREEN}/apk release{Colors.RESET}    Build release APK

{Colors.BOLD}SYSTEM:{Colors.RESET}
  {Colors.GREEN}/web{Colors.RESET}            Start web dashboard
  {Colors.GREEN}/status{Colors.RESET}         System status
  {Colors.GREEN}/sysinfo{Colors.RESET}       System information
  {Colors.GREEN}/stats{Colors.RESET}          Agent statistics
  {Colors.GREEN}/clear{Colors.RESET}         Clear screen
  {Colors.GREEN}/exit{Colors.RESET}           Exit LinuxAI

{Colors.BOLD}KEYBOARD SHORTCUTS:{Colors.RESET}
  {Colors.DIM}Ctrl+C{Colors.RESET}           Interrupt/Cancel
  {Colors.DIM}Ctrl+L{Colors.RESET}           Clear screen
  {Colors.DIM}Ctrl+Q{Colors.RESET}           Quit
  {Colors.DIM}Tab{Colors.RESET}              Auto-complete
  {Colors.DIM}Up/Down{Colors.RESET}          Command history{Colors.RESET}
"""
        print(help_text)
    
    def chat(self, message):
        if not self.agent:
            return f"[Demo Mode] You said: {message}"
        
        response = self.agent.core.query(message)
        return response
    
    def learn(self, text):
        if not self.agent:
            return "Demo mode: Would learn: " + text[:50] + "..."
        
        self.agent.memory.add(text, "user_input")
        return f"Learned: {len(text)} characters"
    
    def recall(self, query):
        if not self.agent:
            return f"Demo mode: Would search for: {query}"
        
        results = self.agent.memory.recall(query)
        if not results:
            return "No memories found."
        
        output = f"Found {len(results)} memories:\n"
        for content, score in results[:5]:
            output += f"  [{score:.2f}] {content[:80]}...\n"
        return output
    
    def search(self, query):
        if not self.agent:
            return f"Demo mode: Would search web for: {query}"
        
        try:
            results = self.agent.web.search(query)
            output = f"Search results for '{query}':\n"
            for r in results[:5]:
                output += f"  - {r.get('title', 'N/A')}\n"
                output += f"    {r.get('url', '')[:60]}...\n"
            return output
        except Exception as e:
            return f"Search error: {e}"
    
    def fetch(self, url):
        if not self.agent:
            return f"Demo mode: Would fetch: {url}"
        
        try:
            result = self.agent.web.summarize_page(url)
            return f"Fetched {url}:\n\n{result[:500]}..."
        except Exception as e:
            return f"Fetch error: {e}"
    
    def show_tasks(self):
        if not self.agent:
            return "Demo mode: No tasks"
        
        tasks = self.agent.tasks.list_tasks()
        if not tasks:
            return "No pending tasks."
        
        output = "Pending tasks:\n"
        for task in tasks:
            output += f"  [{task.get('status', '?'):8}] {task.get('description', 'Task')}\n"
        return output
    
    def execute_task(self, cmd):
        if not self.agent:
            return f"Demo mode: Would execute: {cmd}"
        
        task_id = self.agent.tasks.execute(cmd)
        return f"Task queued: {task_id}"
    
    def run_command(self, cmd):
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
            output = f"Exit code: {result.returncode}\n"
            if result.stdout:
                output += f"\n{result.stdout[:1000]}"
            if result.stderr:
                output += f"\n{Colors.RED}{result.stderr[:500]}{Colors.RESET}"
            return output
        except subprocess.TimeoutExpired:
            return "Command timed out."
        except Exception as e:
            return f"Error: {e}"
    
    def trigger_kill(self):
        if not self.agent:
            return "Demo mode: Kill switch triggered!"
        
        self.agent.kill_switch.trigger()
        return "Kill switch ENGAGED!"
    
    def sim_command(self, subcmd, args):
        if not NEURAL_AVAILABLE:
            return "Neural Agent not installed."
        
        try:
            from neural_agent.simulation import SimulationManager, Dimension
            manager = SimulationManager()
            
            if subcmd == "create":
                name = args[0] if args else "sim"
                dim = args[1] if len(args) > 1 else "3d"
                dim_map = {"2d": Dimension.DIM_2D, "3d": Dimension.DIM_3D, "4d": Dimension.DIM_4D}
                sim = manager.create_simulation(name, dim_map.get(dim, Dimension.DIM_3D))
                return f"Created {dim}D simulation: {name}"
            
            elif subcmd == "list":
                sims = manager.list_simulations()
                if not sims:
                    return "No simulations."
                return "Simulations:\n  " + "\n  ".join(sims)
            
            elif subcmd == "step":
                name = args[0] if args else "default"
                manager.step_all()
                return f"Stepped: {name}"
            
            elif subcmd == "render":
                name = args[0] if args else "default"
                html = manager.render(name)
                out = f"{name}.html"
                with open(out, 'w') as f:
                    f.write(html)
                return f"Rendered to {out} ({len(html)} bytes)"
            
            elif subcmd == "blender":
                name = args[0] if args else "default"
                result = manager.export_blender(name)
                return f"Blender export: {result}"
            
            else:
                return f"Unknown sim command: {subcmd}"
        
        except Exception as e:
            return f"Simulation error: {e}"
    
    def apk_command(self, subcmd):
        if not NEURAL_AVAILABLE:
            return "Neural Agent not installed."
        
        try:
            from neural_agent.deployment.build_apk import APKBuilder
            builder = APKBuilder()
            
            if subcmd == "check":
                deps = builder.check_dependencies()
                output = "APK Build Dependencies:\n"
                for name, ok in deps.items():
                    output += f"  {'[OK]' if ok else '[X]'} {name}\n"
                return output
            
            elif subcmd == "setup":
                builder.setup_environment()
                return "APK build environment setup complete."
            
            elif subcmd == "build":
                result = builder.build_apk(debug=True)
                return f"APK build: {result}" if result else "Build failed."
            
            elif subcmd == "all" or subcmd == "full":
                return "Running full APK build... (this takes 10-30 minutes)"
            
            elif subcmd == "release":
                result = builder.build_apk(debug=False)
                return f"Release APK: {result}" if result else "Build failed."
            
            else:
                return f"Unknown apk command: {subcmd}"
        
        except Exception as e:
            return f"APK error: {e}"
    
    def show_status(self):
        if not self.agent:
            return "Demo mode: System running"
        
        stats = self.agent.monitor.get_stats()
        return f"""System Status:
  Queries: {stats.get('queries', 0)}
  Memory: {self.agent.memory.count()} items
  Tasks: {len(self.agent.tasks.list_tasks())}
  Running: {self.agent.running}
  Kill Switch: {'ENGAGED' if self.agent.kill_switch.engaged else 'Safe'}"""
    
    def show_sysinfo(self):
        if not self.agent:
            return "Demo mode: x86_64 Linux"
        
        info = self.agent.monitor.get_system_info()
        return f"""System Info:
  Platform: {info.get('platform', 'Unknown')}
  Python: {info.get('python_version', 'N/A')}
  CPU: {info.get('cpu_count', 'N/A')} cores
  Memory: {info.get('memory_percent', 'N/A')}% used"""
    
    def show_stats(self):
        if not self.agent:
            return "Demo mode: No statistics"
        
        stats = self.agent.monitor.get_stats()
        return f"""Agent Statistics:
  Uptime queries: {stats.get('queries', 0)}
  Task queue: {stats.get('pending_tasks', 0)}
  Memory count: {stats.get('memory_items', 0)}"""
    
    def start_web(self):
        if not self.agent:
            return "Demo mode: Cannot start web server"
        
        try:
            from neural_agent.api.api_server import APIServer
            api = APIServer(self.agent, 8080)
            thread = threading.Thread(target=api.start, daemon=True)
            thread.start()
            return "Web dashboard started at http://localhost:8080"
        except Exception as e:
            return f"Web server error: {e}"
    
    def process_input(self, line):
        line = line.strip()
        if not line:
            return
        
        self.history.append(line)
        if len(self.history) > self.max_history:
            self.history.pop(0)
        
        if line.startswith('/'):
            parts = line.split(maxsplit=1)
            cmd = parts[0]
            args = parts[1].split() if len(parts) > 1 else []
            
            if cmd == "/help":
                self.print_help()
            elif cmd == "/exit" or cmd == "/quit":
                self.running = False
                print(f"{Colors.YELLOW}Goodbye!{Colors.RESET}")
            elif cmd == "/clear":
                print('\033[2J\033[H')
            elif cmd == "/chat":
                print(self.chat(' '.join(args)))
            elif cmd == "/learn":
                print(self.learn(' '.join(args)))
            elif cmd == "/recall":
                print(self.recall(' '.join(args)))
            elif cmd == "/search":
                print(self.search(' '.join(args)))
            elif cmd == "/fetch":
                print(self.fetch(args[0] if args else ""))
            elif cmd == "/tasks":
                print(self.show_tasks())
            elif cmd == "/task":
                print(self.execute_task(' '.join(args)))
            elif cmd == "/run":
                print(self.run_command(' '.join(args)))
            elif cmd == "/kill":
                print(self.trigger_kill())
            elif cmd == "/sim":
                print(self.sim_command(args[0] if args else "", args[1:]))
            elif cmd == "/apk":
                print(self.apk_command(args[0] if args else ""))
            elif cmd == "/web":
                print(self.start_web())
            elif cmd == "/status":
                print(self.show_status())
            elif cmd == "/sysinfo":
                print(self.show_sysinfo())
            elif cmd == "/stats":
                print(self.show_stats())
            else:
                print(f"{Colors.RED}Unknown command: {cmd}{Colors.RESET}")
                print("Type /help for available commands")
        else:
            print(self.chat(line))
    
    def run(self):
        self.print_banner()
        self.print_help()
        
        prompt = f"{Colors.GREEN}linai>{Colors.RESET} "
        
        try:
            while self.running:
                try:
                    line = input(prompt)
                    if line:
                        self.process_input(line)
                except KeyboardInterrupt:
                    print("\nUse /exit to quit")
                except EOFError:
                    break
        finally:
            self.save_history()


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="LinuxAI - Neural Agent Terminal Interface")
    parser.add_argument("--no-agent", action="store_true", help="Run without neural agent")
    parser.add_argument("--chat", type=str, help="Send single chat message")
    args = parser.parse_args()
    
    if args.no_agent:
        global NEURAL_AVAILABLE
        NEURAL_AVAILABLE = False
    
    if args.chat:
        ai = LinuxAI()
        if NEURAL_AVAILABLE:
            print(ai.chat(args.chat))
        else:
            print(f"[Demo] {args.chat}")
    else:
        ai = LinuxAI()
        ai.run()


if __name__ == "__main__":
    main()