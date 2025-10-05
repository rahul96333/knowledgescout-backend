from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
import uuid
from typing import List, Optional

app = FastAPI(title="KnowledgeScout Backend")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://knowledgescout-frontend.vercel.app",
        "https://knowledgescout-frontend-git-main-rahul-soni1.vercel.app",
        "http://localhost:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Your existing routes continue below...
documents = []

@app.get("/")
async def root():
    return {"message": "KnowledgeScout Backend is running!"}

@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        document = {
            "id": str(uuid.uuid4()),
            "filename": file.filename,
            "content": contents.decode('utf-8'),
            "file_type": file.content_type
        }
        documents.append(document)
        return JSONResponse(content={
            "message": "File uploaded successfully",
            "filename": file.filename,
            "file_type": file.content_type,
            "id": document["id"]
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@app.get("/documents/")
async def get_documents():
    return {"documents": documents}

@app.post("/ask/")
async def ask_question(question: dict):
    try:
        user_question = question.get("question", "")
        
        # Simple response for testing
        answer = f"I received your question: '{user_question}'. This is a demo response."
        
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
            "sources": sources[:3]  # Limit to 3 sources
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Question processing failed: {str(e)}")
