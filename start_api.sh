#!/bin/bash

echo "🔧 Setting up Foundation URL Finder API..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Install requirements
echo "📚 Installing dependencies..."
pip install -r requirements.txt

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  Warning: .env file not found!"
    echo "Please copy sample.env to .env and add your OpenAI API key."
    exit 1
fi

# Start the API
echo "🚀 Starting Foundation URL Finder API..."
echo "📖 API Documentation: http://localhost:8000/docs"
echo "🌐 API Base URL: http://localhost:8000"
echo ""
echo "Press Ctrl+C to stop the server"

python main.py
