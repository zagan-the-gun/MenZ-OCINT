FROM ubuntu:22.04

# 基本的なシステムアップデート
RUN apt-get update && apt-get upgrade -y

# OSINT/セキュリティツールのインストール
RUN DEBIAN_FRONTEND=noninteractive apt-get install -y \
    # ペネトレーションテスト
    nmap nikto \
    # ネットワーク調査
    wireshark-common tcpdump netcat-traditional dnsutils iputils-ping \
    # リバースエンジニアリング
    binwalk \
    # Web調査
    curl wget whois dnsutils \
    # Python環境
    python3 python3-pip python3-venv \
    # その他の基本ツール
    git vim nano build-essential && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# より高度なツールを手動でインストール
RUN pip3 install --upgrade pip
RUN pip3 install volatility3

# Radare2のインストール
RUN git clone https://github.com/radareorg/radare2 && \
    cd radare2 && \
    ./sys/install.sh && \
    cd .. && \
    rm -rf radare2

# SQLMapのインストール
RUN git clone https://github.com/sqlmapproject/sqlmap.git /opt/sqlmap && \
    ln -s /opt/sqlmap/sqlmap.py /usr/local/bin/sqlmap && \
    chmod +x /usr/local/bin/sqlmap

# 作業ディレクトリの設定
WORKDIR /app

# Python依存関係のインストール
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# アプリケーションコードのコピー
COPY app/ ./
COPY test_docker.py ./

# データディレクトリの作成
RUN mkdir -p /data /logs

# ポート公開
EXPOSE 8501

# 環境変数の設定
ENV PYTHONPATH=/app

# アプリケーションの起動
CMD ["streamlit", "run", "main.py", "--server.address", "0.0.0.0", "--server.port", "8501", "--server.headless", "true"] 