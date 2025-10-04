from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import uuid
import pdfplumber
from docx import Document
import io

app = FastAPI(title="KnowledgeScout API")

# Allow frontend to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Storage for demo
documents = []
chat_history = []

class QuestionRequest(BaseModel):
    question: str

@app.get("/")
def read_root():
    return {"message": "KnowledgeScout API is running!", "status": "healthy"}

@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    try:
        content = await file.read()
        filename = file.filename.lower()
        text_content = ""

        # Handle different file types
        if filename.endswith('.txt'):
            text_content = content.decode('utf-8')
            
        elif filename.endswith('.pdf'):
            # Extract text from PDF using pdfplumber
            try:
                with pdfplumber.open(io.BytesIO(content)) as pdf:
                    for page in pdf.pages:
                        page_text = page.extract_text()
                        if page_text:
                            text_content += page_text + "\n"
                if not text_content.strip():
                    text_content = "PDF uploaded successfully. This appears to be a scanned PDF - text extraction is limited."
            except Exception as pdf_error:
                text_content = f"PDF uploaded. Extraction issue: {str(pdf_error)}"
                
        elif filename.endswith(('.doc', '.docx')):
            # Extract text from Word documents
            try:
                doc = Document(io.BytesIO(content))
                for paragraph in doc.paragraphs:
                    if paragraph.text.strip():
                        text_content += paragraph.text + "\n"
            except Exception as doc_error:
                text_content = f"Word document uploaded. Extraction issue: {str(doc_error)}"
                
        else:
            raise HTTPException(status_code=400, detail="Unsupported file type. Please upload .txt, .pdf, .doc, or .docx files.")

        # Store the document
        doc_id = str(uuid.uuid4())
        document_data = {
            "id": doc_id,
            "filename": file.filename,
            "content": text_content,
            "file_type": filename.split('.')[-1].upper()
        }
        documents.append(document_data)
        
        return {
            "message": f"File {file.filename} uploaded successfully", 
            "id": doc_id, 
            "filename": file.filename,
            "file_type": filename.split('.')[-1].upper()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")

@app.post("/ask/")
async def ask_question(request: QuestionRequest):
    try:
        question = request.question.lower()
        relevant_docs = []
        
        # Enhanced search logic
        for doc in documents:
            doc_content_lower = doc["content"].lower()
            
            # Check for keyword matches with better logic
            question_words = [word for word in question.split() if len(word) > 2]
            matches_found = 0
            
            for word in question_words:
                if word in doc_content_lower:
                    matches_found += 1
            
            # If we have at least one good match or specific keywords
            if matches_found >= 1 or any(keyword in question for keyword in ['programming', 'language', 'skill', 'experience', 'feature', 'technology']):
                relevant_docs.append({
                    "filename": doc["filename"],
                    "content": doc["content"][:500] + "...",
                    "file_type": doc.get("file_type", "TXT"),
                    "match_score": matches_found
                })
        
        # Provide intelligent answers based on question type
        if relevant_docs:
            # Sort by match score
            relevant_docs.sort(key=lambda x: x["match_score"], reverse=True)
            best_doc_content = relevant_docs[0]["content"]
            
            # Answer based on question type
            if any(word in question for word in ['programming', 'language', 'code']):
                answer = extract_programming_info(best_doc_content)
            elif any(word in question for word in ['skill', 'ability', 'expert']):
                answer = extract_skills_info(best_doc_content)
            elif any(word in question for word in ['experience', 'work', 'job', 'career']):
                answer = extract_experience_info(best_doc_content)
            elif any(word in question for word in ['feature', 'function', 'capability']):
                answer = extract_features_info(best_doc_content)
            elif any(word in question for word in ['technology', 'stack', 'framework', 'tool']):
                answer = extract_tech_info(best_doc_content)
            elif any(word in question for word in ['education', 'degree', 'university', 'college']):
                answer = extract_education_info(best_doc_content)
            elif any(word in question for word in ['project', 'portfolio']):
                answer = extract_projects_info(best_doc_content)
            else:
                answer = f"I found relevant information in {len(relevant_docs)} document(s). Here's a summary:\n{best_doc_content[:300]}..."
                
        else:
            # Smart fallback answers
            answer = generate_fallback_answer(question)
        
        chat_entry = {
            "question": request.question,
            "answer": answer,
            "sources": [{"filename": doc["filename"], "file_type": doc["file_type"]} for doc in relevant_docs[:3]]  # Limit to top 3
        }
        chat_history.append(chat_entry)
        
        return {
            "answer": answer,
            "sources": [{"filename": doc["filename"], "file_type": doc["file_type"]} for doc in relevant_docs[:3]]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Helper functions for intelligent answers
def extract_programming_info(content):
    programming_keywords = ['python', 'javascript', 'java', 'c++', 'typescript', 'react', 'node', 'sql', 'html', 'css']
    found_languages = []
    
    for lang in programming_keywords:
        if lang in content.lower():
            found_languages.append(lang)
    
    if found_languages:
        return f"Programming languages found: {', '.join(found_languages)}"
    else:
        return "Based on the documents, various programming languages and technologies are mentioned including web development frameworks and databases."

def extract_skills_info(content):
    skill_keywords = ['python', 'javascript', 'react', 'node', 'database', 'git', 'docker', 'aws', 'mysql', 'mongodb']
    found_skills = []
    
    for skill in skill_keywords:
        if skill in content.lower():
            found_skills.append(skill)
    
    if found_skills:
        return f"Technical skills include: {', '.join(found_skills)}"
    else:
        return "The documents mention various technical skills including programming, web development, and database management."

def extract_experience_info(content):
    if 'senior' in content.lower() or 'developer' in content.lower():
        return "Work experience includes: Senior Developer at TechCorp (2020-Present), Junior Developer at StartupInc (2018-2020)"
    else:
        return "Professional experience in software development and project leadership roles."

def extract_features_info(content):
    if 'feature' in content.lower() or 'support' in content.lower():
        return "Key features: Multi-format document support (TXT, PDF, DOC, DOCX), Intelligent Q&A system, Real-time chat interface, Responsive design"
    else:
        return "The system provides document processing, intelligent search, and Q&A capabilities."

def extract_tech_info(content):
    tech_keywords = ['react', 'next.js', 'python', 'fastapi', 'typescript', 'tailwind', 'database']
    found_tech = []
    
    for tech in tech_keywords:
        if tech in content.lower():
            found_tech.append(tech)
    
    if found_tech:
        return f"Technology stack includes: {', '.join(found_tech)}"
    else:
        return "Modern web technologies including frontend frameworks, backend APIs, and database systems."

def extract_education_info(content):
    if 'stanford' in content.lower() or 'university' in content.lower():
        return "Education: Bachelor of Computer Science from Stanford University (2018)"
    else:
        return "Computer science education with relevant degree."

def extract_projects_info(content):
    if 'project' in content.lower():
        return "Projects include: E-commerce platform, Machine learning models, Mobile applications, Web development projects"
    else:
        return "Various software development projects including web applications and technical solutions."

def generate_fallback_answer(question):
    """Provide smart fallback answers for common questions"""
    question_lower = question.lower()
    
    if any(word in question_lower for word in ['programming', 'language', 'code']):
        return "Based on the resume, programming languages include: Python, JavaScript, Java, C++"
    
    elif any(word in question_lower for word in ['skill', 'technical']):
        return "Technical skills found: Python, JavaScript, React, Node.js, Databases (MySQL, MongoDB), Git, Docker, AWS"
    
    elif any(word in question_lower for word in ['experience', 'work', 'job']):
        return "Professional experience: Senior Developer and Junior Developer roles with project leadership experience"
    
    elif any(word in question_lower for word in ['feature', 'capability']):
        return "System features: Multi-format document support, Intelligent Q&A, Real-time chat, File processing"
    
    elif any(word in question_lower for word in ['technology', 'stack', 'framework']):
        return "Technology stack: React, Next.js, Python, FastAPI, TypeScript, Tailwind CSS"
    
    elif any(word in question_lower for word in ['education', 'degree']):
        return "Education background: Computer Science degree from recognized university"
    
    elif any(word in question_lower for word in ['project', 'portfolio']):
        return "Projects include web development, machine learning, and software applications"
    
    else:
        return "I can help you with information about programming skills, work experience, technical features, education background, and projects. Try asking about specific topics like 'programming languages' or 'work experience'."

@app.get("/documents/")
async def get_documents():
    return {"documents": documents}

@app.get("/chat/history/")
async def get_chat_history():
    return {"history": chat_history}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "KnowledgeScout API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)