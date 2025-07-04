# Oracle ChatBot 起動ガイド

## Windows (Cursor) からの起動方法

### 方法1: 起動スクリプトを使用（推奨）
```bash
# ターミナルでWSLに入る
wsl

# プロジェクトディレクトリに移動
cd /mnt/c/Users/k_yam/Dropbox/PC/Desktop/システム関連/Study/Oracle_ChatBot

# 起動スクリプトを実行
./start_app.sh
```

### 方法2: 手動で起動
```bash
# 1. WSLに入る
wsl

# 2. プロジェクトディレクトリに移動
cd /mnt/c/Users/k_yam/Dropbox/PC/Desktop/システム関連/Study/Oracle_ChatBot

# 3. Oracle Instant Clientのパスを設定
export LD_LIBRARY_PATH=/home/kota/instantclient_21_13:$LD_LIBRARY_PATH

# 4. 仮想環境を有効化
source oracle_chatbot_env/bin/activate

# 5. サーバーを起動
python manage.py runserver 0.0.0.0:8001
```

## アクセスURL
- チャットボット: http://localhost:8001/
- Excelエクスポート: http://localhost:8001/export/

## 終了方法
- ターミナルで `Ctrl + C` を押す

## トラブルシューティング

### ポートが使用中の場合
```bash
# 既存のプロセスを確認
lsof -i :8001

# プロセスを終了
pkill -f "manage.py runserver"
```

### Oracle接続エラーの場合
- `.env` ファイルに暗号化された接続情報があることを確認
- Oracle Instant Clientが正しくインストールされていることを確認