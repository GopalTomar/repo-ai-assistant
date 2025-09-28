#!/usr/bin/env python3
"""
Application launcher for Talk to Your Codebase
Handles setup validation and starts the Streamlit app
"""

import os
import sys
import subprocess
import importlib.util

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        print(f"Current version: {sys.version}")
        return False
    print(f"✅ Python {sys.version.split()[0]} detected")
    return True

def check_dependencies():
    """Check if required packages are installed"""
    required_packages = [
        'streamlit', 'langchain', 'gitpython', 'chromadb', 
        'sentence_transformers', 'groq', 'python_dotenv'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        # Handle package name differences
        import_name = package
        if package == 'python_dotenv':
            import_name = 'dotenv'
        elif package == 'sentence_transformers':
            import_name = 'sentence_transformers'
        
        if importlib.util.find_spec(import_name) is None:
            missing_packages.append(package)
        else:
            print(f"✅ {package} found")
    
    if missing_packages:
        print(f"\n❌ Missing packages: {', '.join(missing_packages)}")
        print("Please install them using:")
        print("pip install -r requirements.txt")
        return False
    
    return True

def check_env_file():
    """Check if .env file exists and has required variables"""
    if not os.path.exists('.env'):
        print("❌ .env file not found")
        print("Please create a .env file with your Groq API key:")
        print("GROQ_API_KEY=your_api_key_here")
        return False
    
    try:
        with open('.env', 'r') as f:
            content = f.read()
            if 'GROQ_API_KEY' not in content or '=' not in content:
                print("❌ GROQ_API_KEY not found in .env file")
                return False
            
            # Extract the API key value
            for line in content.split('\n'):
                if line.startswith('GROQ_API_KEY='):
                    api_key = line.split('=', 1)[1].strip()
                    if len(api_key) < 10:  # Basic validation
                        print("❌ GROQ_API_KEY appears to be invalid")
                        return False
                    print("✅ GROQ_API_KEY found in .env")
                    return True
    except Exception as e:
        print(f"❌ Error reading .env file: {e}")
        return False
    
    return False

def create_directories():
    """Create necessary directories"""
    directories = ['chroma_db']
    
    for dir_name in directories:
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)
            print(f"✅ Created directory: {dir_name}")
        else:
            print(f"✅ Directory exists: {dir_name}")

def run_streamlit():
    """Launch the Streamlit application"""
    try:
        print("\n🚀 Starting Streamlit application...")
        print("The app will open in your browser at http://localhost:8501")
        print("Press Ctrl+C to stop the application\n")
        
        # Run streamlit
        subprocess.run(['streamlit', 'run', 'app.py'], check=True)
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to start Streamlit: {e}")
        return False
    except KeyboardInterrupt:
        print("\n👋 Application stopped by user")
        return True
    except FileNotFoundError:
        print("❌ Streamlit not found. Please install it:")
        print("pip install streamlit")
        return False

def main():
    """Main function to run all checks and start the app"""
    print("🔍 Pre-flight checks for Talk to Your Codebase\n")
    
    # Run all checks
    checks = [
        ("Python Version", check_python_version),
        ("Dependencies", check_dependencies),
        ("Environment File", check_env_file),
        ("Directories", create_directories)
    ]
    
    for check_name, check_func in checks:
        print(f"\n📋 Checking {check_name}...")
        if not check_func():
            print(f"\n💥 {check_name} check failed. Please fix the issues above.")
            sys.exit(1)
    
    print("\n" + "="*50)
    print("✅ All checks passed! Ready to launch the application")
    print("="*50)
    
    # Start the application
    run_streamlit()

if __name__ == "__main__":
    main()