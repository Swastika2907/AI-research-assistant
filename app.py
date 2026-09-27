import os
import traceback
 
from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request
from werkzeug.utils import secure_filename
 
from app import gemini_client
from app.rag import DocumentStore, chunk_text, extract_text_from_pdf
 
load_dotenv()
 
UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {"pdf"}
 
app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16 MB cap
 
store = DocumentStore()
gemini_client.configure()  # reads GEMINI_API_KEY from .env
 
 
def _allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
 
 
@app.route("/")
def index():
    return render_template("index.html", doc_count=len(store.chunks))
 
 
@app.route("/upload", methods=["POST"])
def upload():
    if "file" not in request.files:
        return jsonify({"error": "No file part in request"}), 400
 
    file = request.files["file"]
    if file.filename == "" or not _allowed_file(file.filename):
        return jsonify({"error": "Please upload a PDF file"}), 400
 
    filename = secure_filename(file.filename)
    save_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    file.save(save_path)
 
    try:
        text = extract_text_from_pdf(save_path)
        if not text.strip():
            return jsonify({"error": "Couldn't extract any text — is this a scanned/image PDF?"}), 422
 
        chunks = chunk_text(text, doc_name=filename)
        for chunk in chunks:
            chunk.embedding = gemini_client.embed_text(chunk.text, task_type="retrieval_document")
        store.add(chunks)
 
        return jsonify({
            "message": f"Processed '{filename}' into {len(chunks)} chunks.",
            "total_chunks": len(store.chunks),
        })
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": f"Failed to process PDF: {e}"}), 500
 
 
@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json(silent=True) or {}
    question = data.get("question", "").strip()
 
    if not question:
        return jsonify({"error": "Question is empty"}), 400
    if store.is_empty():
        return jsonify({"error": "Upload a PDF first — there's nothing to search yet."}), 400
 
    try:
        query_embedding = gemini_client.embed_text(question, task_type="retrieval_query")
        top_chunks = store.search(query_embedding, top_k=4)
        answer = gemini_client.generate_answer(question, [c.text for c in top_chunks])
 
        return jsonify({
            "answer": answer,
            "sources": [{"doc": c.doc_name, "excerpt": c.text[:150] + "..."} for c in top_chunks],
        })
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": f"Failed to generate answer: {e}"}), 500
 
 
if __name__ == "__main__":
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    app.run(debug=True, port=5000)