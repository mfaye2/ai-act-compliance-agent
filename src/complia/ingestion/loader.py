"""Chargement des PDF."""
from pathlib import Path

from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document


def load_pdfs(raw_dir: Path) -> list[Document]:
    docs: list[Document] = []
    for pdf in sorted(raw_dir.glob("*.pdf")):
        pages = PyPDFLoader(str(pdf)).load()
        for page in pages:
            page.metadata["source"] = pdf.name
            page.metadata["page_number"] = page.metadata.get("page", 0) + 1
        print(f"  📄 {pdf.name}: {len(pages)} pages")
        docs.extend(pages)
    return docs