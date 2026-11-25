"""Test de recherche sémantique sur la base."""
import sys

from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings

from complia import config

question = " ".join(sys.argv[1:]) or "Quels systèmes d'IA sont considérés à haut risque ?"

store = Chroma(
    collection_name=config.COLLECTION_NAME,
    embedding_function=OpenAIEmbeddings(model=config.EMBEDDING_MODEL),
    persist_directory=str(config.VECTORSTORE_DIR),
)

print(f"❓ {question}\n")
for i, doc in enumerate(store.similarity_search(question, k=4), 1):
    print(f"--- Résultat {i} — {doc.metadata['source']} (p. {doc.metadata['page_number']})")
    print(doc.page_content[:400].replace("\n", " "), "...\n")