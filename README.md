# knowledgescout-backend
This is the backend of knowledgescout

#### **Step 2.4: Commit README**
1. Scroll down to **"Commit changes"**
2. Message: `"Add professional README documentation"`
3. Click **"Commit changes"**

---

### **STEP 3: ADD README TO BACKEND REPOSITORY**

#### **Step 3.1: Go to Backend Repository**
1. Open: `https://github.com/rahul96333/knowledgescout-backend`

#### **Step 3.2: Create README.md**
1. Click **"Add file"** → **"Create new file"**
2. File name: **`README.md`**

#### **Step 3.3: Add This Content:**
Copy and paste:

```markdown
# 🔧 KnowledgeScout Backend API

**API Base URL:** [https://knowledgescout-backend.onrender.com](https://knowledgescout-backend.onrender.com)

## 📡 API Endpoints
- `POST /upload/` - Upload documents
- `POST /ask/` - Ask questions about documents
- `GET /documents/` - Get uploaded documents
- `GET /health` - Health check

## 🛠️ Tech Stack
- **Framework:** FastAPI
- **Language:** Python
- **Deployment:** Render
- **CORS:** Configured for frontend

## 🚀 Deployment
```bash
uvicorn app:app --host 0.0.0.0 --port $PORT
