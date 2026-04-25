import chromadb
from chromadb.config import Settings
import json
import os
from datetime import datetime

class MemoryBank:
    def __init__(self):
        self.db_path = "./memory_db"
        os.makedirs(self.db_path, exist_ok=True)
        self.client = chromadb.PersistentClient(path=self.db_path)
        self.collection = self.client.get_or_create_collection("memories")
        self.metadata_file = os.path.join(self.db_path, "metadata.json")
        self.metadata = self._load_metadata()

    def _load_metadata(self):
        if os.path.exists(self.metadata_file):
            with open(self.metadata_file, "r") as f:
                return json.load(f)
        return {"memories": [], "last_id": 0}

    def _save_metadata(self):
        with open(self.metadata_file, "w") as f:
            json.dump(self.metadata, f)

    def load(self):
        print("[MemoryBank] Loaded {} memories.".format(len(self.metadata["memories"])))

    def save(self):
        self._save_metadata()
        print("[MemoryBank] Saved {} memories.".format(len(self.metadata["memories"])))

    def add(self, content, mem_type="general"):
        mem_id = str(self.metadata["last_id"] + 1)
        self.metadata["last_id"] += 1
        timestamp = datetime.now().isoformat()
        
        self.collection.add(
            documents=[content],
            ids=[mem_id],
            metadatas=[{"type": mem_type, "timestamp": timestamp}]
        )
        
        self.metadata["memories"].append({
            "id": mem_id,
            "content": content,
            "type": mem_type,
            "timestamp": timestamp
        })
        self._save_metadata()
        print(f"[MemoryBank] Added memory #{mem_id}")

    def recall(self, query, top_k=5):
        if self.collection.count() == 0:
            return []
        
        results = self.collection.query(
            query_texts=[query],
            n_results=min(top_k, self.collection.count())
        )
        
        memories = []
        if results["documents"] and results["documents"][0]:
            for doc, mid, meta in zip(
                results["documents"][0],
                results["ids"][0],
                results["metadatas"][0]
            ):
                memories.append((doc, 1.0))
        return memories

    def search(self, query, limit=10):
        return self.recall(query, top_k=limit)

    def count(self):
        return self.collection.count()

    def clear(self):
        self.client.delete_collection("memories")
        self.collection = self.client.get_or_create_collection("memories")
        self.metadata = {"memories": [], "last_id": 0}
        self._save_metadata()
        print("[MemoryBank] Cleared all memories.")