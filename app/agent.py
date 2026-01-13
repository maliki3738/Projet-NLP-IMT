import os
from dotenv import load_dotenv

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import initialize_agent, AgentType
from langchain.tools import Tool

# Charger les variables d'environnement
load_dotenv()

# ======================


# 1. Configuration du LLM (Gemini)
# ======================
llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    temperature=0.2,
    google_api_key=os.getenv("GEMINI_API_KEY")
)

# ======================
# 2. Tool de test (pour voir si l'agent réfléchit)
# ======================
def fake_search(query: str) -> str:
    """Outil de test simulant une recherche sur l'IMT."""
    return f"(FAKE SEARCH) Résultat trouvé pour : {query}"

tools = [
    Tool(
        name="IMT_Search",
        func=fake_search,
        description="Utilise cet outil pour rechercher des informations sur l'IMT"
    )
]

# ======================
# 3. Création de l'agent
# ======================
agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True
)

# ======================
# 4. Test local
# ======================
if __name__ == "__main__":
    print("Agent IMT prêt. Pose une question.\n")
    response = agent.run("Quels sont les frais de scolarité à l'IMT ?")
    print("\nRéponse de l'agent :")
    print(response)
