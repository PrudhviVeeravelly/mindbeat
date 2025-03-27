#!/bin/bash

# Exit on error
set -e

echo "🚀 Starting deployment process..."

# Create and activate virtual environment
echo "📦 Setting up virtual environment..."
python -m venv venv
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Run validation script
echo "✅ Running validation checks..."
python scripts/validate_deployment.py

# Run tests
echo "🧪 Running tests..."
pytest

# Create necessary directories
echo "📁 Creating required directories..."
mkdir -p app/static
mkdir -p app/frontend/templates
mkdir -p logs

# Set up git hooks
echo "🔧 Setting up git hooks..."
cat > .git/hooks/pre-commit << 'EOF'
#!/bin/bash
black .
isort .
mypy .
pytest
EOF
chmod +x .git/hooks/pre-commit

# Commit changes
echo "💾 Committing changes..."
git add .
git commit -m "Deployment preparation: $(date +%Y-%m-%d_%H-%M-%S)"
git push origin main

echo "✨ Deployment preparation complete!"
echo "You can now deploy to Railway using: railway up"
