# Deployment Guide - LLM-library Chat Test

This guide covers various deployment options for the LLM-library Chat Test application.

## 🏠 Local Development

### Quick Start
```bash
chmod +x launch_groq_app.sh
./launch_groq_app.sh
```

### Manual Setup
```bash
python3 -m venv groq_env
source groq_env/bin/activate
pip install -r requirements.txt
streamlit run app_groq_chat.py --server.port 8510
```

## 🐳 Docker Deployment

### Build and Run
```bash
# Build the image
docker build -t llm-library-chat .

# Run with environment variable
docker run -p 8510:8510 -e GROQ_API_KEY=your_api_key llm-library-chat

# Or with docker-compose
docker-compose up -d
```

### Production Docker with Environment File
```bash
# Create .env file
echo "GROQ_API_KEY=your_api_key_here" > .env

# Run with docker-compose
docker-compose up -d
```

## ☁️ Cloud Deployment

### Streamlit Cloud
1. **Push to GitHub**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/yourusername/llm-library-chat.git
   git push -u origin main
   ```

2. **Deploy to Streamlit Cloud**
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Connect your GitHub account
   - Select your repository
   - Add secrets in the dashboard:
     ```
     GROQ_API_KEY = "your_api_key_here"
     ```

### Railway
1. **Install Railway CLI**
   ```bash
   npm install -g @railway/cli
   ```

2. **Deploy**
   ```bash
   railway login
   railway init
   railway add
   railway deploy
   ```

3. **Set Environment Variables**
   ```bash
   railway variables set GROQ_API_KEY=your_api_key_here
   ```

### Heroku
1. **Install Heroku CLI and login**
   ```bash
   heroku login
   ```

2. **Create app and deploy**
   ```bash
   heroku create your-app-name
   heroku config:set GROQ_API_KEY=your_api_key_here
   git push heroku main
   ```

### Google Cloud Run
1. **Build and push to Container Registry**
   ```bash
   gcloud builds submit --tag gcr.io/PROJECT_ID/llm-library-chat
   ```

2. **Deploy to Cloud Run**
   ```bash
   gcloud run deploy --image gcr.io/PROJECT_ID/llm-library-chat \
     --platform managed \
     --port 8510 \
     --set-env-vars GROQ_API_KEY=your_api_key_here
   ```

### AWS (EC2 with Docker)
1. **Launch EC2 instance** (Ubuntu 20.04+ recommended)

2. **Install Docker**
   ```bash
   sudo apt update
   sudo apt install docker.io docker-compose
   sudo usermod -aG docker $USER
   ```

3. **Deploy application**
   ```bash
   git clone your-repo
   cd llm-library-chat
   echo "GROQ_API_KEY=your_api_key" > .env
   docker-compose up -d
   ```

4. **Configure security group** to allow port 8510

## 🔒 Production Security

### Environment Variables
Never hardcode API keys. Use environment variables:

```python
import os
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    st.error("Please set GROQ_API_KEY environment variable")
    st.stop()
```

### HTTPS Setup (Nginx)
```nginx
server {
    listen 80;
    server_name yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl;
    server_name yourdomain.com;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    location / {
        proxy_pass http://localhost:8510;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Database Migration (Production)
For production, consider replacing JSON storage with PostgreSQL:

```python
import psycopg2
import os

DATABASE_URL = os.getenv("DATABASE_URL")
conn = psycopg2.connect(DATABASE_URL)
```

## 🔧 Configuration Options

### Environment Variables
- `GROQ_API_KEY`: Your Groq API key (required)
- `PORT`: Server port (default: 8510)
- `HOST`: Server host (default: 0.0.0.0)
- `DATABASE_URL`: PostgreSQL connection string (optional)

### Feature Flags
Add to your environment:
- `ENABLE_REGISTRATION=true`: Allow new user registration
- `MAX_CHAT_HISTORY=50`: Maximum chat history per user
- `DEBUG=true`: Enable debug mode

## 📊 Monitoring

### Health Check Endpoint
The app includes a health check at `/_stcore/health`

### Basic Monitoring Script
```bash
#!/bin/bash
while true; do
    if curl -f http://localhost:8510/_stcore/health; then
        echo "$(date): App is healthy"
    else
        echo "$(date): App is down, restarting..."
        docker-compose restart
    fi
    sleep 30
done
```

## 🚨 Troubleshooting

### Common Issues

1. **Port already in use**
   ```bash
   sudo lsof -i :8510
   sudo kill -9 <PID>
   ```

2. **Permission denied**
   ```bash
   chmod +x launch_groq_app.sh
   ```

3. **Module not found**
   ```bash
   source groq_env/bin/activate
   pip install -r requirements.txt
   ```

4. **API key issues**
   - Verify key is correct in environment variables
   - Check Groq console for API limits
   - Ensure internet connectivity

### Logs
- **Local**: Check terminal output
- **Docker**: `docker logs container_name`
- **Cloud**: Check platform-specific logs

---

For additional support, refer to the main README or open an issue in the repository.