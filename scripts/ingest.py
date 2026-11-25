"""Ingestion : PDF -> chunks -> embeddings -> base Chroma."""
import shutil

from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings

from complia import config
from complia.ingestion.loader import load_pdfs
from complia.ingestion.splitter import split_documents

print("1) Chargement des PDF")
docs = load_pdfs(config.RAW_DIR)
assert docs, f"❌ Aucun PDF trouvé dans {config.RAW_DIR}"

print("\n2) Découpage en chunks")
chunks = split_documents(docs)
print(f"  ✂️  {len(chunks)} chunks")
print("\n  Exemple de chunk :")
print(f"  source={chunks[100].metadata['source']} page={chunks[100].metadata['page_number']}")
print("  " + chunks[100].page_content[:300].replace("\n", " ") + "...")

print("\n3) Embeddings + stockage dans Chroma")
if config.VECTORSTORE_DIR.exists():
    shutil.rmtree(config.VECTORSTORE_DIR)  # on reconstruit à neuf

store = Chroma(
    collection_name=config.COLLECTION_NAME,
    embedding_function=OpenAIEmbeddings(model=config.EMBEDDING_MODEL),
    persist_directory=str(config.VECTORSTORE_DIR),
)
BATCH = 200  # par lots, pour ne pas dépasser les limites de l'API
for i in range(0, len(chunks), BATCH):
    store.add_documents(chunks[i : i + BATCH])
    print(f"  ... {min(i + BATCH, len(chunks))}/{len(chunks)}")

print(f"\n✅ Base prête : {config.VECTORSTORE_DIR}")