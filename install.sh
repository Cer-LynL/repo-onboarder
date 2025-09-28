#!/bin/bash

# Repo Onboarder Installation Script

echo "🚀 Installing Repo Onboarder..."

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    echo "Please install Python 3 and try again."
    exit 1
fi

# Check if pip is available
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 is required but not installed."
    echo "Please install pip3 and try again."
    exit 1
fi

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📚 Installing dependencies..."
pip install -r requirements.txt

# Make onboarder executable
echo "⚙️  Making onboarder executable..."
chmod +x onboarder.py

# Test installation
echo "🧪 Testing installation..."
python test_onboarder.py

if [ $? -eq 0 ]; then
    echo "✅ Installation successful!"
    echo ""
    echo "🎉 Repo Onboarder is ready to use!"
    echo ""
    echo "Usage:"
    echo "  source venv/bin/activate"
    echo "  python onboarder.py /path/to/repository"
    echo ""
    echo "Demo:"
    echo "  python demo.py"
    echo ""
    echo "GitHub Integration:"
    echo "  Copy .github/workflows/onboarder.yml to your repository"
    echo "  Add ANTHROPIC_API_KEY to repository secrets (optional)"
else
    echo "❌ Installation test failed!"
    exit 1
fi
