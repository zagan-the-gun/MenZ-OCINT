import json
import requests
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
import traceback

def web_history_lookup(domain: str, query_type: str = "COMPREHENSIVE") -> str:
    """
    Web履歴調査を実行する関数
    
    Args:
        domain: 調査対象のドメイン
        query_type: 調査タイプ (COMPREHENSIVE, WEB_ARCHIVE, CERT_ANALYSIS, TECH_ANALYSIS, DOMAIN_TIMELINE)
    
    Returns:
        調査結果の文字列
    """
    try:
        domain = domain.strip().lower()
        
        # ドメインの基本的な検証
        if not domain or '.' not in domain:
            return f"エラー: 無効なドメイン名です: {domain}"
        
        if query_type == "COMPREHENSIVE":
            return _comprehensive_analysis(domain)
        elif query_type == "WEB_ARCHIVE":
            return _web_archive_analysis(domain)
        elif query_type == "CERT_ANALYSIS":
            return _certificate_analysis(domain)
        elif query_type == "TECH_ANALYSIS":
            return _technical_analysis(domain)
        elif query_type == "DOMAIN_TIMELINE":
            return _domain_timeline(domain)
        else:
            return f"エラー: 不明な調査タイプです: {query_type}"
            
    except Exception as e:
        return f"Web履歴調査エラー: {str(e)}\n{traceback.format_exc()}"

def _comprehensive_analysis(domain: str) -> str:
    """包括的な分析を実行"""
    result = f"=== {domain} 包括的Web履歴調査 ===\n\n"
    
    # Certificate Transparency分析
    result += "🔐 Certificate Transparency分析\n"
    result += "=" * 50 + "\n"
    cert_data = _get_certificate_data(domain)
    if cert_data:
        result += _format_certificate_analysis(cert_data)
    else:
        result += "証明書データが見つかりませんでした\n"
    result += "\n"
    
    # Wayback Machine分析
    result += "🌐 Wayback Machine履歴分析\n"
    result += "=" * 50 + "\n"
    archive_data = _get_wayback_data(domain)
    if archive_data:
        result += _format_wayback_analysis(archive_data)
    else:
        result += "アーカイブデータが見つかりませんでした\n"
    result += "\n"
    
    # 技術的分析
    result += "🛠️ 技術インフラ分析\n"
    result += "=" * 50 + "\n"
    if cert_data:
        result += _format_technical_analysis(cert_data)
    else:
        result += "技術分析に必要なデータが不足しています\n"
    result += "\n"
    
    # タイムライン分析
    result += "📅 活動タイムライン\n"
    result += "=" * 50 + "\n"
    result += _format_timeline_analysis(cert_data, archive_data)
    
    return result

def _web_archive_analysis(domain: str) -> str:
    """Wayback Machine専用分析"""
    result = f"=== {domain} Wayback Machine履歴調査 ===\n\n"
    
    # メインドメインとwwwサブドメインの両方を調査
    domains_to_check = [domain, f"www.{domain}"]
    
    for check_domain in domains_to_check:
        result += f"📋 {check_domain} のアーカイブ履歴\n"
        result += "-" * 40 + "\n"
        
        archive_data = _get_wayback_data(check_domain)
        if archive_data:
            result += _format_wayback_analysis(archive_data)
        else:
            result += f"{check_domain} のアーカイブが見つかりませんでした\n"
        result += "\n"
    
    return result

def _certificate_analysis(domain: str) -> str:
    """Certificate Transparency専用分析"""
    result = f"=== {domain} Certificate Transparency分析 ===\n\n"
    
    cert_data = _get_certificate_data(domain)
    if cert_data:
        result += _format_certificate_analysis(cert_data)
        result += "\n"
        result += _format_technical_analysis(cert_data)
    else:
        result += "証明書データが見つかりませんでした\n"
    
    return result

def _technical_analysis(domain: str) -> str:
    """技術インフラ専用分析"""
    result = f"=== {domain} 技術インフラ分析 ===\n\n"
    
    cert_data = _get_certificate_data(domain)
    if cert_data:
        result += _format_technical_analysis(cert_data)
    else:
        result += "技術分析に必要なデータが不足しています\n"
    
    return result

def _domain_timeline(domain: str) -> str:
    """ドメインタイムライン専用分析"""
    result = f"=== {domain} ドメインタイムライン ===\n\n"
    
    cert_data = _get_certificate_data(domain)
    archive_data = _get_wayback_data(domain)
    
    result += _format_timeline_analysis(cert_data, archive_data)
    
    return result

def _get_certificate_data(domain: str) -> Optional[List[Dict]]:
    """Certificate Transparencyデータを取得"""
    try:
        url = f'https://crt.sh/?q={domain}&output=json'
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list) and len(data) > 0:
                return data
    except Exception as e:
        print(f"Certificate Transparency取得エラー: {e}")
    
    return None

def _get_wayback_data(domain: str) -> Optional[List[List]]:
    """Wayback Machineデータを取得"""
    try:
        url = f'https://web.archive.org/cdx/search/cdx?url={domain}&output=json&limit=50'
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list) and len(data) > 1:  # ヘッダー行を除く
                return data
    except Exception as e:
        print(f"Wayback Machine取得エラー: {e}")
    
    return None

def _format_certificate_analysis(cert_data: List[Dict]) -> str:
    """証明書分析結果をフォーマット"""
    result = f"総証明書数: {len(cert_data)}件\n\n"
    
    # 証明書を日付順にソート
    sorted_certs = sorted(cert_data, key=lambda x: x.get('not_before', ''))
    
    # 最初と最後の証明書
    if sorted_certs:
        first_cert = sorted_certs[0]
        last_cert = sorted_certs[-1]
        
        result += "🔍 証明書の使用期間\n"
        result += f"  最初の証明書: {first_cert.get('not_before', 'N/A')}\n"
        result += f"  最新の証明書: {last_cert.get('not_before', 'N/A')}\n"
        result += f"  最新の有効期限: {last_cert.get('not_after', 'N/A')}\n\n"
    
    # 証明書発行者の分析
    issuers = {}
    for cert in cert_data:
        issuer = cert.get('issuer_name', 'Unknown')
        issuers[issuer] = issuers.get(issuer, 0) + 1
    
    result += "🔍 証明書発行者の分析\n"
    for issuer, count in sorted(issuers.items(), key=lambda x: x[1], reverse=True):
        result += f"  {issuer}: {count}件\n"
    result += "\n"
    
    # 年別の証明書発行数
    years = {}
    for cert in cert_data:
        date_str = cert.get('not_before', '')
        if date_str:
            try:
                year = date_str[:4]
                years[year] = years.get(year, 0) + 1
            except:
                pass
    
    result += "🔍 年別証明書発行数\n"
    for year, count in sorted(years.items()):
        result += f"  {year}年: {count}件\n"
    result += "\n"
    
    # サブドメインの確認
    subdomains = set()
    for cert in cert_data:
        common_name = cert.get('common_name', '')
        name_value = cert.get('name_value', '')
        if common_name:
            subdomains.add(common_name)
        if name_value:
            for name in name_value.split('\n'):
                if name.strip():
                    subdomains.add(name.strip())
    
    result += "🔍 発見されたサブドメイン\n"
    for subdomain in sorted(subdomains):
        result += f"  {subdomain}\n"
    result += "\n"
    
    return result

def _format_wayback_analysis(archive_data: List[List]) -> str:
    """Wayback Machine分析結果をフォーマット"""
    archives = archive_data[1:]  # ヘッダー行を除く
    result = f"総アーカイブ数: {len(archives)}件\n\n"
    
    if archives:
        # 最初と最後のアーカイブ
        first_archive = archives[0]
        last_archive = archives[-1]
        
        result += "🔍 アーカイブの期間\n"
        result += f"  最初のアーカイブ: {first_archive[1]} - {first_archive[2]}\n"
        result += f"  最後のアーカイブ: {last_archive[1]} - {last_archive[2]}\n\n"
        
        # 年別アーカイブ数
        years = {}
        for archive in archives:
            year = archive[1][:4]
            years[year] = years.get(year, 0) + 1
        
        result += "🔍 年別アーカイブ数\n"
        for year, count in sorted(years.items()):
            result += f"  {year}年: {count}件\n"
        result += "\n"
        
        # HTTPステータスコード分析
        status_codes = {}
        for archive in archives:
            if len(archive) > 4:
                status = archive[4]
                status_codes[status] = status_codes.get(status, 0) + 1
        
        result += "🔍 HTTPステータスコード分布\n"
        for status, count in sorted(status_codes.items()):
            result += f"  {status}: {count}件\n"
        result += "\n"
        
        # 最近のアーカイブ詳細
        result += "🔍 最近のアーカイブ詳細\n"
        for archive in archives[-5:]:
            timestamp = archive[1]
            url = archive[2]
            status = archive[4] if len(archive) > 4 else 'N/A'
            mimetype = archive[3] if len(archive) > 3 else 'N/A'
            result += f"  {timestamp}: {url} (Status: {status}, Type: {mimetype})\n"
        result += "\n"
    
    return result

def _format_technical_analysis(cert_data: List[Dict]) -> str:
    """技術分析結果をフォーマット"""
    result = ""
    
    # Cloudflareの使用履歴分析
    cloudflare_certs = [cert for cert in cert_data if 'cloudflare' in cert.get('issuer_name', '').lower()]
    
    if cloudflare_certs:
        result += "🔍 Cloudflareの使用履歴\n"
        result += f"  Cloudflare証明書: {len(cloudflare_certs)}件\n"
        for cert in cloudflare_certs:
            result += f"  発行期間: {cert.get('not_before', 'N/A')} ～ {cert.get('not_after', 'N/A')}\n"
        result += "\n"
    
    # 証明書更新パターン分析
    sorted_certs = sorted(cert_data, key=lambda x: x.get('not_before', ''))
    renewal_intervals = []
    
    for i in range(1, len(sorted_certs)):
        try:
            prev_date = datetime.fromisoformat(sorted_certs[i-1].get('not_before', '').replace('Z', '+00:00'))
            curr_date = datetime.fromisoformat(sorted_certs[i].get('not_before', '').replace('Z', '+00:00'))
            interval = (curr_date - prev_date).days
            if 0 < interval < 365:  # 1年以内の更新
                renewal_intervals.append(interval)
        except:
            pass
    
    if renewal_intervals:
        avg_interval = sum(renewal_intervals) / len(renewal_intervals)
        result += "🔍 証明書更新パターン分析\n"
        result += f"  平均更新間隔: {avg_interval:.1f}日\n"
        result += f"  最短更新間隔: {min(renewal_intervals)}日\n"
        result += f"  最長更新間隔: {max(renewal_intervals)}日\n"
        
        # 更新頻度の分析
        if avg_interval < 30:
            result += "  🔸 頻繁な証明書更新 - 自動更新システム使用の可能性\n"
        elif avg_interval < 90:
            result += "  🔸 定期的な証明書更新 - 90日サイクル（Let's Encrypt標準）\n"
        else:
            result += "  🔸 長期間の証明書更新 - 有料証明書使用の可能性\n"
        result += "\n"
    
    # 証明書の種類分析
    cert_types = {'DV': 0, 'OV': 0, 'EV': 0, 'Wildcard': 0}
    
    for cert in cert_data:
        common_name = cert.get('common_name', '')
        name_value = cert.get('name_value', '')
        
        if common_name.startswith('*.') or '*.artoautio.com' in name_value:
            cert_types['Wildcard'] += 1
        else:
            cert_types['DV'] += 1  # 基本的にはDV証明書
    
    result += "🔍 証明書種類の分布\n"
    for cert_type, count in cert_types.items():
        if count > 0:
            result += f"  {cert_type}: {count}件\n"
    result += "\n"
    
    # 活動停止時期の推定
    if sorted_certs:
        latest_cert = sorted_certs[-1]
        latest_date = latest_cert.get('not_before', '')
        expiry_date = latest_cert.get('not_after', '')
        
        result += "🔍 活動停止時期の推定\n"
        result += f"  最新の証明書発行: {latest_date}\n"
        result += f"  最新の証明書有効期限: {expiry_date}\n"
        
        try:
            expiry_dt = datetime.fromisoformat(expiry_date.replace('Z', '+00:00'))
            now = datetime.now(timezone.utc)
            if now > expiry_dt:
                result += "  🔴 証明書は既に期限切れ - サイトは停止している可能性が高い\n"
            else:
                days_remaining = (expiry_dt - now).days
                result += f"  🟡 証明書有効期限まで残り {days_remaining} 日\n"
        except:
            result += "  🔴 証明書期限の確認に失敗\n"
        result += "\n"
    
    return result

def _format_timeline_analysis(cert_data: Optional[List[Dict]], archive_data: Optional[List[List]]) -> str:
    """タイムライン分析結果をフォーマット"""
    result = ""
    
    # 証明書とアーカイブの統合タイムライン
    events = []
    
    if cert_data:
        for cert in cert_data:
            date_str = cert.get('not_before', '')
            if date_str:
                try:
                    date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                    issuer = cert.get('issuer_name', 'Unknown')[:50]  # 長すぎる場合は切り詰め
                    events.append((date, 'CERT', f"証明書発行: {issuer}"))
                except:
                    pass
    
    if archive_data:
        archives = archive_data[1:]  # ヘッダー行を除く
        for archive in archives:
            timestamp = archive[1]
            try:
                date = datetime.strptime(timestamp, '%Y%m%d%H%M%S').replace(tzinfo=timezone.utc)
                url = archive[2]
                status = archive[4] if len(archive) > 4 else 'N/A'
                events.append((date, 'ARCHIVE', f"アーカイブ: {url} (Status: {status})"))
            except:
                pass
    
    # イベントを時系列順にソート
    events.sort(key=lambda x: x[0])
    
    if events:
        result += "📅 時系列イベント（最新20件）\n"
        for date, event_type, description in events[-20:]:
            result += f"  {date.strftime('%Y-%m-%d %H:%M:%S')} [{event_type}] {description}\n"
        result += "\n"
        
        # 活動期間の分析
        if len(events) > 1:
            start_date = events[0][0]
            end_date = events[-1][0]
            duration = (end_date - start_date).days
            
            result += "🔍 活動期間の分析\n"
            result += f"  開始日: {start_date.strftime('%Y-%m-%d')}\n"
            result += f"  最終活動日: {end_date.strftime('%Y-%m-%d')}\n"
            result += f"  総活動期間: {duration}日（約{duration//365}年{(duration%365)//30}ヶ月）\n"
    else:
        result += "タイムライン分析に必要なデータが不足しています\n"
    
    return result

def web_history_wrapper(query: str) -> str:
    """
    Web履歴調査のラッパー関数
    
    Args:
        query: "domain_name QUERY_TYPE" 形式の文字列
               例: "example.com COMPREHENSIVE", "example.com WEB_ARCHIVE"
    
    Returns:
        調査結果の文字列
    """
    try:
        parts = query.strip().split()
        if len(parts) < 1:
            return "エラー: ドメイン名を指定してください"
        
        domain = parts[0]
        query_type = parts[1] if len(parts) > 1 else "COMPREHENSIVE"
        
        return web_history_lookup(domain, query_type)
        
    except Exception as e:
        return f"Web履歴調査エラー: {str(e)}"

# LangChain Tool definition
from langchain.tools import Tool

web_history_tool = Tool(
    name="web_history_lookup",
    description=(
        "Web履歴調査ツール。Certificate TransparencyとWayback Machineを使用してドメインの包括的な履歴を調査します。"
        "使用方法: 'domain_name QUERY_TYPE'の形式で入力してください。"
        "QUERY_TYPEは以下から選択: "
        "COMPREHENSIVE（包括的な分析）, WEB_ARCHIVE（Wayback Machine履歴）, CERT_ANALYSIS（証明書分析）, "
        "TECH_ANALYSIS（技術インフラ分析）, DOMAIN_TIMELINE（ドメインタイムライン）。"
        "省略した場合はCOMPREHENSIVEが使用されます。"
        "例: 'example.com COMPREHENSIVE', 'example.com WEB_ARCHIVE'"
    ),
    func=web_history_wrapper
) 