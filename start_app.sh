#!/bin/bash
# Oracle ChatBotアプリケーション起動スクリプト

echo "Oracle ChatBotを起動します..."

# Oracle Instant Clientのパスを設定
export LD_LIBRARY_PATH=/home/kota/instantclient_21_13:$LD_LIBRARY_PATH

# 仮想環境を有効化
source oracle_chatbot_env/bin/activate

# サーバーを起動
echo "サーバーを起動中..."
echo "ブラウザで http://localhost:8001/ にアクセスしてください"
echo "終了するには Ctrl+C を押してください"
python manage.py runserver 0.0.0.0:8001