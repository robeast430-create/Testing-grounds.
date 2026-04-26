#!/usr/bin/env python3
import sys
import argparse
import os
import json
import subprocess

def main():
    from neural_agent.auth import AuthManager, LoginInterface
    from neural_agent import NeuralAgent
    from neural_agent.api.api_server import APIServer
    
    parser = argparse.ArgumentParser(
        description="Neural Agent - Advanced AI with memory and autonomy",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  neural-agent              Start the agent with login
  neural-agent --no-auth    Start without authentication
  neural-agent --web        Start with web dashboard
  neural-agent --port 9000  Start on port 9000
  neural-agent user add      User management
  neural-agent user list     List users
        """
    )
    
    parser.add_argument("--no-auth", action="store_true", help="Skip authentication")
    parser.add_argument("--web", action="store_true", help="Enable web dashboard")
    parser.add_argument("--port", type=int, default=8080, help="Web server port (default: 8080)")
    parser.add_argument("--config", type=str, default="config.json", help="Config file")
    parser.add_argument("--data-dir", type=str, default="./auth_data", help="Data directory")
    parser.add_argument("command", nargs="?", help="Command")
    parser.add_argument("subcommand", nargs="?", help="Subcommand")
    parser.add_argument("args", nargs="*", help="Additional arguments")
    
    args = parser.parse_args()
    
    # USER MANAGEMENT
    if args.command == "user":
        auth = AuthManager(args.data_dir)
        if args.subcommand == "add":
            if len(args.args) < 2:
                print("Usage: neural-agent user add <username> <password> [email]")
                return 1
            username, password = args.args[0], args.args[1]
            email = args.args[2] if len(args.args) > 2 else None
            success, msg = auth.register(username, password, email)
            print(msg)
            return 0 if success else 1
        elif args.subcommand == "list":
            users = auth.list_users()
            for u in users:
                admin = " (admin)" if u["is_admin"] else ""
                print(f"{u['username']}{admin}")
            return 0
        elif args.subcommand == "delete":
            if not args.args:
                print("Usage: neural-agent user delete <username>")
                return 1
            success, msg = auth.delete_user(args.args[0])
            print(msg)
            return 0 if success else 1
        elif args.subcommand == "passwd":
            if len(args.args) < 2:
                print("Usage: neural-agent user passwd <username> <newpassword>")
                return 1
            success, msg = auth.change_password(args.args[0], args.args[1])
            print(msg)
            return 0 if success else 1
        else:
            print("User commands: add, list, delete, passwd")
            return 1
    
    # WEB COMMANDS
    elif args.command == "web" or args.command == "search":
        if args.command == "search" or args.subcommand == "search":
            query = " ".join(args.args) if args.args else ""
            agent = NeuralAgent(args.config)
            results = agent.web.search(query)
            for r in results[:10]:
                print(f"  {r.get('title', 'N/A')}")
                print(f"  {r.get('url', '')}")
                print()
            return 0
        elif args.subcommand == "crawl":
            url = args.args[0] if args.args else ""
            agent = NeuralAgent(args.config)
            result = agent.web.crawl(url)
            print(f"Crawled: {result.get('pages', 0)} pages")
            return 0
        elif args.subcommand == "fetch":
            url = args.args[0] if args.args else ""
            agent = NeuralAgent(args.config)
            content = agent.web.summarize_page(url)
            print(content[:2000])
            return 0
        elif args.subcommand == "scrape":
            url = args.args[0] if args.args else ""
            agent = NeuralAgent(args.config)
            data = agent.web.scrape_page(url)
            print(json.dumps(data, indent=2)[:2000])
            return 0
        elif args.subcommand == "links":
            url = args.args[0] if args.args else ""
            agent = NeuralAgent(args.config)
            links = agent.web.get_links(url)
            for link in links[:20]:
                print(f"  {link}")
            return 0
        else:
            agent = NeuralAgent(args.config)
            api = APIServer(agent, args.port)
            print(f"Starting web server on port {args.port}...")
            api.start()
            print("Press Ctrl+C to stop")
            try:
                import time
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                api.stop()
            return 0
    
    # MEMORY COMMANDS
    elif args.command == "memory" or args.command == "learn":
        agent = NeuralAgent(args.config)
        if args.subcommand == "add" or args.command == "learn":
            content = " ".join(args.args)
            agent.memory.add(content, "cli")
            print(f"Added to memory: {len(content)} chars")
            return 0
        elif args.subcommand == "recall" or args.subcommand == "search":
            query = " ".join(args.args)
            results = agent.memory.recall(query)
            for r in results[:10]:
                print(f"[{r[1]:.2f}] {r[0][:100]}...")
            return 0
        elif args.subcommand == "clear":
            agent.memory.clear()
            print("Memory cleared")
            return 0
        elif args.subcommand == "stats":
            print(f"Memory items: {agent.memory.count()}")
            return 0
        elif args.subcommand == "export":
            out = args.args[0] if args.args else "memory.json"
            data = agent.memory.export()
            with open(out, 'w') as f:
                json.dump(data, f, indent=2)
            print(f"Exported to {out}")
            return 0
        else:
            print("Memory commands: add, recall, clear, stats, export")
            return 1
    
    # TASK COMMANDS
    elif args.command == "task":
        agent = NeuralAgent(args.config)
        if args.subcommand == "do" or args.subcommand == "add":
            task = " ".join(args.args)
            task_id = agent.tasks.execute(task)
            print(f"Task queued: {task_id}")
            return 0
        elif args.subcommand == "list":
            tasks = agent.tasks.list_tasks()
            for t in tasks:
                print(f"[{t.get('status', '?'):10}] {t.get('description', 'Task')}")
            return 0
        elif args.subcommand == "cancel":
            task_id = args.args[0] if args.args else ""
            agent.tasks.cancel(task_id)
            print(f"Task cancelled: {task_id}")
            return 0
        elif args.subcommand == "status":
            task_id = args.args[0] if args.args else ""
            status = agent.tasks.get_status(task_id)
            print(f"Task {task_id}: {status}")
            return 0
        else:
            print("Task commands: do, list, cancel, status")
            return 1
    
    # FILE COMMANDS
    elif args.command == "file" or args.command == "files":
        agent = NeuralAgent(args.config)
        if args.subcommand == "list" or args.subcommand == "ls":
            path = args.args[0] if args.args else "."
            files = agent.files.list_files(path)
            for f in files:
                print(f)
            return 0
        elif args.subcommand == "read" or args.subcommand == "cat":
            path = args.args[0] if args.args else ""
            content = agent.files.read_file(path)
            print(content[:2000])
            return 0
        elif args.subcommand == "write":
            if len(args.args) < 2:
                print("Usage: neural-agent files write <path> <content>")
                return 1
            path, content = args.args[0], " ".join(args.args[1:])
            agent.files.write_file(path, content)
            print(f"Written to {path}")
            return 0
        elif args.subcommand == "mkdir":
            path = args.args[0] if args.args else ""
            agent.files.make_dir(path)
            print(f"Created directory: {path}")
            return 0
        elif args.subcommand == "delete" or args.subcommand == "rm":
            path = args.args[0] if args.args else ""
            agent.files.delete(path)
            print(f"Deleted: {path}")
            return 0
        elif args.subcommand == "copy" or args.subcommand == "cp":
            if len(args.args) < 2:
                print("Usage: neural-agent files copy <src> <dest>")
                return 1
            agent.files.copy(args.args[0], args.args[1])
            print(f"Copied {args.args[0]} to {args.args[1]}")
            return 0
        elif args.subcommand == "move" or args.subcommand == "mv":
            if len(args.args) < 2:
                print("Usage: neural-agent files move <src> <dest>")
                return 1
            agent.files.move(args.args[0], args.args[1])
            print(f"Moved {args.args[0]} to {args.args[1]}")
            return 0
        else:
            print("File commands: list, read, write, mkdir, delete, copy, move")
            return 1
    
    # NETWORK COMMANDS
    elif args.command == "network" or args.command == "net":
        if args.subcommand == "ping":
            host = args.args[0] if args.args else "google.com"
            result = subprocess.run(["ping", "-c", "3", host], capture_output=True, text=True)
            print(result.stdout or result.stderr)
            return 0
        elif args.subcommand == "curl" or args.subcommand == "http":
            url = args.args[0] if args.args else ""
            agent = NeuralAgent(args.config)
            result = agent.http.get(url)
            print(result[:2000])
            return 0
        elif args.subcommand == "dns":
            host = args.args[0] if args.args else ""
            result = subprocess.run(["nslookup", host], capture_output=True, text=True)
            print(result.stdout or result.stderr)
            return 0
        elif args.subcommand == "ports":
            host = args.args[0] if args.args else "localhost"
            agent = NeuralAgent(args.config)
            open_ports = agent.scanner.scan(host)
            print(f"Open ports on {host}:")
            for port in open_ports:
                print(f"  {port}")
            return 0
        elif args.subcommand == "ssl":
            host = args.args[0] if args.args else ""
            agent = NeuralAgent(args.config)
            info = agent.ssl.check_ssl(host)
            print(json.dumps(info, indent=2))
            return 0
        elif args.subcommand == "speedtest":
            print("Running speed test...")
            result = subprocess.run(["speedtest-cli"], capture_output=True, text=True)
            print(result.stdout or result.stderr)
            return 0
        else:
            print("Network commands: ping, curl, dns, ports, ssl, speedtest")
            return 1
    
    # SECURITY COMMANDS
    elif args.command == "security" or args.command == "sec":
        if args.subcommand == "hash":
            text = " ".join(args.args)
            from neural_agent.security.hashing import hash_text
            print(f"SHA256: {hash_text(text)}")
            return 0
        elif args.subcommand == "encode":
            text = " ".join(args.args)
            import base64
            print(f"Base64: {base64.b64encode(text.encode()).decode()}")
            return 0
        elif args.subcommand == "decode":
            text = args.args[0] if args.args else ""
            import base64
            print(base64.b64decode(text.encode()).decode())
            return 0
        elif args.subcommand == "password":
            length = int(args.args[0]) if args.args else 16
            agent = NeuralAgent(args.config)
            pwd = agent.security.generate_password(length)
            print(f"Generated: {pwd}")
            return 0
        elif args.subcommand == "scan":
            host = args.args[0] if args.args else "localhost"
            agent = NeuralAgent(args.config)
            vulns = agent.security.scan_vulnerabilities(host)
            print(json.dumps(vulns, indent=2))
            return 0
        else:
            print("Security commands: hash, encode, decode, password, scan")
            return 1
    
    # DATABASE COMMANDS
    elif args.command == "db" or args.command == "database":
        if args.subcommand == "query" or args.subcommand == "sql":
            query = " ".join(args.args)
            agent = NeuralAgent(args.config)
            results = agent.sql.execute(query)
            for row in results[:20]:
                print(row)
            return 0
        elif args.subcommand == "tables":
            agent = NeuralAgent(args.config)
            tables = agent.sql.list_tables()
            for t in tables:
                print(f"  {t}")
            return 0
        elif args.subcommand == "backup":
            out = args.args[0] if args.args else "backup.db"
            agent = NeuralAgent(args.config)
            agent.db.backup(out)
            print(f"Backup saved to {out}")
            return 0
        elif args.subcommand == "cache":
            if args.args:
                key = args.args[0]
                value = " ".join(args.args[1:]) if len(args.args) > 1 else ""
                agent = NeuralAgent(args.config)
                agent.cache.set(key, value)
                print(f"Cached: {key}")
            else:
                agent = NeuralAgent(args.config)
                print(f"Cache size: {agent.cache.size()}")
            return 0
        else:
            print("Database commands: query, tables, backup, cache")
            return 1
    
    # GIT COMMANDS
    elif args.command == "git":
        if args.subcommand == "init":
            path = args.args[0] if args.args else "."
            agent = NeuralAgent(args.config)
            agent.git.init(path)
            print(f"Initialized git in {path}")
            return 0
        elif args.subcommand == "commit":
            msg = " ".join(args.args)
            agent = NeuralAgent(args.config)
            agent.git.commit(msg)
            print(f"Committed: {msg}")
            return 0
        elif args.subcommand == "push":
            agent = NeuralAgent(args.config)
            agent.git.push()
            print("Pushed to remote")
            return 0
        elif args.subcommand == "pull":
            agent = NeuralAgent(args.config)
            agent.git.pull()
            print("Pulled from remote")
            return 0
        elif args.subcommand == "status":
            agent = NeuralAgent(args.config)
            status = agent.git.status()
            print(json.dumps(status, indent=2))
            return 0
        elif args.subcommand == "log":
            agent = NeuralAgent(args.config)
            commits = agent.git.log()
            for c in commits[:10]:
                print(f"  {c}")
            return 0
        elif args.subcommand == "branch":
            agent = NeuralAgent(args.config)
            branches = agent.git.branch()
            for b in branches:
                print(f"  {b}")
            return 0
        else:
            print("Git commands: init, commit, push, pull, status, log, branch")
            return 1
    
    # CODE ANALYSIS COMMANDS
    elif args.command == "code":
        if args.subcommand == "analyze":
            path = args.args[0] if args.args else "."
            agent = NeuralAgent(args.config)
            result = agent.code_analyzer.analyze(path)
            print(json.dumps(result, indent=2))
            return 0
        elif args.subcommand == "lint":
            path = args.args[0] if args.args else "."
            agent = NeuralAgent(args.config)
            issues = agent.linter.lint(path)
            for issue in issues:
                print(f"  {issue}")
            return 0
        elif args.subcommand == "test":
            path = args.args[0] if args.args else "."
            agent = NeuralAgent(args.config)
            tests = agent.test_gen.generate(path)
            print(f"Generated {len(tests)} tests")
            return 0
        elif args.subcommand == "deps":
            path = args.args[0] if args.args else "."
            agent = NeuralAgent(args.config)
            deps = agent.deps.analyze(path)
            print(json.dumps(deps, indent=2))
            return 0
        elif args.subcommand == "generate":
            lang = args.args[0] if args.args else "python"
            name = " ".join(args.args[1:]) if len(args.args) > 1 else "sample"
            agent = NeuralAgent(args.config)
            code = agent.code_generator.generate(lang, name)
            print(code[:2000])
            return 0
        else:
            print("Code commands: analyze, lint, test, deps, generate")
            return 1
    
    # CONTAINER COMMANDS
    elif args.command == "docker" or args.command == "container":
        if args.subcommand == "build":
            tag = args.args[0] if args.args else "neural-agent:latest"
            agent = NeuralAgent(args.config)
            result = agent.containers.build(tag)
            print(f"Built: {result}")
            return 0
        elif args.subcommand == "run":
            image = args.args[0] if args.args else "neural-agent:latest"
            agent = NeuralAgent(args.config)
            agent.containers.run(image)
            print(f"Running: {image}")
            return 0
        elif args.subcommand == "ps":
            result = subprocess.run(["docker", "ps"], capture_output=True, text=True)
            print(result.stdout)
            return 0
        elif args.subcommand == "images":
            result = subprocess.run(["docker", "images"], capture_output=True, text=True)
            print(result.stdout)
            return 0
        elif args.subcommand == "stop":
            name = args.args[0] if args.args else ""
            subprocess.run(["docker", "stop", name])
            print(f"Stopped: {name}")
            return 0
        else:
            print("Docker commands: build, run, ps, images, stop")
            return 1
    
    # MONITORING COMMANDS
    elif args.command == "monitor" or args.command == "stats":
        agent = NeuralAgent(args.config)
        if args.subcommand == "cpu":
            print(json.dumps(agent.monitor.get_cpu_usage(), indent=2))
        elif args.subcommand == "memory":
            print(json.dumps(agent.monitor.get_memory_usage(), indent=2))
        elif args.subcommand == "disk":
            print(json.dumps(agent.monitor.get_disk_usage(), indent=2))
        elif args.subcommand == "network":
            print(json.dumps(agent.monitor.get_network_stats(), indent=2))
        elif args.subcommand == "all" or args.subcommand == "sysinfo":
            print(json.dumps(agent.monitor.get_system_info(), indent=2))
        else:
            print(json.dumps(agent.monitor.get_stats(), indent=2))
        return 0
    
    # ALERT COMMANDS
    elif args.command == "alert":
        agent = NeuralAgent(args.config)
        if args.subcommand == "add":
            if len(args.args) < 2:
                print("Usage: neural-agent alert add <name> <condition>")
                return 1
            name, condition = args.args[0], " ".join(args.args[1:])
            agent.alerts.add(name, condition)
            print(f"Alert added: {name}")
            return 0
        elif args.subcommand == "list":
            alerts = agent.alerts.list()
            for a in alerts:
                print(f"  [{a.get('status', '?')}] {a.get('name', 'Alert')}")
            return 0
        elif args.subcommand == "check":
            agent.alerts.check_all()
            print("Alerts checked")
            return 0
        else:
            print("Alert commands: add, list, check")
            return 1
    
    # SCHEDULER COMMANDS
    elif args.command == "schedule":
        agent = NeuralAgent(args.config)
        if args.subcommand == "add":
            if len(args.args) < 2:
                print("Usage: neural-agent schedule add <interval> <command>")
                return 1
            interval, cmd = args.args[0], " ".join(args.args[1:])
            agent.scheduler.add_interval(interval, cmd)
            print(f"Scheduled: {cmd} every {interval}")
            return 0
        elif args.subcommand == "list":
            jobs = agent.scheduler.list()
            for j in jobs:
                print(f"  {j}")
            return 0
        elif args.subcommand == "clear":
            agent.scheduler.clear()
            print("Scheduler cleared")
            return 0
        else:
            print("Schedule commands: add, list, clear")
            return 1
    
    # BACKUP COMMANDS
    elif args.command == "backup":
        agent = NeuralAgent(args.config)
        if args.subcommand == "create":
            out = args.args[0] if args.args else "backup.tar.gz"
            agent.backup.create(out)
            print(f"Backup created: {out}")
            return 0
        elif args.subcommand == "restore":
            path = args.args[0] if args.args else "backup.tar.gz"
            agent.backup.restore(path)
            print(f"Restored from: {path}")
            return 0
        elif args.subcommand == "list":
            backups = agent.backup.list()
            for b in backups:
                print(f"  {b}")
            return 0
        else:
            print("Backup commands: create, restore, list")
            return 1
    
    # SIMULATION COMMANDS
    elif args.command == "sim":
        from neural_agent.simulation import SimulationManager, Simulation2D, Simulation3D, Simulation4D, Dimension
        import random
        manager = SimulationManager()
        
        if args.subcommand == "create":
            name = args.args[0] if args.args else "default_sim"
            dim = args.args[1] if len(args.args) > 1 else "3d"
            dim_map = {"2d": Dimension.DIM_2D, "3d": Dimension.DIM_3D, "4d": Dimension.DIM_4D}
            dimension = dim_map.get(dim.lower(), Dimension.DIM_3D)
            sim = manager.create_simulation(name, dimension)
            print(f"Created {dim} simulation: {name}")
            return 0
        elif args.subcommand == "list":
            for name in manager.list_simulations():
                print(f"  {name}")
            return 0
        elif args.subcommand == "add-particle":
            name = args.args[0] if args.args else "default_sim"
            sim = manager.get_simulation(name)
            if not sim:
                print(f"Simulation {name} not found")
                return 1
            for _ in range(50):
                if isinstance(sim, Simulation2D):
                    sim.add_particle(random.uniform(0, 800), random.uniform(0, 600),
                                    random.uniform(-2, 2), random.uniform(-2, 2))
                elif isinstance(sim, Simulation3D):
                    sim.add_particle(random.uniform(-50, 50), random.uniform(-50, 50),
                                    random.uniform(-50, 50), 0, 0, 0)
                elif isinstance(sim, Simulation4D):
                    sim.add_hyperparticle(random.uniform(-30, 30), random.uniform(-30, 30),
                                        random.uniform(-30, 30), random.uniform(-10, 10))
            print(f"Added particles to {name}")
            return 0
        elif args.subcommand == "step":
            name = args.args[0] if args.args else "default_sim"
            sim = manager.get_simulation(name)
            if not sim:
                print(f"Simulation {name} not found")
                return 1
            manager.step_all()
            print(f"Stepped {name}")
            return 0
        elif args.subcommand == "render":
            name = args.args[0] if args.args else "default_sim"
            sim = manager.get_simulation(name)
            if not sim:
                print(f"Simulation {name} not found")
                return 1
            html = manager.render(name)
            out_file = args.args[1] if len(args.args) > 1 else f"{name}.html"
            with open(out_file, 'w') as f:
                f.write(html)
            print(f"Rendered to {out_file}")
            return 0
        elif args.subcommand == "blender":
            name = args.args[0] if args.args else "default_sim"
            result = manager.export_blender(name, args.args[1] if len(args.args) > 1 else "/tmp/blender.png")
            if result.get("success"):
                print(f"Exported to Blender: {result}")
            else:
                print(f"Blender error: {result.get('error', 'Unknown')}")
            return 0
        else:
            print("Simulation commands: create, list, add-particle, step, render, blender")
            return 1
    
    # APK COMMANDS
    elif args.command == "apk":
        from neural_agent.deployment.build_apk import APKBuilder
        builder = APKBuilder(args.data_dir if args.data_dir != "./auth_data" else ".")
        
        if args.subcommand == "check":
            deps = builder.check_dependencies()
            print("\nDependency Status:")
            for name, available in deps.items():
                status = "OK" if available else "MISSING"
                print(f"  [{status}] {name}")
            if not all(deps.values()):
                print("\nRun 'neural-agent apk setup' to install dependencies")
            return 0
        elif args.subcommand == "setup":
            print("Setting up APK build environment...")
            builder.setup_environment()
            return 0
        elif args.subcommand == "build":
            print("Building debug APK...")
            result = builder.build_apk(debug=True)
            if result:
                print(f"APK built: {result}")
                return 0
            return 1
        elif args.subcommand == "full":
            print("Building full APK with all features...")
            result = builder.build_flexible_apk()
            if result:
                print(f"Full APK built: {result}")
                return 0
            return 1
        elif args.subcommand == "release":
            print("Building release APK...")
            result = builder.build_apk(debug=False)
            if result:
                print(f"Release APK built: {result}")
                return 0
            return 1
        elif args.subcommand == "all" or args.subcommand == "compile":
            print("="*50)
            print("NEURAL AGENT APK COMPILER")
            print("="*50)
            print("\n[1/4] Checking dependencies...")
            deps = builder.check_dependencies()
            for name, available in deps.items():
                print(f"  {'[OK]' if available else '[MISSING]'} {name}")
            
            print("\n[2/4] Setting up build environment...")
            builder.setup_environment()
            
            print("\n[3/4] Creating Kivy app with all features...")
            builder.create_spec_file()
            builder.prepare_source()
            print("  - Core neural agent")
            print("  - 2D/3D/4D simulations")
            print("  - Web/coding/network tools")
            print("  - Voice/bluetooth")
            print("  - Security utilities")
            
            print("\n[4/4] Building APK (this may take 10-30 minutes)...")
            result = builder.build_apk(debug=True)
            
            if result:
                print(f"\n{'='*50}")
                print(f"SUCCESS! APK built: {result}")
                print(f"{'='*50}")
                return 0
            else:
                print("\nBuild failed. Check errors above.")
                return 1
        else:
            print("APK commands: check, setup, build, full, release, all")
            return 1
    
    # KILL SWITCH
    elif args.command == "kill":
        agent = NeuralAgent(args.config)
        agent.kill_switch.trigger()
        print("KILL SWITCH ENGAGED!")
        return 0
    
    # START COMMAND
    elif args.command == "start" or args.command is None:
        if args.no_auth:
            username = "default"
            session_token = None
        else:
            auth = AuthManager(args.data_dir)
            login = LoginInterface(auth)
            session_token = login.authenticate()
            if session_token is None:
                print("Authentication required")
                return 1
            username = auth.verify_session(session_token)
        
        agent = NeuralAgent(args.config)
        agent.current_user = username
        agent.session_token = session_token
        
        api = None
        if args.web:
            api = APIServer(agent, args.port)
            api.start()
        
        print(f"\nWelcome, {username}! Starting Neural Agent...\n")
        agent.start()
        
        if api:
            api.stop()
        
        return 0
    
    print("Unknown command. Use 'neural-agent --help' for usage")
    print("""
Available commands:
  user        - User management (add, list, delete, passwd)
  web         - Web server or web commands (search, crawl, fetch, scrape)
  memory      - Memory management (add, recall, clear, stats, export)
  task        - Task management (do, list, cancel, status)
  files       - File operations (list, read, write, mkdir, delete, copy, move)
  network     - Network tools (ping, curl, dns, ports, ssl, speedtest)
  security    - Security tools (hash, encode, decode, password, scan)
  db          - Database commands (query, tables, backup, cache)
  git         - Git operations (init, commit, push, pull, status, log, branch)
  code        - Code analysis (analyze, lint, test, deps, generate)
  docker      - Docker commands (build, run, ps, images, stop)
  monitor     - System monitoring (cpu, memory, disk, network, sysinfo)
  alert       - Alert management (add, list, check)
  schedule    - Task scheduling (add, list, clear)
  backup      - Backup operations (create, restore, list)
  sim         - Simulations (create, list, add-particle, step, render, blender)
  apk         - APK building (check, setup, build, full, release, all)
  kill        - Trigger kill switch
  start       - Start Neural Agent
    """)
    return 1

if __name__ == "__main__":
    sys.exit(main())