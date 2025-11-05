#!/bin/bash
# Setup script for Vector Packing Project

echo "================================================"
echo "Vector Packing Project Setup"
echo "================================================"

# Check Python version
echo -e "\n1. Checking Python version..."
python_version=$(python3 --version 2>&1)
echo "Found: $python_version"

if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed!"
    exit 1
fi

# Create virtual environment
echo -e "\n2. Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo -e "\n3. Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo -e "\n4. Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo -e "\n5. Installing dependencies..."
pip install -r requirements.txt

# Create necessary directories
echo -e "\n6. Creating directories..."
mkdir -p results
mkdir -p data
mkdir -p logs

echo -e "\n================================================"
echo "Setup complete!"
echo "================================================"
echo -e "\nTo activate the environment, run:"
echo "  source venv/bin/activate"
echo -e "\nTo run a test experiment:"
echo "  python main.py --scenario small --generations 100"
echo -e "\nTo see all options:"
echo "  python main.py --help"
echo "================================================"
