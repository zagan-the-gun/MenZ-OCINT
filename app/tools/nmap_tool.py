"""
Nmap Tool for LangChain Agent
"""

from langchain.tools import Tool
from langchain.pydantic_v1 import BaseModel, Field
import subprocess
import json
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class NmapInput(BaseModel):
    """Input for nmap tool"""
    target: str = Field(description="Target host or IP address to scan")
    scan_type: str = Field(
        default="basic", 
        description="Type of scan: basic, port, service, or stealth"
    )
    ports: str = Field(
        default="", 
        description="Specific ports to scan (e.g., '22,80,443' or '1-1000')"
    )

def run_nmap(target: str, scan_type: str = "basic", ports: str = "") -> str:
    """Execute nmap scan in Docker environment"""
    
    # Build nmap command based on scan type
    nmap_commands = {
        "basic": ["nmap", "-sS", "-O", target],
        "port": ["nmap", "-sS", "-p", ports or "1-1000", target],
        "service": ["nmap", "-sS", "-sV", "-O", target],
        "stealth": ["nmap", "-sS", "-T2", "-f", target]
    }
    
    if scan_type not in nmap_commands:
        return f"Error: Unknown scan type '{scan_type}'. Available: basic, port, service, stealth"
    
    cmd = nmap_commands[scan_type]
    
    try:
        logger.info(f"Running nmap scan: {' '.join(cmd)}")
        
        # Execute directly in current environment
        result = subprocess.run(
            cmd, 
            capture_output=True, 
            text=True, 
            timeout=300,  # 5 minutes timeout
            cwd=None
        )
        
        if result.returncode == 0:
            output = result.stdout.strip()
            logger.info(f"Nmap scan completed successfully")
            return f"Nmap scan results for {target}:\n\n{output}"
        else:
            error_msg = result.stderr.strip() or "Unknown error"
            logger.error(f"Nmap scan failed: {error_msg}")
            return f"Nmap scan failed for {target}: {error_msg}"
            
    except subprocess.TimeoutExpired:
        logger.error(f"Nmap scan timed out for {target}")
        return f"Nmap scan timed out for {target}"
    except Exception as e:
        logger.error(f"Nmap scan error: {str(e)}")
        return f"Nmap scan error for {target}: {str(e)}"

def nmap_scan_wrapper(input_str: str) -> str:
    """Wrapper function for nmap tool"""
    try:
        # Parse input (simple format: "target [scan_type] [ports]")
        parts = input_str.strip().split()
        if not parts:
            return "Error: Please provide a target host or IP address"
        
        target = parts[0]
        scan_type = parts[1] if len(parts) > 1 else "basic"
        ports = parts[2] if len(parts) > 2 else ""
        
        return run_nmap(target, scan_type, ports)
    except Exception as e:
        return f"Error parsing nmap input: {str(e)}"

# Create LangChain Tool
nmap_tool = Tool(
    name="nmap_scan",
    description="""
    Perform network port scanning using nmap.
    
    Usage: "target [scan_type] [ports]"
    - target: Host or IP address to scan (required)
    - scan_type: basic, port, service, or stealth (default: basic)
    - ports: Specific ports like '22,80,443' or '1-1000' (for port scan)
    
    Examples:
    - "google.com" - Basic scan
    - "google.com service" - Service detection scan
    - "google.com port 80,443" - Scan specific ports
    - "192.168.1.1 stealth" - Stealth scan
    """,
    func=nmap_scan_wrapper
) 