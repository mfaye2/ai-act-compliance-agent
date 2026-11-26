"""Génération de la réponse avec citations."""
from langchain_core.documents import Document
from langchain_openai import ChatOpenAI

from complia import config
from complia.rag.retriever import multilingual_search
from complia.rag.reranker import rerank

SYSTEM_PROMPT = """Tu es ComplIA, un assistant qui aide à comprendre l'AI Act et le RGPD.
Règles :
- Réponds en français, de façon claire et courte.
- Appuie-toi UNIQUEMENT sur les extraits fournis.
- Après chaque affirmation, cite l'extrait avec son numéro, par exemple [2].
- Si les extraits ne permettent pas de répondre, dis-le franchement.
- Termine par une phrase rappelant que ce n'est pas un avis juridique."""


def format_context(docs: list[Document]) -> str:
    blocks = []
    for i, doc in enumerate(docs, 1):
        header = f"[{i}] ({doc.metadata['source']}, p. {doc.metadata['page_number']})"
        blocks.append(f"{header}\n{doc.page_content}")
    return "\n\n".join(blocks)


def answer_question(question: str) -> tuple[str, list[Document]]:
    _, candidats = multilingual_search(question, k=8)
    docs = rerank(question, candidats, top_n=6)
    llm = ChatOpenAI(model=config.OPENAI_MODEL)
    messages = [
        ("system", SYSTEM_PROMPT),
        ("human", f"Extraits :\n{format_context(docs)}\n\nQuestion : {question}"),
    ]
    reply = llm.invoke(messages)
    return reply.content, docs