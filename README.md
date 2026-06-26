# 📄 RAG Multi-PDF Question Answering System

A web-based application that lets you upload multiple PDF documents and ask natural language questions against them. Built on the **Retrieval-Augmented Generation (RAG)** architecture — answers are grounded in your documents, not generated from thin air.

# DEMO
<img width="1917" height="1102" alt="Screenshot 2026-06-26 234853 - Copy" src="https://github.com/user-attachments/assets/0d6effe5-2fb2-4fd9-acc2-76f4e36cf7b9" />




# How It Works

User uploads PDF(s)
        ↓
Text extracted using PyPDF2
        ↓
Text split into smaller chunks
        ↓
Each chunk converted into embeddings (Sentence Transformers)
        ↓
Embeddings stored in FAISS vector database
        ↓
User asks a question
        ↓
Question converted into embedding
        ↓
Semantic similarity search (FAISS)
        ↓
Top-k relevant chunks retrieved
        ↓
Context-aware answer generated from retrieved data


## 🛠️ Tech Stack

| Layer          | Technology            |
| -------------- | --------------------- |
| Backend        | Python, Flask         |
| PDF Processing | PyPDF2                |
| Embeddings     | Sentence Transformers |
| Vector Store   | FAISS                 |
| Frontend       | HTML, CSS, JavaScript |




### Installation

# 1. Clone the repository
git clone https://github.com/meenakshymeenu025-pixel/rag--question-answering

# 2. Navigate to project folder
cd your-repo-name

# 3. Create virtual environment
python -m venv venv

# 4. Activate environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# 5. Install dependencies
pip install -r requirements.txt

# 6. Run the app
python app.py


## 📁 Project Structure

├── app.py
├── requirements.txt
├── static/
│   ├── style.css
│   └── script.js
├── templates/
│   └── index.html
├── assets/
│   └── screenshot.png




## 🔍 Features

Upload multiple PDFs at once
Intelligent chunk-based text processing
Semantic search using vector embeddings
Fast retrieval with FAISS
Chat-style Q&A interface
Context-grounded answers (reduces hallucination)

## 🧩 Architecture

This project implements the **RAG (Retrieval-Augmented Generation)** pattern:

- **Retrieval** — relevant document chunks are fetched using vector similarity search
- **Augmented** — the retrieved context augments the query before answering
- **Generation** — answers are produced strictly from the retrieved context, reducing hallucination

---


## 👤 Author

 MEENAKSHY D R
- LinkedIn: www.linkedin.com/in/meenakshydr025


