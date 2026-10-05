#!/bin/bash
# Quick Start Script for DeFi Fraud Detection (Mac/Linux)
# ========================================================

echo ""
echo "================================================================"
echo "  🛡️  Aegis DeFi Fraud Detection - Quick Start"
echo "================================================================"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "ERROR: Failed to create virtual environment"
        echo "Please ensure Python 3.8+ is installed"
        exit 1
    fi
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Check if dependencies are installed
python -c "import flask" 2>/dev/null
if [ $? -ne 0 ]; then
    echo ""
    echo "Installing dependencies..."
    echo "This may take a few minutes..."
    pip install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "ERROR: Failed to install dependencies"
        exit 1
    fi
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo ""
    echo "⚠️  WARNING: .env file not found!"
    echo ""
    echo "Please create a .env file with your API keys:"
    echo "  1. Copy .env.example to .env"
    echo "  2. Edit .env and add your credentials"
    echo ""
    read -p "Create .env from template? (y/n) " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        cp .env.example .env
        echo ""
        echo "✅ .env file created. Please edit it with your API keys."
        echo ""
        if command -v nano &> /dev/null; then
            nano .env
        elif command -v vim &> /dev/null; then
            vim .env
        else
            echo "Please edit .env file manually"
        fi
    fi
fi

# Check if model files exist
if [ ! -f "notebooks/models/fraud_model.pkl" ]; then
    echo ""
    echo "⚠️  WARNING: ML model files not found!"
    echo "Please ensure model files exist in notebooks/models/"
    echo ""
fi

echo ""
echo "================================================================"
echo "  🚀 Starting Server..."
echo "================================================================"
echo ""
echo "  Frontend: http://localhost:5000"
echo "  API Docs: http://localhost:5000/api/health"
echo ""
echo "  Press Ctrl+C to stop the server"
echo "================================================================"
echo ""

# Start the Flask server
python backend/server.py
