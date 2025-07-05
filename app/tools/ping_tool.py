"""
Ping Tool for LangChain Agent using nping
"""

from langchain.tools import Tool
import subprocess
import logging

logger = logging.getLogger(__name__)

def run_ping(target: str, count: int = 4) -> str:
    """Execute ping using nping"""
    
    try:
        logger.info(f"Running ping for: {target} (count: {count})")
        
        # Use nping instead of ping
        cmd = ["nping", "--icmp", "-c", str(count), target]
        
        result = subprocess.run(
            cmd, 
            capture_output=True, 
            text=True, 
            timeout=30,  # 30 seconds timeout
            cwd=None
        )
        
        if result.returncode == 0:
            output = result.stdout.strip()
            logger.info(f"Ping completed successfully for {target}")
            return f"Ping results for {target}:\n\n{output}"
        else:
            error_msg = result.stderr.strip() or "Unknown error"
            logger.error(f"Ping failed: {error_msg}")
            return f"Ping failed for {target}: {error_msg}"
            
    except subprocess.TimeoutExpired:
        logger.error(f"Ping timed out for {target}")
        return f"Ping timed out for {target}"
    except Exception as e:
        logger.error(f"Ping error: {str(e)}")
        return f"Ping error for {target}: {str(e)}"

def ping_wrapper(input_str: str) -> str:
    """Wrapper function for ping tool"""
    try:
        parts = input_str.strip().split()
        if not parts:
            return "Error: Please provide a target host or IP address"
        
        target = parts[0]
        count = int(parts[1]) if len(parts) > 1 else 4
        
        return run_ping(target, count)
    except Exception as e:
        return f"Error parsing ping input: {str(e)}"

# Create LangChain Tool
ping_tool = Tool(
    name="ping_test",
    description="""
    Perform network connectivity test using ping.
    
    Usage: "target [count]"
    - target: Host or IP address to ping (required)
    - count: Number of ping packets to send (default: 4)
    
    Examples:
    - "google.com" - Ping google.com 4 times
    - "google.com 10" - Ping google.com 10 times
    - "8.8.8.8" - Ping Google DNS server
    - "192.168.1.1" - Ping local gateway
    """,
    func=ping_wrapper
) 