# Git Repository Setup Instructions

## Current Situation
- Project is currently at: `/Users/stephen/Aiken-Project`
- Target location: `/Users/stephen/Documents/GitHub/Aiken-Project`

## Steps to Initialize Git Repository

### Option 1: Move Project and Initialize Git (Recommended)

1. **Move the project to the correct location:**
   ```bash
   mv /Users/stephen/Aiken-Project /Users/stephen/Documents/GitHub/Aiken-Project
   ```

2. **Navigate to the project:**
   ```bash
   cd /Users/stephen/Documents/GitHub/Aiken-Project
   ```

3. **Initialize Git repository:**
   ```bash
   git init
   ```

4. **Check Git status:**
   ```bash
   git status
   ```

5. **Add all files (if ready):**
   ```bash
   git add .
   ```

6. **Make initial commit:**
   ```bash
   git commit -m "Initial commit"
   ```

7. **Add remote repository (if you have one):**
   ```bash
   git remote add origin <your-repository-url>
   ```

### Option 2: Use the Python Script

Run the provided Python script:
```bash
cd /Users/stephen/Aiken-Project
python3 init_git_repo.py
```

### Option 3: Use the Bash Script

Run the provided bash script:
```bash
cd /Users/stephen/Aiken-Project
chmod +x setup_git.sh
./setup_git.sh
```

## Verify Setup

After setup, verify everything is correct:

```bash
cd /Users/stephen/Documents/GitHub/Aiken-Project
git status
git remote -v  # Check if remote is configured
```

## Important Notes

- The `.gitignore` file is already configured and will exclude:
  - Build artifacts
  - Sensitive files (keys, addresses)
  - Database directories
  - Log files
  - Node binaries

- Make sure Docker Compose file paths are correct after moving:
  - `docker-compose.preprod.yml` uses relative paths (`./preprod-socket`, `./share/preprod`)
  - These should work correctly from the new location

