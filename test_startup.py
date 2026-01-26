#!/usr/bin/env python3
"""Test import chainlit_app"""
import sys
print("✅ Python OK")

try:
    from app.agent import agent
    print("✅ app.agent OK")
except Exception as e:
    print(f"❌ app.agent: {e}")
    sys.exit(1)

try:
    from app.langchain_agent import create_imt_agent
    print("✅ app.langchain_agent OK")
except Exception as e:
    print(f"❌ app.langchain_agent: {e}")
    sys.exit(1)

try:
    from memory.redis_memory import RedisMemory
    print("✅ memory.redis_memory OK")
except Exception as e:
    print(f"❌ memory.redis_memory: {e}")
    sys.exit(1)

try:
    import chainlit
    print(f"✅ chainlit {chainlit.__version__} OK")
except Exception as e:
    print(f"❌ chainlit: {e}")
    sys.exit(1)

print("\n🎉 Tous les imports OK!")
