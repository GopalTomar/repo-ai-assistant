#!/usr/bin/env python3
"""
Troubleshooting script to check file structure and imports
"""

import os
import sys

def check_file_structure():
    """Check if all required files exist"""
    required_files = [
        'app.py',
        'utils.py', 
        'rag_pipeline.py',
        'requirements.txt',
        '.env'
    ]
    
    print("📁 Checking file structure...")
    missing_files = []
    
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ {file} found")
        else:
            print(f"❌ {file} missing")
            missing_files.append(file)
    
    if missing_files:
        print(f"\n🚫 Missing files: {', '.join(missing_files)}")
        return False
    
    return True

def check_imports():
    """Check if imports work correctly"""
    print("\n🔍 Checking imports...")
    
    try:
        from utils import CodebaseManager, format_code_snippet, extract_repo_name, safe_markdown
        print("✅ utils.py imports working")
    except ImportError as e:
        print(f"❌ utils.py import error: {e}")
        return False
    
    try:
        from rag_pipeline import RAGPipeline
        print("✅ rag_pipeline.py imports working")
    except ImportError as e:
        print(f"❌ rag_pipeline.py import error: {e}")
        return False
    
    return True

def check_dependencies():
    """Check critical dependencies"""
    print("\n📦 Checking critical dependencies...")
    
    critical_deps = ['streamlit', 'groq', 'gitpython', 'chromadb']
    
    for dep in critical_deps:
        try:
            __import__(dep)
            print(f"✅ {dep} installed")
        except ImportError:
            print(f"❌ {dep} not installed")
            return False
    
    return True

def main():
    print("🔧 Troubleshooting Talk to Your Codebase")
    print("=" * 50)
    
    checks = [
        check_file_structure,
        check_imports,
        check_dependencies
    ]
    
    all_good = True
    for check in checks:
        if not check():
            all_good = False
        print()
    
    if all_good:
        print("🎉 All checks passed! Try running the app again:")
        print("streamlit run app.py")
    else:
        print("💥 Some issues found. Please fix them before running the app.")

if __name__ == "__main__":
    main()