# Oracle 不具合情報チャットボット

## 概要
Oracle データベースの「T_不連書」テーブルに接続し、TR品番やTR品名、車種などを入力すると、関連する不具合内容、推定不具合原因、対策案などを返答するチャットボットです。

## 主な機能
- **検索機能**: キーワードで不具合情報を検索（最大5件表示）
- **要約機能**: 検索結果を要約し、主要な情報を抽出（最大10件から要約）
- **詳細表示**: 要約結果から個別の詳細情報をモーダルで表示

## 必要な環境
- Python 3.12+
- Django 3.2.25（Oracle 12.2対応）
- cx_Oracle 8.3.0
- Oracle Database 12.2
- Oracle Instant Client 21.13
- libaio ライブラリ（libaio1t64）

## セットアップ

### 1. 仮想環境の作成と有効化
```bash
python3 -m venv oracle_chatbot_env
source oracle_chatbot_env/bin/activate
```

### 2. 必要なパッケージのインストール
```bash
pip install -r requirements.txt
```

### 3. Oracle Instant Client の設定
```bash
# Oracle Instant Client を展開（ホームディレクトリにzipファイルがある場合）
unzip ~/instantclient-basic-linux.x64-21.13.0.0.0dbru.zip

# 環境変数の設定（.bashrc に追加推奨）
export LD_LIBRARY_PATH=/home/kota/instantclient_21_13:$LD_LIBRARY_PATH
```

### 4. libaio のインストール
```bash
sudo apt-get update
sudo apt-get install -y libaio1t64 libaio-dev

# シンボリックリンクの作成（必要な場合）
sudo ln -sf /usr/lib/x86_64-linux-gnu/libaio.so.1t64 /usr/lib/x86_64-linux-gnu/libaio.so.1
```

### 5. データベース設定
`oracle_chatbot/settings.py`でOracle接続設定を確認：
- HOST: 192.168.1.19
- PORT: 1521
- NAME: JKNA
- USER: exesa1
- PASSWORD: oanbdc1

### 6. マイグレーションの実行
```bash
python manage.py migrate
```

### 7. アプリケーションの起動
```bash
# 起動スクリプトを使用
./start_server.sh

# または手動で起動
export LD_LIBRARY_PATH=/home/kota/instantclient_21_13:$LD_LIBRARY_PATH
source oracle_chatbot_env/bin/activate
python manage.py runserver 8001
```

### 8. アクセス
ブラウザで http://127.0.0.1:8001/ にアクセス

## 使用方法

### 検索機能
1. キーワード（TR品番、TR品名、車種など）を入力
2. 「送信」ボタンをクリック
3. 最大5件の詳細情報が表示されます

### 要約機能
1. キーワードを入力
2. 「要約」ボタンをクリック
3. 以下の要約情報が表示されます：
   - 関連車種一覧
   - 主な不具合内容（上位3件）
   - 主な推定原因（上位3件）
   - 主な対策案（上位3件）
4. 各項目（青色のテキスト）をクリックすると詳細情報が表示されます

## データベーステーブル構造
テーブル名: `T_不連書`
- HNO (主キー)
- TR品番
- TR品名
- 車種
- 不具合内容
- 推定不具合原因
- 対策案等

## プロジェクト構造
```
oracle_chatbot/
├── chatbot/
│   ├── models.py        # データベースモデル定義
│   ├── views.py         # ビューロジック（検索・要約・詳細表示）
│   ├── urls.py          # URLルーティング
│   └── __init__.py
├── oracle_chatbot/
│   ├── settings.py      # Django設定ファイル
│   ├── urls.py          # メインURLルーティング
│   └── wsgi.py
├── templates/
│   └── chatbot/
│       └── index.html   # フロントエンドテンプレート
├── manage.py
├── requirements.txt
├── start_server.sh      # 起動スクリプト
└── db.sqlite3          # セッション管理用（Oracle接続失敗時のフォールバック）
```

## トラブルシューティング

### Oracle Client エラー
```
DPI-1047: Cannot locate a 64-bit Oracle Client library
```
→ LD_LIBRARY_PATH が正しく設定されているか確認

### libaio エラー
```
libaio.so.1: cannot open shared object file
```
→ libaio のインストールとシンボリックリンクの作成を確認

### ポート使用中エラー
```
Error: That port is already in use.
```
→ 別のポートを指定するか、既存のプロセスを終了

## 注意事項
- 本番環境では SECRET_KEY を変更してください
- データベース接続情報は環境変数で管理することを推奨
- セッション情報はデフォルトで1時間保持されます