import json
import re
from pathlib import Path
from typing import List, Dict, Any

import faiss
from sentence_transformers import SentenceTransformer

BASE_DIR = Path(__file__).resolve().parent.parent
INDEX_DIR = BASE_DIR / "index"
FAISS_INDEX_PATH = INDEX_DIR / "qna.index"
METADATA_PATH = INDEX_DIR / "metadata.json"
MODEL_PATH = BASE_DIR / "all-MiniLM-L6-v2"


class HotelQnARetriever:
    def __init__(self) -> None:
        if not FAISS_INDEX_PATH.exists() or not METADATA_PATH.exists():
            raise FileNotFoundError(
                "Index files not found. Run: python src/build_pipeline.py"
            )

        self.model = SentenceTransformer(str(MODEL_PATH))
        self.index = faiss.read_index(str(FAISS_INDEX_PATH))
        self.metadata = json.loads(METADATA_PATH.read_text(encoding="utf-8"))

    @staticmethod
    def _clean_query(text: str) -> str:
        text = text.lower().strip()
        text = re.sub(r"\s+", " ", text)
        return text

    def search(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        query = self._clean_query(query)
        if not query:
            return []

        vec = self.model.encode([query], normalize_embeddings=True).astype("float32")
        scores, idxs = self.index.search(vec, top_k)

        results = []
        for score, idx in zip(scores[0], idxs[0]):
            if idx < 0 or idx >= len(self.metadata):
                continue
            row = self.metadata[idx]
            results.append(
                {
                    "question": row["question"],
                    "answer": row["answer"],
                    "category": row.get("category", "general"),
                    "score": float(score),
                }
            )
        return results
