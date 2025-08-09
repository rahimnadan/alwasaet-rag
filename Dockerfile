# Use Python 3.11 for better compatibility with all dependencies
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Set environment variables for better performance
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV TOKENIZERS_PARALLELISM=false
ENV HF_HOME=/app/hf_cache
ENV TRANSFORMERS_CACHE=/app/hf_cache
ENV SENTENCE_TRANSFORMERS_HOME=/app/hf_cache

# Install system dependencies required for PDF processing and compilation
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    git \
    poppler-utils \
    tesseract-ocr \
    && rm -rf /var/lib/apt/lists/*

# Create necessary directories
RUN mkdir -p /app/hf_cache /tmp/milvus

# Install specific protobuf version first to avoid conflicts
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir "protobuf>=3.20.0,<5.0.0" "grpcio>=1.60.0"

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy Streamlit configuration
COPY .streamlit/ .streamlit/

# Copy application code
COPY app.py .
COPY rag.py .

# Create a non-root user for security
RUN useradd -m -u 1000 streamlit && \
    chown -R streamlit:streamlit /app
USER streamlit

# Expose Streamlit port
EXPOSE 8501

# Health check to ensure the app is running
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

# Run Streamlit with optimized configuration for Hugging Face Spaces
CMD ["streamlit", "run", "app.py", \
     "--server.port=8501", \
     "--server.address=0.0.0.0", \
     "--server.headless=true", \
     "--server.enableCORS=false", \
     "--server.enableXsrfProtection=false", \
     "--browser.gatherUsageStats=false"]
