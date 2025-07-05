"""
DNS Tool for LangChain Agent
"""

from langchain.tools import Tool
import subprocess
import logging

logger = logging.getLogger(__name__)

def run_dns_query(domain: str, record_type: str = "A") -> str:
    """Execute DNS query directly"""
    
    valid_types = ["A", "AAAA", "MX", "NS", "TXT", "CNAME", "SOA", "PTR"]
    if record_type.upper() not in valid_types:
        return f"Error: Invalid record type '{record_type}'. Valid types: {', '.join(valid_types)}"
    
    try:
        logger.info(f"Running DNS query for: {domain} (type: {record_type})")
        
        # Execute directly in current environment
        cmd = ["dig", "+short", domain, record_type.upper()]
        
        result = subprocess.run(
            cmd, 
            capture_output=True, 
            text=True, 
            timeout=30,  # 30 seconds timeout
            cwd=None
        )
        
        if result.returncode == 0:
            output = result.stdout.strip()
            if not output:
                return f"No {record_type} records found for {domain}"
            
            logger.info(f"DNS query completed successfully for {domain}")
            return f"DNS {record_type} records for {domain}:\n\n{output}"
        else:
            error_msg = result.stderr.strip() or "Unknown error"
            logger.error(f"DNS query failed: {error_msg}")
            return f"DNS query failed for {domain}: {error_msg}"
            
    except subprocess.TimeoutExpired:
        logger.error(f"DNS query timed out for {domain}")
        return f"DNS query timed out for {domain}"
    except Exception as e:
        logger.error(f"DNS query error: {str(e)}")
        return f"DNS query error for {domain}: {str(e)}"

def dns_query_wrapper(input_str: str) -> str:
    """Wrapper function for DNS tool"""
    try:
        parts = input_str.strip().split()
        if not parts:
            return "Error: Please provide a domain name"
        
        domain = parts[0]
        record_type = parts[1] if len(parts) > 1 else "A"
        
        return run_dns_query(domain, record_type)
    except Exception as e:
        return f"Error parsing DNS input: {str(e)}"

# Create LangChain Tool
dns_tool = Tool(
    name="dns_lookup",
    description="""
    Perform DNS lookups for various record types.
    
    Usage: "domain.com [record_type]"
    - domain: Domain name to query (required)
    - record_type: A, AAAA, MX, NS, TXT, CNAME, SOA, PTR (default: A)
    
    Examples:
    - "google.com" - Get A records
    - "google.com MX" - Get mail server records
    - "google.com NS" - Get nameserver records
    - "google.com TXT" - Get text records
    """,
    func=dns_query_wrapper
) 