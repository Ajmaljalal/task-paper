#!/bin/bash

# Quick build script for development/testing
echo "🔨 Quick Build - TaskPaper"
echo "========================="

# Activate virtual environment if needed
if [[ -z "$VIRTUAL_ENV" ]] && [[ -f "env/bin/activate" ]]; then
    source env/bin/activate
    echo "✅ Activated virtual environment"
fi

# Clean and build
echo "🧹 Cleaning previous build..."
rm -rf build dist

echo "📦 Building app..."
pyinstaller TaskPaper.spec

if [[ -d "dist/TaskPaper.app" ]]; then
    echo "✅ Build successful!"
    echo "🚀 Test with: open dist/TaskPaper.app"
else
    echo "❌ Build failed!"
    exit 1
fi
