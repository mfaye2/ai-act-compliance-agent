"""Pose une question à ComplIA."""
import sys

from complia.rag.answer import answer_question

question = " ".join(sys.argv[1:]) or "Un chatbot qui trie des CV est-il à haut risque ?"
answer, docs = answer_question(question)

print(f"❓ {question}\n")
print(answer)
print("\n📚 Sources")
for i, doc in enumerate(docs, 1):
    print(f"[{i}] {doc.metadata['source']} (p. {doc.metadata['page_number']})")