from memory.redis_memory import RedisMemory

# Test Redis connection
try:
    memory = RedisMemory()
    # Test ping
    memory.r.ping()
    print("Redis est connecté et fonctionne.")
except Exception as e:c
    print(f"Erreur de connexion à Redis : {e}")
    print("Assurez-vous que Redis est installé et en cours d'exécution.")