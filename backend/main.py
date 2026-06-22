import os
import shutil
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from rag import build_index, answer_question

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "uploaded_pdfs"
os.makedirs(UPLOAD_DIR, exist_ok=True)

indexed_files = []

class QuestionRequest(BaseModel):
    question: str

@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    num_chunks = build_index(file_path, file.filename)

    if file.filename not in indexed_files:
        indexed_files.append(file.filename)

    return {
        "message": f"'{file.filename}' indexed successfully with {num_chunks} chunks.",
        "indexed_files": indexed_files
    }

@app.post("/ask")
async def ask_question(request: QuestionRequest):
    if not request.question.strip():
        return {"answer": "Please enter a valid question.", "citations": []}
    result = answer_question(request.question)
    return result

@app.get("/files")
def get_files():
    return {"indexed_files": indexed_files}

@app.get("/health")
def health():
    return {"status": "ok"}