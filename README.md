# 📄 RAG Q&A App

An AI-powered document Q&A application that lets you upload PDFs and ask questions about them using Retrieval-Augmented Generation (RAG).

## 🚀 Features

- Upload one or more PDF documents
- Ask natural language questions across all uploaded documents
- Get accurate answers powered by Claude (Anthropic)
- See page-level citations showing exactly where answers came from
- Sidebar showing all indexed documents

## 🛠️ Tech Stack

- **LLM:** Anthropic Claude (claude-sonnet-4-6)
- **Embeddings:** sentence-transformers (all-MiniLM-L6-v2)
- **Vector Store:** FAISS
- **PDF Parsing:** PyMuPDF
- **Backend:** FastAPI
- **Frontend:** Streamlit

## ⚙️ Setup

### 1. Clone the repository
```bash
git clone https://github.com/yourusername/rag-qa-app.git
cd rag-qa-app
```

### 2. Create and activate virtual environment
```bash
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux
```

### 3. Install dependencies
```bash
pip install -r backend/requirements.txt
```

### 4. Set up environment variables
Create a `.env` file in the root directory:
```
ANTHROPIC_API_KEY=your_api_key_here
```

### 5. Run the app

**Terminal 1 - Backend:**
```bash
cd backend
uvicorn main:app --reload
```

**Terminal 2 - Frontend:**
```bash
cd frontend
streamlit run app.py
```

Then open [http://localhost:8501](http://localhost:8501) in your browser.

## 📁 Project Structure

```
rag-qa-app/
├── backend/
│   ├── main.py        # FastAPI server
│   ├── rag.py         # RAG logic (embed, index, retrieve)
│   └── requirements.txt
├── frontend/
│   └── app.py         # Streamlit UI
├── .env               # API keys
├── .gitignore
└── README.md
```

## 🔍 How It Works

1. PDFs are parsed and split into overlapping text chunks
2. Each chunk is embedded using sentence-transformers
3. Embeddings are stored in a FAISS vector index
4. On query, the most similar chunks are retrieved
5. Claude generates an answer grounded in the retrieved context
6. Page-level citations are returned alongside the answer