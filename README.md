# MenZ-OSINT

**MCP (Model Context Protocol) OSINTサーバー**

LLMを活用したOSINT調査のためのMCPサーバーです。Docker上でペネトレーションテスト、セキュリティ監査、フォレンジック、リバースエンジニアリングなどのツールを安全に実行できます。

## 特徴

- **セキュリティ重視**: Dockerコンテナ内でのツール実行により、ホストシステムを保護
- **豊富なツール**: Kali Linuxベースで主要なセキュリティ/OSINTツールを提供
- **MCPプロトコル**: LLMとの統合に最適化された標準プロトコル
- **非同期処理**: FastAPIによる高速な並列処理

## インストールされるツール

### ペネトレーションテスト
- `nmap` - ネットワークスキャン
- `nikto` - Webサーバー脆弱性スキャン
- `sqlmap` - SQLインジェクション検出
- `metasploit-framework` - 包括的なペネトレーション検査

### ネットワーク調査
- `wireshark-common` - パケット解析
- `tcpdump` - ネットワーク監視
- `netcat-traditional` - ネットワーク接続
- `dnsutils` - DNS調査

### フォレンジック
- `volatility3` - メモリ解析
- `sleuthkit` - ファイルシステム解析

### リバースエンジニアリング
- `radare2` - バイナリ解析
- `binwalk` - ファームウェア解析

### Web調査
- `curl` - HTTPクライアント
- `wget` - ファイルダウンロード
- `whois` - ドメイン情報
- `dig` - DNS解析

## 起動手順

### 1. 前提条件

- Docker
- Docker Compose

### 2. プロジェクトクローンとディレクトリ作成

```bash
# プロジェクトディレクトリに移動
cd /path/to/MenZ-OSINT

# データディレクトリを作成
mkdir -p data logs
```

### 3. Docker環境の起動

```bash
# Dockerコンテナをビルド・起動
docker-compose up --build

# バックグラウンドで起動する場合
docker-compose up -d --build
```

### 4. 動作確認

```bash
# サーバーの起動確認
curl http://localhost:8000/

# ヘルスチェック
curl http://localhost:8000/health

# MCPツールリストの確認
curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/list",
    "id": "test1"
  }'
```

### 5. 基本的な使用例

#### Nmapスキャンの実行
```bash
curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/call",
    "params": {
      "name": "nmap_scan",
      "arguments": {
        "target": "8.8.8.8",
        "options": "-sS -p 80,443"
      }
    },
    "id": "nmap1"
  }'
```

#### WHOIS情報の取得
```bash
curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/call",
    "params": {
      "name": "whois_lookup",
      "arguments": {
        "domain": "google.com"
      }
    },
    "id": "whois1"
  }'
```

#### カスタムコマンドの実行
```bash
curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/call",
    "params": {
      "name": "execute_command",
      "arguments": {
        "command": "dig",
        "args": ["google.com", "MX"]
      }
    },
    "id": "dig1"
  }'
```

## セキュリティ機能

### 許可されたコマンド制限
セキュリティのため、以下のコマンドのみが実行可能です：
- `nmap`, `nikto`, `whois`, `dig`, `curl`, `wget`
- `radare2`, `binwalk`, `volatility3`, `tcpdump`

### Docker分離
- コンテナ内でのツール実行により、ホストシステムを保護
- 必要な権限のみ付与（NET_ADMIN, NET_RAW）
- ログ記録によるすべての操作の監査

## API仕様

### エンドポイント
- `GET /` - サーバー状態確認
- `GET /health` - ヘルスチェック
- `POST /mcp` - MCPプロトコルメインエンドポイント
- `GET /docs` - FastAPI自動生成ドキュメント

### MCPメソッド
- `initialize` - MCP初期化
- `tools/list` - 利用可能ツールリスト
- `tools/call` - ツール実行

## 停止手順

```bash
# コンテナを停止
docker-compose down

# ボリュームも削除する場合
docker-compose down -v
```

## トラブルシューティング

### ログの確認
```bash
# アプリケーションログ
docker-compose logs -f mcp-osint-server

# ログファイルの確認
tail -f logs/mcp-server.log
```

### コンテナ内での作業
```bash
# コンテナ内でのシェル実行
docker-compose exec mcp-osint-server /bin/bash

# ツールの動作確認
docker-compose exec mcp-osint-server nmap --version
```

## 開発・拡張

### 新しいツールの追加
1. `Dockerfile`で必要なツールをインストール
2. `app/main.py`の`ALLOWED_COMMANDS`に追加
3. 必要に応じて専用の実行関数を作成

### 設定のカスタマイズ
- `docker-compose.yml` - Docker設定
- `requirements.txt` - Python依存関係
- `app/main.py` - アプリケーション設定