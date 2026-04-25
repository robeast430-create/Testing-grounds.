import numpy as np
from sentence_transformers import SentenceTransformer
import json

class NeuralCore:
    def __init__(self, memory):
        self.memory = memory
        self.model = None
        self.embedding_cache = {}
        self.think_context = []

    def initialize(self):
        print("[NeuralCore] Loading embedding model...")
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        print("[NeuralCore] Model loaded.")

    def embed(self, text):
        if text in self.embedding_cache:
            return self.embedding_cache[text]
        vec = self.model.encode(text)
        self.embedding_cache[text] = vec
        return vec

    def similarity(self, text1, text2):
        e1, e2 = self.embed(text1), self.embed(text2)
        return float(np.dot(e1, e2) / (np.linalg.norm(e1) * np.linalg.norm(e2)))

    def think(self, context):
        self.think_context.append(context)
        if len(self.think_context) > 100:
            self.think_context.pop(0)
        
        related = self.memory.recall(context, top_k=5)
        
        response = self.compose_thought(context, related)
        return response

    def compose_thought(self, context, related_memories):
        thoughts = f"Analyzing: {context}\n"
        if related_memories:
            thoughts += "Related memories:\n"
            for mem, score in related_memories:
                thoughts += f"- {mem} ({score:.2f})\n"
        else:
            thoughts += "No related memories found.\n"
        
        thoughts += "\nI should consider how to respond based on what I know..."
        return thoughts

    def query(self, prompt):
        return self.think(prompt)