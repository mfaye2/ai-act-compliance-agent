"""Configuration centrale de ComplIA."""
import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = ROOT / "data" / "raw"
VECTORSTORE_DIR = ROOT / "vectorstore"

OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-5-mini")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")

COLLECTION_NAME = "complia"
CHUNK_SIZE = 1200      # taille d'un morceau, en caractères
CHUNK_OVERLAP = 200    # chevauchement entre deux morceaux consécutifs