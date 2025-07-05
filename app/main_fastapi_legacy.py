"""
MCP OSINT Server (LEGACY - 使用されていません)

注意: このファイルは旧MCPベースのシステムです。
現在のシステムはLangChain + Streamlit (main.py) を使用しています。
"""

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import subprocess
import asyncio
import json
import os
from typing import Dict, List, Optional, Any
import logging
import requests

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/logs/mcp-server.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="MCP OSINT Server",
    description="Model Context Protocol Server for OSINT investigations",
    version="1.0.0"
)

# MCPリクエストモデル
class MCPRequest(BaseModel):
    jsonrpc: str = "2.0"
    method: str
    params: Optional[Dict[str, Any]] = None
    id: Optional[str] = None

class MCPResponse(BaseModel):
    jsonrpc: str = "2.0"
    result: Optional[Any] = None
    error: Optional[Dict[str, Any]] = None
    id: Optional[str] = None

# 許可されたコマンドのリスト（セキュリティ制限）
ALLOWED_COMMANDS = [
    "nmap", "nikto", "whois", "dig", "curl", "wget", 
    "radare2", "binwalk", "volatility3", "tcpdump", "sqlmap"
]

@app.get("/")
async def root():
    return {"message": "MCP OSINT Server is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "mcp-osint-server"}

@app.post("/mcp")
async def handle_mcp_request(request: MCPRequest):
    """MCPプロトコルのメインエンドポイント"""
    try:
        logger.info(f"Received MCP request: {request.method}")
        
        if request.method == "tools/list":
            return await list_tools(request)
        elif request.method == "tools/call":
            return await call_tool(request)
        elif request.method == "initialize":
            return await initialize(request)
        else:
            raise HTTPException(status_code=400, detail=f"Unknown method: {request.method}")
    
    except Exception as e:
        logger.error(f"Error handling MCP request: {str(e)}")
        return MCPResponse(
            error={"code": -32603, "message": f"Internal error: {str(e)}"},
            id=request.id
        )

async def initialize(request: MCPRequest):
    """MCP初期化"""
    return MCPResponse(
        result={
            "protocolVersion": "2024-11-05",
            "capabilities": {
                "tools": {}
            },
            "serverInfo": {
                "name": "mcp-osint-server",
                "version": "1.0.0"
            }
        },
        id=request.id
    )

async def list_tools(request: MCPRequest):
    """利用可能なツールのリスト"""
    tools = [
        {
            "name": "nmap_scan",
            "description": "ネットワークスキャンを実行",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "target": {"type": "string", "description": "スキャン対象のIPまたはドメイン"},
                    "options": {"type": "string", "description": "nmapオプション"}
                },
                "required": ["target"]
            }
        },
        {
            "name": "whois_lookup",
            "description": "ドメインのWHOIS情報を取得",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "domain": {"type": "string", "description": "調査対象のドメイン"}
                },
                "required": ["domain"]
            }
        },
        {
            "name": "execute_command",
            "description": "許可されたセキュリティコマンドを実行",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "command": {"type": "string", "description": "実行するコマンド"},
                    "args": {"type": "array", "items": {"type": "string"}, "description": "コマンド引数"}
                },
                "required": ["command"]
            }
        }
    ]
    
    return MCPResponse(
        result={"tools": tools},
        id=request.id
    )

async def call_tool(request: MCPRequest):
    """ツールの実行"""
    if not request.params:
        raise HTTPException(status_code=400, detail="Missing params")
    
    tool_name = request.params.get("name")
    arguments = request.params.get("arguments", {})
    
    if tool_name == "nmap_scan":
        return await execute_nmap(arguments, request.id)
    elif tool_name == "whois_lookup":
        return await execute_whois(arguments, request.id)
    elif tool_name == "execute_command":
        return await execute_system_command(arguments, request.id)
    else:
        raise HTTPException(status_code=400, detail=f"Unknown tool: {tool_name}")

async def execute_nmap(arguments: dict, request_id: str):
    """Nmapスキャンの実行"""
    target = arguments.get("target")
    options = arguments.get("options", "-sS")
    
    if not target:
        return MCPResponse(
            error={"code": -32602, "message": "Missing target parameter"},
            id=request_id
        )
    
    try:
        cmd = ["nmap"] + options.split() + [target]
        result = await run_command(cmd)
        
        return MCPResponse(
            result={
                "content": [
                    {
                        "type": "text",
                        "text": f"Nmap scan results for {target}:\n\n{result}"
                    }
                ]
            },
            id=request_id
        )
    except Exception as e:
        return MCPResponse(
            error={"code": -32603, "message": f"Nmap execution failed: {str(e)}"},
            id=request_id
        )

async def execute_whois(arguments: dict, request_id: str):
    """WHOIS情報の取得"""
    domain = arguments.get("domain")
    
    if not domain:
        return MCPResponse(
            error={"code": -32602, "message": "Missing domain parameter"},
            id=request_id
        )
    
    try:
        cmd = ["whois", domain]
        result = await run_command(cmd)
        
        return MCPResponse(
            result={
                "content": [
                    {
                        "type": "text",
                        "text": f"WHOIS information for {domain}:\n\n{result}"
                    }
                ]
            },
            id=request_id
        )
    except Exception as e:
        return MCPResponse(
            error={"code": -32603, "message": f"WHOIS lookup failed: {str(e)}"},
            id=request_id
        )

async def execute_system_command(arguments: dict, request_id: str):
    """システムコマンドの実行（セキュリティ制限付き）"""
    command = arguments.get("command")
    args = arguments.get("args", [])
    
    if not command:
        return MCPResponse(
            error={"code": -32602, "message": "Missing command parameter"},
            id=request_id
        )
    
    # セキュリティチェック
    if command not in ALLOWED_COMMANDS:
        return MCPResponse(
            error={"code": -32602, "message": f"Command '{command}' not allowed"},
            id=request_id
        )
    
    try:
        cmd = [command] + args
        result = await run_command(cmd)
        
        return MCPResponse(
            result={
                "content": [
                    {
                        "type": "text",
                        "text": f"Command '{' '.join(cmd)}' output:\n\n{result}"
                    }
                ]
            },
            id=request_id
        )
    except Exception as e:
        return MCPResponse(
            error={"code": -32603, "message": f"Command execution failed: {str(e)}"},
            id=request_id
        )

async def run_command(cmd: List[str], timeout: int = 60):
    """コマンドの非同期実行"""
    try:
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=timeout)
        
        if process.returncode != 0:
            raise Exception(f"Command failed with return code {process.returncode}: {stderr.decode()}")
        
        return stdout.decode()
    except asyncio.TimeoutError:
        raise Exception(f"Command timed out after {timeout} seconds")
    except Exception as e:
        raise Exception(f"Command execution error: {str(e)}")

# ChatGPT/Gemini用の簡単なエンドポイントを追加
class SimpleOSINTRequest(BaseModel):
    target: str
    investigation_type: str = "domain"
    tools: List[str] = ["whois", "nmap", "dns"]

class SimpleOSINTResponse(BaseModel):
    success: bool
    summary: str
    details: Dict[str, Any]
    recommendations: List[str]

@app.post("/investigate", response_model=SimpleOSINTResponse)
async def simple_investigate(request: SimpleOSINTRequest):
    """
    ChatGPT/Gemini向けのシンプルなOSINT調査API
    既存のMCPサーバー機能を活用
    """
    try:
        results = {}
        
        # 1. WHOIS調査
        if "whois" in request.tools:
            try:
                whois_args = {"domain": request.target}
                whois_result = await execute_whois(whois_args, "whois_simple")
                if hasattr(whois_result, 'result'):
                    results["whois"] = whois_result.result if whois_result.result else {"error": "No result"}
                else:
                    results["whois"] = whois_result
            except Exception as e:
                results["whois"] = {"error": str(e)}
        
        # 2. Nmap調査
        if "nmap" in request.tools:
            try:
                nmap_args = {"target": request.target, "options": "-sS -p 80,443,8080"}
                nmap_result = await execute_nmap(nmap_args, "nmap_simple")
                if hasattr(nmap_result, 'result'):
                    results["nmap"] = nmap_result.result if nmap_result.result else {"error": "No result"}
                else:
                    results["nmap"] = nmap_result
            except Exception as e:
                results["nmap"] = {"error": str(e)}
        
        # 3. DNS調査
        if "dns" in request.tools:
            try:
                dns_args = {"command": "dig", "args": [request.target, "ANY"]}
                dns_result = await execute_system_command(dns_args, "dns_simple")
                if hasattr(dns_result, 'result'):
                    results["dns"] = dns_result.result if dns_result.result else {"error": "No result"}
                else:
                    results["dns"] = dns_result
            except Exception as e:
                results["dns"] = {"error": str(e)}
        
        # 結果の解析とサマリー生成
        summary = f"🔍 {request.target} の調査結果:\n\n"
        
        # WHOIS結果の分析
        if "whois" in results and "error" not in results["whois"]:
            summary += "✅ WHOIS情報: 正常に取得されました\n"
        else:
            summary += "❌ WHOIS情報: 取得に失敗しました\n"
        
        # Nmap結果の分析
        if "nmap" in results and "error" not in results["nmap"]:
            nmap_content = results["nmap"].get("content", []) if isinstance(results["nmap"], dict) else []
            if nmap_content and "open" in str(nmap_content):
                summary += "⚠️  開放ポートが検出されました\n"
            else:
                summary += "✅ 開放ポートは検出されませんでした\n"
        else:
            summary += "❌ ポートスキャン: 実行に失敗しました\n"
        
        # DNS結果の分析
        if "dns" in results and "error" not in results["dns"]:
            summary += "✅ DNS情報: 正常に取得されました\n"
        else:
            summary += "❌ DNS情報: 取得に失敗しました\n"
        
        # 推奨事項の生成
        recommendations = []
        if "nmap" in results and "error" not in results["nmap"]:
            nmap_content = results["nmap"].get("content", []) if isinstance(results["nmap"], dict) else []
            if nmap_content and "open" in str(nmap_content):
                recommendations.append("開放ポートが検出されました。不要なサービスは停止を検討してください。")
                recommendations.append("ファイアウォール設定の見直しを推奨します。")
        
        recommendations.extend([
            "定期的なセキュリティ監査を実施してください。",
            "脆弱性スキャンを定期的に実行してください。"
        ])
        
        return SimpleOSINTResponse(
            success=True,
            summary=summary,
            details=results,
            recommendations=recommendations
        )
    
    except Exception as e:
        logger.error(f"Simple investigate error: {str(e)}")
        return SimpleOSINTResponse(
            success=False,
            summary=f"調査中にエラーが発生しました: {str(e)}",
            details={"error": str(e)},
            recommendations=["エラーログを確認してください。"]
        )

@app.get("/chatgpt-config")
async def get_chatgpt_config():
    """
    ChatGPT Custom GPT用の設定情報を提供
    """
    return {
        "openapi_schema": {
            "openapi": "3.0.0",
            "info": {
                "title": "OSINT Investigation API",
                "description": "セキュリティ調査とOSINT分析を実行するAPI",
                "version": "1.0.0"
            },
            "servers": [
                {"url": "http://localhost:8000"}
            ],
            "paths": {
                "/investigate": {
                    "post": {
                        "operationId": "investigate_target",
                        "summary": "OSINT調査を実行",
                        "requestBody": {
                            "required": True,
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "target": {
                                                "type": "string",
                                                "description": "調査対象（ドメイン、IPアドレス等）"
                                            },
                                            "investigation_type": {
                                                "type": "string",
                                                "description": "調査タイプ",
                                                "enum": ["domain", "ip", "url"]
                                            },
                                            "tools": {
                                                "type": "array",
                                                "description": "使用するツール",
                                                "items": {
                                                    "type": "string",
                                                    "enum": ["whois", "nmap", "dns"]
                                                }
                                            }
                                        },
                                        "required": ["target"]
                                    }
                                }
                            }
                        },
                        "responses": {
                            "200": {
                                "description": "調査結果",
                                "content": {
                                    "application/json": {
                                        "schema": {
                                            "type": "object",
                                            "properties": {
                                                "success": {"type": "boolean"},
                                                "summary": {"type": "string"},
                                                "details": {"type": "object"},
                                                "recommendations": {
                                                    "type": "array",
                                                    "items": {"type": "string"}
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 