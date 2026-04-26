import getpass
import sys

class LoginInterface:
    def __init__(self, auth_manager):
        self.auth = auth_manager
    
    def show_banner(self):
        print("""
╔══════════════════════════════════════════════════════════╗
║                                                          ║
║     ███╗   ██╗███████╗██╗  ██╗██╗   ██╗███████╗         ║
║     ████╗  ██║██╔════╝╚██╗██╔╝██║   ██║██╔════╝         ║
║     ██╔██╗ ██║█████╗   ╚███╔╝ ██║   ██║███████╗         ║
║     ██║╚██╗██║██╔══╝   ██╔██╗ ██║   ██║╚════██║         ║
║     ██║ ╚████║███████╗██╔╝ ╚██╗╚██████╔╝███████║         ║
║     ╚═╝  ╚═══╝╚══════╝╚═╝   ╚═╝ ╚═════╝ ╚══════╝         ║
║                         AGENT                            ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝
        """)
    
    def login(self):
        self.show_banner()
        print("                    Login")
        print("=" * 45)
        
        username = input("Username: ").strip()
        if not username:
            print("Username cannot be empty")
            return None
        
        password = getpass.getpass("Password: ")
        if not password:
            print("Password cannot be empty")
            return None
        
        token, message = self.auth.login(username, password)
        
        if token:
            print(f"\n{message} Welcome, {username}!")
            return token
        else:
            print(f"\nError: {message}")
            return None
    
    def register(self):
        print("\n" + "=" * 45)
        print("                 Create Account")
        print("=" * 45)
        
        username = input("Username: ").strip()
        if not username:
            print("Username cannot be empty")
            return None
        
        if username in self.auth.users:
            print("Username already exists")
            return None
        
        password = getpass.getpass("Password (min 8 chars): ")
        if len(password) < 8:
            print("Password must be at least 8 characters")
            return None
        
        confirm = getpass.getpass("Confirm Password: ")
        if password != confirm:
            print("Passwords do not match")
            return None
        
        email = input("Email (optional): ").strip() or None
        
        success, message = self.auth.register(username, password, email)
        
        if success:
            print(f"\n{message}")
            token, _ = self.auth.login(username, password)
            return token
        else:
            print(f"\nError: {message}")
            return None
    
    def show_menu(self):
        print("\n" + "=" * 45)
        print("1. Login")
        print("2. Create Account")
        print("3. Exit")
        print("=" * 45)
        
        choice = input("Select: ").strip()
        
        if choice == "1":
            return self.login()
        elif choice == "2":
            return self.register()
        else:
            return None
    
    def authenticate(self):
        if not self.auth.users:
            print("\nNo users found. Creating admin account...")
            return self.register()
        
        return self.show_menu()