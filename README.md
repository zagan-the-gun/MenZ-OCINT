# MenZ-OSINT

**LangChain搭載のOSINT調査システム**

LLMを活用したOSINT調査のためのLangChainベースのシステムです。Docker上でペネトレーションテスト、セキュリティ監査、フォレンジック、リバースエンジニアリングなどのツールを安全に実行できます。

## 特徴

- **LangChainエージェント**: 自然言語でのOSINT調査指示が可能
- **マルチLLM対応**: OpenAI、Claude、Gemini、Ollamaをサポート
- **直感的なUI**: Streamlitベースのチャットインターフェース
- **セキュリティ重視**: Dockerコンテナ内でのツール実行により、ホストシステムを保護
- **豊富なツール**: 主要なセキュリティ/OSINTツールを提供
- **日本語対応**: 調査結果を日本語で報告

## インストールされるツール

### ペネトレーションテスト
- `nmap` - ネットワークスキャン
- `nikto` - Webサーバー脆弱性スキャン
- `sqlmap` - SQLインジェクション検出

### ネットワーク調査
- `wireshark-common` - パケット解析
- `tcpdump` - ネットワーク監視
- `netcat-traditional` - ネットワーク接続
- `dnsutils` - DNS調査

### フォレンジック
- `volatility3` - メモリ解析

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

### 4. Webインターフェースにアクセス

```bash
# ブラウザで以下のURLにアクセス
http://localhost:8501
```

### 5. 基本的な使用例

#### 1. LLMプロバイダーの設定
サイドバーでLLMプロバイダーを選択し、APIキーを入力：

**推奨設定（無料）:**
- **プロバイダー**: Google Gemini
- **モデル**: gemini-1.5-flash
- **APIキー**: Google AI StudioのAPIキー

**または:**
- **プロバイダー**: Ollama (Local)
- **モデル**: llama3.1:8b
- **APIキー**: 不要

#### 2. エージェントの初期化
「Initialize Agent」ボタンをクリックしてエージェントを初期化

#### 3. OSINT調査の実行

**ドメイン調査:**
```
google.comについて調査してください
```

**ネットワーク調査:**
```
8.8.8.8をスキャンしてください
```

**包括的調査:**
```
microsoft.comのwhois情報とDNS設定を調査してください
```

## 利用可能なツール

### 🔍 Nmap Scan
- ネットワークポートスキャン
- サービス検出
- OS推測

### 📋 Whois Lookup
- ドメイン登録情報
- 登録者情報
- 有効期限

### 🌐 DNS Lookup
- A, AAAA, MX, NS, TXT レコード
- DNS設定の詳細分析

### 🏓 Ping Test
- ネットワーク接続テスト
- 応答時間測定

### ⚡ Command Execution
- 許可されたセキュリティコマンドの実行
- カスタムOSINTタスク

## セキュリティ機能

### 許可されたコマンド制限
セキュリティのため、以下のコマンドのみが実行可能です：
- `nmap`, `nikto`, `whois`, `dig`, `curl`, `wget`
- `radare2`, `binwalk`, `volatility3`, `tcpdump`
- `sqlmap`, `netcat`, `traceroute`

### Docker分離
- コンテナ内でのツール実行により、ホストシステムを保護
- 必要な権限のみ付与（NET_ADMIN, NET_RAW）
- ログ記録によるすべての操作の監査

## 対応LLMプロバイダー

### 🤖 OpenAI
- GPT-3.5-turbo, GPT-4
- APIキー必要

### 🧠 Anthropic Claude
- Claude-3-Sonnet, Claude-3-Opus
- APIキー必要

### 🌟 Google Gemini
- gemini-1.5-flash, gemini-1.5-pro
- APIキー必要（無料枠あり）

### 🦙 Ollama (Local)
- llama3.1:8b, phi3:mini, mistral:7b
- APIキー不要、完全プライベート

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
docker-compose logs -f osint-server

# ログファイルの確認
tail -f logs/osint-server.log
```

### コンテナ内での作業
```bash
# コンテナ内でのシェル実行
docker-compose exec osint-server /bin/bash

# ツールの動作確認
docker-compose exec osint-server nmap --version
```

## 開発・拡張

### 新しいツールの追加
1. `app/tools/` ディレクトリに新しいツールを作成
2. `app/tools/__init__.py` にインポートを追加
3. `app/agents/osint_agent.py` にツールを登録

### LLMプロバイダーの追加
1. `app/config/llm_config.py` に新しいプロバイダーを追加
2. 必要なライブラリを `requirements.txt` に追加

## システム構成

```
MenZ-OSINT/
├── app/
│   ├── main.py                 # Streamlitアプリケーション
│   ├── agents/
│   │   └── osint_agent.py      # LangChainエージェント
│   ├── tools/                  # OSINTツール群
│   │   ├── nmap_tool.py
│   │   ├── whois_tool.py
│   │   ├── dns_tool.py
│   │   ├── ping_tool.py
│   │   └── command_tool.py
│   └── config/
│       └── llm_config.py       # LLM設定
├── Dockerfile                  # Docker設定
├── docker-compose.yml          # Docker Compose設定
├── requirements.txt            # Python依存関係
└── README.md                   # このファイル
```

## ライセンス

MIT License

## 貢献

プルリクエストやイシューの報告を歓迎します。