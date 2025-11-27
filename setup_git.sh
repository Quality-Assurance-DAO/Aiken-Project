#!/bin/bash
# Script to initialize Git repository in the correct location

set -e

PROJECT_DIR="/Users/stephen/Documents/GitHub/Aiken-Project"
CURRENT_DIR="/Users/stephen/Aiken-Project"

echo "Setting up Git repository..."
echo ""

# Check if target directory exists
if [ ! -d "$PROJECT_DIR" ]; then
    echo "Creating target directory: $PROJECT_DIR"
    mkdir -p "$PROJECT_DIR"
    
    # Move project if it's in a different location
    if [ -d "$CURRENT_DIR" ] && [ "$CURRENT_DIR" != "$PROJECT_DIR" ]; then
        echo "Moving project from $CURRENT_DIR to $PROJECT_DIR"
        mv "$CURRENT_DIR" "$PROJECT_DIR"
    fi
fi

cd "$PROJECT_DIR"

# Check if Git is already initialized
if [ -d .git ]; then
    echo "✓ Git repository already initialized"
    git status
else
    echo "Initializing Git repository..."
    git init
    
    echo "✓ Git repository initialized"
fi

# Check if remote is configured
if git remote -v | grep -q origin; then
    echo "✓ Git remote 'origin' is configured"
    git remote -v
else
    echo "⚠ No Git remote configured. You may want to add one with:"
    echo "  git remote add origin <repository-url>"
fi

echo ""
echo "Git setup complete!"
echo "Repository location: $PROJECT_DIR"

