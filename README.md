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

A professional, multilingual RAG (Retrieval-Augmented Generation) application with a modern ChatGPT-like interface.

## Features

- 💬 **Professional Chat Interface** - ChatGPT-like design with smooth interactions
- 🎨 **Modern Admin Dashboard** - Full-screen dashboard with beautiful UI
- 📄 **Multiple PDF uploads** - Upload and process multiple documents
- 🌍 **Arabic and English support** - Multilingual capabilities
- 📚 **Citation generation** - Get answers with source references
- ⚡ **Fast retrieval** - BGE-M3 embeddings with <15ms latency
- 🔍 **Binary quantization** - Efficient vector search
- 🎯 **Real-time streaming** - WebSocket-based streaming responses

## Technology Stack

### Frontend
- **Framework**: Next.js 14 with TypeScript
- **Styling**: Tailwind CSS
- **UI**: Custom components with lucide-react icons
- **Real-time**: WebSocket for streaming

### Backend
- **API**: FastAPI with WebSocket support
- **Embeddings**: BGE-M3 (multilingual)
- **Vector DB**: Milvus with binary quantization
- **LLM**: Groq (Moonshot AI Kimi K2)
- **Languages**: Arabic, English, 100+ others

## Setup and Installation

### Prerequisites

- Python 3.11 or later
- Node.js 18 or later
- npm or yarn

### Installation Steps

1. **Clone the repository**:
```bash
git clone https://github.com/rahimnadan/alwasaet-rag.git
cd alwasaet-rag
```

2. **Install Python dependencies**:
```bash
pip install -r requirements.txt
```

3. **Install Frontend dependencies**:
```bash
cd frontend
npm install
cd ..
```

4. **Setup Groq API Key**:

Get an API key from [Groq](https://console.groq.com/) and set it in the `.env` file:

```bash
GROQ_API_KEY=<YOUR_GROQ_API_KEY> 
```

Or enter it directly in the Admin Dashboard UI.

## Running the Application

### Option 1: Using the start script (Recommended)

```bash
./start.sh
```

This will start both the backend and frontend services.

### Option 2: Manual start

**Terminal 1 - Start Backend**:
```bash
python backend.py
```

**Terminal 2 - Start Frontend**:
```bash
cd frontend
npm run dev
```

## Accessing the Application

- **Chat Interface**: http://localhost:3000
- **Admin Dashboard**: http://localhost:3000/admin
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## Usage Guide

### Admin Dashboard

1. Open http://localhost:3000/admin
2. Enter your Groq API key
3. Click "Initialize" to create a session
4. Upload PDF documents using the upload area
5. Wait for processing to complete
6. Navigate to the Chat Interface

### Chat Interface

1. Open http://localhost:3000 (or click "Go to Chat" from Admin)
2. Type your questions in the input field
3. Get AI-powered answers with citations
4. View source documents in the response

## API Endpoints

- `POST /api/init-session` - Initialize a new session
- `GET /api/session/{session_id}` - Get session information
- `POST /api/upload` - Upload and process documents
- `POST /api/query` - Query documents (non-streaming)
- `WS /ws/chat/{session_id}` - WebSocket for streaming chat
- `DELETE /api/session/{session_id}` - Delete session
- `GET /api/health` - Health check

## Architecture

```
┌─────────────────┐
│   Next.js UI    │  (Port 3000)
│  - Chat Page    │
│  - Admin Page   │
└────────┬────────┘
         │ HTTP/WebSocket
┌────────▼────────┐
│  FastAPI Backend│  (Port 8000)
│  - REST API     │
│  - WebSocket    │
└────────┬────────┘
         │
    ┌────▼─────┬──────────┐
┌───▼───┐ ┌────▼────┐ ┌───▼────┐
│BGE-M3 │ │ Milvus  │ │ Groq   │
│Embed  │ │Vector DB│ │  LLM   │
└───────┘ └─────────┘ └────────┘
```

## Development

### Frontend Development

```bash
cd frontend
npm run dev     # Start dev server
npm run build   # Build for production
npm run start   # Start production server
npm run lint    # Run linter
```

### Backend Development

```bash
# Start with auto-reload
uvicorn backend:app --reload --host 0.0.0.0 --port 8000

# Run tests (if available)
pytest
```

## Features Overview

### Chat Interface
- Clean, modern ChatGPT-like design
- Real-time streaming responses
- Message history
- Citation badges showing document sources
- Responsive layout

### Admin Dashboard
- Full-screen professional design
- Beautiful gradient cards
- Interactive file upload with drag & drop
- Real-time document processing status
- Quick stats overview
- Session management

## License

MIT License - see LICENSE file for details

## Support

For issues and questions, please open an issue on GitHub.
