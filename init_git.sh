#!/bin/bash
# Quick Git initialization script

# Move project if needed
if [ ! -d "/Users/stephen/Documents/GitHub/Aiken-Project" ] && [ -d "/Users/stephen/Aiken-Project" ]; then
    echo "Moving project to correct location..."
    mkdir -p /Users/stephen/Documents/GitHub
    mv /Users/stephen/Aiken-Project /Users/stephen/Documents/GitHub/Aiken-Project
fi

# Navigate to project
cd /Users/stephen/Documents/GitHub/Aiken-Project || exit 1

# Initialize Git if not already done
if [ ! -d .git ]; then
    echo "Initializing Git repository..."
    git init
    echo "✓ Git repository initialized"
else
    echo "✓ Git repository already exists"
fi

# Show status
echo ""
echo "Git status:"
git status

echo ""
echo "Repository location: $(pwd)"
echo ""
echo "Next steps:"
echo "1. Review files: git status"
echo "2. Add files: git add ."
echo "3. Commit: git commit -m 'Initial commit'"
echo "4. Add remote: git remote add origin <url>"

