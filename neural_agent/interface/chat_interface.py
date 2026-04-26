import sys
import threading
import re

class ChatInterface:
    def __init__(self, agent):
        self.agent = agent

    def start(self):
        print("\n=== Neural Agent ===")
        print("Commands:")
        print("  learn <info>     - Store information")
        print("  do <task>        - Execute a task")
        print("  think <query>    - Think about something")
        print("  recall <query>   - Search memories")
        print("  read <file>      - Read a file")
        print("  list / ls       - List directory")
        print("  search <query>  - Web search")
        print("  fetch <url>      - Fetch webpage")
        print("  setdir <dir>    - Change directory")
        print("  schedule        - List scheduled tasks")
        print("  schedule at <time> every <interval> do <task>")
        print("  timeout          - Show timeouts")
        print("  timeout set <op> <seconds>")
        print("  sysinfo          - System information")
        print("  stats            - Agent statistics")
        print("  config           - Show configuration")
        print("  config set <key> <value>")
        print("  run <cmd>        - Run shell command")
        print("  runbg <cmd>      - Run command in background")
        print("  jobs             - List background jobs")
        print("  killjob <id>     - Kill background job")
        print("  KILL             - Kill switch")
        print("  quit             - Exit")
        print("====================\n")
        
        while self.agent.can_run():
            try:
                user_input = input("You> ").strip()
                if not user_input:
                    continue
                
                self.process_input(user_input)
            except KeyboardInterrupt:
                print("\n[Interrupted]")
                self.agent.shutdown()
                break
            except EOFError:
                break
        
        print("Session ended.")

    def process_input(self, user_input):
        self.agent.monitor.increment("queries")
        self.agent.logger.log_query(user_input)
        
        if user_input.upper() == "QUIT":
            self.agent.shutdown()
            return
        
        if user_input.upper() == "KILL":
            self.agent.kill_switch.trigger()
            print("Kill switch engaged. Goodnight.")
            return
        
        if user_input.startswith("learn "):
            info = user_input[6:].strip()
            self.agent.memory.add(info, "learned")
            self.agent.monitor.increment("memories_added")
            print(f"Learned: {info[:100]}{'...' if len(info) > 100 else ''}")
            return
        
        if user_input.startswith("do "):
            task = user_input[3:].strip()
            task_id = self.agent.tasks.execute(task)
            print(f"Task started: {task_id}")
            return
        
        if user_input.startswith("think "):
            query = user_input[6:].strip()
            response = self.agent.core.think(query)
            print(f"Agent> {response}")
            return
        
        if user_input.startswith("recall "):
            query = user_input[7:].strip()
            memories = self.agent.memory.recall(query)
            if memories:
                print("Memories:")
                for mem, score in memories:
                    print(f"  - {mem[:80]}{'...' if len(mem) > 80 else ''} ({score:.2f})")
            else:
                print("No memories found.")
            return
        
        if user_input.startswith("read ") or user_input.startswith("import "):
            parts = user_input.split(" ", 1)
            if len(parts) > 1:
                result = self.agent.files.read(parts[1].strip())
                print(result[:2000] if len(result) > 2000 else result)
                self.agent.monitor.increment("files_read")
            else:
                print("Usage: read ")
            return
        
        if user_input.startswith("write "):
            match = re.match(r'write\s+(\S+)\s+(.+)', user_input)
            if match:
                filepath, content = match.groups()
                result = self.agent.files.write(filepath, content)
                print(result)
                self.agent.monitor.increment("files_written")
            else:
                print("Usage: write  <content>")
            return
        
        if user_input.startswith("list") or user_input == "ls":
            print(self.agent.files.list())
            return
        
        if user_input.startswith("setdir "):
            parts = user_input.split(" ", 1)
            if len(parts) > 1:
                print(self.agent.files.set_workdir(parts[1].strip()))
            else:
                print("Usage: setdir <directory>")
            return
        
        if user_input.startswith("search "):
            query = user_input[7:].strip()
            results = self.agent.web.search(query, limit=5)
            self.agent.monitor.increment("web_requests")
            print(f"Search results for '{query}':")
            for r in results:
                print(f"- {r['title']}")
                print(f"  {r['url']}")
            return
        
        if user_input.startswith("fetch "):
            parts = user_input.split(" ", 1)
            if len(parts) > 1:
                url = parts[1].strip()
                result = self.agent.web.summarize_page(url)
                self.agent.monitor.increment("web_requests")
                print(result)
            else:
                print("Usage: fetch <url>")
            return
        
        if user_input == "schedule":
            tasks = self.agent.scheduler.list()
            if tasks:
                print("Scheduled tasks:")
                for t in tasks:
                    print(f"  [{t['id']}] {t['description']} - {t['status']}")
            else:
                print("No scheduled tasks")
            return
        
        if user_input.startswith("schedule "):
            match = re.match(r'schedule\s+(?:at\s+(\S+)\s+)?(?:every\s+(\S+)\s+)?do\s+(.+)', user_input)
            if match:
                when, repeat, task = match.groups()
                task_id = self.agent.scheduler.schedule(task, when=when, repeat=repeat)
                print(f"Scheduled task {task_id}")
            else:
                print("Usage: schedule [at <time>] [every <interval>] do <task>")
            return
        
        if user_input == "timeout":
            timeouts = self.agent.timeouts.list_timeouts()
            print("Timeouts (seconds):")
            for op, secs in timeouts.items():
                print(f"  {op}: {secs}")
            return
        
        if user_input.startswith("timeout set "):
            match = re.match(r'timeout\s+set\s+(\S+)\s+(\d+)', user_input)
            if match:
                op, secs = match.groups()
                self.agent.timeouts.set(op, int(secs))
                print(f"Timeout for {op} set to {secs}s")
            else:
                print("Usage: timeout set <operation> <seconds>")
            return
        
        if user_input == "sysinfo":
            print(self.agent.monitor.full_report())
            return
        
        if user_input == "stats":
            stats = self.agent.monitor.get_stats()
            print("Agent Statistics:")
            for key, value in stats.items():
                print(f"  {key}: {value}")
            return
        
        if user_input == "config":
            print(self.agent.config.export())
            return
        
        if user_input.startswith("config set "):
            match = re.match(r'config\s+set\s+(\S+)\s+(.+)', user_input)
            if match:
                key, value = match.groups()
                try:
                    value = int(value)
                except:
                    try:
                        value = float(value)
                    except:
                        pass
                self.agent.config.set(key, value)
            else:
                print("Usage: config set <key> <value>")
            return
        
        if user_input.startswith("run "):
            cmd = user_input[4:].strip()
            result = self.agent.processes.run_shell(cmd)
            if isinstance(result, dict):
                if result.get("stdout"):
                    print(result["stdout"][:2000])
                if result.get("stderr"):
                    print(f"STDERR: {result['stderr'][:500]}")
                print(f"Exit code: {result.get('returncode')}")
            else:
                print(result)
            return
        
        if user_input.startswith("runbg "):
            cmd = user_input[6:].strip()
            pid = self.agent.processes.run_shell(cmd, background=True)
            print(f"Background job: {pid}")
            return
        
        if user_input == "jobs":
            jobs = self.agent.processes.list_processes()
            if jobs:
                print("Background jobs:")
                for j in jobs:
                    print(f"  [{j['pid']}] {j['command'][:50]} - {j['status']}")
            else:
                print("No background jobs")
            return
        
        if user_input.startswith("killjob "):
            match = re.match(r'killjob\s+(\S+)', user_input)
            if match:
                pid = match.group(1)
                if self.agent.processes.kill(pid):
                    print(f"Killed job {pid}")
                else:
                    print(f"Job not found: {pid}")
            else:
                print("Usage: killjob <pid>")
            return
        
        response = self.agent.core.query(user_input)
        print(f"Agent> {response}")