"""
Memory service — lightweight file-based replacement for the broken `hindsight` package.
Stores memories as JSON lines under data/memories/, one file per query.
"""
import os
import json

SERVICE_DIR = os.path.dirname(os.path.abspath(__file__))
MEM_PATH = os.path.join(SERVICE_DIR, "..", "..", "data", "memories")
os.makedirs(MEM_PATH, exist_ok=True)

_MEM_FILE = os.path.join(MEM_PATH, "memories.jsonl")
_memories: list[str] = []

def _load():
    global _memories
    if not _memories and os.path.exists(_MEM_FILE):
        with open(_MEM_FILE, "r", encoding="utf-8") as f:
            _memories = [line.strip() for line in f if line.strip()]

def retain_memory(text: str):
    """Store a fact or interaction."""
    try:
        _load()
        _memories.append(text)
        with open(_MEM_FILE, "a", encoding="utf-8") as f:
            f.write(text.replace("\n", " ") + "\n")
    except Exception as e:
        print(f"Memory Retain Error: {e}")

def recall_memories(query: str) -> list[str]:
    """Return memories that contain any of the query words."""
    try:
        _load()
        words = set(query.lower().split())
        results = [m for m in _memories if any(w in m.lower() for w in words)]
        return results[-10:]  # return at most last 10 relevant memories
    except Exception as e:
        print(f"Memory Recall Error: {e}")
        return []

def reflect_memories():
    """No-op for compatibility."""
    pass
