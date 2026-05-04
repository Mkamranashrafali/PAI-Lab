# Hotel Receptionist QnA Chatbot (MiniLM + FAISS + Flask)

This project includes the complete pipeline:

1. Preprocess QnA dataset
2. Embed questions with local Hugging Face MiniLM (`all-MiniLM-L6-v2`)
3. Store vectors in FAISS
4. Search by similarity
5. Serve results via Flask + HTML UI

## Project Structure

- `data/hotel_qna.csv` -> receptionist-style QnA dataset
- `src/build_pipeline.py` -> preprocess + embeddings + FAISS index build
- `src/retriever.py` -> similarity search logic
- `app.py` -> Flask app
- `templates/index.html` -> UI
- `static/styles.css` -> styling
- `index/` -> generated FAISS and metadata artifacts

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Build the Retrieval Index

```bash
python src/build_pipeline.py
```

## Run App

```bash
python app.py
```

Open in browser: `http://127.0.0.1:5000`

## Notes

- The model is loaded from local folder: `all-MiniLM-L6-v2`
- If dataset changes, rebuild index by running `python src/build_pipeline.py` again.
