# LLM-library Chat Test

A modern, dark-themed chat application powered by Groq's lightning-fast LLM inference API. Features real-time model selection, user authentication, persistent chat history, and intelligent response formatting.

## 🚀 Features

- **🌟 Modern Dark UI**: Beautiful dark theme with gradient title and smooth interactions
- **⚡ Multiple Groq Models**: Dynamic model selection from Groq's API (filtered and alphabetically sorted)
- **🔐 User Authentication**: Optional login system with email/password registration
- **👤 Guest Mode**: Temporary user accounts with automatic cleanup after disconnection
- **📜 Chat History**: Persistent conversation storage across sessions (for registered users)
- **🟢 API Status**: Real-time API connectivity monitoring in sidebar
- **📱 Responsive Design**: Clean sidebar layout with organized controls
- **🧠 Thinking Tags**: Automatic formatting of model thoughts in italic with `<think>` tags
- **📏 Response Limits**: Intelligent 200-word response limiting for concise answers
- **🚀 Auto-Launch**: Automatic browser opening on startup

## 🛠️ Installation & Quick Start

### Prerequisites

- Python 3.8+
- Git

### One-Command Launch

```bash
git clone <repository-url> && cd app_test_groq && chmod +x launch_groq_app.sh && ./launch_groq_app.sh
```

### Manual Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd app_test_groq
   ```

2. **Launch with the provided script** (Recommended)
   ```bash
   chmod +x launch_groq_app.sh
   ./launch_groq_app.sh
   ```
   
   *The launch script will automatically:*
   - Create virtual environment if needed
   - Install all dependencies
   - Clean up any existing processes
   - Launch the app with auto-browser opening

3. **Manual launch**
   ```bash
   python -m venv groq_env
   source groq_env/bin/activate
   pip install -r requirements.txt
   streamlit run app_groq_chat.py --server.port 8510
   ```

4. **Access the app**
   - The app will automatically open in your browser
   - Or manually visit: http://localhost:8510

## 📦 Dependencies

```
streamlit>=1.28.0
groq>=0.4.0
requests>=2.31.0
```

## 🔧 Configuration & Security

### 🔐 API Key Setup (IMPORTANT!)

**⚠️ Never commit your API key to GitHub!**

#### Quick Security Setup:
```bash
# Run the security setup script
chmod +x setup_security.sh
./setup_security.sh

# Edit .env file with your actual API key
nano .env
```

#### Manual Setup:
1. **Get your Groq API key** from [Groq Console](https://console.groq.com/)
2. **Create .env file**:
   ```bash
   echo "GROQ_API_KEY=your-actual-key-here" > .env
   ```
3. **Verify .env is in .gitignore** ✅ (already included)

#### Alternative Methods:
- **Environment variable**: `export GROQ_API_KEY="your-key"`
- **Streamlit secrets**: Add to `.streamlit/secrets.toml`

### 🚀 Deployment Security

**Streamlit Cloud:**
- Dashboard → Settings → Secrets → Add `GROQ_API_KEY`

**Railway/Heroku:**
```bash
railway add GROQ_API_KEY           # Railway
heroku config:set GROQ_API_KEY=... # Heroku
```

**Docker:**
```bash
docker run -e GROQ_API_KEY=your-key llm-chat
```

📖 **Full security guide**: See `API_KEY_SECURITY.md`

### Port Configuration

Default port is 8510. To change:
```bash
streamlit run app_groq_chat.py --server.port [your-port]
```

## 📁 Project Structure

```
app_test_groq/
├── app_groq_chat.py          # Main application file
├── requirements.txt          # Python dependencies
├── launch_groq_app.sh       # Launch script
├── users.json               # User data storage (auto-created)
├── groq_env/               # Virtual environment
└── README.md               # This file
```

## 🎯 Usage

### For Guests
1. App automatically creates a temporary guest account
2. Chat with any available model
3. View conversation history in sidebar
4. History is preserved during session but lost on app restart

### For Registered Users
1. Click "Sign In with Email" in sidebar
2. Register with email/password or login with existing account
3. All conversations are permanently saved
4. Access chat history across sessions
5. Switch between guest and registered modes

### Available Models
The app dynamically fetches available models from Groq API:
- **Llama 3.1** (70B, 8B variants)
- **Llama 3.2** (11B, 3B, 1B variants)
- **Mixtral 8x7B**
- **Gemma 2** (9B, 7B variants)
- **Tool-use variants** for advanced functionality

## 🚀 Deployment Options

### 🖥️ Local Development
```bash
./launch_groq_app.sh
# or manually:
streamlit run app_groq_chat.py --server.port 8510
```

### ☁️ Streamlit Cloud (Free & Easy)
1. **Push to GitHub**: Commit all files to a GitHub repository
2. **Connect Streamlit Cloud**: Visit [share.streamlit.io](https://share.streamlit.io)
3. **Deploy**: Connect your GitHub repo and select `app_groq_chat.py`
4. **Add Secrets**: In Streamlit Cloud dashboard, add your Groq API key as secrets
5. **Launch**: Your app will be live at `https://[app-name].streamlit.app`

### 🐳 Docker Deployment
```bash
# Build image
docker build -t llm-library-chat .

# Run container
docker run -p 8510:8510 llm-library-chat
```

### 🚄 Railway (One-Click Deploy)
[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/template/your-template)

1. Click "Deploy on Railway" button
2. Connect your GitHub account
3. Set `GROQ_API_KEY` environment variable
4. Deploy with one click

### 🟣 Heroku Deployment
```bash
# Install Heroku CLI, then:
heroku create your-app-name
heroku config:set GROQ_API_KEY=your-api-key
git push heroku main
```

### ⚡ Vercel/Netlify
- Upload `app_groq_chat.py` and `requirements.txt`
- Set build command: `pip install -r requirements.txt`
- Set start command: `streamlit run app_groq_chat.py --server.port=$PORT`

## � Production Configuration

### Environment Variables (Recommended)
```bash
export GROQ_API_KEY="your-secure-api-key"
export PORT=8510
export STREAMLIT_SERVER_HEADLESS=true
```

### Security Considerations
- **API Key**: Never commit API keys to version control
- **HTTPS**: Use HTTPS in production deployments
- **Rate Limiting**: Consider implementing rate limiting for public deployments
- **User Data**: Use proper database (PostgreSQL/MongoDB) instead of JSON for production

## 🎨 Customization

### Theme Colors
Edit the CSS section in `app_groq_chat.py`:
```python
st.markdown("""
<style>
    .main-title {
        background: linear-gradient(90deg, #your-color1, #your-color2);
        /* ... */
    }
</style>
""", unsafe_allow_html=True)
```

### Model Filtering
Modify the filter in the model selection:
```python
filtered_models = [model for model in all_models 
                  if not model.startswith('unwanted-prefix')]
```

## 📊 Monitoring & Analytics

### Basic Metrics
- Track API usage in Groq Console
- Monitor response times and user engagement
- Set up alerts for API quota limits

### Advanced Monitoring
- Integrate with analytics platforms (Google Analytics, Mixpanel)
- Add logging for user interactions and error tracking
- Set up health checks for production deployments

## �️ Troubleshooting

### Common Issues

| Issue | Solution |
|-------|----------|
| **Import errors** | Activate virtual environment: `source groq_env/bin/activate` |
| **API errors** | Check internet connection and API key validity |
| **Port conflicts** | Use different port: `--server.port 8511` |
| **Permission errors** | Check file permissions: `chmod 755 launch_groq_app.sh` |
| **Browser not opening** | Check firewall settings or manually visit localhost:8510 |
| **Models not loading** | Verify API key and internet connection |

### Debug Mode
Run with verbose logging:
```bash
streamlit run app_groq_chat.py --logger.level=debug
```

## � Performance Tips

1. **Model Selection**: Smaller models (3B, 7B) are faster for simple queries
2. **Response Length**: Keep max_tokens low for faster responses
3. **Caching**: Consider implementing response caching for repeated queries
4. **Resource Limits**: Monitor memory usage for long chat sessions

## 🤝 Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **Groq** for providing lightning-fast LLM inference
- **Streamlit** for the amazing web app framework
- **Community** for feedback and contributions

---

**🚀 Ready to Deploy? Run `./launch_groq_app.sh` and start chatting!**

*Built with ❤️ using Streamlit and Groq API*
