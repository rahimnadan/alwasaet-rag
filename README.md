---
title: Alwasaet RAG Application
emoji: "🚀"
colorFrom: blue
colorTo: purple
sdk: docker
app_port: 8501
pinned: false
license: mit
---

# Alwasaet RAG Application

> **🎉 Version 2.0 Now Available!** This application now features a professional FastAPI backend with admin dashboard. See [README_NEW.md](README_NEW.md) for the new architecture.

A multilingual RAG (Retrieval-Augmented Generation) application that supports:

- 📄 **Multiple PDF uploads**
- 🌍 **Arabic and English language support** 
- 📚 **Citation generation**
- ⚡ **Fast retrieval** with BGE-M3 embeddings
- 🔍 **Binary quantization** for efficient vector search
- 🔐 **Admin dashboard** for document management (v2.0)
- 💼 **Production-ready** FastAPI backend (v2.0)

## 🚀 Quick Start

### Version 2.0 (FastAPI + Modern UI) - Recommended

**Features:**
- Professional admin dashboard
- Secure authentication
- RESTful API
- Modern Tailwind CSS UI
- Production-ready

```bash
# Start the new version
./start.sh        # Linux/Mac
start.bat         # Windows
```

Or with Docker:
```bash
docker-compose up --build
```

Access at: http://localhost:8000

**See [README_NEW.md](README_NEW.md) for complete v2.0 documentation.**

### Version 1.0 (Streamlit) - Legacy

The original Streamlit version is still available:

```bash
streamlit run app.py
```

## 📖 Documentation

- **[Version 2.0 Documentation](README_NEW.md)** - FastAPI backend with admin dashboard (Recommended)
- **Version 1.0 Documentation** - Below (Streamlit-based)

---

## Version 1.0 Features

- Upload multiple PDF documents simultaneously
- Ask questions in Arabic or English
- Get accurate answers with source citations
- Powered by BGE-M3 multilingual embeddings
- Fast retrieval with <15ms latency
- Groq-powered inference for quick responses

## Version 1.0 Usage

1. Enter your Groq API key in the sidebar
2. Upload your PDF documents
3. Wait for processing to complete
4. Ask questions about your documents
5. Get answers with citations showing source and page numbers

## Technology Stack

### Version 2.0 (New)
- **Frontend**: HTML + Tailwind CSS + JavaScript
- **Backend**: FastAPI
- **Authentication**: JWT (JSON Web Tokens)
- **Database**: Milvus (in-memory for now)
- **Embeddings**: BGE-M3 (multilingual)
- **Vector DB**: Milvus with binary quantization
- **LLM**: Groq (Moonshot AI Kimi K2)

### Version 1.0 (Legacy)
- **Frontend**: Streamlit
- **Embeddings**: BGE-M3 (multilingual)
- **Vector DB**: Milvus with binary quantization
- **LLM**: Groq (Moonshot AI Kimi K2)
- **Languages**: Arabic, English, 100+ others

## Setup and Installation

Ensure you have Python 3.11 or later installed on your system.

First, let’s install uv and set up our Python project and environment:
```bash
# MacOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**Install dependencies**:

```bash
# Create a new directory for our project
uv init fastest-rag
cd fastest-rag

# Create virtual environment and activate it
uv venv
source .venv/bin/activate  # MacOS/Linux

.venv\Scripts\activate     # Windows

# Install dependencies
uv add pymilvus llama-index llama-index-embeddings-huggingface llama-index-llms-groq streamlit beam-client
```

**Setup Groq**:

Get an API key from [Groq](https://console.groq.com/) and set it in the `.env` file as follows:

```bash
GROQ_API_KEY=<YOUR_GROQ_API_KEY> 
```

**Run the app**:

  you can also run the app by running the following command:

   ```bash
   streamlit run app.py
   ```



