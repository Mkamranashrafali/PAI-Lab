import json
import re
from pathlib import Path

import faiss
import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = BASE_DIR / "data" / "hotel_qna.csv"
INDEX_DIR = BASE_DIR / "index"
EMBEDDINGS_PATH = INDEX_DIR / "question_embeddings.npy"
METADATA_PATH = INDEX_DIR / "metadata.json"
FAISS_INDEX_PATH = INDEX_DIR / "qna.index"
MODEL_PATH = BASE_DIR / "all-MiniLM-L6-v2"


def clean_text(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"\s+", " ", text)
    return text


def preprocess_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    required_cols = {"question", "answer"}
    if not required_cols.issubset(df.columns):
        raise ValueError("Dataset must include at least 'question' and 'answer' columns")

    cleaned = df.copy()
    cleaned["question"] = cleaned["question"].astype(str).map(clean_text)
    cleaned["answer"] = cleaned["answer"].astype(str).str.strip()

    cleaned = cleaned.drop_duplicates(subset=["question"])
    cleaned = cleaned[cleaned["question"].str.len() > 0]
    cleaned = cleaned[cleaned["answer"].str.len() > 0]
    cleaned = cleaned.reset_index(drop=True)
    return cleaned


def build_index() -> None:
    INDEX_DIR.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(DATA_PATH)
    processed = preprocess_dataframe(df)

    model = SentenceTransformer(str(MODEL_PATH))
    embeddings = model.encode(
        processed["question"].tolist(),
        convert_to_numpy=True,
        normalize_embeddings=True,
        show_progress_bar=False,
    ).astype("float32")

    dim = embeddings.shape[1]
    index = faiss.IndexFlatIP(dim)
    index.add(embeddings)

    faiss.write_index(index, str(FAISS_INDEX_PATH))
    np.save(EMBEDDINGS_PATH, embeddings)

    metadata = processed.to_dict(orient="records")
    METADATA_PATH.write_text(json.dumps(metadata, indent=2), encoding="utf-8")

    print(f"Indexed {len(metadata)} QnA rows")
    print(f"FAISS index: {FAISS_INDEX_PATH}")


if __name__ == "__main__":
    build_index()
