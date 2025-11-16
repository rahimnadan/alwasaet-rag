import os
import gc
import tempfile
import time
import uuid
from typing import List, Optional
from fastapi import FastAPI, File, UploadFile, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from dotenv import load_dotenv
from llama_index.core import SimpleDirectoryReader
from rag import EmbedData, MilvusVDB_BQ, Retriever, RAG
import json

load_dotenv()

app = FastAPI(title="Alwasaet RAG API")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global state management
sessions = {}
batch_size = 512

class QueryRequest(BaseModel):
    query: str
    session_id: str
    groq_api_key: str

class InitSessionRequest(BaseModel):
    groq_api_key: str

class SessionResponse(BaseModel):
    session_id: str
    message: str

class DocumentInfo(BaseModel):
    filename: str
    processed: bool

class SessionInfo(BaseModel):
    session_id: str
    documents: List[DocumentInfo]
    is_indexed: bool

def get_or_create_session(session_id: str = None, groq_api_key: str = None):
    if session_id and session_id in sessions:
        return sessions[session_id]
    
    new_session_id = session_id or str(uuid.uuid4())[:8]
    sessions[new_session_id] = {
        "id": new_session_id,
        "query_engine": None,
        "milvus_vdb": None,
        "embeddata": None,
        "processed_files": {},
        "is_indexed": False,
        "groq_api_key": groq_api_key or os.getenv("GROQ_API_KEY", "")
    }
    return sessions[new_session_id]

@app.post("/api/init-session", response_model=SessionResponse)
async def init_session(request: InitSessionRequest):
    """Initialize a new session"""
    session = get_or_create_session(groq_api_key=request.groq_api_key)
    return SessionResponse(
        session_id=session["id"],
        message="Session initialized successfully"
    )

@app.get("/api/session/{session_id}", response_model=SessionInfo)
async def get_session_info(session_id: str):
    """Get session information"""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = sessions[session_id]
    documents = [
        DocumentInfo(filename=filename, processed=processed)
        for filename, processed in session["processed_files"].items()
    ]
    
    return SessionInfo(
        session_id=session_id,
        documents=documents,
        is_indexed=session["is_indexed"]
    )

@app.post("/api/upload")
async def upload_documents(
    session_id: str,
    groq_api_key: str,
    files: List[UploadFile] = File(...)
):
    """Upload and process PDF documents"""
    try:
        session = get_or_create_session(session_id, groq_api_key)
        collection_name = f"docs_{session_id}"
        
        # Filter new files
        new_files = [f for f in files if f.filename not in session["processed_files"]]
        
        if not new_files:
            return JSONResponse(content={
                "message": "All files already processed",
                "processed_count": len(session["processed_files"])
            })
        
        # Save files and process
        with tempfile.TemporaryDirectory() as temp_dir:
            for file in new_files:
                file_path = os.path.join(temp_dir, file.filename)
                with open(file_path, "wb") as f:
                    content = await file.read()
                    f.write(content)
            
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
                        filename = doc.metadata['source'].split('/')[-1] if '/' in doc.metadata['source'] else doc.metadata['source']
                    
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
                
                if filename == "unknown" and new_files:
                    filename = new_files[0].filename
                
                metadata.append({
                    "filename": filename,
                    "page": page + 1
                })
            
            if not documents:
                raise HTTPException(status_code=400, detail="No text could be extracted from PDFs")
            
            # Process embeddings
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
                    groq_api_key=groq_api_key or session["groq_api_key"]
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
            
            # Mark files as processed
            for file in new_files:
                session["processed_files"][file.filename] = True
            
            session["is_indexed"] = True
        
        return JSONResponse(content={
            "message": f"Successfully processed {len(new_files)} document(s)",
            "processed_count": len(session["processed_files"]),
            "new_files": [f.filename for f in new_files]
        })
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/query")
async def query_documents(request: QueryRequest):
    """Query documents (non-streaming)"""
    try:
        if request.session_id not in sessions:
            raise HTTPException(status_code=404, detail="Session not found")
        
        session = sessions[request.session_id]
        
        if not session["is_indexed"] or session["query_engine"] is None:
            raise HTTPException(status_code=400, detail="Please upload and process documents first")
        
        query_engine = session["query_engine"]
        
        # Generate context and response
        start_time = time.perf_counter()
        context_text, citations = query_engine.generate_context_with_citations(query=request.query)
        retrieval_time = time.perf_counter() - start_time
        
        prompt_text = query_engine.prompt_template.format(context=context_text, query=request.query)
        response = query_engine.llm.complete(prompt_text)
        
        response_text = response.text
        
        # Append citations if available
        if citations and "Citation:" not in response_text:
            citation_text = f"\n\nCitation: {', '.join(citations)}"
            response_text += citation_text
        
        return JSONResponse(content={
            "response": response_text,
            "retrieval_time_ms": int(retrieval_time * 1000),
            "citations": citations
        })
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.websocket("/ws/chat/{session_id}")
async def websocket_chat(websocket: WebSocket, session_id: str):
    """WebSocket endpoint for streaming chat responses"""
    await websocket.accept()
    
    try:
        if session_id not in sessions:
            await websocket.send_json({
                "type": "error",
                "message": "Session not found"
            })
            await websocket.close()
            return
        
        session = sessions[session_id]
        
        if not session["is_indexed"] or session["query_engine"] is None:
            await websocket.send_json({
                "type": "error",
                "message": "Please upload and process documents first"
            })
            await websocket.close()
            return
        
        query_engine = session["query_engine"]
        
        # Receive query from client
        data = await websocket.receive_text()
        query_data = json.loads(data)
        query = query_data.get("query", "")
        
        if not query:
            await websocket.send_json({
                "type": "error",
                "message": "Query is required"
            })
            return
        
        # Generate context
        start_time = time.perf_counter()
        context_text, citations = query_engine.generate_context_with_citations(query=query)
        retrieval_time = time.perf_counter() - start_time
        
        # Send retrieval time
        await websocket.send_json({
            "type": "retrieval",
            "retrieval_time_ms": int(retrieval_time * 1000)
        })
        
        # Stream response
        prompt_text = query_engine.prompt_template.format(context=context_text, query=query)
        streaming_response = query_engine.llm.stream_complete(prompt_text)
        
        full_response = ""
        for chunk in streaming_response:
            try:
                if hasattr(chunk, 'delta') and chunk.delta:
                    new_text = chunk.delta
                elif hasattr(chunk, 'text') and chunk.text is not None:
                    candidate = chunk.text
                    if candidate.startswith(full_response):
                        new_text = candidate[len(full_response):]
                    else:
                        new_text = candidate
                else:
                    candidate = str(chunk)
                    new_text = candidate if not candidate.startswith(full_response) else ""
                
                if new_text:
                    full_response += new_text
                    await websocket.send_json({
                        "type": "chunk",
                        "content": new_text
                    })
            except Exception:
                continue
        
        # Send citations
        if citations and "Citation:" not in full_response:
            citation_text = f"\n\nCitation: {', '.join(citations)}"
            await websocket.send_json({
                "type": "chunk",
                "content": citation_text
            })
        
        # Send completion signal
        await websocket.send_json({
            "type": "done",
            "citations": citations
        })
    
    except WebSocketDisconnect:
        pass
    except Exception as e:
        await websocket.send_json({
            "type": "error",
            "message": str(e)
        })
    finally:
        try:
            await websocket.close()
        except:
            pass

@app.delete("/api/session/{session_id}")
async def delete_session(session_id: str):
    """Delete a session and cleanup resources"""
    if session_id in sessions:
        session = sessions[session_id]
        # Cleanup
        if session["milvus_vdb"]:
            try:
                session["milvus_vdb"].client.close()
            except:
                pass
        del sessions[session_id]
        gc.collect()
        return JSONResponse(content={"message": "Session deleted successfully"})
    raise HTTPException(status_code=404, detail="Session not found")

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "active_sessions": len(sessions)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
