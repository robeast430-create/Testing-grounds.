import sys
import threading
import re
import json

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
        
        if hasattr(self.agent, 'current_user') and self.agent.current_user:
            self.agent.history.add(self.agent.current_user, user_input)
        
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
        
        if user_input == "history":
            hist = self.agent.history.get(self.agent.current_user, limit=20)
            if hist:
                print("Recent commands:")
                for i, h in enumerate(hist):
                    print(f"  {i+1}. {h['command'][:60]}")
            else:
                print("No command history")
            return
        
        if user_input.startswith("history search "):
            query = user_input[15:].strip()
            results = self.agent.history.search(self.agent.current_user, query)
            if results:
                print(f"Found {len(results)} matches:")
                for r in results:
                    print(f"  - {r['command'][:60]}")
            else:
                print("No matches found")
            return
        
        if user_input == "users":
            users = self.agent.auth.list_users()
            print("Users:")
            for u in users:
                admin = " (admin)" if u["is_admin"] else ""
                print(f"  {u['username']}{admin} - last login: {u['last_login'] or 'never'}")
            return
        
        if user_input.startswith("user add "):
            import shlex
            parts = shlex.split(user_input[9:])
            if len(parts) >= 2:
                username, password = parts[0], parts[1]
                email = parts[2] if len(parts) > 2 else None
                success, msg = self.agent.auth.register(username, password, email)
                print(msg)
            else:
                print("Usage: user add <username> <password> [email]")
            return
        
        if user_input.startswith("user delete "):
            username = user_input[12:].strip()
            if username == self.agent.current_user:
                print("Cannot delete yourself")
                return
            success, msg = self.agent.auth.delete_user(username)
            print(msg)
            return
        
        if user_input.startswith("user settings "):
            parts = user_input[14:].split()
            if parts:
                username = parts[0]
                settings = self.agent.auth.get_user_settings(username)
                if settings:
                    print(f"Settings for {username}:")
                    print(json.dumps(settings, indent=2))
                else:
                    print(f"User not found: {username}")
            else:
                print("Usage: user settings <username>")
            return
        
        if user_input.startswith("logout"):
            if self.agent.session_token:
                self.agent.auth.logout(self.agent.session_token)
            print("Logged out. Closing session...")
            self.agent.running = False
            return
        
        if user_input == "plugins":
            plugins = self.agent.plugins.list_plugins()
            if plugins:
                print("Loaded plugins:")
                for p in plugins:
                    print(f"  - {p['name']} v{p['version']}: {p['description']}")
            else:
                print("No plugins loaded")
            return
        
        if user_input.startswith("plugin "):
            parts = user_input[7:].split(maxsplit=1)
            if len(parts) > 1:
                plugin_name, args = parts
                result = self.agent.plugins.execute_plugin(plugin_name, args)
                print(result)
            else:
                print(f"Available plugins: {', '.join(self.agent.plugins.list_plugins().keys())}")
            return
        
        if user_input == "db stats":
            stats = self.agent.db.get_stats()
            print("Database Stats:")
            for k, v in stats.items():
                print(f"  {k}: {v}")
            return
        
        if user_input.startswith("db search "):
            query = user_input[10:].strip()
            results = self.agent.db.search_memories(query)
            if results:
                print(f"Found {len(results)} results:")
                for r in results:
                    print(f"  - {r['content'][:60]}...")
            else:
                print("No results found")
            return
        
        if user_input == "notifications":
            stats = self.agent.notifications.get_stats()
            print("Notifications:")
            print(f"  Total: {stats['total']}")
            print(f"  Unread: {stats['unread']}")
            print(f"  Muted: {', '.join(stats['muted']) or 'none'}")
            return
        
        if user_input.startswith("notify "):
            msg = user_input[7:].strip()
            self.agent.notifications.info(msg, self.agent.current_user or "user")
            print(f"Notified: {msg}")
            return
        
        if user_input == "export":
            filepath = self.agent.export_import.export_all()
            print(f"Exported to: {filepath}")
            return
        
        if user_input.startswith("export memories"):
            parts = user_input.split(maxsplit=2)
            filepath = parts[2] if len(parts) > 2 else "memories_export.json"
            print(self.agent.export_import.export_memories(filepath))
            return
        
        if user_input.startswith("import "):
            filepath = user_input[7:].strip()
            print(self.agent.export_import.import_all(filepath))
            return
        
        if user_input == "prompts":
            templates = self.agent.prompts.list_templates()
            print("Available prompts:")
            for t in templates:
                print(f"  - {t['name']}: {t['description']}")
                if t['variables']:
                    print(f"    Variables: {', '.join(t['variables'])}")
            return
        
        if user_input.startswith("prompt "):
            parts = user_input[7:].split(maxsplit=1)
            if len(parts) > 1:
                name, rest = parts
                try:
                    kwargs = dict(item.split("=", 1) for item in rest.split(" --") if "=" in item)
                    result = self.agent.prompts.render_template(name, **kwargs)
                    print(result)
                except:
                    print("Usage: prompt <name> var1=value --var2=value")
            else:
                print(f"Available: {', '.join(self.agent.prompts.list_templates().keys())}")
            return
        
        if user_input.startswith("watch "):
            path = user_input[6:].strip()
            result = self.agent.file_watcher.watch(path)
            print(result)
            return
        
        if user_input == "watching":
            watched = self.agent.file_watcher.list_watched()
            if watched:
                print("Watching:")
                for w in watched:
                    print(f"  - {w['path']} (recursive: {w['recursive']})")
            else:
                print("Not watching any paths")
            return
        
        if user_input.startswith("unwatch "):
            path = user_input[8:].strip()
            print(self.agent.file_watcher.unwatch(path))
            return
        
        if user_input.startswith("api key "):
            parts = user_input[8:].split(maxsplit=2)
            if len(parts) > 1:
                action, key = parts[0], parts[1]
                if action == "add":
                    name = parts[2] if len(parts) > 2 else None
                    print(self.agent.api_keys.add_key(key, name))
                elif action == "remove":
                    print(self.agent.api_keys.remove_key(key))
            else:
                print("Usage: api key add <service> <key> [name]")
            return
        
        if user_input == "api keys":
            keys = self.agent.api_keys.list_services()
            print("API Keys:")
            for k in keys:
                print(f"  - {k['service']} ({k['name']}) - {'active' if k['active'] else 'inactive'}")
            return
        
        if user_input == "bluetooth":
            print(self.agent.bluetooth.status())
            return
        
        if user_input == "bluetooth scan":
            result = self.agent.bluetooth.scan()
            print(result)
            return
        
        if user_input == "bluetooth devices":
            print(self.agent.bluetooth.devices())
            return
        
        if user_input == "bluetooth paired":
            print(self.agent.bluetooth.paired())
            return
        
        if user_input == "bluetooth connected":
            print(self.agent.bluetooth.connected())
            return
        
        if user_input.startswith("bluetooth pair "):
            mac = user_input[14:].strip()
            print(self.agent.bluetooth.pair(mac))
            return
        
        if user_input.startswith("bluetooth connect "):
            mac = user_input[17:].strip()
            print(self.agent.bluetooth.connect(mac))
            return
        
        if user_input.startswith("bluetooth disconnect "):
            mac = user_input[20:].strip()
            print(self.agent.bluetooth.disconnect(mac))
            return
        
        if user_input.startswith("bluetooth remove "):
            mac = user_input[16:].strip()
            print(self.agent.bluetooth.remove(mac))
            return
        
        if user_input.startswith("bluetooth power "):
            state = user_input[16:].strip().lower()
            print(self.agent.bluetooth.power(state == "on"))
            return
        
        if user_input.startswith("bluetooth send "):
            parts = user_input[14:].split(maxsplit=1)
            if len(parts) == 2:
                mac, filepath = parts
                print(self.agent.bluetooth.send_file(mac, filepath))
            else:
                print("Usage: bluetooth send <mac> <filepath>")
            return
        
        if user_input == "voice":
            status = "Listening" if self.agent.voice.listening else "Not listening"
            print(f"Voice: {status}")
            return
        
        if user_input == "voice devices":
            print(self.agent.voice.list_devices())
            return
        
        if user_input.startswith("voice record "):
            parts = user_input[13:].split()
            duration = int(parts[0]) if parts else 5
            output = parts[1] if len(parts) > 1 else "recording.wav"
            print(self.agent.voice.record(duration, output))
            return
        
        if user_input.startswith("voice play "):
            filepath = user_input[11:].strip()
            print(self.agent.voice.play(filepath))
            return
        
        if user_input.startswith("voice speak "):
            text = user_input[12:].strip()
            print(self.agent.voice.speak(text))
            return
        
        if user_input == "voice start":
            print(self.agent.voice.start_listening())
            return
        
        if user_input == "voice stop":
            print(self.agent.voice.stop_listening())
            return
        
        if user_input == "backup":
            path = self.agent.backup.create_backup()
            print(f"Backup created: {path}")
            return
        
        if user_input == "backup list":
            print(self.agent.backup.list_backups())
            return
        
        if user_input.startswith("backup restore "):
            name = user_input[15:].strip()
            print(self.agent.backup.restore(name))
            return
        
        if user_input.startswith("backup delete "):
            name = user_input[14:].strip()
            print(self.agent.backup.delete_backup(name))
            return
        
        if user_input == "backup clean":
            print(self.agent.backup.clean_old_backups())
            return
        
        if user_input == "hostname":
            print(self.agent.utils.hostname())
            return
        
        if user_input == "ip":
            print(self.agent.utils.ip_address())
            return
        
        if user_input == "network":
            print(self.agent.utils.network_status())
            return
        
        if user_input == "disk":
            print(self.agent.utils.disk_usage())
            return
        
        if user_input == "top":
            print(self.agent.utils.processes())
            return
        
        if user_input == "battery":
            print(self.agent.utils.battery())
            return
        
        if user_input == "temp":
            print(self.agent.utils.temperature())
            return
        
        if user_input.startswith("analyze "):
            filepath = user_input[8:].strip()
            result = self.agent.code_analyzer.analyze_file(filepath)
            if isinstance(result, dict):
                print(f"Analysis of {result.get('file', filepath)}:")
                print(f"  Language: {result.get('language', 'Unknown')}")
                print(f"  Lines: {result.get('lines', 'N/A')}")
                print(f"  Classes: {result.get('classes', 0)}")
                print(f"  Functions: {result.get('functions', 0)}")
                if result.get('complexity'):
                    print(f"  Complexity: {result.get('complexity')}")
            else:
                print(result)
            return
        
        if user_input.startswith("issues "):
            filepath = user_input[7:].strip()
            issues = self.agent.code_analyzer.find_issues(filepath)
            if issues:
                print("Issues found:")
                for i in issues:
                    print(f"  [{i['severity']}] {i['message']}")
            else:
                print("No issues found")
            return
        
        if user_input.startswith("lint "):
            filepath = user_input[5:].strip()
            results = self.agent.linter.lint(filepath)
            for r in results:
                print(f"  [{r.get('severity', 'info')}] {r.get('message', '')}")
            return
        
        if user_input.startswith("gen "):
            parts = user_input[4:].split(maxsplit=1)
            if len(parts) > 1:
                template = parts[0]
                params = parts[1] if len(parts) > 1 else ""
                print(self.agent.code_generator.generate(template, **{"params": params}))
            else:
                templates = self.agent.code_generator.list_templates()
                print(f"Available templates: {', '.join(templates)}")
            return
        
        if user_input.startswith("genfile "):
            parts = user_input[8:].split(maxsplit=2)
            if len(parts) >= 2:
                filepath, template = parts[0], parts[1]
                kwargs = {}
                if len(parts) > 2:
                    for arg in parts[2].split(" --"):
                        if "=" in arg:
                            k, v = arg.split("=", 1)
                            kwargs[k.strip()] = v.strip()
                print(self.agent.code_generator.generate_file(filepath, template, **kwargs))
            else:
                print("Usage: genfile  <template> [var=value ...]")
            return
        
        if user_input.startswith("gentest "):
            filepath = user_input[9:].strip()
            print(self.agent.test_gen.generate_tests(filepath))
            return
        
        if user_input == "deps":
            deps = self.agent.deps.analyze_dependencies()
            print("Dependencies:")
            for lang, dep_list in deps.items():
                print(f"  {lang}: {len(dep_list) if isinstance(dep_list, list) else 'found'}")
            return
        
        if user_input == "deps outdated":
            outdated = self.agent.deps.check_outdated()
            for item in outdated:
                print(item)
            return
        
        if user_input == "git status":
            print(self.agent.git.status())
            return
        
        if user_input == "git log":
            print(self.agent.git.log())
            return
        
        if user_input.startswith("git commit "):
            message = user_input[11:].strip()
            print(self.agent.git.commit(message))
            return
        
        if user_input == "git diff":
            print(self.agent.git.diff())
            return
        
        if user_input.startswith("git add "):
            files = user_input[8:].strip().split()
            print(self.agent.git.add(files if files else ["."]))
            return
        
        if user_input == "git branch":
            print(self.agent.git.branch("list"))
            return
        
        if user_input.startswith("git checkout "):
            branch = user_input[13:].strip()
            print(self.agent.git.branch("checkout", branch))
            return
        
        if user_input.startswith("git push"):
            parts = user_input.split()
            remote = parts[2] if len(parts) > 2 else "origin"
            branch = parts[3] if len(parts) > 3 else None
            print(self.agent.git.push(remote, branch))
            return
        
        if user_input.startswith("git pull"):
            parts = user_input.split()
            remote = parts[2] if len(parts) > 2 else "origin"
            branch = parts[3] if len(parts) > 3 else None
            print(self.agent.git.pull(remote, branch))
            return
        
        if user_input == "build":
            info = self.agent.build.get_project_info()
            print(f"Project type: {info['type']}")
            result = self.agent.build.build()
            print(result)
            return
        
        if user_input.startswith("build "):
            target = user_input[6:].strip()
            result = self.agent.build.build(target=target)
            print(result)
            return
        
        if user_input == "build clean":
            print(self.agent.build.clean())
            return
        
        if user_input == "project info":
            print(json.dumps(self.agent.build.get_project_info(), indent=2))
            return
        
        if user_input == "docker ps":
            print(self.agent.containers.list_containers())
            return
        
        if user_input == "docker images":
            print(self.agent.containers.list_images())
            return
        
        if user_input.startswith("docker start "):
            name = user_input[13:].strip()
            print(self.agent.containers.start_container(name))
            return
        
        if user_input.startswith("docker stop "):
            name = user_input[12:].strip()
            print(self.agent.containers.stop_container(name))
            return
        
        response = self.agent.core.query(user_input)
        print(f"Agent> {response}")