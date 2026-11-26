"""Reranking : le LLM note chaque extrait selon sa pertinence."""
from langchain_core.documents import Document
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

from complia import config


class Scores(BaseModel):
    scores: list[int] = Field(description="Une note de 0 à 10 par extrait, dans l'ordre")


def rerank(question: str, docs: list[Document], top_n: int = 6) -> list[Document]:
    llm = ChatOpenAI(model=config.OPENAI_MODEL).with_structured_output(Scores)
    extraits = "\n\n".join(f"[{i}] {d.page_content[:600]}" for i, d in enumerate(docs))
    prompt = (
        f"Question : {question}\n\n"
        "Note chaque extrait de 0 à 10 selon son utilité pour répondre à la question "
        f"(10 = répond directement). Donne exactement {len(docs)} notes, dans l'ordre.\n\n"
        + extraits
    )
    notes = llm.invoke(prompt).scores
    if len(notes) != len(docs):  # sécurité : si le LLM se trompe, on garde l'ordre d'origine
        return docs[:top_n]
    classement = sorted(zip(notes, docs), key=lambda paire: paire[0], reverse=True)
    return [doc for _, doc in classement[:top_n]]