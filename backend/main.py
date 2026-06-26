import os
import shutil
from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List, Dict, Any
from intrebare import process_pdf
from rag import generate_answer

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryRequest(BaseModel):
    intrebare: str
    istoric: Optional[List[Dict[str, Any]]] = []

@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Fisierul trebuie sa fie PDF")

    if not os.path.exists("data"):
        os.makedirs("data")

    file_path = f"data/{file.filename}"

    if os.path.exists(file_path):
        return {"mesaj": f"Documentul '{file.filename}' exista deja in biblioteca."}

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        chunks_count = process_pdf(file_path)
        return {"mesaj": f"Fișier adăugat cu succes: {chunks_count} fragmente noi."}
    except Exception as e:
        print(f"[Error] Ingestion failed pentru {file.filename}: {e}")
        return {"mesaj": "A aparut o eroare la procesarea documentului."}

@app.post("/chat")
async def chat(request: QueryRequest):
    if not request.intrebare.strip():
        raise HTTPException(status_code=400, detail="Intrebarea nu poate fi vida")

    try:
        answer, sources = generate_answer(request.intrebare, request.istoric)
        return {
            "raspuns_ai": answer,
            "surse": sources
        }
    except Exception as e:
        print(f"[Error] Pipeline execution failed: {e}")
        raise HTTPException(status_code=500, detail="Eroare interna LLM pipeline")

@app.get("/documents")
async def list_documents():
    if not os.path.exists("data"):
        return {"documente": []}

    fisiere = [f for f in os.listdir("data") if f.endswith('.pdf')]
    return {"documente": fisiere}