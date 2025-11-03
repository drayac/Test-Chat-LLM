FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create directory for user data
RUN mkdir -p /app/data

# Expose port
EXPOSE 8510

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8510/_stcore/health || exit 1

# Run the application
CMD ["streamlit", "run", "app_groq_chat.py", "--server.port=8510", "--server.address=0.0.0.0", "--server.headless=true", "--server.enableCORS=false"]