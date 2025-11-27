#!/usr/bin/env python3
"""
Initialize Git repository in the correct location.
"""
import os
import subprocess
import shutil
from pathlib import Path

TARGET_DIR = Path("/Users/stephen/Documents/GitHub/Aiken-Project")
CURRENT_DIR = Path("/Users/stephen/Aiken-Project")

def main():
    print("Setting up Git repository...")
    print()
    
    # Check if we need to move the project
    if CURRENT_DIR.exists() and not TARGET_DIR.exists():
        print(f"Moving project from {CURRENT_DIR} to {TARGET_DIR}")
        TARGET_DIR.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(CURRENT_DIR), str(TARGET_DIR))
        print("✓ Project moved")
    elif CURRENT_DIR.exists() and TARGET_DIR.exists():
        print(f"⚠ Both directories exist:")
        print(f"  Current: {CURRENT_DIR}")
        print(f"  Target: {TARGET_DIR}")
        print("  Please manually resolve this conflict.")
        return
    elif not TARGET_DIR.exists():
        print(f"⚠ Target directory does not exist: {TARGET_DIR}")
        print("  Please ensure the project is in the correct location.")
        return
    
    # Change to target directory
    os.chdir(TARGET_DIR)
    print(f"Working directory: {TARGET_DIR}")
    print()
    
    # Check if Git is already initialized
    if (TARGET_DIR / ".git").exists():
        print("✓ Git repository already initialized")
        try:
            result = subprocess.run(
                ["git", "status"],
                capture_output=True,
                text=True,
                check=False
            )
            print(result.stdout)
            if result.stderr:
                print(result.stderr)
        except FileNotFoundError:
            print("⚠ Git is not installed or not in PATH")
            return
    else:
        print("Initializing Git repository...")
        try:
            subprocess.run(["git", "init"], check=True)
            print("✓ Git repository initialized")
        except FileNotFoundError:
            print("✗ Error: Git is not installed or not in PATH")
            return
        except subprocess.CalledProcessError as e:
            print(f"✗ Error initializing Git: {e}")
            return
    
    # Check for remote
    try:
        result = subprocess.run(
            ["git", "remote", "-v"],
            capture_output=True,
            text=True,
            check=False
        )
        if result.stdout.strip():
            print("\n✓ Git remotes configured:")
            print(result.stdout)
        else:
            print("\n⚠ No Git remote configured.")
            print("  You may want to add one with:")
            print("    git remote add origin <repository-url>")
    except FileNotFoundError:
        pass
    
    print()
    print("=" * 50)
    print("Git setup complete!")
    print(f"Repository location: {TARGET_DIR}")
    print("=" * 50)

if __name__ == "__main__":
    main()

