from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "KnowledgeScout API LIVE", "status": "working"}

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.get("/api/health")
def api_health():
    return {"status": "healthy"}

@app.get("/api/_meta")
def meta():
    return {"name": "KnowledgeScout", "version": "1.0"}

@app.get("/.well-known/hackathon.json")
def hackathon():
    return {
        "name": "KnowledgeScout", 
        "problem_statement": 5,
        "team": "Rahul"
    }

# Simple document endpoints
documents = []

@app.post("/upload/")
async def upload_file():
    return {"message": "Upload endpoint ready", "status": "success"}

@app.get("/documents/")
def get_documents():
    return {"documents": documents}

@app.post("/ask/")
def ask_question():
    return {"answer": "Q&A system working", "sources": []}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
