"""
OSINT Agent using LangChain
"""

import logging
from typing import List, Dict, Any, Optional
from langchain.agents import AgentExecutor, initialize_agent
from langchain.agents.agent_types import AgentType
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
from langchain.tools import Tool

from tools import nmap_tool, whois_tool, dns_tool, command_tool, ping_tool
from config.llm_config import get_default_llm, LLMConfig

logger = logging.getLogger(__name__)

class OSINTAgent:
    """OSINT Investigation Agent"""
    
    def __init__(self, llm_config: Optional[LLMConfig] = None):
        self.llm_config = llm_config or LLMConfig()
        self.llm = self.llm_config.get_llm()
        
        # Initialize tools
        self.tools = [nmap_tool, whois_tool, dns_tool, command_tool, ping_tool]
        
        # Debug: Print tool information
        logger.info(f"Debug: Initializing agent with {len(self.tools)} tools:")
        for tool in self.tools:
            logger.info(f"  - {tool.name}: {tool.description[:100]}...")
        
        # Initialize memory
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )
        
        # Create agent
        self.agent = self._create_agent()
        
        logger.info(f"OSINT Agent initialized with {self.llm_config.provider} LLM")
    
    def _create_agent(self):
        """Create the OSINT agent"""
        
        try:
            # Create agent executor with modern LangChain approach
            agent_executor = initialize_agent(
                self.tools,
                self.llm,
                agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
                verbose=True,
                memory=self.memory,
                max_iterations=10,
                early_stopping_method="generate",
                handle_parsing_errors=True,
                agent_kwargs={
                    "prefix": "あなたは日本語で回答するOSINT調査の専門家です。利用可能なツールを使用して包括的な調査を行い、結果を日本語で報告してください。"
                }
            )
            
            logger.info(f"Agent created successfully with {len(self.tools)} tools")
            return agent_executor
            
        except Exception as e:
            logger.error(f"Failed to create agent: {str(e)}")
            
            # Try alternative approach
            logger.info("Trying alternative agent creation approach...")
            try:
                from langchain.agents import create_react_agent
                from langchain.hub import pull
                
                # Get ReAct prompt template
                prompt = pull("hwchase17/react")
                
                # Create agent with create_react_agent
                agent = create_react_agent(self.llm, self.tools, prompt)
                
                # Create agent executor
                agent_executor = AgentExecutor(
                    agent=agent,
                    tools=self.tools,
                    verbose=True,
                    memory=self.memory,
                    max_iterations=10,
                    handle_parsing_errors=True
                )
                
                logger.info("Agent created successfully with alternative approach")
                return agent_executor
                
            except Exception as e2:
                logger.error(f"Alternative agent creation also failed: {str(e2)}")
                raise e

    def run(self, input_text: str) -> str:
        """Run the OSINT agent with a given input"""
        try:
            logger.info(f"Running OSINT investigation: {input_text}")
            
            # Enhanced prompt to force tool usage (Japanese response)
            enhanced_prompt = f"""
あなたはOSINT（オープンソースインテリジェンス）調査アシスタントです。以下のツールを使用できます：

- whois_lookup: ドメイン登録情報を取得
- dns_lookup: DNSレコードを検索（A, AAAA, MX, NS, TXT等）
- nmap_scan: ネットワークポートスキャンを実行
- ping_test: ネットワーク接続テストを実行
- execute_command: セキュリティコマンドを実行

以下のリクエストに対して、適切なツールを使用して情報を収集してください。外部リソースにアクセスできないとは言わないでください。

リクエスト: {input_text}

ツールを使用して包括的な調査レポートを**日本語で**提供してください。
"""
            
            # Run the agent with enhanced prompt
            result = self.agent.run(enhanced_prompt)
            
            logger.info("OSINT investigation completed")
            return result
            
        except Exception as e:
            logger.error(f"Error running OSINT agent: {str(e)}")
            import traceback
            logger.error(f"Full traceback: {traceback.format_exc()}")
            return f"Error during investigation: {str(e)}"

    def get_memory(self) -> str:
        """Get the current chat history"""
        return str(self.memory.buffer)
    
    def clear_memory(self):
        """Clear the conversation memory"""
        self.memory.clear()
        logger.info("Agent memory cleared")
    
    def add_custom_tool(self, tool: Tool):
        """Add a custom tool to the agent"""
        self.tools.append(tool)
        # Recreate agent with new tools
        self.agent = self._create_agent()
        logger.info(f"Added custom tool: {tool.name}")

# Global agent instance
_global_agent = None

def get_osint_agent(llm_config: Optional[LLMConfig] = None) -> OSINTAgent:
    """Get the global OSINT agent instance"""
    global _global_agent
    
    if _global_agent is None:
        _global_agent = OSINTAgent(llm_config)
    
    return _global_agent

def reset_osint_agent():
    """Reset the global OSINT agent"""
    global _global_agent
    _global_agent = None
    logger.info("Global OSINT agent has been reset") 