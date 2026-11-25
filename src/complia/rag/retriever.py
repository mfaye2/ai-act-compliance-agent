"""Recherche multilingue avec réécriture de la question."""
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

from complia import config


def get_store() -> Chroma:
    return Chroma(
        collection_name=config.COLLECTION_NAME,
        embedding_function=OpenAIEmbeddings(model=config.EMBEDDING_MODEL),
        persist_directory=str(config.VECTORSTORE_DIR),
    )


def rewrite_query(question: str) -> str:
    """Traduit en anglais ET reformule avec le vocabulaire des textes de loi européens."""
    llm = ChatOpenAI(model=config.OPENAI_MODEL)
    prompt = (
        "You help search the EU AI Act and the GDPR. Rewrite the user's question "
        "as a short English search query that uses the vocabulary of EU legal texts "
        "(for example: 'recruitment or selection of natural persons', "
        "'high-risk AI systems', 'processing of personal data', 'lawful basis'). "
        "Reply with the search query only.\n\nQuestion: " + question
    )
    return llm.invoke(prompt).content.strip()


def multilingual_search(question: str, k: int = 4) -> tuple[str, list[Document]]:
    store = get_store()
    rewritten = rewrite_query(question)
    results: list[Document] = []
    seen = set()
    for query in (question, rewritten):
        for doc in store.similarity_search(query, k=k):
            key = (doc.metadata["source"], doc.metadata["page_number"], doc.page_content[:80])
            if key not in seen:
                seen.add(key)
                results.append(doc)
    return rewritten, results