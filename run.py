#!/usr/bin/env python
"""
Run script for the AI Agent Chatbot application.
"""

import os
import sys
import argparse
import subprocess
import importlib.util

def check_dependencies():
    """Check if all required dependencies are installed."""
    required_packages = [
        "streamlit",
        "langchain",
        "langchain_community",
        "langchain_openai",
        "langchain_groq",
        "openai",
        "numpy",
        "faiss-cpu"
    ]
    
    missing_packages = []
    
    for package in required_packages:
        if importlib.util.find_spec(package) is None:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"Missing required packages: {', '.join(missing_packages)}")
        print("Please install them using:")
        print(f"pip install {' '.join(missing_packages)}")
        return False
    
    return True

def run_app():
    """Run the streamlit app."""
    print("Starting AI Agent Chatbot...")
    app_path = os.path.join("agents_chatbot", "ui", "app.py")
    
    if not os.path.exists(app_path):
        print(f"Error: App file not found at {app_path}")
        return
    
    # Run the streamlit app
    subprocess.run([sys.executable, "-m", "streamlit", "run", app_path])

def main():
    parser = argparse.ArgumentParser(description='Run the AI Agent Chatbot application')
    parser.add_argument('--check-deps', action='store_true', help='Check dependencies without running the app')
    
    args = parser.parse_args()
    
    if args.check_deps:
        check_dependencies()
        return
    
    if not check_dependencies():
        print("Please install all required dependencies before running the app")
        return
    
    run_app()

if __name__ == "__main__":
    main() 