#!/bin/bash
# Build script for macOS
# Usage: ./build_scripts/build_mac.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$ROOT_DIR"

echo "🏗️  Building Hillshade Converter for macOS..."
echo ""

# Pick Python interpreter (.venv preferred)
if [ -x ".venv/bin/python" ]; then
    PYTHON_BIN=".venv/bin/python"
    echo "🐍 Using virtual environment: .venv"
elif command -v python3 &> /dev/null; then
    PYTHON_BIN="python3"
    echo "🐍 Using system Python: $(python3 --version)"
else
    echo "❌ Python 3 not found. Please install Python 3.8+"
    exit 1
fi

# Install dependencies
echo "📦 Installing dependencies..."
"$PYTHON_BIN" -m pip install -r requirements.txt

# Clean previous builds
if [ -d "build" ]; then
    echo "🧹 Cleaning previous build..."
    rm -rf build dist *.spec
fi

# Build with PyInstaller
echo "🔨 Building with PyInstaller..."
"$PYTHON_BIN" -m PyInstaller pyinstaller/hillshade_mac.spec

echo ""
echo "✅ Build complete!"
echo "App created at: dist/Hillshade Converter.app"
echo ""
echo "Next steps:"
echo "  1. (Optional) Sign the app: ./build_scripts/sign_mac.sh"
echo "  2. Test the app: open dist/Hillshade\ Converter.app"
echo "  3. Create release: tar -czf Hillshade_Converter_macOS_arm64.tar.gz -C dist Hillshade\ Converter.app"
