import os
import gc
import tempfile
import time
import uuid
import streamlit as st
from dotenv import load_dotenv
from llama_index.core import SimpleDirectoryReader
from rag import EmbedData, MilvusVDB_BQ, Retriever, RAG

load_dotenv()

# Professional CSS styling
st.markdown("""
<style>
    /* Main container styling */
    .main {
        background: linear-gradient(135deg, #F8FAFC 0%, #F1F5F9 100%);
        padding: 2rem;
    }
    
    /* Header styling */
    .main-header {
        background: linear-gradient(135deg, #6366F1 0%, #8B5CF6 100%);
        padding: 2rem;
        border-radius: 16px;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(99, 102, 241, 0.2);
    }
    
    .main-header h1 {
        color: white !important;
        font-weight: 700 !important;
        font-size: 2.5rem !important;
        margin: 0 !important;
        text-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #FFFFFF 0%, #F8FAFC 100%);
        border-right: 1px solid #E2E8F0;
        box-shadow: 2px 0 10px rgba(0,0,0,0.05);
    }
    
    [data-testid="stSidebar"] h2 {
        color: #6366F1 !important;
        font-weight: 700 !important;
        font-size: 1.5rem !important;
        padding: 1rem 0;
        border-bottom: 2px solid #6366F1;
        margin-bottom: 1.5rem !important;
    }
    
    /* File uploader styling */
    [data-testid="stFileUploader"] {
        background: white;
        border: 2px dashed #6366F1;
        border-radius: 12px;
        padding: 1.5rem;
        transition: all 0.3s ease;
    }
    
    [data-testid="stFileUploader"]:hover {
        border-color: #8B5CF6;
        box-shadow: 0 4px 12px rgba(99, 102, 241, 0.15);
        transform: translateY(-2px);
    }
    
    /* Input field styling */
    .stTextInput > div > div > input {
        border: 2px solid #E2E8F0;
        border-radius: 10px;
        padding: 0.75rem 1rem;
        font-size: 1rem;
        transition: all 0.3s ease;
        background: white;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #6366F1;
        box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #6366F1 0%, #8B5CF6 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        font-size: 1rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3);
        cursor: pointer;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(99, 102, 241, 0.4);
    }
    
    .stButton > button:active {
        transform: translateY(0);
    }
    
    /* Chat message styling */
    [data-testid="stChatMessage"] {
        background: white;
        border-radius: 12px;
        padding: 1rem;
        margin: 0.5rem 0;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
        transition: all 0.3s ease;
    }
    
    [data-testid="stChatMessage"]:hover {
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
    }
    
    /* User message styling */
    [data-testid="stChatMessage"][data-testid*="user"] {
        background: linear-gradient(135deg, #EEF2FF 0%, #E0E7FF 100%);
        border-left: 4px solid #6366F1;
    }
    
    /* Assistant message styling */
    [data-testid="stChatMessage"][data-testid*="assistant"] {
        background: white;
        border-left: 4px solid #8B5CF6;
    }
    
    /* Chat input styling */
    [data-testid="stChatInput"] {
        background: white;
        border: 2px solid #E2E8F0;
        border-radius: 12px;
        padding: 0.5rem;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    }
    
    [data-testid="stChatInput"]:focus-within {
        border-color: #6366F1;
        box-shadow: 0 4px 20px rgba(99, 102, 241, 0.2);
    }
    
    /* Success message styling */
    .stSuccess {
        background: linear-gradient(135deg, #ECFDF5 0%, #D1FAE5 100%);
        border-left: 4px solid #10B981;
        border-radius: 10px;
        padding: 1rem;
        color: #065F46;
    }
    
    /* Info message styling */
    .stInfo {
        background: linear-gradient(135deg, #EFF6FF 0%, #DBEAFE 100%);
        border-left: 4px solid #3B82F6;
        border-radius: 10px;
        padding: 1rem;
        color: #1E40AF;
    }
    
    /* Warning message styling */
    .stWarning {
        background: linear-gradient(135deg, #FFFBEB 0%, #FEF3C7 100%);
        border-left: 4px solid #F59E0B;
        border-radius: 10px;
        padding: 1rem;
        color: #92400E;
    }
    
    /* Error message styling */
    .stError {
        background: linear-gradient(135deg, #FEF2F2 0%, #FEE2E2 100%);
        border-left: 4px solid #EF4444;
        border-radius: 10px;
        padding: 1rem;
        color: #991B1B;
    }
    
    /* Progress bar styling */
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #6366F1 0%, #8B5CF6 100%);
        border-radius: 10px;
    }
    
    /* Metric styling */
    [data-testid="stMetric"] {
        background: white;
        border-radius: 12px;
        padding: 1rem;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
    }
    
    /* Caption styling */
    .stCaption {
        color: #64748B !important;
        font-size: 0.875rem !important;
        font-style: italic;
    }
    
    /* Scrollbar styling */
    ::-webkit-scrollbar {
        width: 10px;
        height: 10px;
    }
    
    ::-webkit-scrollbar-track {
        background: #F1F5F9;
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(180deg, #6366F1 0%, #8B5CF6 100%);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(180deg, #4F46E5 0%, #7C3AED 100%);
    }
    
    /* Animation for loading */
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }
    
    .stSpinner > div {
        border-color: #6366F1 !important;
    }
    
    /* Card-like containers */
    .element-container {
        transition: all 0.3s ease;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Responsive design */
    @media (max-width: 768px) {
        .main-header h1 {
            font-size: 1.8rem !important;
        }
        
        .main {
            padding: 1rem;
        }
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "id" not in st.session_state:
    st.session_state.id = str(uuid.uuid4())[:8]
    st.session_state.file_cache = {}
    st.session_state.is_indexed = False
    st.session_state.uploaded_files = []  # List to track multiple files
    st.session_state.processed_files = {}  # Dict to track processed files
    st.session_state.groq_api_key = os.getenv("GROQ_API_KEY", "")

session_id = st.session_state.id
collection_name = f"docs_{session_id}"  # Unique collection per session
batch_size = 512

def reset_chat():
    st.session_state.messages = []
    st.session_state.context = None
    gc.collect()

with st.sidebar:
    st.markdown("## 📚 Add your documents!")

    groq_api_key = st.text_input(
        "🔑 Enter your Groq API Key:",
        type="password",
        value=st.session_state.groq_api_key,
        help="Get your API key from https://console.groq.com/",
        key="groq_api_key"
    )
    
    if groq_api_key != st.session_state.groq_api_key:
        st.session_state.groq_api_key = groq_api_key

    uploaded_files = st.file_uploader("Choose your `.pdf` files", type="pdf", accept_multiple_files=True, key="pdf_uploader")
    
    # Check for new files
    current_file_names = [f.name for f in uploaded_files] if uploaded_files else []
    if current_file_names != st.session_state.uploaded_files:
        st.session_state.uploaded_files = current_file_names
        # Mark new files as not indexed
        for file_name in current_file_names:
            if file_name not in st.session_state.processed_files:
                st.session_state.processed_files[file_name] = False

    if st.session_state.uploaded_files:
        processed_count = sum(1 for status in st.session_state.processed_files.values() if status)
        total_count = len(st.session_state.uploaded_files)
        if processed_count == total_count and total_count > 0:
            st.success(f"✅ All {total_count} documents processed and ready for chat!")
        elif processed_count > 0:
            st.info(f"📄 {processed_count}/{total_count} documents processed")

    if uploaded_files and groq_api_key:
        try:
            # Process new files
            new_files_to_process = []
            for uploaded_file in uploaded_files:
                if not st.session_state.processed_files.get(uploaded_file.name, False):
                    new_files_to_process.append(uploaded_file)
            
            if new_files_to_process:
                with tempfile.TemporaryDirectory() as temp_dir:
                    # Save all new files to temp directory
                    for uploaded_file in new_files_to_process:
                        file_path = os.path.join(temp_dir, uploaded_file.name)
                        with open(file_path, "wb") as f:
                            f.write(uploaded_file.getvalue())

                    st.write(f"Indexing {len(new_files_to_process)} new document(s)...")

                    loader = SimpleDirectoryReader(
                        input_dir=temp_dir,
                        required_exts=[".pdf"],
                        recursive=True
                    )

                    docs = loader.load_data()
                    documents = [doc.text for doc in docs]
                    
                    # Extract metadata from documents
                    metadata = []
                    for doc in docs:
                        # Extract filename from document metadata
                        filename = "unknown"
                        page = 0
                        
                        if hasattr(doc, 'metadata') and doc.metadata:
                            # Get filename from metadata
                            if 'file_name' in doc.metadata:
                                filename = doc.metadata['file_name']
                            elif 'source' in doc.metadata:
                                filename = doc.metadata['source'].split('/')[-1] if '/' in doc.metadata['source'] else doc.metadata['source']
                            
                            # Get page number from metadata
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
                        
                        # If filename is still unknown, try to get it from uploaded files
                        if filename == "unknown" and new_files_to_process:
                            for uploaded_file in new_files_to_process:
                                if uploaded_file.name.replace('.pdf', '') in doc.text[:100]:
                                    filename = uploaded_file.name
                                    break
                            if filename == "unknown":
                                filename = new_files_to_process[0].name  # Default to first file
                        
                        metadata.append({
                            "filename": filename,
                            "page": page + 1  # Convert to 1-based page numbering
                        })

                    if not documents:
                        st.error("No text could be extracted from the PDFs. Please try different files.")
                        st.stop()

                    progress_bar = st.progress(0)
                    status_placeholder = st.empty()
                    status_placeholder.markdown("""
                        <div style="
                            background: linear-gradient(135deg, #EFF6FF 0%, #DBEAFE 100%);
                            border-radius: 10px;
                            padding: 0.75rem 1rem;
                            border-left: 4px solid #3B82F6;
                        ">
                            <p style="color: #1E40AF; margin: 0; font-weight: 600;">⚙️ Generating embeddings...</p>
                        </div>
                    """, unsafe_allow_html=True)

                    # Check if we need to initialize embeddings and vector DB
                    if "query_engine" not in st.session_state.file_cache:
                        # First time setup
                        embeddata = EmbedData(
                            embed_model_name="BAAI/bge-m3",
                            batch_size=batch_size
                        )
                        embeddata.embed(documents, metadata)
                        progress_bar.progress(40)
                        status_placeholder.markdown("""
                            <div style="
                                background: linear-gradient(135deg, #EFF6FF 0%, #DBEAFE 100%);
                                border-radius: 10px;
                                padding: 0.75rem 1rem;
                                border-left: 4px solid #3B82F6;
                            ">
                                <p style="color: #1E40AF; margin: 0; font-weight: 600;">🔧 Creating vector index...</p>
                            </div>
                        """, unsafe_allow_html=True)

                        db_file = os.path.join(tempfile.gettempdir(), f"milvus_{session_id}.db")
                        
                        test_embedding = embeddata.embed_model.encode("test")
                        actual_dim = len(test_embedding)

                        milvus_vdb = MilvusVDB_BQ(
                            collection_name=collection_name,
                            batch_size=batch_size,
                            vector_dim=actual_dim,
                            db_file=db_file
                        )
                        progress_bar.progress(60)
                        status_placeholder.markdown("""
                            <div style="
                                background: linear-gradient(135deg, #EFF6FF 0%, #DBEAFE 100%);
                                border-radius: 10px;
                                padding: 0.75rem 1rem;
                                border-left: 4px solid #3B82F6;
                            ">
                                <p style="color: #1E40AF; margin: 0; font-weight: 600;">💾 Storing in vector database...</p>
                            </div>
                        """, unsafe_allow_html=True)

                        milvus_vdb.define_client()
                        milvus_vdb.create_collection(drop_existing=True)
                        milvus_vdb.ingest_data(embeddata=embeddata)
                        
                        progress_bar.progress(80)
                        status_placeholder.markdown("""
                            <div style="
                                background: linear-gradient(135deg, #EFF6FF 0%, #DBEAFE 100%);
                                border-radius: 10px;
                                padding: 0.75rem 1rem;
                                border-left: 4px solid #3B82F6;
                            ">
                                <p style="color: #1E40AF; margin: 0; font-weight: 600;">🚀 Creating query engine...</p>
                            </div>
                        """, unsafe_allow_html=True)

                        retriever = Retriever(vector_db=milvus_vdb, embeddata=embeddata)
                        query_engine = RAG(
                            retriever=retriever,
                            llm_model="moonshotai/kimi-k2-instruct",
                            groq_api_key=groq_api_key
                        )

                        st.session_state.file_cache["query_engine"] = query_engine
                        st.session_state.file_cache["milvus_vdb"] = milvus_vdb
                        st.session_state.file_cache["embeddata"] = embeddata
                    else:
                        # Add to existing collection
                        embeddata = st.session_state.file_cache["embeddata"]
                        milvus_vdb = st.session_state.file_cache["milvus_vdb"]
                        
                        # Generate embeddings for new documents
                        new_embeddata = EmbedData(
                            embed_model_name="BAAI/bge-m3",
                            batch_size=batch_size
                        )
                        new_embeddata.embed(documents, metadata)
                        progress_bar.progress(60)
                        status_placeholder.markdown("""
                            <div style="
                                background: linear-gradient(135deg, #EFF6FF 0%, #DBEAFE 100%);
                                border-radius: 10px;
                                padding: 0.75rem 1rem;
                                border-left: 4px solid #3B82F6;
                            ">
                                <p style="color: #1E40AF; margin: 0; font-weight: 600;">➕ Adding to vector database...</p>
                            </div>
                        """, unsafe_allow_html=True)
                        
                        # Add new embeddings to existing collection
                        milvus_vdb.ingest_data(embeddata=new_embeddata)
                        progress_bar.progress(80)

                    progress_bar.progress(100)
                    status_placeholder.empty()  # Clear status message
                    
                    # Mark files as processed
                    for uploaded_file in new_files_to_process:
                        st.session_state.processed_files[uploaded_file.name] = True
                    
                    st.session_state.is_indexed = True
                
                st.success(f"✅ Added {len(new_files_to_process)} new document(s)!")
            
            if uploaded_files:
                st.info(f"📄 Total documents: {len(uploaded_files)}")
                # Display preview of first PDF
                # display_pdf(uploaded_files[0]) # This line is removed

        except Exception as e:
            st.error(f"❌ An error occurred: {e}")
            st.stop()

    elif uploaded_files and not groq_api_key:
        st.warning("⚠️ Please enter your Groq API key to process the documents.")
    elif not uploaded_files:
        st.info("👆 Upload PDF files to get started!")

# Main chat interface
st.markdown('''
    <div class="main-header">
        <h1>🚀 Alwasaet RAG Application</h1>
        <p style="color: rgba(255,255,255,0.9); font-size: 1.1rem; margin-top: 0.5rem;">
            Multilingual AI-Powered Document Intelligence
        </p>
    </div>
''', unsafe_allow_html=True)

col1, col2 = st.columns([6, 1])

with col1:
    pass  # Header is now displayed above

with col2:
    st.markdown("""
        <style>
        div[data-testid="column"]:nth-of-type(2) button {
            background: linear-gradient(135deg, #EF4444 0%, #DC2626 100%) !important;
            color: white !important;
            border-radius: 10px !important;
            padding: 0.5rem 1.5rem !important;
            font-weight: 600 !important;
            box-shadow: 0 4px 12px rgba(239, 68, 68, 0.3) !important;
        }
        div[data-testid="column"]:nth-of-type(2) button:hover {
            background: linear-gradient(135deg, #DC2626 0%, #B91C1C 100%) !important;
            transform: translateY(-2px) !important;
            box-shadow: 0 6px 20px rgba(239, 68, 68, 0.4) !important;
        }
        </style>
    """, unsafe_allow_html=True)
    st.button("🗑️ Clear Chat", on_click=reset_chat, key="clear_button")

# Initialize chat history
if "messages" not in st.session_state:
    reset_chat()

# Display welcome message when no documents are uploaded
if not st.session_state.is_indexed and not st.session_state.messages:
    st.markdown("""
        <div style="
            background: linear-gradient(135deg, #EFF6FF 0%, #DBEAFE 100%);
            border-radius: 16px;
            padding: 2rem;
            margin: 2rem 0;
            border-left: 4px solid #3B82F6;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
        ">
            <h2 style="color: #1E40AF; margin-top: 0;">👋 Welcome to Alwasaet RAG!</h2>
            <p style="color: #1E3A8A; font-size: 1.1rem; line-height: 1.6;">
                Upload your PDF documents in the sidebar to get started. Our AI will help you:
            </p>
            <ul style="color: #1E3A8A; font-size: 1rem; line-height: 1.8;">
                <li>📄 <strong>Extract insights</strong> from multiple documents simultaneously</li>
                <li>🌍 <strong>Ask questions</strong> in Arabic, English, or 100+ languages</li>
                <li>⚡ <strong>Get instant answers</strong> with source citations</li>
                <li>🔍 <strong>Fast retrieval</strong> with cutting-edge embeddings</li>
            </ul>
            <p style="color: #1E3A8A; font-size: 0.95rem; margin-top: 1rem;">
                <em>💡 Tip: Enter your Groq API key in the sidebar and upload your PDFs to begin!</em>
            </p>
        </div>
    """, unsafe_allow_html=True)

# Display chat messages from history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("💬 Ask a question about your documents... (Supports Arabic & English)"):
    if not st.session_state.is_indexed or "query_engine" not in st.session_state.file_cache:
        st.error("Please upload and process PDF documents first!")
        st.stop()

    query_engine = st.session_state.file_cache["query_engine"]

    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        try:
            # Measure retrieval time
            retrieval_start = time.perf_counter()
            context_text, citations = query_engine.generate_context_with_citations(query=prompt)
            retrieval_time = time.perf_counter() - retrieval_start

            prompt_text = query_engine.prompt_template.format(context=context_text, query=prompt)
            # Call the LLM for streaming
            streaming_response = query_engine.llm.stream_complete(prompt_text)

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
                        message_placeholder.markdown(full_response + "▌")
                except Exception:
                    continue

            # Always append citations if available
            if citations:
                citation_text = f"\n\nCitation: {', '.join(citations)}"
                # Check if citation is not already in the response
                if "Citation:" not in full_response:
                    full_response += citation_text

            message_placeholder.markdown(full_response)

            retrieval_ms = int(retrieval_time * 1000)
            st.markdown(f"""
                <div style="
                    display: inline-block;
                    background: linear-gradient(135deg, #F0FDF4 0%, #DCFCE7 100%);
                    border-radius: 8px;
                    padding: 0.5rem 1rem;
                    margin-top: 0.5rem;
                    border-left: 3px solid #10B981;
                ">
                    <span style="color: #065F46; font-weight: 600;">⏱️ Retrieval: {retrieval_ms}ms</span>
                </div>
            """, unsafe_allow_html=True)

        except Exception as e:
            st.error(f"Error generating response: {str(e)}")
            full_response = "I apologize, but I encountered an error while processing your question. Please try again."
            message_placeholder.markdown(full_response)

    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": full_response})