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
    st.header("📚 Add your documents!")

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
                    st.text("Generating embeddings...")

                    # Check if we need to initialize embeddings and vector DB
                    if "query_engine" not in st.session_state.file_cache:
                        # First time setup
                        embeddata = EmbedData(
                            embed_model_name="BAAI/bge-m3",
                            batch_size=batch_size
                        )
                        embeddata.embed(documents, metadata)
                        progress_bar.progress(40)
                        st.text("Creating vector index...")

                        db_file = os.path.join(tempfile.gettempdir(), f"milvus_{session_id}.db")
                        
                        test_embedding = embeddata.embed_model.get_text_embedding("test")
                        actual_dim = len(test_embedding)

                        milvus_vdb = MilvusVDB_BQ(
                            collection_name=collection_name,
                            batch_size=batch_size,
                            vector_dim=actual_dim,
                            db_file=db_file
                        )
                        progress_bar.progress(60)
                        st.text("Storing in vector DB...")

                        milvus_vdb.define_client()
                        milvus_vdb.create_collection(drop_existing=True)
                        milvus_vdb.ingest_data(embeddata=embeddata)
                        
                        progress_bar.progress(80)
                        st.text("Creating query engine...")

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
                        st.text("Adding to vector DB...")
                        
                        # Add new embeddings to existing collection
                        milvus_vdb.ingest_data(embeddata=new_embeddata)
                        progress_bar.progress(80)

                    progress_bar.progress(100)
                    
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
col1, col2 = st.columns([6, 1])

with col1:
    st.markdown('''
        <h1 style="text-align: center; font-weight: 500;">
            🚀 Alwasaet RAG Application
        </h1>
    ''', unsafe_allow_html=True)

with col2:
    st.button("Clear ↺", on_click=reset_chat, key="clear_button")

# Initialize chat history
if "messages" not in st.session_state:
    reset_chat()

# Display chat messages from history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Ask a question about your documents..."):
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
            st.caption(f"⏱️ Retrieval time: {retrieval_ms} ms")

        except Exception as e:
            st.error(f"Error generating response: {str(e)}")
            full_response = "I apologize, but I encountered an error while processing your question. Please try again."
            message_placeholder.markdown(full_response)

    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": full_response})