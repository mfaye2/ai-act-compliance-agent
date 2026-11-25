"""Test de recherche multilingue."""
import sys

from complia.rag.retriever import multilingual_search

question = " ".join(sys.argv[1:]) or "Un chatbot qui trie des CV est-il à haut risque ?"
english, docs = multilingual_search(question)

print(f"❓ {question}")
print(f"🌍 Traduction : {english}\n")
for i, doc in enumerate(docs, 1):
    print(f"--- Résultat {i} — {doc.metadata['source']} (p. {doc.metadata['page_number']})")
    print(doc.page_content[:300].replace("\n", " "), "...\n")