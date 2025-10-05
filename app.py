from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
import uuid
from typing import List, Optional

app = FastAPI(title="KnowledgeScout Backend")

# Fix CORS - Allow all origins for now
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins temporarily
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Store documents in memory
documents = []

@app.get("/")
async def root():
    return {"message": "KnowledgeScout Backend is running!"}

@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        
        # Try to decode as text, if fails use binary
        try:
            content_str = contents.decode('utf-8')
        except:
            content_str = f"Binary file: {file.filename}"
        
        document = {
            "id": str(uuid.uuid4()),
            "filename": file.filename,
            "content": content_str,
            "file_type": file.content_type
        }
        documents.append(document)
        
        return {
            "message": "File uploaded successfully",
            "filename": file.filename,
            "file_type": file.content_type or "unknown",
            "id": document["id"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@app.get("/documents/")
async def get_documents():
    return {"documents": documents}

@app.post("/ask/")
async def ask_question(question: dict):
    try:
        user_question = question.get("question", "")
        
        if not user_question:
            return {"answer": "Please ask a question.", "sources": []}
        
        # Simple demo response
        answer = f"I received your question: '{user_question}'. Backend is working!"
        
        # Find relevant documents
        sources = []
        for doc in documents:
            if user_question.lower() in doc["content"].lower():
                sources.append({
                    "filename": doc["filename"],
                    "content": doc["content"][:100] + "..."
                })
        
        return {
            "answer": answer,
            "sources": sources[:3]
        }
    except Exception as e:
        return {"answer": f"Error: {str(e)}", "sources": []}

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "documents_count": len(documents)}
