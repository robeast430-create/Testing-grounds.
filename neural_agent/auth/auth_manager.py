import hashlib
import secrets
import json
import os
from datetime import datetime, timedelta

class AuthManager:
    def __init__(self, data_dir="./auth_data"):
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
        self.users_file = os.path.join(data_dir, "users.json")
        self.sessions_file = os.path.join(data_dir, "sessions.json")
        self.users = self._load_users()
        self.sessions = self._load_sessions()
        self._cleanup_old_sessions()
    
    def _load_users(self):
        if os.path.exists(self.users_file):
            with open(self.users_file, "r") as f:
                return json.load(f)
        return {}
    
    def _save_users(self):
        with open(self.users_file, "w") as f:
            json.dump(self.users, f, indent=2)
    
    def _load_sessions(self):
        if os.path.exists(self.sessions_file):
            with open(self.sessions_file, "r") as f:
                return json.load(f)
        return {}
    
    def _save_sessions(self):
        with open(self.sessions_file, "w") as f:
            json.dump(self.sessions, f, indent=2)
    
    def _cleanup_old_sessions(self):
        now = datetime.now().isoformat()
        expired = [sid for sid, sess in self.sessions.items() if sess.get("expires_at", "") < now]
        for sid in expired:
            del self.sessions[sid]
        if expired:
            self._save_sessions()
    
    def _hash_password(self, password, salt=None):
        if salt is None:
            salt = secrets.token_hex(16)
        hash_obj = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 100000)
        return hash_obj.hex(), salt
    
    def _verify_password(self, password, hash_value, salt):
        computed_hash, _ = self._hash_password(password, salt)
        return computed_hash == hash_value
    
    def register(self, username, password, email=None):
        if username in self.users:
            return False, "Username already exists"
        
        if len(password) < 8:
            return False, "Password must be at least 8 characters"
        
        hash_value, salt = self._hash_password(password)
        
        self.users[username] = {
            "password_hash": hash_value,
            "salt": salt,
            "email": email,
            "created_at": datetime.now().isoformat(),
            "last_login": None,
            "is_admin": len(self.users) == 0,
            "settings": {
                "theme": "dark",
                "notifications": True,
                "timeout": 300
            }
        }
        self._save_users()
        return True, f"User '{username}' registered successfully"
    
    def login(self, username, password):
        if username not in self.users:
            return None, "Invalid username or password"
        
        user = self.users[username]
        if not self._verify_password(password, user["password_hash"], user["salt"]):
            return None, "Invalid username or password"
        
        session_token = secrets.token_hex(32)
        expires_at = (datetime.now() + timedelta(hours=24)).isoformat()
        
        self.sessions[session_token] = {
            "username": username,
            "created_at": datetime.now().isoformat(),
            "expires_at": expires_at,
            "ip_address": None
        }
        
        self.users[username]["last_login"] = datetime.now().isoformat()
        self._save_users()
        self._save_sessions()
        
        return session_token, "Login successful"
    
    def logout(self, session_token):
        if session_token in self.sessions:
            del self.sessions[session_token]
            self._save_sessions()
            return True
        return False
    
    def verify_session(self, session_token):
        if session_token not in self.sessions:
            return None
        
        session = self.sessions[session_token]
        expires_at = datetime.fromisoformat(session["expires_at"])
        
        if expires_at < datetime.now():
            del self.sessions[session_token]
            self._save_sessions()
            return None
        
        return session["username"]
    
    def change_password(self, username, old_password, new_password):
        if username not in self.users:
            return False, "User not found"
        
        user = self.users[username]
        if not self._verify_password(old_password, user["password_hash"], user["salt"]):
            return False, "Current password is incorrect"
        
        if len(new_password) < 8:
            return False, "New password must be at least 8 characters"
        
        hash_value, salt = self._hash_password(new_password)
        self.users[username]["password_hash"] = hash_value
        self.users[username]["salt"] = salt
        self._save_users()
        return True, "Password changed successfully"
    
    def delete_user(self, username):
        if username not in self.users:
            return False, "User not found"
        
        del self.users[username]
        self._save_users()
        
        expired_tokens = [sid for sid, sess in self.sessions.items() if sess["username"] == username]
        for sid in expired_tokens:
            del self.sessions[sid]
        self._save_sessions()
        
        return True, f"User '{username}' deleted"
    
    def list_users(self):
        return [{
            "username": username,
            "email": user.get("email"),
            "created_at": user["created_at"],
            "last_login": user.get("last_login"),
            "is_admin": user.get("is_admin", False)
        } for username, user in self.users.items()]
    
    def get_user_settings(self, username):
        if username in self.users:
            return self.users[username].get("settings", {})
        return None
    
    def update_user_settings(self, username, settings):
        if username in self.users:
            self.users[username]["settings"].update(settings)
            self._save_users()
            return True
        return False