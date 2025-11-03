#!/bin/bash

# Launch script for LLM-library Chat Test
echo "🚀 Starting LLM-library Chat Test..."

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Check if virtual environment exists
if [ ! -d "groq_env" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv groq_env
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source groq_env/bin/activate

# Install/update dependencies
echo "📚 Installing dependencies..."
pip install -r requirements.txt

# Create data directory if it doesn't exist
mkdir -p data

# Kill any existing Streamlit processes on this port
echo "🧹 Cleaning up existing processes..."
pkill -f "streamlit.*8510" 2>/dev/null || true

# Wait a moment for cleanup
sleep 2

# Launch the app
echo "🎉 Launching app on http://localhost:8510"
echo "   Network URL: http://$(hostname -I | awk '{print $1}'):8510"
echo ""
echo "📝 Press Ctrl+C to stop the application"
echo ""

# Run with proper configuration and auto-open browser
streamlit run app_groq_chat.py \
    --server.port 8510 \
    --server.address 0.0.0.0 \
    --server.headless false \
    --browser.gatherUsageStats false \
    --server.runOnSave false

echo ""
echo "🛑 LLM-library Chat Test stopped."