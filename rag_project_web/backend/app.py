from flask import Flask, render_template, request, jsonify
import os
import traceback
from PyPDF2 import PdfReader
from sentence_transformers import SentenceTransformer
import numpy as np
import faiss
import ollama


# ===================================
# Flask Setup
# ===================================
app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
VECTOR_STORE = "vector_store"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(VECTOR_STORE, exist_ok=True)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


# ===================================
# Load Embedding Model
# ===================================
print("\nLoading embedding model...")

model = SentenceTransformer("all-MiniLM-L6-v2")

print("Embedding model loaded successfully!")
print("RAG System Ready")
print("Server URL: http://127.0.0.1:5000\n")


# ===================================
# FAISS Setup
# ===================================
EMBEDDING_DIMENSION = 384

index = faiss.IndexFlatIP(EMBEDDING_DIMENSION)

stored_chunks = []



# ===================================
# Text Chunking
# ===================================
def chunk_text(text, chunk_size=700, overlap=120):
    chunks = []

    start = 0

    while start < len(text):

        end = start + chunk_size

        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        start += chunk_size - overlap

    return chunks


# ===================================
# Confidence Score
# ===================================
def get_confidence(score):

    if score > 0.75:
        return "High"

    elif score > 0.60:
        return "Medium"

    return "Low"

# ===================================
# Save Vector Store
# ===================================
def save_vector_store():

    faiss.write_index(
        index,
        os.path.join(
            VECTOR_STORE,
            "faiss_index.bin"
        )
    )

    np.save(
        os.path.join(
            VECTOR_STORE,
            "chunks.npy"
        ),
        np.array(
            stored_chunks,
            dtype=object
        )
    )

    print("Vector store saved")



# ===================================
# Load Vector Store
# ===================================
def load_vector_store():

    global index
    global stored_chunks

    index_file = os.path.join(
        VECTOR_STORE,
        "faiss_index.bin"
    )

    chunk_file = os.path.join(
        VECTOR_STORE,
        "chunks.npy"
    )

    if (
        os.path.exists(index_file)
        and
        os.path.exists(chunk_file)
    ):

        index = faiss.read_index(
            index_file
        )

        stored_chunks = list(
            np.load(
                chunk_file,
                allow_pickle=True
            )
        )

        print(
            f"Loaded {len(stored_chunks)} chunks from vector store"
        )

    else:

        print(
            "No existing vector store found"
        )


# ===================================
# Home Page
# ===================================
@app.route("/")
def home():
    return render_template("index.html")


# ===================================
# Upload PDF
# ===================================
@app.route("/upload", methods=["POST"])
def upload_pdf():

    global index, stored_chunks

    try:

        # -----------------------------
        # Validate Upload
        # -----------------------------
        if "file" not in request.files:
            return jsonify({
                "error": "No file uploaded."
            }), 400

        file = request.files["file"]

        if file.filename == "":
            return jsonify({
                "error": "No file selected."
            }), 400

        if not file.filename.lower().endswith(".pdf"):
            return jsonify({
                "error": "Only PDF files are allowed."
            }), 400

        # -----------------------------
        # Save PDF
        # -----------------------------
        filepath = os.path.join(
            app.config["UPLOAD_FOLDER"],
            file.filename
        )

        file.save(filepath)

        print("\n" + "=" * 60)
        print(f"Reading PDF: {file.filename}")

        # -----------------------------
        # Read PDF
        # -----------------------------
        reader = PdfReader(filepath)

        page_chunks = []
        total_characters = 0

        for page_num, page in enumerate(
            reader.pages,
            start=1
        ):

            page_text = page.extract_text()

            if page_text:

                total_characters += len(page_text)

                chunks = chunk_text(page_text)

                for chunk in chunks:

                    page_chunks.append({
                        "text": chunk,
                        "page": page_num,
                        "filename": file.filename
                    })

        if len(page_chunks) == 0:

            return jsonify({
                "error": "No text found in PDF."
            }), 400

        print(f"Characters Extracted: {total_characters}")
        print(f"Chunks Created: {len(page_chunks)}")

        # -----------------------------
        # Generate Embeddings
        # -----------------------------
        print("Generating embeddings...")

        chunk_texts = [
            item["text"]
            for item in page_chunks
        ]

        embeddings = model.encode(
            chunk_texts,
            convert_to_numpy=True,
            batch_size=32,
            show_progress_bar=True,
            normalize_embeddings=True
        ).astype("float32")

        print("Embeddings generated successfully")

        # ==================================================
        # MULTI PDF STORAGE
        # ==================================================
        # Add new embeddings to existing FAISS index
        # Do NOT clear old data
        # ==================================================

        index.add(embeddings)

        stored_chunks.extend(page_chunks)

        save_vector_store()

        print(
            f"Total Chunks In System: "
            f"{len(stored_chunks)}"
        )

        print("Embeddings stored in FAISS")
        print("=" * 60)

        return jsonify({
            "message": "PDF processed successfully",
            "filename": file.filename,
            "chunks_created": len(page_chunks),
            "total_documents_chunks": len(stored_chunks)
        })

    except Exception as e:

        print("\nUPLOAD ERROR")
        traceback.print_exc()

        return jsonify({
            "error": str(e)
        }), 500

# ===================================
# Ask Question
# ===================================
@app.route("/ask", methods=["POST"])
def ask_question():

    try:

        if len(stored_chunks) == 0:

            return jsonify({
                "error": "Please upload a PDF first."
            }), 400

        data = request.get_json()

        if not data:

            return jsonify({
                "error": "Invalid JSON request."
            }), 400

        question = data.get(
            "question",
            ""
        ).strip()

        if not question:

            return jsonify({
                "error": "Question cannot be empty."
            }), 400

        print("\n" + "=" * 60)
        print(f"Question: {question}")

        question_embedding = model.encode(
            [question],
            convert_to_numpy=True,
            normalize_embeddings=True
        ).astype("float32")

        k = min(8, len(stored_chunks))

        distances, indices = index.search(
            question_embedding,
            k=k
        )

        retrieved_chunks = []

        for rank, idx in enumerate(indices[0]):

            if idx < len(stored_chunks):

                chunk_data = stored_chunks[idx].copy()

                distance = float(
                    distances[0][rank]
                )

                chunk_data["distance"] = round(
                    distance,
                    4
                )

                chunk_data["confidence"] = (
                    get_confidence(distance)
                )

                retrieved_chunks.append(
                    chunk_data
                )

        context = "\n\n".join(
            chunk["text"]
            for chunk in retrieved_chunks
        )

        print(
            f"Retrieved Chunks: "
            f"{len(retrieved_chunks)}"
        )

        MAX_CONTEXT_LENGTH = 4000

        if len(context) > MAX_CONTEXT_LENGTH:

            context = context[
                :MAX_CONTEXT_LENGTH
            ]

        prompt = f"""
        You are DocMind AI.

        You answer questions ONLY using the retrieved PDF context.

        Instructions:

        - Read the context carefully.
        - If the answer exists, explain it clearly.
        - If multiple chunks contain the answer, combine them.
        - Never invent information.
        - Never use outside knowledge.
        - If the answer does not exist in the context, reply exactly:

        "I could not find that information in the uploaded PDF."

        Answer in Markdown.

        If possible use:

        • Bullet points

        • Headings

        • Numbered lists

        Context:

        {context}

        Question:

       {question}

       Answer:
       """

        print("Sending prompt to Ollama...")

        response = ollama.chat(
            model="mistral",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        answer = response["message"]["content"]

        

        best_distance = float(
            distances[0][0]
        )

        overall_confidence = (
            get_confidence(best_distance)
        )

        print("Answer generated successfully")
        print("=" * 60)

        return jsonify({
            "question": question,
            "answer": answer,
            "confidence": overall_confidence,
            "sources": retrieved_chunks
        })

    except Exception as e:

        print("\nASK QUESTION ERROR")
        traceback.print_exc()

        return jsonify({
            "error": str(e)
        }), 500


# ===================================
# Load Existing Vector Store
# ===================================
load_vector_store()


# ===================================
# Run Application
# ===================================
if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=False
    )
