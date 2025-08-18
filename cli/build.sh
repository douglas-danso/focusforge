#!/bin/bash

# FocusForge CLI Build Script

echo "🚀 Building FocusForge CLI..."

# Check if Go is installed
if ! command -v go &> /dev/null; then
    echo "❌ Go is not installed. Please install Go 1.21 or later."
    exit 1
fi

# Check Go version
GO_VERSION=$(go version | awk '{print $3}' | sed 's/go//')
REQUIRED_VERSION="1.21"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$GO_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    echo "❌ Go version $GO_VERSION is too old. Please install Go $REQUIRED_VERSION or later."
    exit 1
fi

echo "✅ Go version $GO_VERSION detected"

# Clean previous builds
echo "🧹 Cleaning previous builds..."
rm -f focusforge-cli
rm -f focusforge-cli.exe

# Install dependencies
echo "📦 Installing dependencies..."
go mod tidy

if [ $? -ne 0 ]; then
    echo "❌ Failed to install dependencies"
    exit 1
fi

# Build for current platform
echo "🔨 Building CLI..."
go build -o focusforge-cli -ldflags="-s -w" .

if [ $? -ne 0 ]; then
    echo "❌ Build failed"
    exit 1
fi

# Check if build was successful
if [ -f "focusforge-cli" ] || [ -f "focusforge-cli.exe" ]; then
    echo "✅ Build successful!"
    
    # Show file info
    if [ -f "focusforge-cli" ]; then
        echo "📁 Binary: focusforge-cli"
        ls -lh focusforge-cli
    else
        echo "📁 Binary: focusforge-cli.exe"
        ls -lh focusforge-cli.exe
    fi
    
    echo ""
    echo "🎉 You can now run the CLI with:"
    if [ -f "focusforge-cli" ]; then
        echo "   ./focusforge-cli"
    else
        echo "   ./focusforge-cli.exe"
    fi
    
else
    echo "❌ Build failed - binary not found"
    exit 1
fi
