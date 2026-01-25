import redis

class RedisMemory:
    """
    Memory management class with Redis backend and RAM fallback.
    Stores conversation history per session for persistence across app restarts.
    """
    def __init__(self, host='localhost', port=6379, db=0):
        try:
            self.r = redis.Redis(host=host, port=port, db=db)
            self.r.ping()  # Test connection
            self.redis_available = True
            print("✅ Redis connecté - historique persistant disponible")
        except Exception:
            print("⚠️  Redis non disponible, utilisation de la mémoire en RAM.")
            self.redis_available = False
            self.memory = {}  # Fallback in-memory dict

    def add_message(self, session_id: str, role: str, content: str):
        """Add a message to the chat history for a specific session."""
        if self.redis_available:
            key = f"chat_history:{session_id}"
            self.r.rpush(key, f"{role}: {content}")
        else:
            if session_id not in self.memory:
                self.memory[session_id] = []
            self.memory[session_id].append(f"{role}: {content}")

    def get_history(self, session_id: str) -> list:
        """Retrieve the full chat history for a specific session."""
        if self.redis_available:
            key = f"chat_history:{session_id}"
            return [msg.decode('utf-8') for msg in self.r.lrange(key, 0, -1)]
        else:
            return self.memory.get(session_id, [])

    def clear_history(self, session_id: str):
        """Clear the chat history for a specific session."""
        if self.redis_available:
            key = f"chat_history:{session_id}"
            self.r.delete(key)
        else:
            if session_id in self.memory:
                self.memory[session_id] = []
    
    def set_entity(self, session_id: str, entity_type: str, value: str):
        """Store a personal entity (name, email, etc.) for a session."""
        if self.redis_available:
            key = f"entities:{session_id}"
            self.r.hset(key, entity_type, value)
        else:
            entities_key = f"entities:{session_id}"
            if entities_key not in self.memory:
                self.memory[entities_key] = {}
            self.memory[entities_key][entity_type] = value
    
    def get_entity(self, session_id: str, entity_type: str) -> str:
        """Retrieve a personal entity for a session."""
        if self.redis_available:
            key = f"entities:{session_id}"
            value = self.r.hget(key, entity_type)
            return value.decode('utf-8') if value else None
        else:
            entities_key = f"entities:{session_id}"
            if entities_key in self.memory:
                return self.memory[entities_key].get(entity_type)
            return None
    
    def get_all_entities(self, session_id: str) -> dict:
        """Retrieve all personal entities for a session."""
        if self.redis_available:
            key = f"entities:{session_id}"
            entities = self.r.hgetall(key)
            return {k.decode('utf-8'): v.decode('utf-8') for k, v in entities.items()}
        else:
            entities_key = f"entities:{session_id}"
            return self.memory.get(entities_key, {})