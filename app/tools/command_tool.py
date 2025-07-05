"""
Command Tool for LangChain Agent
"""

from langchain.tools import Tool
import subprocess
import logging

logger = logging.getLogger(__name__)

# Allowed commands for security
ALLOWED_COMMANDS = [
    "nmap", "nikto", "sqlmap", "radare2", "r2", "binwalk", "volatility",
    "whois", "dig", "nslookup", "curl", "wget", "nc", "netcat",
    "traceroute", "host", "ss", "netstat", "ps", "top", "ls", "cat",
    "grep", "head", "tail", "find", "file", "strings", "hexdump",
    "python3", "python", "bash", "sh"
]

def run_command(command: str) -> str:
    """Execute command in Docker environment"""
    
    # Parse command
    cmd_parts = command.strip().split()
    if not cmd_parts:
        return "Error: No command provided"
    
    base_command = cmd_parts[0]
    
    # Check if command is allowed
    if base_command not in ALLOWED_COMMANDS:
        return f"Error: Command '{base_command}' is not allowed. Allowed commands: {', '.join(ALLOWED_COMMANDS)}"
    
    try:
        logger.info(f"Running command: {command}")
        
        # Execute directly in current environment
        result = subprocess.run(
            ["sh", "-c", command], 
            capture_output=True, 
            text=True, 
            timeout=180,  # 3 minutes timeout
            cwd=None
        )
        
        if result.returncode == 0:
            output = result.stdout.strip()
            logger.info(f"Command completed successfully: {command}")
            return f"Command output:\n\n{output}"
        else:
            error_msg = result.stderr.strip() or "Unknown error"
            logger.error(f"Command failed: {error_msg}")
            return f"Command failed: {error_msg}"
            
    except subprocess.TimeoutExpired:
        logger.error(f"Command timed out: {command}")
        return f"Command timed out: {command}"
    except Exception as e:
        logger.error(f"Command error: {str(e)}")
        return f"Command error: {str(e)}"

def command_wrapper(input_str: str) -> str:
    """Wrapper function for command tool"""
    try:
        command = input_str.strip()
        if not command:
            return "Error: Please provide a command to execute"
        
        return run_command(command)
    except Exception as e:
        return f"Error parsing command input: {str(e)}"

# Create LangChain Tool
command_tool = Tool(
    name="execute_command",
    description=f"""
    Execute allowed security commands in the Docker environment.
    
    Allowed commands: {', '.join(ALLOWED_COMMANDS)}
    
    Usage: "command with arguments"
    
    Examples:
    - "curl -I https://google.com" - Get HTTP headers
    - "ping -c 4 google.com" - Ping test
    - "python3 -c 'import socket; print(socket.gethostbyname(\"google.com\"))'" - Python script
    - "nikto -h google.com" - Web vulnerability scan
    - "sqlmap -u 'http://target.com/page?id=1' --batch" - SQL injection test
    """,
    func=command_wrapper
) 