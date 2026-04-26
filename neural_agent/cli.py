#!/usr/bin/env python3
import sys
import argparse
import os

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
    parser.add_argument("command", nargs="?", help="Command (user, start, web, sim)")
    parser.add_argument("subcommand", nargs="?", help="Subcommand")
    parser.add_argument("args", nargs="*", help="Additional arguments")
    
    args = parser.parse_args()
    
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
        else:
            print("User commands: add, list, delete")
            return 1
    
    if args.command == "sim":
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
    
    if args.command == "apk":
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
    
    if args.command == "web":
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
    
    if args.command == "start" or args.command is None:
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
    return 1

if __name__ == "__main__":
    sys.exit(main())