"""
LLM Configuration for OSINT Agent
"""

import os
from typing import Dict, Any, Optional
from dotenv import load_dotenv
from langchain.llms import OpenAI
from langchain.chat_models import ChatOpenAI
from langchain.llms import Ollama

# Load environment variables
load_dotenv()

class LLMConfig:
    """Configuration for LLM providers"""
    
    def __init__(self):
        self.provider = os.getenv("LLM_PROVIDER", "openai")
        self.api_key = os.getenv("LLM_API_KEY", "")
        self.model_name = os.getenv("LLM_MODEL", "gpt-3.5-turbo")
        self.temperature = float(os.getenv("LLM_TEMPERATURE", "0.1"))
        self.max_tokens = int(os.getenv("LLM_MAX_TOKENS", "2000"))
        
        # Ollama specific
        self.ollama_base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        
        # Claude specific
        self.claude_api_key = os.getenv("CLAUDE_API_KEY", "")
        
        # Gemini specific
        self.gemini_api_key = os.getenv("GEMINI_API_KEY", "")
    
    def get_llm(self):
        """Get configured LLM instance"""
        
        if self.provider == "openai":
            return self._get_openai_llm()
        elif self.provider == "claude":
            return self._get_claude_llm()
        elif self.provider == "gemini":
            return self._get_gemini_llm()
        elif self.provider == "ollama":
            return self._get_ollama_llm()
        else:
            raise ValueError(f"Unsupported LLM provider: {self.provider}")
    
    def _get_openai_llm(self):
        """Get OpenAI LLM"""
        if not self.api_key:
            raise ValueError("OpenAI API key is required. Set LLM_API_KEY environment variable.")
        
        return ChatOpenAI(
            model_name=self.model_name,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            openai_api_key=self.api_key,
            model_kwargs={"system_message": "あなたは日本語で回答するOSINT調査の専門家です。必ず日本語で回答してください。英語での回答は禁止されています。"}
        )
    
    def _get_claude_llm(self):
        """Get Claude LLM"""
        try:
            from langchain_anthropic import ChatAnthropic
            
            if not self.claude_api_key:
                raise ValueError("Claude API key is required. Set CLAUDE_API_KEY environment variable.")
            
            return ChatAnthropic(
                model=self.model_name or "claude-3-sonnet-20240229",
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                anthropic_api_key=self.claude_api_key,
                system_message="あなたは日本語で回答するOSINT調査の専門家です。必ず日本語で回答してください。英語での回答は禁止されています。"
            )
        except ImportError:
            raise ImportError("langchain-anthropic package is required for Claude support")
    
    def _get_gemini_llm(self):
        """Get Gemini LLM"""
        try:
            from langchain_google_genai import ChatGoogleGenerativeAI
            
            if not self.gemini_api_key:
                raise ValueError("Gemini API key is required. Set GEMINI_API_KEY environment variable.")
            
            return ChatGoogleGenerativeAI(
                model=self.model_name or "gemini-1.5-flash",
                temperature=self.temperature,
                max_output_tokens=self.max_tokens,
                google_api_key=self.gemini_api_key,
                system_instruction="あなたは日本語で回答するOSINT調査の専門家です。必ず日本語で回答してください。英語での回答は禁止されています。"
            )
        except ImportError:
            raise ImportError("langchain-google-genai package is required for Gemini support")
    
    def _get_ollama_llm(self):
        """Get Ollama LLM"""
        try:
            from langchain_ollama import OllamaLLM
            
            return OllamaLLM(
                model=self.model_name or "llama2",
                temperature=self.temperature,
                base_url=self.ollama_base_url
            )
        except ImportError:
            raise ImportError("langchain-ollama package is required for Ollama support")

# Default configuration
DEFAULT_LLM_CONFIG = LLMConfig()

def get_default_llm():
    """Get default LLM instance"""
    return DEFAULT_LLM_CONFIG.get_llm()

# Available LLM providers
AVAILABLE_PROVIDERS = {
    "openai": {
        "name": "OpenAI GPT",
        "models": ["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo"],
        "requires_api_key": True,
        "env_var": "LLM_API_KEY"
    },
    "claude": {
        "name": "Anthropic Claude",
        "models": ["claude-3-sonnet-20240229", "claude-3-opus-20240229", "claude-3-haiku-20240307"],
        "requires_api_key": True,
        "env_var": "CLAUDE_API_KEY"
    },
    "gemini": {
        "name": "Google Gemini",
        "models": ["gemini-1.5-flash", "gemini-1.5-pro", "gemini-pro"],
        "requires_api_key": True,
        "env_var": "GEMINI_API_KEY"
    },
    "ollama": {
        "name": "Ollama (Local)",
        "models": ["llama2", "mistral", "codellama", "phi"],
        "requires_api_key": False,
        "env_var": "OLLAMA_BASE_URL"
    }
}

def get_provider_info():
    """Get available LLM providers information"""
    return AVAILABLE_PROVIDERS 