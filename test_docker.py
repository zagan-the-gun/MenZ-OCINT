#!/usr/bin/env python3
"""
Simple test script to verify Docker environment
"""

import sys
import os

def test_python_environment():
    """Test basic Python environment"""
    print("Python version:", sys.version)
    print("Python path:", sys.path)
    print("Current working directory:", os.getcwd())
    print("Files in current directory:", os.listdir('.'))
    
    # Test basic imports
    try:
        import streamlit as st
        print("✅ Streamlit imported successfully")
    except ImportError as e:
        print("❌ Streamlit import failed:", e)
    
    try:
        import langchain
        print("✅ LangChain imported successfully")
    except ImportError as e:
        print("❌ LangChain import failed:", e)
    
    # Test project imports
    try:
        from app.tools import nmap_tool
        print("✅ OSINT tools imported successfully")
    except ImportError as e:
        print("❌ OSINT tools import failed:", e)

if __name__ == "__main__":
    test_python_environment() 