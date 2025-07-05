# Oracle 不具合情報チャットボット

## 概要
Oracle データベースの「T_不連書」テーブルに接続し、TR品番やTR品名、車種などを入力すると、関連する不具合内容、推定不具合原因、対策案などを返答するチャットボットです。

## 主な機能
- **検索機能**: キーワードで不具合情報を検索（最大5件表示）
- **要約機能**: 検索結果を要約し、主要な情報を抽出（最大10件から要約）
- **詳細表示**: 要約結果から個別の詳細情報をモーダルで表示
- **Excelエクスポート機能**: 検索結果をExcelファイルとしてダウンロード

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

### 3. 環境変数の設定
```bash
# .env.example を .env にコピー
cp .env.example .env

# .env ファイルを編集して実際の値を設定
nano .env
```

### 4. Oracle Instant Client の設定
```bash
# Oracle Instant Client を展開（ホームディレクトリにzipファイルがある場合）
unzip ~/instantclient-basic-linux.x64-21.13.0.0.0dbru.zip

# 環境変数の設定（.bashrc に追加推奨）
export LD_LIBRARY_PATH=/home/kota/instantclient_21_13:$LD_LIBRARY_PATH
```

### 5. libaio のインストール
```bash
sudo apt-get update
sudo apt-get install -y libaio1t64 libaio-dev

# シンボリックリンクの作成（必要な場合）
sudo ln -sf /usr/lib/x86_64-linux-gnu/libaio.so.1t64 /usr/lib/x86_64-linux-gnu/libaio.so.1
```

### 6. マイグレーションの実行
```bash
python manage.py migrate
```

### 7. アプリケーションの起動

#### WSLから起動
```bash
# 起動スクリプトを使用
./start_app.sh

# または手動で起動
export LD_LIBRARY_PATH=/home/kota/instantclient_21_13:$LD_LIBRARY_PATH
source oracle_chatbot_env/bin/activate
python manage.py runserver 0.0.0.0:8001
```

#### Windowsから起動
```batch
# バッチファイルをダブルクリック
start.bat
```

### 8. アクセス
- チャットボット: http://localhost:8001/
- Excelエクスポート: http://localhost:8001/export/

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
│       ├── index.html   # フロントエンドテンプレート
│       └── export.html  # Excelエクスポート画面
├── manage.py
├── requirements.txt
├── start_app.sh         # WSL用起動スクリプト
├── start.bat           # Windows用起動バッチ
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

## セキュリティと暗号化

### データベース認証情報の暗号化
本プロジェクトでは、データベース接続情報を安全に管理するため、以下の暗号化システムを実装しています：

1. **暗号化方式**: Fernet（対称鍵暗号、AES 128ビット）
2. **暗号化対象**: データベースホスト、ユーザー名、パスワード、データベース名
3. **保存形式**: Base64エンコード後、.envファイルに保存
4. **復号化**: アプリケーション起動時に自動的に復号化

### 環境変数の設定例
```bash
# .env ファイル
ENCRYPTION_KEY=your-encryption-key-here
DB_HOST_ENCRYPTED=encrypted-host-value
DB_USER_ENCRYPTED=encrypted-user-value
DB_PASSWORD_ENCRYPTED=encrypted-password-value
DB_NAME_ENCRYPTED=encrypted-dbname-value
DB_PORT=1521
SECRET_KEY=your-django-secret-key-here
DEBUG=False  # 本番環境では必ずFalse
```

### セキュリティ上の推奨事項
1. **SECRET_KEY**: 本番環境では強力なランダム値に変更
2. **DEBUG**: 本番環境では必ず`False`に設定
3. **ALLOWED_HOSTS**: 本番環境では特定のホストのみ許可
4. **暗号化キー**: 環境変数として直接設定（.envファイルに含めない）
5. **.gitignore**: .envファイルは必ずバージョン管理から除外

## Excelエクスポート機能

### 概要
検索結果をExcelファイルとしてダウンロードできる機能を提供しています。

### 使用方法
1. ブラウザで http://localhost:8001/export/ にアクセス
2. 検索キーワードを入力
3. 「Excel出力」ボタンをクリック
4. 検索結果がExcelファイルとしてダウンロードされます

### Excelファイルの内容
- ファイル名: `oracle_不具合情報_YYYYMMDD_HHMMSS.xlsx`
- 含まれる列:
  - HNO（管理番号）
  - TR品番
  - TR品名
  - 車種
  - 不具合内容
  - 推定不具合原因
  - 対策案等
- 書式設定:
  - ヘッダー行: 背景色付き、太字
  - 列幅: 自動調整
  - セル内の改行: 自動折り返し

## 注意事項
- 本番環境では SECRET_KEY を変更してください
- データベース接続情報は暗号化されていますが、暗号化キーの管理には注意してください
- セッション情報はデフォルトで1時間保持されます
- Excelエクスポートは最大1000件まで出力されます