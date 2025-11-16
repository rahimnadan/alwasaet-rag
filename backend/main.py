"""
FastAPI Backend for Alwasaet RAG Application
Production-ready with authentication, document management, and RAG queries
"""

import os
import tempfile
import uuid
import logging
from typing import List, Optional
from datetime import datetime, timedelta
from contextlib import asynccontextmanager

from fastapi import FastAPI, File, UploadFile, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
import jwt
from passlib.context import CryptContext

from llama_index.core import SimpleDirectoryReader
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from rag import EmbedData, MilvusVDB_BQ, Retriever, RAG

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Security configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

# In-memory storage (replace with proper database in production)
users_db = {
    "admin": {
        "username": "admin",
        "hashed_password": pwd_context.hash("admin123"),  # Change in production!
        "role": "admin"
    }
}

documents_db = {}
sessions = {}

# Models
class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class QueryRequest(BaseModel):
    query: str
    session_id: str
    top_k: int = Field(default=5, ge=1, le=20)

class DocumentInfo(BaseModel):
    id: str
    filename: str
    uploaded_at: str
    session_id: str
    status: str

class HealthResponse(BaseModel):
    status: str
    timestamp: str

# Lifespan context manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    logger.info("Starting Alwasaet RAG API Server...")
    yield
    logger.info("Shutting down Alwasaet RAG API Server...")

# Create FastAPI app
app = FastAPI(
    title="Alwasaet RAG API",
    description="Production-ready RAG API with document management and authentication",
    version="2.0.0",
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Authentication functions
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Validate JWT token and return current user"""
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials"
            )
        user = users_db.get(username)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        return user
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired"
        )
    except jwt.JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )

# API Endpoints

@app.get("/", response_model=HealthResponse)
async def root():
    """Root endpoint - health check"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.post("/api/auth/login", response_model=Token)
async def login(user_login: UserLogin):
    """Authenticate user and return JWT token"""
    user = users_db.get(user_login.username)
    if not user or not verify_password(user_login.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["username"], "role": user["role"]},
        expires_delta=access_token_expires
    )
    
    logger.info(f"User {user_login.username} logged in successfully")
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/api/session/create")
async def create_session(current_user: dict = Depends(get_current_user)):
    """Create a new RAG session"""
    session_id = str(uuid.uuid4())[:8]
    groq_api_key = os.getenv("GROQ_API_KEY", "")
    
    if not groq_api_key:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="GROQ_API_KEY not configured"
        )
    
    sessions[session_id] = {
        "id": session_id,
        "created_at": datetime.utcnow().isoformat(),
        "documents": [],
        "query_engine": None,
        "embeddata": None,
        "milvus_vdb": None
    }
    
    logger.info(f"Created new session: {session_id}")
    return {"session_id": session_id}

@app.post("/api/documents/upload")
async def upload_documents(
    session_id: str,
    files: List[UploadFile] = File(...),
    current_user: dict = Depends(get_current_user)
):
    """Upload and process PDF documents"""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = sessions[session_id]
    groq_api_key = os.getenv("GROQ_API_KEY", "")
    
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            # Save uploaded files
            uploaded_files = []
            for file in files:
                if not file.filename.endswith('.pdf'):
                    continue
                file_path = os.path.join(temp_dir, file.filename)
                content = await file.read()
                with open(file_path, "wb") as f:
                    f.write(content)
                uploaded_files.append(file.filename)
            
            if not uploaded_files:
                raise HTTPException(status_code=400, detail="No valid PDF files uploaded")
            
            logger.info(f"Processing {len(uploaded_files)} documents for session {session_id}")
            
            # Load documents
            loader = SimpleDirectoryReader(
                input_dir=temp_dir,
                required_exts=[".pdf"],
                recursive=True
            )
            docs = loader.load_data()
            documents = [doc.text for doc in docs]
            
            # Extract metadata
            metadata = []
            for doc in docs:
                filename = "unknown"
                page = 0
                
                if hasattr(doc, 'metadata') and doc.metadata:
                    if 'file_name' in doc.metadata:
                        filename = doc.metadata['file_name']
                    elif 'source' in doc.metadata:
                        filename = doc.metadata['source'].split('/')[-1]
                    
                    if 'page_label' in doc.metadata:
                        try:
                            page = int(doc.metadata['page_label'])
                        except (ValueError, TypeError):
                            page = 0
                    elif 'page' in doc.metadata:
                        try:
                            page = int(doc.metadata['page'])
                        except (ValueError, TypeError):
                            page = 0
                
                metadata.append({
                    "filename": filename,
                    "page": page + 1
                })
            
            if not documents:
                raise HTTPException(status_code=400, detail="No text could be extracted from PDFs")
            
            # Generate embeddings and create vector DB
            batch_size = 512
            collection_name = f"docs_{session_id}"
            
            if session["query_engine"] is None:
                # First time setup
                embeddata = EmbedData(
                    embed_model_name="BAAI/bge-m3",
                    batch_size=batch_size
                )
                embeddata.embed(documents, metadata)
                
                db_file = os.path.join(tempfile.gettempdir(), f"milvus_{session_id}.db")
                test_embedding = embeddata.embed_model.encode("test")
                actual_dim = len(test_embedding)
                
                milvus_vdb = MilvusVDB_BQ(
                    collection_name=collection_name,
                    batch_size=batch_size,
                    vector_dim=actual_dim,
                    db_file=db_file
                )
                
                milvus_vdb.define_client()
                milvus_vdb.create_collection(drop_existing=True)
                milvus_vdb.ingest_data(embeddata=embeddata)
                
                retriever = Retriever(vector_db=milvus_vdb, embeddata=embeddata)
                query_engine = RAG(
                    retriever=retriever,
                    llm_model="moonshotai/kimi-k2-instruct",
                    groq_api_key=groq_api_key
                )
                
                session["query_engine"] = query_engine
                session["milvus_vdb"] = milvus_vdb
                session["embeddata"] = embeddata
            else:
                # Add to existing collection
                new_embeddata = EmbedData(
                    embed_model_name="BAAI/bge-m3",
                    batch_size=batch_size
                )
                new_embeddata.embed(documents, metadata)
                session["milvus_vdb"].ingest_data(embeddata=new_embeddata)
            
            # Store document info
            for filename in uploaded_files:
                doc_id = str(uuid.uuid4())
                doc_info = {
                    "id": doc_id,
                    "filename": filename,
                    "uploaded_at": datetime.utcnow().isoformat(),
                    "session_id": session_id,
                    "status": "processed"
                }
                documents_db[doc_id] = doc_info
                session["documents"].append(doc_id)
            
            logger.info(f"Successfully processed {len(uploaded_files)} documents for session {session_id}")
            
            return {
                "message": f"Successfully processed {len(uploaded_files)} documents",
                "document_ids": [documents_db[doc_id]["id"] for doc_id in session["documents"][-len(uploaded_files):]]
            }
    
    except Exception as e:
        logger.error(f"Error processing documents: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing documents: {str(e)}")

@app.get("/api/documents/list")
async def list_documents(
    session_id: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """List all documents, optionally filtered by session"""
    if session_id:
        if session_id not in sessions:
            raise HTTPException(status_code=404, detail="Session not found")
        doc_ids = sessions[session_id]["documents"]
        docs = [documents_db[doc_id] for doc_id in doc_ids if doc_id in documents_db]
    else:
        docs = list(documents_db.values())
    
    return {"documents": docs, "count": len(docs)}

@app.delete("/api/documents/{document_id}")
async def delete_document(
    document_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Delete a document"""
    if document_id not in documents_db:
        raise HTTPException(status_code=404, detail="Document not found")
    
    doc_info = documents_db[document_id]
    session_id = doc_info["session_id"]
    
    # Remove from session
    if session_id in sessions:
        if document_id in sessions[session_id]["documents"]:
            sessions[session_id]["documents"].remove(document_id)
    
    # Remove from database
    del documents_db[document_id]
    
    logger.info(f"Deleted document: {document_id}")
    return {"message": "Document deleted successfully"}

@app.post("/api/query")
async def query_documents(
    request: QueryRequest,
    current_user: dict = Depends(get_current_user)
):
    """Query documents using RAG"""
    if request.session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = sessions[request.session_id]
    
    if session["query_engine"] is None:
        raise HTTPException(status_code=400, detail="No documents uploaded in this session")
    
    try:
        query_engine = session["query_engine"]
        context_text, citations = query_engine.generate_context_with_citations(
            query=request.query,
            top_k=request.top_k
        )
        
        prompt_text = query_engine.prompt_template.format(
            context=context_text,
            query=request.query
        )
        
        # Get complete response (non-streaming for simplicity)
        response = query_engine.llm.complete(prompt_text)
        answer = response.text
        
        # Add citations
        if citations:
            citation_text = f"\n\nCitation: {', '.join(citations)}"
            if "Citation:" not in answer:
                answer += citation_text
        
        logger.info(f"Query processed for session {request.session_id}")
        
        return {
            "answer": answer,
            "citations": citations,
            "context": context_text
        }
    
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")

@app.get("/api/stats")
async def get_stats(current_user: dict = Depends(get_current_user)):
    """Get system statistics"""
    return {
        "total_sessions": len(sessions),
        "total_documents": len(documents_db),
        "active_sessions": sum(1 for s in sessions.values() if s["query_engine"] is not None)
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
