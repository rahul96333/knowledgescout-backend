from fastapi import FastAPI, UploadFile, File, HTTPException, Header, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import uuid
import time
from datetime import datetime

app = FastAPI(title="KnowledgeScout API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Storage
documents = []
query_cache = {}
rate_limits = {}

class AskRequest(BaseModel):
    query: str
    k: int = 3

class ErrorResponse(BaseModel):
    error: dict

# Rate limiting
def check_rate_limit(user_id: str):
    now = time.time()
    if user_id in rate_limits:
        if now - rate_limits[user_id] < 60:  # 60 seconds
            raise HTTPException(status_code=429, detail={"error": {"code": "RATE_LIMIT"}})
    rate_limits[user_id] = now

@app.get("/")
def root():
    return {"message": "KnowledgeScout API", "status": "live"}

@app.get("/api/health")
def health():
    return {"status": "healthy"}

@app.get("/api/_meta")
def meta():
    return {
        "name": "KnowledgeScout",
        "version": "1.0",
        "problem_statement": "Doc Q&A"
    }

@app.get("/.well-known/hackathon.json")
def hackathon_info():
    return {
        "name": "KnowledgeScout",
        "problem_statement": 5,
        "team": "Your Team Name"
    }

# Document APIs
@app.post("/api/docs")
async def upload_doc(
    file: UploadFile = File(...),
    idempotency_key: Optional[str] = Header(None)
):
    check_rate_limit("upload_user")
    
    try:
        content = await file.read()
        text_content = content.decode('utf-8')
        
        doc_id = str(uuid.uuid4())
        document = {
            "id": doc_id,
            "filename": file.filename,
            "content": text_content,
            "pages": text_content.split('\n'),  # Simple page splitting
            "uploaded_at": datetime.now().isoformat(),
            "is_private": False
        }
        documents.append(document)
        
        return {
            "id": doc_id,
            "filename": file.filename,
            "message": "Document uploaded successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/docs")
def list_docs(
    limit: int = Query(10, ge=1),
    offset: int = Query(0, ge=0)
):
    check_rate_limit("list_user")
    
    end_idx = offset + limit
    paginated_docs = documents[offset:end_idx]
    
    return {
        "items": [
            {
                "id": doc["id"],
                "filename": doc["filename"],
                "uploaded_at": doc["uploaded_at"]
            } for doc in paginated_docs
        ],
        "next_offset": end_idx if end_idx < len(documents) else None
    }

@app.get("/api/docs/{doc_id}")
def get_doc(doc_id: str):
    check_rate_limit("get_user")
    
    for doc in documents:
        if doc["id"] == doc_id:
            return {
                "id": doc["id"],
                "filename": doc["filename"],
                "content": doc["content"],
                "pages": doc["pages"],
                "uploaded_at": doc["uploaded_at"]
            }
    
    raise HTTPException(status_code=404, detail="Document not found")

# Q&A API
@app.post("/api/ask")
def ask_question(request: AskRequest):
    check_rate_limit("ask_user")
    
    # Simple cache check (60 seconds)
    cache_key = f"query_{request.query}"
    if cache_key in query_cache:
        cache_data = query_cache[cache_key]
        if time.time() - cache_data["timestamp"] < 60:
            return cache_data["response"]
    
    # Simple search logic
    relevant_docs = []
    for doc in documents:
        if request.query.lower() in doc["content"].lower():
            # Find which pages contain the query
            matching_pages = []
            for i, page in enumerate(doc["pages"]):
                if request.query.lower() in page.lower():
                    matching_pages.append(i + 1)  # 1-based page numbers
            
            relevant_docs.append({
                "doc_id": doc["id"],
                "filename": doc["filename"],
                "pages": matching_pages[:request.k],
                "content_snippet": doc["content"][:200] + "..."
            })
    
    response = {
        "answer": f"Found {len(relevant_docs)} relevant documents for: {request.query}",
        "sources": relevant_docs,
        "cached": False
    }
    
    # Cache the response
    query_cache[cache_key] = {
        "response": response,
        "timestamp": time.time()
    }
    
    return response

# Admin APIs
@app.post("/api/index/rebuild")
def rebuild_index():
    check_rate_limit("admin_user")
    return {"message": "Index rebuild completed", "documents_processed": len(documents)}

@app.get("/api/index/stats")
def get_stats():
    check_rate_limit("admin_user")
    return {
        "total_documents": len(documents),
        "total_pages": sum(len(doc["pages"]) for doc in documents),
        "cache_size": len(query_cache)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
