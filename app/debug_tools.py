#!/usr/bin/env python3
"""
Debug script to test OSINT tools directly
"""

import sys
import logging
from tools.whois_tool import whois_tool
from tools.dns_tool import dns_tool
from tools.nmap_tool import nmap_tool
from tools.command_tool import command_tool
from tools.ping_tool import ping_tool

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_tools():
    """Test all OSINT tools"""
    
    print("🔍 Testing OSINT Tools\n")
    
    # Test whois tool
    print("1. Testing whois_tool:")
    try:
        result = whois_tool.func("google.com")
        print(f"✅ Whois Result: {result[:200]}...")
    except Exception as e:
        print(f"❌ Whois Error: {str(e)}")
    
    print("\n" + "="*50 + "\n")
    
    # Test DNS tool
    print("2. Testing dns_tool:")
    try:
        result = dns_tool.func("google.com A")
        print(f"✅ DNS Result: {result}")
    except Exception as e:
        print(f"❌ DNS Error: {str(e)}")
    
    print("\n" + "="*50 + "\n")
    
    # Test command tool
    print("3. Testing command_tool:")
    try:
        result = command_tool.func("ping -c 2 google.com")
        print(f"✅ Command Result: {result[:200]}...")
    except Exception as e:
        print(f"❌ Command Error: {str(e)}")
    
    print("\n" + "="*50 + "\n")
    
    # Test nmap tool
    print("4. Testing nmap_tool:")
    try:
        result = nmap_tool.func("google.com basic")
        print(f"✅ Nmap Result: {result[:200]}...")
    except Exception as e:
        print(f"❌ Nmap Error: {str(e)}")
    
    print("\n" + "="*50 + "\n")
    
    # Test ping tool
    print("5. Testing ping_tool:")
    try:
        result = ping_tool.func("google.com 2")
        print(f"✅ Ping Result: {result[:200]}...")
    except Exception as e:
        print(f"❌ Ping Error: {str(e)}")

if __name__ == "__main__":
    test_tools() 