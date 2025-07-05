"""
OSINT Investigation Chat Interface
LangChain-based OSINT system with Streamlit UI
"""

import streamlit as st
import logging
import os
from typing import Optional, Dict, Any
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import our modules
from agents.osint_agent import get_osint_agent, reset_osint_agent
from config.llm_config import LLMConfig, get_provider_info, AVAILABLE_PROVIDERS

# Page configuration
st.set_page_config(
    page_title="MenZ-OSINT Agent",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "agent" not in st.session_state:
    st.session_state.agent = None
if "llm_config" not in st.session_state:
    st.session_state.llm_config = None

def initialize_agent(llm_config: LLMConfig) -> bool:
    """Initialize the OSINT agent"""
    try:
        # Reset the global agent to force new initialization
        reset_osint_agent()
        
        # Initialize new agent
        st.session_state.agent = get_osint_agent(llm_config)
        st.session_state.llm_config = llm_config
        
        # Debug: Show agent tools
        if hasattr(st.session_state.agent, 'tools'):
            tool_names = [tool.name for tool in st.session_state.agent.tools]
            st.info(f"Debug: Available tools: {tool_names}")
        elif hasattr(st.session_state.agent, 'agent') and hasattr(st.session_state.agent.agent, 'tools'):
            tool_names = [tool.name for tool in st.session_state.agent.agent.tools]
            st.info(f"Debug: Available tools: {tool_names}")
        else:
            st.warning("Debug: Could not find tools in agent")
        
        return True
    except Exception as e:
        st.error(f"Failed to initialize agent: {str(e)}")
        import traceback
        st.code(traceback.format_exc())
        return False

def main():
    """Main application"""
    
    # Header
    st.title("🔍 MenZ-OSINT Agent")
    st.markdown("**LangChain-powered OSINT Investigation Assistant**")
    st.markdown("---")
    
    # Sidebar for configuration
    with st.sidebar:
        st.header("🛠️ Configuration")
        
        # LLM Provider Selection
        provider_info = get_provider_info()
        provider_names = {k: v["name"] for k, v in provider_info.items()}
        
        selected_provider = st.selectbox(
            "Select LLM Provider",
            options=list(provider_names.keys()),
            format_func=lambda x: provider_names[x],
            index=0
        )
        
        # Model Selection
        available_models = provider_info[selected_provider]["models"]
        selected_model = st.selectbox(
            "Select Model",
            options=available_models,
            index=0
        )
        
        # API Key Input (if required)
        api_key = ""
        if provider_info[selected_provider]["requires_api_key"]:
            env_var = provider_info[selected_provider]["env_var"]
            api_key = st.text_input(
                f"API Key ({env_var})",
                type="password",
                help=f"Enter your {provider_names[selected_provider]} API key"
            )
        
        # Advanced Settings
        st.subheader("Advanced Settings")
        temperature = st.slider("Temperature", 0.0, 1.0, 0.1, 0.1)
        max_tokens = st.slider("Max Tokens", 100, 4000, 2000, 100)
        
        # Initialize Agent Button
        if st.button("Initialize Agent", type="primary"):
            if provider_info[selected_provider]["requires_api_key"] and not api_key:
                st.error("API key is required for this provider")
            else:
                # Set environment variables
                if api_key:
                    if selected_provider == "openai":
                        os.environ["LLM_API_KEY"] = api_key
                    elif selected_provider == "claude":
                        os.environ["CLAUDE_API_KEY"] = api_key
                    elif selected_provider == "gemini":
                        os.environ["GEMINI_API_KEY"] = api_key
                
                # Set other environment variables
                os.environ["LLM_PROVIDER"] = selected_provider
                os.environ["LLM_MODEL"] = selected_model
                os.environ["LLM_TEMPERATURE"] = str(temperature)
                os.environ["LLM_MAX_TOKENS"] = str(max_tokens)
                
                # Debug: Show configuration
                st.info(f"Debug: Provider={selected_provider}, Model={selected_model}")
                if selected_provider == "gemini":
                    st.info(f"Debug: Gemini API Key set: {bool(os.environ.get('GEMINI_API_KEY'))}")
                
                # Create LLM config
                try:
                    llm_config = LLMConfig()
                    
                    # Test LLM initialization
                    test_llm = llm_config.get_llm()
                    st.info(f"Debug: LLM type: {type(test_llm)}")
                    
                    # Initialize agent
                    if initialize_agent(llm_config):
                        st.success(f"Agent initialized with {provider_names[selected_provider]}!")
                        st.rerun()
                except Exception as e:
                    st.error(f"Configuration error: {str(e)}")
                    st.error(f"Debug: Exception type: {type(e)}")
                    import traceback
                    st.code(traceback.format_exc())
        
        # Agent Status
        st.subheader("Agent Status")
        if st.session_state.agent:
            st.success("✅ Agent Ready")
            st.info(f"Provider: {st.session_state.llm_config.provider}")
            st.info(f"Model: {st.session_state.llm_config.model_name}")
        else:
            st.warning("⚠️ Agent Not Initialized")
        
        # Clear Memory Button
        if st.session_state.agent:
            if st.button("Clear Memory"):
                st.session_state.agent.clear_memory()
                st.session_state.messages = []
                st.success("Memory cleared!")
                st.rerun()
        
        # Available Tools
        st.subheader("Available Tools")
        st.markdown("""
        - **🔍 Nmap Scan** - Network reconnaissance
        - **📋 Whois Lookup** - Domain registration info
        - **🌐 DNS Lookup** - DNS record queries
        - **📜 DNS History** - Historical DNS records & Certificate Transparency
        - **🌍 Web History** - Certificate Transparency + Wayback Machine (サブドメイン検出)
        - **🏓 Ping Test** - Network connectivity test
        - **⚡ Command Execution** - Security tools
        """)
    
    # Main chat interface
    if not st.session_state.agent:
        st.info("👈 Please configure and initialize the agent in the sidebar to begin.")
        st.markdown("""
        ### Welcome to MenZ-OSINT Agent!
        
        This is a LangChain-powered OSINT investigation assistant that can help you:
        
        - 🔍 **Network Reconnaissance** - Scan ports and services
        - 📋 **Domain Intelligence** - Gather domain registration information
        - 🌐 **DNS Analysis** - Query various DNS records
        - ⚡ **Tool Execution** - Run security tools in a safe environment
        
        **Example investigations:**
        - "Investigate google.com"
        - "magn8soft.tokyoのサブドメインを全て教えて下さい"
        - "Perform a comprehensive scan of 192.168.1.1"
        - "Find all DNS records for example.com"
        - "example.comの過去の履歴を詳細に調査してください"
        - "Check what services are running on port 80 for github.com"
        """)
        return
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if "timestamp" in message:
                st.caption(f"⏰ {message['timestamp']}")
    
    # Chat input
    if prompt := st.chat_input("What would you like to investigate?"):
        # Add user message
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        st.session_state.messages.append({
            "role": "user", 
            "content": prompt,
            "timestamp": timestamp
        })
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
            st.caption(f"⏰ {timestamp}")
        
        # Get agent response
        with st.chat_message("assistant"):
            with st.spinner("🔍 Investigating..."):
                try:
                    response = st.session_state.agent.run(prompt)
                    st.markdown(response)
                    
                    # Add assistant message
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    st.session_state.messages.append({
                        "role": "assistant", 
                        "content": response,
                        "timestamp": timestamp
                    })
                    st.caption(f"⏰ {timestamp}")
                    
                except Exception as e:
                    error_msg = f"Error during investigation: {str(e)}"
                    st.error(error_msg)
                    st.session_state.messages.append({
                        "role": "assistant", 
                        "content": error_msg,
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    })

# Run the main application
main()