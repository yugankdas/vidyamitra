import os
from hindsight import Hindsight

# Initialize Hindsight with a persistent bank near the installation
SERVICE_DIR = os.path.dirname(os.path.abspath(__file__))
MEM_PATH = os.path.join(SERVICE_DIR, "..", "..", "data", "memories")
os.makedirs(MEM_PATH, exist_ok=True)

# Shared Hindsight instance
hs = Hindsight(path=MEM_PATH)

def retain_memory(text: str):
    """Store a fact or interaction in Hindsight."""
    try:
        hs.retain(text)
        # Immediate reflection to ensure indexing for same-session recall
        hs.reflect()
    except Exception as e:
        print(f"Hindsight Retain Error: {e}")

def recall_memories(query: str) -> list[str]:
    """Retrieve relevant memories for a query."""
    try:
        return hs.recall(query) or []
    except Exception as e:
        print(f"Hindsight Recall Error: {e}")
        return []

def reflect_memories():
    """Consolidate observations."""
    try:
        hs.reflect()
    except Exception as e:
        print(f"Hindsight Reflect Error: {e}")
