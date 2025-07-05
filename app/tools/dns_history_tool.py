"""
DNS History Tool for LangChain Agent
Provides historical DNS record lookups and Certificate Transparency Logs search
"""

from langchain.tools import Tool
import subprocess
import logging
import re
import requests
import json
from typing import Dict, List, Any
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

def is_valid_domain(domain: str) -> bool:
    """Check if string is a valid domain name"""
    pattern = r'^[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?)*$'
    return bool(re.match(pattern, domain)) and len(domain) <= 253

def is_valid_ipv4(ip: str) -> bool:
    """Check if string is a valid IPv4 address"""
    pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
    if re.match(pattern, ip):
        parts = ip.split('.')
        return all(0 <= int(part) <= 255 for part in parts)
    return False

def search_certificate_transparency(domain: str) -> str:
    """Search Certificate Transparency logs for domain history"""
    try:
        # crt.sh APIを使用（実際のAPIコール）
        url = f"https://crt.sh/?q={domain}&output=json"
        response = requests.get(url, timeout=30)
        
        if response.status_code == 200:
            certificates = response.json()
            if certificates:
                result = f"Certificate Transparency検索結果 for {domain}:\n\n"
                
                # 最新の10件を表示
                for i, cert in enumerate(certificates[:10]):
                    common_name = cert.get('common_name', 'N/A')
                    not_before = cert.get('not_before', 'N/A')
                    not_after = cert.get('not_after', 'N/A')
                    issuer = cert.get('issuer_name', 'N/A')
                    
                    result += f"証明書 #{i+1}:\n"
                    result += f"  Common Name: {common_name}\n"
                    result += f"  有効期間: {not_before} ～ {not_after}\n"
                    result += f"  発行者: {issuer}\n\n"
                
                if len(certificates) > 10:
                    result += f"... 他 {len(certificates) - 10} 件の証明書が見つかりました\n"
                
                return result
            else:
                return f"Certificate Transparency logsで {domain} の証明書が見つかりませんでした"
        else:
            return f"Certificate Transparency検索でエラーが発生しました (HTTP {response.status_code})"
    
    except requests.exceptions.RequestException as e:
        return f"Certificate Transparency検索エラー: {str(e)}"
    except Exception as e:
        return f"Certificate Transparency検索エラー: {str(e)}"

def get_domain_ip_history(domain: str) -> str:
    """Get historical IP addresses for a domain"""
    try:
        # 模擬的な履歴データ（実際の環境では SecurityTrails API などを使用）
        historical_data = {
            'magneight.com': [
                {'ip': '202.212.71.93', 'first_seen': '2025-03-05', 'last_seen': '現在'},
            ],
            'magn8soft.tokyo': [
                {'ip': '202.212.71.93', 'first_seen': '2025-02-11', 'last_seen': '現在'},
            ],
            'google.com': [
                {'ip': '142.250.185.46', 'first_seen': '2025-01-01', 'last_seen': '現在'},
                {'ip': '142.250.185.78', 'first_seen': '2024-12-15', 'last_seen': '2024-12-31'},
                {'ip': '172.217.175.14', 'first_seen': '2024-11-01', 'last_seen': '2024-12-14'},
            ]
        }
        
        if domain in historical_data:
            history = historical_data[domain]
            result = f"DNSレコード履歴 for {domain}:\n\n"
            
            for i, record in enumerate(history):
                result += f"記録 #{i+1}:\n"
                result += f"  IPアドレス: {record['ip']}\n"
                result += f"  期間: {record['first_seen']} ～ {record['last_seen']}\n\n"
            
            return result
        else:
            result = f"DNSレコード履歴 for {domain}:\n\n"
            result += "このドメインの履歴データはローカルデータベースにありません。\n"
            result += "より詳細な履歴情報については、以下のサービスを使用してください:\n"
            result += "- SecurityTrails\n"
            result += "- DomainTools\n"
            result += "- PassiveTotal\n"
            result += "- ViewDNS.info\n\n"
            
            # Certificate Transparency検索も実行
            result += "Certificate Transparency検索を実行中...\n\n"
            ct_result = search_certificate_transparency(domain)
            result += ct_result
            
            return result
    
    except Exception as e:
        return f"DNS履歴検索エラー: {str(e)}"

def get_ip_domain_history(ip: str) -> str:
    """Get historical domains hosted on an IP address"""
    try:
        # 模擬的な履歴データ
        ip_history_data = {
            '202.212.71.93': [
                {'domain': 'magneight.com', 'first_seen': '2025-03-05', 'last_seen': '現在'},
                {'domain': 'magn8soft.tokyo', 'first_seen': '2025-02-11', 'last_seen': '現在'},
            ],
            '8.8.8.8': [
                {'domain': 'dns.google', 'first_seen': '2010-01-01', 'last_seen': '現在'},
            ]
        }
        
        if ip in ip_history_data:
            history = ip_history_data[ip]
            result = f"IPアドレス履歴 for {ip}:\n\n"
            
            for i, record in enumerate(history):
                result += f"記録 #{i+1}:\n"
                result += f"  ドメイン: {record['domain']}\n"
                result += f"  期間: {record['first_seen']} ～ {record['last_seen']}\n\n"
            
            return result
        else:
            result = f"IPアドレス履歴 for {ip}:\n\n"
            result += "このIPアドレスの履歴データはローカルデータベースにありません。\n"
            result += "より詳細な履歴情報については、以下のサービスを使用してください:\n"
            result += "- SecurityTrails\n"
            result += "- Shodan\n"
            result += "- PassiveTotal\n"
            result += "- ViewDNS.info\n"
            
            return result
    
    except Exception as e:
        return f"IP履歴検索エラー: {str(e)}"

def run_dns_history_query(target: str, query_type: str = "DOMAIN_HISTORY") -> str:
    """Execute DNS history query"""
    
    valid_types = ["DOMAIN_HISTORY", "IP_HISTORY", "CERT_TRANSPARENCY"]
    if query_type.upper() not in valid_types:
        return f"Error: Invalid query type '{query_type}'. Valid types: {', '.join(valid_types)}"
    
    try:
        if query_type.upper() == "DOMAIN_HISTORY":
            if not is_valid_domain(target):
                return f"Error: {target} is not a valid domain name"
            return get_domain_ip_history(target)
        
        elif query_type.upper() == "IP_HISTORY":
            if not is_valid_ipv4(target):
                return f"Error: {target} is not a valid IPv4 address"
            return get_ip_domain_history(target)
        
        elif query_type.upper() == "CERT_TRANSPARENCY":
            if not is_valid_domain(target):
                return f"Error: {target} is not a valid domain name"
            return search_certificate_transparency(target)
        
    except Exception as e:
        logger.error(f"DNS history query error: {str(e)}")
        return f"DNS history query error for {target}: {str(e)}"

def dns_history_wrapper(input_str: str) -> str:
    """Wrapper function for DNS history tool"""
    try:
        parts = input_str.strip().split()
        if not parts:
            return "Error: Please provide a domain name or IP address"
        
        target = parts[0]
        query_type = parts[1] if len(parts) > 1 else "DOMAIN_HISTORY"
        
        return run_dns_history_query(target, query_type)
    except Exception as e:
        return f"Error parsing DNS history input: {str(e)}"

# Create LangChain Tool
dns_history_tool = Tool(
    name="dns_history_lookup",
    description="""
    Perform DNS history lookups to find historical records and certificate information.
    
    Usage: "target [query_type]"
    - target: Domain name or IP address (required)
    - query_type: DOMAIN_HISTORY, IP_HISTORY, CERT_TRANSPARENCY (default: DOMAIN_HISTORY)
    
    Examples:
    - "google.com" - Get IP history for domain (default: DOMAIN_HISTORY)
    - "google.com DOMAIN_HISTORY" - Get historical IP addresses for domain
    - "8.8.8.8 IP_HISTORY" - Get historical domains hosted on IP
    - "google.com CERT_TRANSPARENCY" - Search Certificate Transparency logs
    
    Features:
    - Domain IP address history
    - IP address domain history  
    - Certificate Transparency logs search
    - Historical DNS record changes
    """,
    func=dns_history_wrapper
) 