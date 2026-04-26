import json
import os
from datetime import datetime

class ConversationManager:
    def __init__(self, agent, db=None):
        self.agent = agent
        self.db = db
        self.current_session = None
        self.context = {}
        self.context_max_size = 1000
        self.sessions_file = "./auth_data/sessions.json"
        self._ensure_sessions_file()
    
    def _ensure_sessions_file(self):
        os.makedirs(os.path.dirname(self.sessions_file), exist_ok=True)
        if not os.path.exists(self.sessions_file):
            with open(self.sessions_file, "w") as f:
                json.dump({}, f)
    
    def create_session(self, session_id=None):
        if session_id is None:
            import secrets
            session_id = secrets.token_hex(16)
        
        self.current_session = session_id
        
        if self.db:
            pass
        
        return session_id
    
    def add_message(self, role, content, metadata=None):
        if not self.current_session:
            self.create_session()
        
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        }
        
        if self.db:
            self.db.insert_conversation(self.current_session, role, content, metadata)
        
        return message
    
    def get_conversation(self, session_id=None, limit=100):
        session = session_id or self.current_session
        if not session:
            return []
        
        if self.db:
            return self.db.get_conversation(session, limit)
        
        return []
    
    def get_context(self):
        return dict(self.context)
    
    def update_context(self, key, value):
        self.context[key] = value
        if len(self.context) > self.context_max_size:
            oldest = list(self.context.keys())[0]
            del self.context[oldest]
    
    def clear_context(self):
        self.context.clear()
    
    def export_conversation(self, session_id=None, filepath="conversation.json"):
        session = session_id or self.current_session
        if not session:
            return "No active session"
        
        messages = self.get_conversation(session)
        
        export_data = {
            "session_id": session,
            "exported_at": datetime.now().isoformat(),
            "messages": messages
        }
        
        with open(filepath, "w") as f:
            json.dump(export_data, f, indent=2)
        
        return f"Exported to {filepath}"
    
    def import_conversation(self, filepath):
        if not os.path.exists(filepath):
            return f"File not found: {filepath}"
        
        with open(filepath, "r") as f:
            data = json.load(f)
        
        session_id = data.get("session_id")
        messages = data.get("messages", [])
        
        if not session_id:
            return "Invalid file: no session_id"
        
        self.create_session(session_id)
        
        for msg in messages:
            self.add_message(msg["role"], msg["content"], msg.get("metadata"))
        
        return f"Imported {len(messages)} messages to session {session_id}"
    
    def list_sessions(self):
        with open(self.sessions_file, "r") as f:
            sessions = json.load(f)
        return sessions
    
    def get_or_create_context(self, topic):
        if topic not in self.context:
            self.context[topic] = {
                "created": datetime.now().isoformat(),
                "data": {}
            }
        return self.context[topic]
    
    def summarize_context(self):
        summary = {
            "session": self.current_session,
            "message_count": len(self.get_conversation()),
            "context_topics": list(self.context.keys()),
            "context_size": len(self.context)
        }
        return summary