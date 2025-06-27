#!/bin/bash

echo "🐍 Setting up Python virtual environment..."

# Remove existing venv if it exists
if [ -d "venv" ]; then
    echo "🗑️ Removing existing virtual environment..."
    rm -rf venv
fi

# Create new virtual environment
echo "📦 Creating new virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "✅ Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️ Upgrading pip..."
pip install --upgrade pip

# Install backend dependencies
echo "📦 Installing backend dependencies..."
cd backend
pip install -r requirements.txt
cd ..

echo ""
echo "🎉 Virtual environment setup complete!"
echo "✅ You can now run ./run_all.sh to start all services"
echo ""
echo "📝 To activate the virtual environment manually:"
echo "   source venv/bin/activate" 