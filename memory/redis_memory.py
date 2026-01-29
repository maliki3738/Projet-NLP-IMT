import redis
import time
from typing import Optional, List, Dict

class RedisMemory:
    """
    Memory management class with Redis backend and RAM fallback.
    Stores conversation history per session with:
    - Max 3 simultaneous active sessions
    - 1 hour TTL per session (auto-cleanup)
    - Ability to switch between sessions
    """
    
    MAX_SESSIONS = 3
    SESSION_TTL = 3600  # 1 heure en secondes
    
    def __init__(self, host='localhost', port=6379, db=0):
        try:
            self.r = redis.Redis(host=host, port=port, db=db, decode_responses=True)
            self.r.ping()  # Test connection
            self.redis_available = True
            self.current_session = None
            print("✅ Redis connecté - Multi-sessions avec TTL 1h disponible")
        except Exception as e:
            print(f"⚠️  Redis non disponible ({e}), utilisation de la mémoire en RAM.")
            self.redis_available = False
            self.memory = {}  # Fallback in-memory dict
            self.sessions_meta = {}  # Métadonnées des sessions en RAM
            self.current_session = None
    
    def _get_sessions_key(self) -> str:
        """Clé Redis pour stocker la liste des sessions actives."""
        return "active_sessions"
    
    def _get_session_key(self, session_id: str, key_type: str) -> str:
        """Génère une clé Redis pour une session donnée."""
        return f"{key_type}:{session_id}"
    
    def create_session(self, session_id: str) -> Dict[str, any]:
        """Crée une nouvelle session de chat avec TTL de 1h.
        
        Limite à MAX_SESSIONS (3) simultanées. Si dépassé, supprime la plus ancienne.
        
        Returns:
            dict avec status (success/error) et message
        """
        if self.redis_available:
            # Récupérer les sessions actives
            active_sessions = self.r.smembers(self._get_sessions_key())
            
            # Si max atteint, supprimer la plus ancienne
            if len(active_sessions) >= self.MAX_SESSIONS:
                # Trouver la plus ancienne (TTL le plus court restant)
                oldest = None
                min_ttl = float('inf')
                
                for sess_id in active_sessions:
                    ttl = self.r.ttl(self._get_session_key(sess_id, "chat_history"))
                    if ttl < min_ttl:
                        min_ttl = ttl
                        oldest = sess_id
                
                if oldest:
                    self.delete_session(oldest)
                    print(f"⚠️  Session {oldest} supprimée (limite de {self.MAX_SESSIONS} atteinte)")
            
            # Créer la nouvelle session
            self.r.sadd(self._get_sessions_key(), session_id)
            
            # Définir le TTL sur toutes les clés de cette session
            history_key = self._get_session_key(session_id, "chat_history")
            entities_key = self._get_session_key(session_id, "entities")
            
            # Initialiser avec des listes vides
            self.r.delete(history_key)  # S'assurer que c'est vide
            self.r.rpush(history_key, f"system: Session {session_id} créée")
            self.r.expire(history_key, self.SESSION_TTL)
            self.r.expire(entities_key, self.SESSION_TTL)
            
            self.current_session = session_id
            
            return {
                "status": "success",
                "message": f"Session '{session_id}' créée avec succès (TTL: 1h)",
                "session_id": session_id,
                "active_sessions": len(active_sessions) + 1
            }
        
        else:
            # Mode RAM
            if len(self.sessions_meta) >= self.MAX_SESSIONS:
                # Supprimer la plus ancienne
                oldest = min(self.sessions_meta.keys(), key=lambda s: self.sessions_meta[s]["created_at"])
                del self.memory[oldest]
                del self.sessions_meta[oldest]
                print(f"⚠️  Session {oldest} supprimée (limite RAM de {self.MAX_SESSIONS} atteinte)")
            
            self.memory[session_id] = []
            self.sessions_meta[session_id] = {
                "created_at": time.time(),
                "ttl": self.SESSION_TTL
            }
            self.current_session = session_id
            
            return {
                "status": "success",
                "message": f"Session '{session_id}' créée en RAM (TTL: 1h)",
                "session_id": session_id,
                "active_sessions": len(self.sessions_meta)
            }
    
    def switch_session(self, session_id: str) -> Dict[str, any]:
        """Bascule vers une session existante.
        
        Returns:
            dict avec status et informations de la session
        """
        if self.redis_available:
            # Vérifier si la session existe
            if not self.r.sismember(self._get_sessions_key(), session_id):
                return {
                    "status": "error",
                    "message": f"Session '{session_id}' n'existe pas. Créez-la d'abord."
                }
            
            # Récupérer le TTL restant
            history_key = self._get_session_key(session_id, "chat_history")
            ttl_remaining = self.r.ttl(history_key)
            
            if ttl_remaining <= 0:
                # Session expirée
                self.delete_session(session_id)
                return {
                    "status": "error",
                    "message": f"Session '{session_id}' a expiré (TTL dépassé)."
                }
            
            self.current_session = session_id
            history = self.get_history(session_id)
            
            return {
                "status": "success",
                "message": f"Basculé vers session '{session_id}'",
                "session_id": session_id,
                "ttl_remaining": ttl_remaining,
                "message_count": len(history)
            }
        
        else:
            # Mode RAM
            if session_id not in self.memory:
                return {
                    "status": "error",
                    "message": f"Session '{session_id}' n'existe pas en RAM."
                }
            
            # Vérifier TTL
            meta = self.sessions_meta.get(session_id)
            if meta:
                elapsed = time.time() - meta["created_at"]
                if elapsed > meta["ttl"]:
                    # Expirée
                    del self.memory[session_id]
                    del self.sessions_meta[session_id]
                    return {
                        "status": "error",
                        "message": f"Session '{session_id}' a expiré (TTL RAM dépassé)."
                    }
            
            self.current_session = session_id
            return {
                "status": "success",
                "message": f"Basculé vers session '{session_id}' (RAM)",
                "session_id": session_id,
                "message_count": len(self.memory[session_id])
            }
    
    def list_sessions(self) -> List[Dict[str, any]]:
        """Liste toutes les sessions actives avec leurs métadonnées.
        
        Returns:
            Liste de dict avec session_id, message_count, ttl_remaining
        """
        sessions = []
        
        if self.redis_available:
            active_sessions = self.r.smembers(self._get_sessions_key())
            
            for sess_id in active_sessions:
                history_key = self._get_session_key(sess_id, "chat_history")
                ttl = self.r.ttl(history_key)
                
                if ttl > 0:
                    msg_count = self.r.llen(history_key)
                    sessions.append({
                        "session_id": sess_id,
                        "message_count": msg_count,
                        "ttl_remaining": ttl,
                        "is_current": (sess_id == self.current_session)
                    })
                else:
                    # Session expirée, la supprimer
                    self.delete_session(sess_id)
        
        else:
            # Mode RAM
            for sess_id, messages in self.memory.items():
                meta = self.sessions_meta.get(sess_id, {})
                elapsed = time.time() - meta.get("created_at", 0)
                ttl_remaining = max(0, meta.get("ttl", 0) - int(elapsed))
                
                if ttl_remaining > 0:
                    sessions.append({
                        "session_id": sess_id,
                        "message_count": len(messages),
                        "ttl_remaining": ttl_remaining,
                        "is_current": (sess_id == self.current_session)
                    })
        
        return sessions
    
    def delete_session(self, session_id: str) -> Dict[str, any]:
        """Supprime complètement une session et ses données.
        
        Returns:
            dict avec status et message
        """
        if self.redis_available:
            # Supprimer de la liste des sessions actives
            self.r.srem(self._get_sessions_key(), session_id)
            
            # Supprimer toutes les clés associées
            history_key = self._get_session_key(session_id, "chat_history")
            entities_key = self._get_session_key(session_id, "entities")
            
            self.r.delete(history_key)
            self.r.delete(entities_key)
            
            if self.current_session == session_id:
                self.current_session = None
            
            return {
                "status": "success",
                "message": f"Session '{session_id}' supprimée"
            }
        
        else:
            # Mode RAM
            if session_id in self.memory:
                del self.memory[session_id]
            if session_id in self.sessions_meta:
                del self.sessions_meta[session_id]
            
            if self.current_session == session_id:
                self.current_session = None
            
            return {
                "status": "success",
                "message": f"Session '{session_id}' supprimée (RAM)"
            }

    def add_message(self, session_id: str, role: str, content: str):
        """Add a message to the chat history for a specific session."""
        if self.redis_available:
            key = self._get_session_key(session_id, "chat_history")
            self.r.rpush(key, f"{role}: {content}")
            # Renouveler le TTL à chaque message
            self.r.expire(key, self.SESSION_TTL)
        else:
            if session_id not in self.memory:
                self.memory[session_id] = []
            self.memory[session_id].append(f"{role}: {content}")

    def get_history(self, session_id: str) -> list:
        """Retrieve the full chat history for a specific session."""
        if self.redis_available:
            key = self._get_session_key(session_id, "chat_history")
            return self.r.lrange(key, 0, -1)
        else:
            return self.memory.get(session_id, [])

    def clear_history(self, session_id: str):
        """Clear the chat history for a specific session."""
        if self.redis_available:
            key = self._get_session_key(session_id, "chat_history")
            self.r.delete(key)
            # Recréer avec TTL
            self.r.rpush(key, f"system: Historique effacé")
            self.r.expire(key, self.SESSION_TTL)
        else:
            if session_id in self.memory:
                self.memory[session_id] = []
    
    def set_entity(self, session_id: str, entity_type: str, value: str):
        """Store a personal entity (name, email, etc.) for a session."""
        if self.redis_available:
            key = self._get_session_key(session_id, "entities")
            self.r.hset(key, entity_type, value)
            # Renouveler le TTL
            self.r.expire(key, self.SESSION_TTL)
        else:
            entities_key = f"entities:{session_id}"
            if entities_key not in self.memory:
                self.memory[entities_key] = {}
            self.memory[entities_key][entity_type] = value
    
    def get_entity(self, session_id: str, entity_type: str) -> Optional[str]:
        """Retrieve a personal entity for a session."""
        if self.redis_available:
            key = self._get_session_key(session_id, "entities")
            return self.r.hget(key, entity_type)
        else:
            entities_key = f"entities:{session_id}"
            if entities_key in self.memory:
                return self.memory[entities_key].get(entity_type)
            return None
    
    def get_all_entities(self, session_id: str) -> dict:
        """Retrieve all personal entities for a session."""
        if self.redis_available:
            key = self._get_session_key(session_id, "entities")
            return self.r.hgetall(key)
        else:
            entities_key = f"entities:{session_id}"
            return self.memory.get(entities_key, {})