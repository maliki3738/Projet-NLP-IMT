from dotenv import load_dotenv
import os
from langfuse import Langfuse

# 1. Charger le .env
load_dotenv()

print("PUBLIC KEY =", os.getenv("LANGFUSE_PUBLIC_KEY"))

# 2. Initialiser Langfuse
langfuse = Langfuse(
    public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
    secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
    host=os.getenv("LANGFUSE_HOST"),
)

print("✅ Langfuse OK")

# 3. Créer une trace (NOUVELLE API)
with langfuse.trace(
    name="test-langfuse",
    input="hello langfuse"
) as trace:
    trace.output = "langfuse fonctionne"
