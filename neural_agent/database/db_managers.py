import sqlite3
import json
import os
from datetime import datetime

class SQLManager:
    def __init__(self, data_dir="./data"):
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
        self.connections = {}
    
    def connect(self, db_name):
        db_path = os.path.join(self.data_dir, f"{db_name}.db")
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        self.connections[db_name] = conn
        return conn
    
    def disconnect(self, db_name):
        if db_name in self.connections:
            self.connections[db_name].close()
            del self.connections[db_name]
            return f"Disconnected from {db_name}"
        return f"Database {db_name} not connected"
    
    def execute(self, db_name, query, params=None):
        if db_name not in self.connections:
            self.connect(db_name)
        
        conn = self.connections[db_name]
        cursor = conn.cursor()
        
        try:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            if query.strip().upper().startswith("SELECT"):
                rows = cursor.fetchall()
                conn.commit()
                return [dict(row) for row in rows]
            else:
                conn.commit()
                return {"affected": cursor.rowcount}
        except Exception as e:
            conn.rollback()
            return {"error": str(e)}
    
    def create_table(self, db_name, table_name, columns):
        col_defs = ", ".join([f"{name} {dtype}" for name, dtype in columns.items()])
        query = f"CREATE TABLE IF NOT EXISTS {table_name} ({col_defs})"
        return self.execute(db_name, query)
    
    def insert(self, db_name, table, data):
        columns = list(data.keys())
        placeholders = ["?" for _ in columns]
        query = f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({', '.join(placeholders)})"
        return self.execute(db_name, query, list(data.values()))
    
    def select(self, db_name, table, where=None, limit=100):
        query = f"SELECT * FROM {table}"
        if where:
            query += f" WHERE {where}"
        query += f" LIMIT {limit}"
        return self.execute(db_name, query)
    
    def update(self, db_name, table, data, where):
        set_clause = ", ".join([f"{k} = ?" for k in data.keys()])
        query = f"UPDATE {table} SET {set_clause} WHERE {where}"
        return self.execute(db_name, query, list(data.values()))
    
    def delete(self, db_name, table, where):
        query = f"DELETE FROM {table} WHERE {where}"
        return self.execute(db_name, query)
    
    def list_tables(self, db_name):
        if db_name not in self.connections:
            self.connect(db_name)
        return self.execute(db_name, "SELECT name FROM sqlite_master WHERE type='table'")
    
    def drop_table(self, db_name, table):
        return self.execute(db_name, f"DROP TABLE IF EXISTS {table}")
    
    def dump(self, db_name):
        if db_name not in self.connections:
            self.connect(db_name)
        
        lines = []
        conn = self.connections[db_name]
        cursor = conn.cursor()
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        for table in tables:
            table_name = table[0]
            lines.append(f"-- Table: {table_name}")
            
            cursor.execute(f"SELECT sql FROM sqlite_master WHERE name='{table_name}'")
            lines.append(cursor.fetchone()[0] + ";")
            
            cursor.execute(f"SELECT * FROM {table_name}")
            rows = cursor.fetchall()
            for row in rows:
                vals = []
                for v in row:
                    if v is None:
                        vals.append("NULL")
                    elif isinstance(v, str):
                        vals.append(f"'{v.replace("'", "''")}'")
                    else:
                        vals.append(str(v))
                lines.append(f"INSERT INTO {table_name} VALUES ({', '.join(vals)});")
        
        return "\n".join(lines)


class QueryBuilder:
    def __init__(self):
        self.query_parts = []
        self.params = []
    
    def select(self, *columns):
        cols = ", ".join(columns) if columns else "*"
        self.query_parts.append(f"SELECT {cols}")
        return self
    
    def from_table(self, table):
        self.query_parts.append(f"FROM {table}")
        return self
    
    def where(self, condition, *params):
        self.query_parts.append(f"WHERE {condition}")
        self.params.extend(params)
        return self
    
    def and_where(self, condition, *params):
        self.query_parts.append(f"AND {condition}")
        self.params.extend(params)
        return self
    
    def or_where(self, condition, *params):
        self.query_parts.append(f"OR {condition}")
        self.params.extend(params)
        return self
    
    def order_by(self, column, direction="ASC"):
        self.query_parts.append(f"ORDER BY {column} {direction}")
        return self
    
    def limit(self, num):
        self.query_parts.append(f"LIMIT {num}")
        return self
    
    def join(self, table, condition, join_type="INNER"):
        self.query_parts.append(f"{join_type} JOIN {table} ON {condition}")
        return self
    
    def group_by(self, column):
        self.query_parts.append(f"GROUP BY {column}")
        return self
    
    def build(self):
        return " ".join(self.query_parts), self.params
    
    def reset(self):
        self.query_parts = []
        self.params = []
        return self


class DatabaseMigration:
    def __init__(self, db_manager, migrations_dir="./migrations"):
        self.db = db_manager
        self.migrations_dir = migrations_dir
        os.makedirs(migrations_dir, exist_ok=True)
    
    def create_migration(self, name):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_{name}.sql"
        filepath = os.path.join(self.migrations_dir, filename)
        
        with open(filepath, "w") as f:
            f.write(f"-- Migration: {name}\n-- Created: {datetime.now().isoformat()}\n\n")
        
        return filepath
    
    def list_migrations(self):
        if not os.path.exists(self.migrations_dir):
            return []
        return sorted(os.listdir(self.migrations_dir))
    
    def run_migration(self, db_name, filepath):
        with open(filepath, "r") as f:
            sql = f.read()
        
        statements = sql.split(";")
        results = []
        for stmt in statements:
            stmt = stmt.strip()
            if stmt and not stmt.startswith("--"):
                result = self.db.execute(db_name, stmt)
                results.append(result)
        
        return f"Ran migration: {os.path.basename(filepath)}"
    
    def rollback_migration(self, db_name, steps=1):
        migrations = self.list_migrations()
        rolled_back = []
        
        for _ in range(steps):
            if migrations:
                migration = migrations.pop()
                filepath = os.path.join(self.migrations_dir, migration)
                os.remove(filepath)
                rolled_back.append(migration)
        
        return f"Rolled back {len(rolled_back)} migrations"


class CacheManager:
    def __init__(self, cache_dir="./cache"):
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)
    
    def get(self, key, max_age=3600):
        filepath = os.path.join(self.cache_dir, f"{key}.json")
        
        if not os.path.exists(filepath):
            return None
        
        mtime = os.path.getmtime(filepath)
        age = datetime.now().timestamp() - mtime
        
        if age > max_age:
            os.remove(filepath)
            return None
        
        with open(filepath, "r") as f:
            return json.load(f)
    
    def set(self, key, value, ttl=3600):
        filepath = os.path.join(self.cache_dir, f"{key}.json")
        
        data = {
            "value": value,
            "created": datetime.now().isoformat(),
            "ttl": ttl
        }
        
        with open(filepath, "w") as f:
            json.dump(data, f)
        
        return True
    
    def delete(self, key):
        filepath = os.path.join(self.cache_dir, f"{key}.json")
        if os.path.exists(filepath):
            os.remove(filepath)
            return True
        return False
    
    def clear(self):
        count = 0
        for f in os.listdir(self.cache_dir):
            if f.endswith(".json"):
                os.remove(os.path.join(self.cache_dir, f))
                count += 1
        return f"Cleared {count} cache entries"
    
    def list_keys(self):
        return [f[:-5] for f in os.listdir(self.cache_dir) if f.endswith(".json")]


class RedisManager:
    def __init__(self, host="localhost", port=6379, db=0):
        self.host = host
        self.port = port
        self.db = db
        self._client = None
    
    def connect(self):
        try:
            import redis
            self._client = redis.Redis(host=self.host, port=self.port, db=self.db)
            return "Connected to Redis"
        except ImportError:
            return "redis-py not installed"
        except Exception as e:
            return f"Connection failed: {e}"
    
    def set(self, key, value, ttl=None):
        if not self._client:
            return "Not connected"
        try:
            if ttl:
                self._client.setex(key, ttl, json.dumps(value))
            else:
                self._client.set(key, json.dumps(value))
            return f"Set {key}"
        except Exception as e:
            return f"Error: {e}"
    
    def get(self, key):
        if not self._client:
            return None
        try:
            val = self._client.get(key)
            if val:
                return json.loads(val)
            return None
        except Exception as e:
            return f"Error: {e}"
    
    def delete(self, key):
        if not self._client:
            return "Not connected"
        return self._client.delete(key)
    
    def keys(self, pattern="*"):
        if not self._client:
            return []
        return [k.decode() if isinstance(k, bytes) else k for k in self._client.keys(pattern)]