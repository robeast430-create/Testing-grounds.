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
    parser.add_argument("command", nargs="?", help="Command (user, start, web)")
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