import sqlite3
import json
import os
from datetime import datetime

class Database:
    def __init__(self, db_path="./data/agent.db"):
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.conn = None
        self._connect()
        self._init_tables()
    
    def _connect(self):
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
    
    def _init_tables(self):
        cursor = self.conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS memories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT NOT NULL,
                type TEXT DEFAULT 'general',
                embedding_id TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                accessed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                access_count INTEGER DEFAULT 0,
                tags TEXT
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT,
                role TEXT,
                content TEXT,
                metadata TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_type TEXT,
                data TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS key_value (
                key TEXT PRIMARY KEY,
                value TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS backups (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                backup_type TEXT,
                file_path TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_memories_type ON memories(type)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_memories_created ON memories(created_at)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_conversations_session ON conversations(session_id)")
        
        self.conn.commit()
    
    def insert_memory(self, content, mem_type="general", embedding_id=None, tags=None):
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO memories (content, type, embedding_id, tags) VALUES (?, ?, ?, ?)",
            (content, mem_type, embedding_id, json.dumps(tags) if tags else None)
        )
        self.conn.commit()
        return cursor.lastrowid
    
    def get_memory(self, memory_id):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM memories WHERE id = ?", (memory_id,))
        row = cursor.fetchone()
        if row:
            cursor.execute("UPDATE memories SET access_count = access_count + 1, accessed_at = CURRENT_TIMESTAMP WHERE id = ?", (memory_id,))
            self.conn.commit()
        return dict(row) if row else None
    
    def get_memories(self, limit=100, offset=0, mem_type=None):
        cursor = self.conn.cursor()
        if mem_type:
            cursor.execute("SELECT * FROM memories WHERE type = ? ORDER BY created_at DESC LIMIT ? OFFSET ?", 
                          (mem_type, limit, offset))
        else:
            cursor.execute("SELECT * FROM memories ORDER BY created_at DESC LIMIT ? OFFSET ?", 
                          (limit, offset))
        return [dict(row) for row in cursor.fetchall()]
    
    def delete_memory(self, memory_id):
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM memories WHERE id = ?", (memory_id,))
        self.conn.commit()
        return cursor.rowcount > 0
    
    def search_memories(self, query, limit=10):
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT * FROM memories WHERE content LIKE ? ORDER BY access_count DESC LIMIT ?",
            (f"%{query}%", limit)
        )
        return [dict(row) for row in cursor.fetchall()]
    
    def insert_conversation(self, session_id, role, content, metadata=None):
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO conversations (session_id, role, content, metadata) VALUES (?, ?, ?, ?)",
            (session_id, role, content, json.dumps(metadata) if metadata else None)
        )
        self.conn.commit()
        return cursor.lastrowid
    
    def get_conversation(self, session_id, limit=100):
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT * FROM conversations WHERE session_id = ? ORDER BY created_at DESC LIMIT ?",
            (session_id, limit)
        )
        return [dict(row) for row in cursor.fetchall()]
    
    def insert_event(self, event_type, data):
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO events (event_type, data) VALUES (?, ?)",
            (event_type, json.dumps(data) if isinstance(data, dict) else data)
        )
        self.conn.commit()
        return cursor.lastrowid
    
    def get_events(self, event_type=None, limit=100):
        cursor = self.conn.cursor()
        if event_type:
            cursor.execute(
                "SELECT * FROM events WHERE event_type = ? ORDER BY created_at DESC LIMIT ?",
                (event_type, limit)
            )
        else:
            cursor.execute("SELECT * FROM events ORDER BY created_at DESC LIMIT ?", (limit,))
        return [dict(row) for row in cursor.fetchall()]
    
    def set_value(self, key, value):
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT OR REPLACE INTO key_value (key, value, updated_at) VALUES (?, ?, CURRENT_TIMESTAMP)",
            (key, json.dumps(value) if isinstance(value, (dict, list)) else str(value))
        )
        self.conn.commit()
    
    def get_value(self, key):
        cursor = self.conn.cursor()
        cursor.execute("SELECT value FROM key_value WHERE key = ?", (key,))
        row = cursor.fetchone()
        if row:
            try:
                return json.loads(row["value"])
            except:
                return row["value"]
        return None
    
    def delete_value(self, key):
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM key_value WHERE key = ?", (key,))
        self.conn.commit()
        return cursor.rowcount > 0
    
    def record_backup(self, backup_type, file_path):
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO backups (backup_type, file_path) VALUES (?, ?)",
            (backup_type, file_path)
        )
        self.conn.commit()
        return cursor.lastrowid
    
    def get_stats(self):
        cursor = self.conn.cursor()
        stats = {}
        
        cursor.execute("SELECT COUNT(*) as count FROM memories")
        stats["total_memories"] = cursor.fetchone()["count"]
        
        cursor.execute("SELECT COUNT(*) as count FROM conversations")
        stats["total_conversations"] = cursor.fetchone()["count"]
        
        cursor.execute("SELECT COUNT(*) as count FROM events")
        stats["total_events"] = cursor.fetchone()["count"]
        
        cursor.execute("SELECT COUNT(*) as count FROM key_value")
        stats["total_keys"] = cursor.fetchone()["count"]
        
        cursor.execute("SELECT COUNT(*) as count FROM backups")
        stats["total_backups"] = cursor.fetchone()["count"]
        
        return stats
    
    def close(self):
        if self.conn:
            self.conn.close()
    
    def backup(self, backup_path):
        import shutil
        self.conn.close()
        shutil.copy2(self.db_path, backup_path)
        self._connect()
        self.record_backup("full", backup_path)
        return backup_path