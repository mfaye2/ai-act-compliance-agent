"""Découpage des documents en chunks."""
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from complia import config


def split_documents(docs: list[Document]) -> list[Document]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=config.CHUNK_SIZE,
        chunk_overlap=config.CHUNK_OVERLAP,
        # On essaie de couper d'abord aux "Article N", puis aux paragraphes
        separators=["\nArticle ", "\n\n", "\n", ". ", " ", ""],
    )
    return splitter.split_documents(docs)