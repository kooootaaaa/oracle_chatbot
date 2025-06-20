#!/bin/bash

echo "Oracle 不具合情報チャットボット - 開発版"
echo "=" * 50

# Oracle環境変数設定
export LD_LIBRARY_PATH=/home/kota/instantclient_21_13:$LD_LIBRARY_PATH

# 仮想環境有効化
source /home/kota/oracle_chatbot_env/bin/activate

# Pythonスクリプト実行
python oracle_chatbot_standalone.py