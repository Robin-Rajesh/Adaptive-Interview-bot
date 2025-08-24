#!/usr/bin/env python3
"""
Simple startup script for the Adaptive Interview Preparation Bot
"""
import os
import sys
import subprocess
from pathlib import Path

def check_dependencies():
    """Check if all required packages are installed"""
    try:
        import streamlit
        import groq
        import pandas
        import numpy
        import plotly
        import nltk
        import dotenv
        return True
    except ImportError as e:
        print(f"Missing dependency: {e}")
        print("\nInstall dependencies first:")
        print("pip install -r requirements.txt")
        return False

def check_environment():
    """Check environment variables"""
    # Try to load .env file
    if os.path.exists('.env'):
        from dotenv import load_dotenv
        load_dotenv()
    
    required_env = ['GROQ_API_KEY']
    missing_env = []
    
    for env_var in required_env:
        if not os.getenv(env_var):
            missing_env.append(env_var)
    
    if missing_env:
        print("Missing required environment variables:")
        for env_var in missing_env:
            print(f"  - {env_var}")
        print("\nSet environment variables in your .env file or system environment")
        print("Copy .env.template to .env and add your Groq API key")
        return False
    
    return True

def setup_database():
    """Initialize the database"""
    try:
        from database.models import DatabaseManager
        db = DatabaseManager()
        print("Database initialized successfully")
        return True
    except Exception as e:
        print(f"Error initializing database: {e}")
        return False

def main():
    """Main startup routine"""
    print("🎯 Starting Adaptive Interview Preparation Bot")
    print("=" * 50)
    
    # Check dependencies
    print("Checking dependencies...")
    if not check_dependencies():
        print("\nInstall dependencies first:")
        print("pip install -r requirements.txt")
        sys.exit(1)
    print("✅ Dependencies OK")
    
    # Check environment
    print("Checking environment...")
    if not check_environment():
        print("⚠️  Please set up your .env file with the Groq API key")
        sys.exit(1)
    print("✅ Environment OK")
    
    # Setup database
    print("Setting up database...")
    if not setup_database():
        print("⚠️  Database setup had issues, but continuing...")
    else:
        print("✅ Database OK")
    
    # Start the application
    print("\n🚀 Starting Streamlit application...")
    print("Access the app at: http://localhost:8501")
    print("Press Ctrl+C to stop the application")
    
    try:
        subprocess.run([
            sys.executable, '-m', 'streamlit', 'run', 'main.py',
            '--server.port', '8501',
            '--server.address', '0.0.0.0'
        ])
    except KeyboardInterrupt:
        print("\n\n👋 Application stopped")
    except FileNotFoundError:
        print("Error: Streamlit not found. Install it with: pip install streamlit")

if __name__ == "__main__":
    main()
