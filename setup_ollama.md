# Ollama + MenZ-OSINT セットアップガイド

## 1. Ollamaのインストール

### macOS/Linux
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

### Windows
[Ollama公式サイト](https://ollama.ai/)からダウンロード

## 2. モデルのダウンロード

```bash
# 軽量で高性能（推奨）
ollama pull llama3.1:8b

# より軽量（低スペックPC向け）
ollama pull phi3:mini

# コード生成特化
ollama pull codellama:7b

# 日本語対応
ollama pull llama2-japanese:7b
```

## 3. 動作確認

```bash
# Ollamaサーバー起動
ollama serve

# 別ターミナルでテスト
ollama run llama3.1:8b "Hello, how are you?"
```

## 4. MenZ-OSINTでの設定

1. **Streamlit UIにアクセス**: http://localhost:8501
2. **サイドバーで設定**:
   - Provider: `Ollama (Local)`
   - Model: `llama3.1:8b`
   - API Key: 不要
3. **Initialize Agent**をクリック

## 5. 推奨モデル

| モデル | サイズ | 用途 | 必要メモリ |
|--------|--------|------|------------|
| phi3:mini | 2.3GB | 軽量・高速 | 4GB |
| llama3.1:8b | 4.7GB | バランス型 | 8GB |
| mistral:7b | 4.1GB | 推論特化 | 8GB |
| codellama:7b | 3.8GB | 技術調査 | 8GB |

## 6. パフォーマンス調整

```bash
# GPU使用（NVIDIA）
ollama run llama3.1:8b --gpu

# メモリ制限
ollama run llama3.1:8b --memory 4GB
```

## トラブルシューティング

### 接続エラー
```bash
# Ollamaが起動しているか確認
ollama list

# サーバー再起動
pkill ollama
ollama serve
```

### メモリ不足
- より軽量なモデル（phi3:mini）を使用
- 他のアプリケーションを終了 