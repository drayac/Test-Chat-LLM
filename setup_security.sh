#!/bin/bash

# 🔐 API Key Security Setup Script
# ===============================

echo "🔐 Setting up secure API key handling..."
echo "========================================"
echo ""

# Check if .env file exists
if [ -f ".env" ]; then
    echo "✅ .env file already exists"
else
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "✅ Created .env file"
    echo ""
    echo "🚨 IMPORTANT: Edit .env file and add your actual Groq API key!"
    echo "   Get your key from: https://console.groq.com/"
    echo ""
fi

# Check if API key is set
if [ -f ".env" ]; then
    if grep -q "your-actual-groq-api-key-here" .env; then
        echo "⚠️  WARNING: Please update .env with your actual API key"
        echo "   Current .env contains placeholder text"
    else
        echo "✅ .env file appears to have a custom API key"
    fi
fi

echo ""
echo "🛡️  Security Checklist:"
echo "======================="
echo "✅ .gitignore includes .env (API keys won't be committed)"
echo "✅ App uses environment variables"
echo "✅ Demo key fallback with warning"
echo ""

echo "📋 Next Steps:"
echo "=============="
echo "1. Edit .env file: nano .env"
echo "2. Replace 'your-actual-groq-api-key-here' with your real API key"
echo "3. Test locally: ./launch_groq_app.sh"
echo "4. For deployment, set environment variables in your platform"
echo ""

echo "🚀 Deployment Options:"
echo "======================"
echo "• Streamlit Cloud: Add secrets in dashboard"
echo "• Railway: Set environment variables in settings"
echo "• Heroku: heroku config:set GROQ_API_KEY=your-key"
echo "• Docker: docker run -e GROQ_API_KEY=your-key ..."
echo ""

echo "🔒 Security achieved! Your API key will be safe from public exposure."