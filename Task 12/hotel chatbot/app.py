from flask import Flask, render_template, request

from src.retriever import HotelQnARetriever

app = Flask(__name__)
retriever = None
startup_error = None

try:
    retriever = HotelQnARetriever()
except Exception as exc:
    startup_error = str(exc)


@app.route("/", methods=["GET", "POST"])
def home():
    query = ""
    results = []
    best_answer = None

    if request.method == "POST":
        query = request.form.get("query", "").strip()
        if retriever and query:
            results = retriever.search(query, top_k=3)
            if results:
                best_answer = results[0]["answer"]

    return render_template(
        "index.html",
        query=query,
        results=results,
        best_answer=best_answer,
        startup_error=startup_error,
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
