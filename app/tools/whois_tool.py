"""
Whois Tool for LangChain Agent
"""

from langchain.tools import Tool
import subprocess
import logging

logger = logging.getLogger(__name__)

def run_whois(domain: str) -> str:
    """Execute whois lookup directly"""
    
    try:
        logger.info(f"Running whois lookup for: {domain}")
        
        # Execute directly in current environment
        cmd = ["whois", domain]
        
        result = subprocess.run(
            cmd, 
            capture_output=True, 
            text=True, 
            timeout=60,  # 1 minute timeout
            cwd=None
        )
        
        if result.returncode == 0:
            output = result.stdout.strip()
            logger.info(f"Whois lookup completed successfully for {domain}")
            return f"Whois information for {domain}:\n\n{output}"
        else:
            error_msg = result.stderr.strip() or "Unknown error"
            logger.error(f"Whois lookup failed: {error_msg}")
            return f"Whois lookup failed for {domain}: {error_msg}"
            
    except subprocess.TimeoutExpired:
        logger.error(f"Whois lookup timed out for {domain}")
        return f"Whois lookup timed out for {domain}"
    except Exception as e:
        logger.error(f"Whois lookup error: {str(e)}")
        return f"Whois lookup error for {domain}: {str(e)}"

def whois_lookup_wrapper(input_str: str) -> str:
    """Wrapper function for whois tool"""
    try:
        domain = input_str.strip()
        if not domain:
            return "Error: Please provide a domain name"
        
        return run_whois(domain)
    except Exception as e:
        return f"Error parsing whois input: {str(e)}"

# Create LangChain Tool
whois_tool = Tool(
    name="whois_lookup",
    description="""
    Perform WHOIS domain lookup to get registration information.
    
    Usage: "domain.com"
    
    Examples:
    - "google.com" - Get whois info for Google
    - "example.org" - Get whois info for any domain
    
    Returns registration details, nameservers, contacts, etc.
    """,
    func=whois_lookup_wrapper
) 