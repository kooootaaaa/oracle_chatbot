#!/bin/bash
# 簡単起動スクリプト - パスを間違えないように

echo "=== Oracle ChatBot 起動スクリプト ==="
echo "現在のディレクトリ: $(pwd)"

# 正しいディレクトリにいるかチェック
if [[ $(basename "$PWD") == "Oracle_ChatBot" ]]; then
    echo "✓ 正しいディレクトリにいます"
else
    echo "❌ 間違ったディレクトリです"
    echo "正しいディレクトリに移動してください:"
    echo "cd /mnt/c/Users/k_yam/Dropbox/PC/Desktop/システム関連/Study/Oracle_ChatBot"
    exit 1
fi

# 必要なファイルの存在確認
if [[ ! -f "start_app.sh" ]]; then
    echo "❌ start_app.sh が見つかりません"
    exit 1
fi

if [[ ! -d "oracle_chatbot_env" ]]; then
    echo "❌ 仮想環境が見つかりません"
    exit 1
fi

echo "✓ すべてのファイルが見つかりました"
echo "アプリケーションを起動します..."

# 実際の起動
./start_app.sh