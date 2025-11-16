# Deployment and Testing Guide

## Quick Start

### Option 1: Using Startup Scripts (Recommended for Development)

**Linux/Mac:**
```bash
chmod +x start.sh
./start.sh
```

**Windows:**
```bash
start.bat
```

The script will:
1. Create `.env` from `.env.example` if needed
2. Set up Python virtual environment
3. Install all dependencies
4. Start the FastAPI server on http://localhost:8000

### Option 2: Using Docker Compose (Recommended for Production)

```bash
# Make sure .env file exists with your GROQ_API_KEY
cp .env.example .env
# Edit .env and add your API key

# Start the application
docker-compose up --build

# Stop the application
docker-compose down
```

### Option 3: Manual Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env
# Edit .env and add your GROQ_API_KEY

# Run the server
python server.py
```

## Accessing the Application

Once started, access these URLs:

- **Main Chat Interface**: http://localhost:8000/
- **Admin Dashboard**: http://localhost:8000/dashboard
- **Login Page**: http://localhost:8000/login
- **API Documentation**: http://localhost:8000/docs
- **Alternative API Docs**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## Testing the Application

### 1. Test Login
1. Navigate to http://localhost:8000/login
2. Use credentials: `admin` / `admin123`
3. You should be redirected to the dashboard

### 2. Test Document Upload
1. In the admin dashboard, click the upload area
2. Select one or more PDF files
3. Wait for processing (requires valid GROQ_API_KEY)
4. Documents should appear in the "Uploaded Documents" section

### 3. Test Chat Interface
1. After uploading documents, use the chat interface in the dashboard
2. Ask questions about your documents
3. Verify you get answers with citations

### 4. Test API Endpoints

**Get Health Status:**
```bash
curl http://localhost:8000/health
```

**Login:**
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'
```

**Create Session (use token from login):**
```bash
curl -X POST http://localhost:8000/api/session/create \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

## Production Deployment

### Pre-Deployment Checklist

- [ ] Change default admin password in `backend/main.py`
- [ ] Set strong SECRET_KEY in `.env` (min 32 characters)
- [ ] Configure proper CORS origins in `backend/main.py`
- [ ] Set up HTTPS/TLS
- [ ] Configure proper database (replace in-memory storage)
- [ ] Set up monitoring and logging
- [ ] Configure backup strategy
- [ ] Set up rate limiting
- [ ] Review security headers

### Docker Production Deployment

1. **Build the image:**
```bash
docker build -f Dockerfile.fastapi -t alwasaet-rag:latest .
```

2. **Run the container:**
```bash
docker run -d \
  -p 8000:8000 \
  -e GROQ_API_KEY=your_key \
  -e SECRET_KEY=your_secret_key \
  --name alwasaet-rag \
  alwasaet-rag:latest
```

3. **Check logs:**
```bash
docker logs alwasaet-rag
```

### Environment Variables

Required:
- `GROQ_API_KEY`: Your Groq API key from https://console.groq.com/
- `SECRET_KEY`: Secret key for JWT token signing (min 32 chars)

Optional:
- `PORT`: Server port (default: 8000)

## Troubleshooting

### Server won't start
- Check if port 8000 is already in use
- Verify Python version (3.11+ required)
- Check if all dependencies are installed
- Review logs for specific errors

### Document upload fails
- Verify GROQ_API_KEY is set correctly
- Check if PDF files are valid
- Ensure sufficient disk space
- Review backend logs

### Authentication errors
- Verify SECRET_KEY is set
- Check if token has expired (24h default)
- Clear browser localStorage and try again

### Missing embeddings
- First upload may take time to download models
- Check HuggingFace model cache directory
- Ensure internet connection for initial download

## API Reference

See the interactive API documentation at http://localhost:8000/docs for:
- Complete endpoint descriptions
- Request/response schemas
- Try-it-out functionality
- Authentication examples

## Support

For issues:
1. Check the logs: `docker logs alwasaet-rag` or console output
2. Review API documentation at `/docs`
3. Check GitHub issues
4. Consult README_NEW.md for detailed information

## Migration from v1.0 (Streamlit)

The old Streamlit version (`app.py`) is still available:
```bash
streamlit run app.py
```

However, the new v2.0 FastAPI version is recommended for:
- Better security
- Professional UI
- API access
- Scalability
- Production deployment
