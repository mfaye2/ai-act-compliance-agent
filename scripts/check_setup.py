"""Vérifie que l'environnement et la clé OpenAI fonctionnent."""
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

load_dotenv()

assert os.getenv("OPENAI_API_KEY"), "❌ OPENAI_API_KEY manquante dans .env"

# 1) Test du LLM
llm = ChatOpenAI(model=os.getenv("OPENAI_MODEL", "gpt-5-mini"))
reponse = llm.invoke("Réponds uniquement par : OK")
print("✅ LLM :", reponse.content)

# 2) Test des embeddings (le cœur du RAG)
emb = OpenAIEmbeddings(model=os.getenv("EMBEDDING_MODEL", "text-embedding-3-small"))
vecteur = emb.embed_query("Qu'est-ce qu'un système d'IA à haut risque ?")
print(f"✅ Embeddings : vecteur de {len(vecteur)} dimensions")