#!/usr/bin/env python3
"""
Setup script to install dependencies and run the keyword categorization script.
"""

import subprocess
import sys
import os

def install_requirements():
    """Install required packages"""
    print("Installing requirements...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("Requirements installed successfully!")
        return True
    except subprocess.CalledProcessError:
        print("Failed to install requirements!")
        return False

def check_api_key():
    """Check if OpenAI API key is set"""
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("\n⚠️  OpenAI API key not found!")
        print("Please set your OPENAI_API_KEY environment variable:")
        print("export OPENAI_API_KEY='your-api-key-here'")
        print("\nOr set it for this session:")
        api_key = input("Enter your OpenAI API Key (or press Enter to skip): ").strip()
        if api_key:
            os.environ['OPENAI_API_KEY'] = api_key
            return True
        return False
    print("✅ OpenAI API key found!")
    return True

def run_main_script():
    """Run the main keyword categorization script"""
    print("\nRunning keyword categorization script...")
    try:
        subprocess.check_call([sys.executable, "main.py"])
        print("Script completed successfully!")
    except subprocess.CalledProcessError as e:
        print(f"Script failed with error: {e}")

if __name__ == "__main__":
    print("🚀 Keyword Categorization Setup")
    print("=" * 40)
    
    # Step 1: Install requirements
    if not install_requirements():
        sys.exit(1)
    
    # Step 2: Check API key
    if not check_api_key():
        print("Exiting - API key required to continue.")
        sys.exit(1)
    
    # Step 3: Run main script
    run_main_script() 