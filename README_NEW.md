# Alwasaet RAG Application - Production Ready

A professional, production-ready RAG (Retrieval-Augmented Generation) application with modern architecture, featuring a FastAPI backend and polished frontend with admin dashboard.

![Version](https://img.shields.io/badge/version-2.0.0-blue)
![Python](https://img.shields.io/badge/python-3.11+-green)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-teal)
![License](https://img.shields.io/badge/license-MIT-orange)

## 🚀 Features

### Core Capabilities
- 📄 **Multiple PDF Document Support** - Upload and process multiple PDFs simultaneously
- 🌍 **Multilingual Support** - Arabic, English, and 100+ languages
- 📚 **Smart Citations** - Get answers with source document and page references
- ⚡ **Fast Retrieval** - BGE-M3 embeddings with binary quantization for <15ms latency
- 🔍 **Accurate RAG** - Powered by Groq (Moonshot AI Kimi K2) for high-quality responses

### Professional Features
- 🔐 **Secure Authentication** - JWT-based authentication system
- 👨‍💼 **Admin Dashboard** - Full document management interface
- 💬 **Modern Chat Interface** - Real-time chat with streaming responses
- 📊 **System Statistics** - Monitor sessions, documents, and usage
- 🎨 **Professional UI** - Built with Tailwind CSS, fully responsive
- 🐳 **Docker Support** - Easy deployment with Docker and docker-compose
- 📖 **API Documentation** - Interactive Swagger/OpenAPI docs

## 🏗️ Architecture

### Backend (FastAPI)
```
backend/
├── main.py          # FastAPI application with all API endpoints
└── ...              # Additional modules as needed
```

**Key Endpoints:**
- `POST /api/auth/login` - User authentication
- `POST /api/session/create` - Create RAG session
- `POST /api/documents/upload` - Upload and process PDFs
- `GET /api/documents/list` - List all documents
- `DELETE /api/documents/{id}` - Delete document
- `POST /api/query` - Query documents with RAG
- `GET /api/stats` - System statistics
- `GET /health` - Health check

### Frontend
```
frontend/
├── templates/
│   ├── login.html       # Admin login page
│   ├── dashboard.html   # Admin dashboard
│   └── index.html       # Public chat interface
└── static/              # Static assets (CSS, JS, images)
```

### Core RAG Engine
```
rag.py                   # RAG implementation with Milvus & BGE-M3
```

## 📦 Technology Stack

### Backend
- **Framework**: FastAPI
- **Authentication**: JWT (PyJWT, Passlib)
- **Vector Database**: Milvus with binary quantization
- **Embeddings**: BGE-M3 (multilingual)
- **LLM**: Groq (Moonshot AI Kimi K2)
- **Document Processing**: LlamaIndex

### Frontend
- **Styling**: Tailwind CSS
- **Icons**: Font Awesome 6
- **JavaScript**: Vanilla JS (no framework dependencies)
- **Design**: Responsive, mobile-first

## 🚀 Quick Start

### Prerequisites
- Python 3.11 or later
- Docker & Docker Compose (optional)
- Groq API key ([Get one here](https://console.groq.com/))

### Option 1: Docker (Recommended)

1. **Clone the repository**
```bash
git clone https://github.com/rahimnadan/alwasaet-rag.git
cd alwasaet-rag
```

2. **Set up environment variables**
```bash
cp .env.example .env
# Edit .env and add your GROQ_API_KEY
```

3. **Run with Docker Compose**
```bash
docker-compose up --build
```

4. **Access the application**
- Main Interface: http://localhost:8000
- Admin Dashboard: http://localhost:8000/dashboard
- API Docs: http://localhost:8000/docs

### Option 2: Local Development

1. **Clone and setup**
```bash
git clone https://github.com/rahimnadan/alwasaet-rag.git
cd alwasaet-rag
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up environment**
```bash
cp .env.example .env
# Edit .env and add your GROQ_API_KEY
```

5. **Run the server**
```bash
python server.py
```

6. **Access the application**
- Main Interface: http://localhost:8000
- Admin Dashboard: http://localhost:8000/dashboard
- API Docs: http://localhost:8000/docs

## 🔐 Default Credentials

For the admin dashboard:
- **Username**: `admin`
- **Password**: `admin123`

⚠️ **Important**: Change these credentials in production by modifying `backend/main.py`

## 📖 Usage Guide

### Admin Dashboard

1. **Login**: Navigate to `/login` and use admin credentials
2. **Upload Documents**: 
   - Drag and drop PDF files or click to browse
   - Multiple files supported
   - Progress indicator shows upload status
3. **Manage Documents**: 
   - View all uploaded documents
   - Delete documents as needed
4. **Test Chat**: Use the integrated chat to test document queries
5. **Monitor Stats**: View system statistics in real-time

### User Chat Interface

1. Navigate to the main page (`/`)
2. Type questions in the chat input
3. Get AI-powered answers with citations
4. Works in Arabic, English, and other languages

### API Integration

Example using cURL:

```bash
# Login
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'

# Create session (use token from login)
curl -X POST http://localhost:8000/api/session/create \
  -H "Authorization: Bearer YOUR_TOKEN"

# Upload document
curl -X POST "http://localhost:8000/api/documents/upload?session_id=SESSION_ID" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "files=@document.pdf"

# Query documents
curl -X POST http://localhost:8000/api/query \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is the main topic?",
    "session_id": "SESSION_ID",
    "top_k": 5
  }'
```

## 🛠️ Configuration

### Environment Variables

Create a `.env` file with:

```env
GROQ_API_KEY=your_groq_api_key_here
SECRET_KEY=your-secret-jwt-key-min-32-characters
PORT=8000
```

### Security Settings

In `backend/main.py`, configure:
- JWT expiration time
- CORS origins
- User credentials
- Rate limiting (add as needed)

## 🚢 Deployment

### Docker Deployment

Use the provided `Dockerfile.fastapi`:

```bash
docker build -f Dockerfile.fastapi -t alwasaet-rag:latest .
docker run -p 8000:8000 --env-file .env alwasaet-rag:latest
```

### Production Checklist

- [ ] Change default admin credentials
- [ ] Set strong SECRET_KEY (min 32 characters)
- [ ] Configure proper CORS origins
- [ ] Enable HTTPS/TLS
- [ ] Set up proper database (replace in-memory storage)
- [ ] Configure rate limiting
- [ ] Set up monitoring and logging
- [ ] Configure backup strategy
- [ ] Set up CI/CD pipeline

## 📊 API Documentation

Interactive API documentation is available at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 🧪 Testing

```bash
# Test health endpoint
curl http://localhost:8000/health

# Test API with authentication
# (See Usage Guide for detailed examples)
```

## 📝 Project Structure

```
alwasaet-rag/
├── backend/
│   └── main.py              # FastAPI application
├── frontend/
│   ├── templates/
│   │   ├── login.html       # Login page
│   │   ├── dashboard.html   # Admin dashboard
│   │   └── index.html       # Chat interface
│   └── static/              # Static files
├── rag.py                   # RAG core engine
├── server.py                # Main server file
├── requirements.txt         # Python dependencies
├── Dockerfile.fastapi       # FastAPI Dockerfile
├── docker-compose.yml       # Docker Compose config
├── .env.example             # Environment template
├── .gitignore              # Git ignore rules
└── README_NEW.md           # This file
```

## 🤝 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- **BGE-M3**: Multilingual embeddings by BAAI
- **Groq**: Fast LLM inference
- **Milvus**: Vector database
- **FastAPI**: Modern Python web framework
- **Tailwind CSS**: Utility-first CSS framework

## 📞 Support

For issues and questions:
- Open an issue on GitHub
- Check the API documentation at `/docs`

## 🔄 Migration from v1.0

If you're migrating from the Streamlit version:

1. **Data Migration**: Sessions are now managed via API, no automatic migration
2. **Authentication**: New JWT-based auth system
3. **Configuration**: Update environment variables (see `.env.example`)
4. **Deployment**: Use new Docker setup or FastAPI server

---

**Made with ❤️ for production-ready document intelligence**
