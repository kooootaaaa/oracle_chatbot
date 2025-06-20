#!/usr/bin/env python3
"""
Oracle 不具合情報チャットボット - スタンドアロン版
単一ファイルで実行可能なチャットボットアプリケーション
"""

import os
import sys
import json
import html
import webbrowser
import threading
import time
from pathlib import Path
from flask import Flask, render_template_string, request, jsonify
from dotenv import load_dotenv

# 実行ファイルのパスを取得
if getattr(sys, 'frozen', False):
    # PyInstallerで実行ファイル化された場合
    BASE_DIR = Path(sys._MEIPASS)
    APP_DIR = Path(sys.executable).parent
else:
    # 通常のPythonスクリプトとして実行された場合
    BASE_DIR = Path(__file__).parent
    APP_DIR = BASE_DIR

# 環境変数の読み込み
env_file = APP_DIR / '.env'
if env_file.exists():
    load_dotenv(env_file)

# デフォルト設定
DEFAULT_CONFIG = {
    'DB_ENGINE': 'django.db.backends.sqlite3',
    'DB_NAME': str(APP_DIR / 'chatbot.db'),
    'DB_USER': '',
    'DB_PASSWORD': '',
    'DB_HOST': '',
    'DB_PORT': '',
    'SECRET_KEY': 'standalone-chatbot-key',
    'DEBUG': 'True'
}

# 設定の読み込み
def get_config():
    config = {}
    for key, default in DEFAULT_CONFIG.items():
        config[key] = os.getenv(key, default)
    return config

# Oracle接続用のモデルクラス
class OracleConnection:
    def __init__(self, config):
        self.config = config
        self.connection = None
        
    def connect(self):
        if self.config['DB_ENGINE'] == 'django.db.backends.oracle':
            try:
                import cx_Oracle
                dsn = cx_Oracle.makedsn(
                    self.config['DB_HOST'],
                    self.config['DB_PORT'],
                    self.config['DB_NAME']
                )
                self.connection = cx_Oracle.connect(
                    self.config['DB_USER'],
                    self.config['DB_PASSWORD'],
                    dsn
                )
                return True
            except Exception as e:
                print(f"Oracle接続エラー: {e}")
                return False
        return False
    
    def search(self, keywords):
        if not self.connection:
            return []
        
        try:
            cursor = self.connection.cursor()
            
            # 検索クエリの構築
            where_conditions = []
            params = []
            
            for keyword in keywords:
                condition = """(
                    UPPER("TR品番") LIKE UPPER('%' || :keyword || '%') OR
                    UPPER("TR品名") LIKE UPPER('%' || :keyword || '%') OR
                    UPPER("車種") LIKE UPPER('%' || :keyword || '%') OR
                    UPPER("不具合内容") LIKE UPPER('%' || :keyword || '%') OR
                    UPPER("推定不具合原因") LIKE UPPER('%' || :keyword || '%') OR
                    UPPER("対策案等") LIKE UPPER('%' || :keyword || '%')
                )"""
                where_conditions.append(condition)
                params.append(keyword)
            
            query = f'''
                SELECT "HNO", "TR品番", "TR品名", "車種", "不具合内容", "推定不具合原因", "対策案等"
                FROM "T_不連書"
                WHERE {' OR '.join(where_conditions)}
                AND ROWNUM <= 10
            '''
            
            cursor.execute(query, params)
            results = cursor.fetchall()
            cursor.close()
            
            # LOBデータを適切に処理
            processed_results = []
            for row in results:
                def process_value(value):
                    if value is None:
                        return ''
                    # LOBオブジェクトの場合は読み込む
                    if hasattr(value, 'read'):
                        try:
                            return value.read()
                        except:
                            return str(value)
                    return str(value)
                
                processed_results.append({
                    'hno': process_value(row[0]),
                    'tr_hinban': process_value(row[1]),
                    'tr_hinmei': process_value(row[2]),
                    'shashu': process_value(row[3]),
                    'fuguai_naiyou': process_value(row[4]),
                    'suitei_fuguai_genin': process_value(row[5]),
                    'taisaku_an': process_value(row[6])
                })
            
            return processed_results
        except Exception as e:
            print(f"検索エラー: {e}")
            return []

# HTMLテンプレート
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Oracle 不具合情報チャットボット</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 0;
            background-color: #f5f5f5;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
        }
        .header {
            text-align: center;
            background-color: #2c3e50;
            color: white;
            padding: 20px;
            border-radius: 10px 10px 0 0;
        }
        .chat-container {
            background-color: white;
            border: 1px solid #ddd;
            border-radius: 0 0 10px 10px;
            height: 400px;
            overflow-y: auto;
            padding: 20px;
            margin-bottom: 20px;
        }
        .message {
            margin-bottom: 15px;
            padding: 10px;
            border-radius: 10px;
            max-width: 80%;
        }
        .user-message {
            background-color: #3498db;
            color: white;
            margin-left: auto;
            text-align: right;
        }
        .bot-message {
            background-color: #ecf0f1;
            color: #2c3e50;
            white-space: pre-line;
        }
        .input-container {
            display: flex;
            gap: 10px;
        }
        #userInput {
            flex: 1;
            padding: 15px;
            border: 2px solid #ddd;
            border-radius: 25px;
            font-size: 16px;
            outline: none;
        }
        #userInput:focus {
            border-color: #3498db;
        }
        #sendButton, #summaryButton {
            padding: 15px 30px;
            background-color: #3498db;
            color: white;
            border: none;
            border-radius: 25px;
            cursor: pointer;
            font-size: 16px;
            margin-left: 10px;
        }
        #sendButton:hover {
            background-color: #2980b9;
        }
        #sendButton:disabled, #summaryButton:disabled {
            background-color: #bdc3c7;
            cursor: not-allowed;
        }
        #summaryButton {
            background-color: #27ae60;
        }
        #summaryButton:hover {
            background-color: #229954;
        }
        .loading {
            color: #7f8c8d;
            font-style: italic;
        }
        .clickable-item {
            color: #3498db;
            cursor: pointer;
            text-decoration: underline;
        }
        .clickable-item:hover {
            color: #2980b9;
            font-weight: bold;
        }
        .status {
            text-align: center;
            padding: 10px;
            background-color: #ecf0f1;
            border-radius: 5px;
            margin-bottom: 10px;
        }
        .error {
            color: #e74c3c;
        }
        .success {
            color: #27ae60;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 Oracle 不具合情報チャットボット</h1>
            <p>TR品番、TR品名、車種などを入力して不具合情報を検索できます</p>
        </div>
        
        <div id="status" class="status"></div>
        
        <div class="chat-container" id="chatContainer">
            <div class="message bot-message">
                こんにちは！不具合情報チャットボットです。<br>
                TR品番、TR品名、車種名などを入力して、関連する不具合情報を検索してください。<br><br>
                例：「310D」「エンジン」「プリウス」など
            </div>
        </div>
        
        <div class="input-container">
            <input type="text" id="userInput" placeholder="TR品番、TR品名、車種などを入力してください..." onkeypress="handleKeyPress(event)">
            <button id="sendButton" onclick="sendMessage()">送信</button>
            <button id="summaryButton" onclick="sendSummary()">要約</button>
        </div>
    </div>

    <script>
        // 接続状態をチェック
        function checkConnection() {
            fetch('/status')
                .then(response => response.json())
                .then(data => {
                    const statusDiv = document.getElementById('status');
                    if (data.database_connected) {
                        statusDiv.innerHTML = '<span class="success">✅ Oracle データベースに接続済み</span>';
                    } else {
                        statusDiv.innerHTML = '<span class="error">❌ Oracle データベースに接続できません</span>';
                    }
                })
                .catch(() => {
                    const statusDiv = document.getElementById('status');
                    statusDiv.innerHTML = '<span class="error">❌ サーバーとの通信に失敗しました</span>';
                });
        }

        function addMessage(message, isUser = false) {
            const chatContainer = document.getElementById('chatContainer');
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${isUser ? 'user-message' : 'bot-message'}`;
            
            if (isUser) {
                messageDiv.textContent = message;
            } else {
                messageDiv.innerHTML = message;
            }
            
            chatContainer.appendChild(messageDiv);
            chatContainer.scrollTop = chatContainer.scrollHeight;
        }

        function addLoadingMessage() {
            const chatContainer = document.getElementById('chatContainer');
            const messageDiv = document.createElement('div');
            messageDiv.className = 'message bot-message loading';
            messageDiv.id = 'loadingMessage';
            messageDiv.textContent = '検索中...';
            chatContainer.appendChild(messageDiv);
            chatContainer.scrollTop = chatContainer.scrollHeight;
            return messageDiv;
        }

        function removeLoadingMessage() {
            const loadingMessage = document.getElementById('loadingMessage');
            if (loadingMessage) {
                loadingMessage.remove();
            }
        }

        async function sendMessage() {
            const userInput = document.getElementById('userInput');
            const sendButton = document.getElementById('sendButton');
            const message = userInput.value.trim();
            
            if (!message) return;
            
            addMessage(message, true);
            userInput.value = '';
            sendButton.disabled = true;
            
            const loadingMessage = addLoadingMessage();
            
            try {
                const response = await fetch('/chat/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ message: message })
                });
                
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                
                const data = await response.json();
                removeLoadingMessage();
                addMessage(data.response);
                
            } catch (error) {
                removeLoadingMessage();
                console.error('Error:', error);
                addMessage(`エラーが発生しました: ${error.message}\\nもう一度お試しください。`);
            } finally {
                sendButton.disabled = false;
                userInput.focus();
            }
        }

        async function sendSummary() {
            const userInput = document.getElementById('userInput');
            const summaryButton = document.getElementById('summaryButton');
            const sendButton = document.getElementById('sendButton');
            const message = userInput.value.trim();
            
            if (!message) {
                addMessage('要約するキーワードを入力してください。');
                return;
            }
            
            addMessage(`「${message}」の要約を作成`, true);
            userInput.value = '';
            summaryButton.disabled = true;
            sendButton.disabled = true;
            
            const loadingMessage = addLoadingMessage();
            
            try {
                const response = await fetch('/chat/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ 
                        message: message,
                        action: 'summary'
                    })
                });
                
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                
                const data = await response.json();
                removeLoadingMessage();
                addMessage(data.response);
                
            } catch (error) {
                removeLoadingMessage();
                console.error('Error:', error);
                addMessage(`エラーが発生しました: ${error.message}\\nもう一度お試しください。`);
            } finally {
                summaryButton.disabled = false;
                sendButton.disabled = false;
                userInput.focus();
            }
        }

        function handleKeyPress(event) {
            if (event.key === 'Enter') {
                sendMessage();
            }
        }

        // ページ読み込み時の処理
        document.addEventListener('DOMContentLoaded', function() {
            document.getElementById('userInput').focus();
            checkConnection();
        });
    </script>
</body>
</html>
'''

# Flaskアプリケーション
app = Flask(__name__)
app.secret_key = 'standalone-chatbot-secret'

# グローバル変数
oracle_db = None
session_data = {}

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/status')
def status():
    global oracle_db
    config = get_config()
    
    if config['DB_ENGINE'] == 'django.db.backends.oracle':
        if oracle_db is None:
            oracle_db = OracleConnection(config)
        
        connected = oracle_db.connect()
        return jsonify({'database_connected': connected})
    else:
        return jsonify({'database_connected': False, 'message': 'SQLite mode'})

@app.route('/chat/', methods=['POST'])
def chat():
    global oracle_db, session_data
    
    try:
        data = request.get_json()
        user_input = data.get('message', '').strip()
        action = data.get('action', 'search')
        
        if not user_input:
            return jsonify({'response': '質問を入力してください。'})
        
        config = get_config()
        
        # Oracle接続の確認
        if config['DB_ENGINE'] == 'django.db.backends.oracle':
            if oracle_db is None:
                oracle_db = OracleConnection(config)
            
            if not oracle_db.connect():
                return jsonify({'response': 'Oracle データベースに接続できません。設定を確認してください。'})
            
            # 検索実行
            keywords = user_input.split()
            results = oracle_db.search(keywords)
            
            if results:
                if action == 'summary':
                    # 要約処理
                    response_text = f"「{user_input}」に関連する不具合情報の要約:\\n\\n"
                    response_text += f"【検索結果】 {len(results)}件\\n\\n"
                    
                    # 分析
                    shashu_set = set()
                    fuguai_list = []
                    genin_list = []
                    taisaku_list = []
                    
                    for result in results:
                        if result['shashu']:
                            shashu_set.add(result['shashu'])
                        if result['fuguai_naiyou']:
                            fuguai_list.append(result['fuguai_naiyou'][:100])
                        if result['suitei_fuguai_genin']:
                            genin_list.append(result['suitei_fuguai_genin'][:100])
                        if result['taisaku_an']:
                            taisaku_list.append(result['taisaku_an'][:100])
                    
                    response_text += "【関連車種】\\n"
                    if shashu_set:
                        response_text += "、".join(sorted(shashu_set)) + "\\n\\n"
                    else:
                        response_text += "車種情報なし\\n\\n"
                    
                    response_text += "【主な不具合内容】\\n"
                    for i, fuguai in enumerate(fuguai_list[:3], 1):
                        response_text += f"{i}. {html.escape(fuguai)}...\\n"
                    
                    response_text += "\\n【主な推定原因】\\n"
                    for i, genin in enumerate(genin_list[:3], 1):
                        response_text += f"{i}. {html.escape(genin)}...\\n"
                    
                    response_text += "\\n【主な対策案】\\n"
                    for i, taisaku in enumerate(taisaku_list[:3], 1):
                        response_text += f"{i}. {html.escape(taisaku)}...\\n"
                    
                    # セッションに保存
                    session_data['summary_results'] = results
                    
                else:
                    # 通常検索
                    response_text = f"「{user_input}」に関連する情報を{len(results)}件見つけました:\\n\\n"
                    
                    for i, result in enumerate(results[:5], 1):
                        response_text += f"【{i}】\\n"
                        response_text += f"TR品番: {result['tr_hinban']}\\n"
                        response_text += f"TR品名: {result['tr_hinmei']}\\n"
                        response_text += f"車種: {result['shashu']}\\n"
                        response_text += f"不具合内容: {result['fuguai_naiyou']}\\n"
                        response_text += f"推定不具合原因: {result['suitei_fuguai_genin']}\\n"
                        response_text += f"対策案: {result['taisaku_an']}\\n"
                        response_text += "-" * 50 + "\\n"
            else:
                response_text = f"申し訳ございませんが、「{user_input}」に関連する情報が見つかりませんでした。\\n\\nTR品番、TR品名、車種名などで検索してみてください。"
        else:
            response_text = "Oracle データベースが設定されていません。.env ファイルを確認してください。"
        
        return jsonify({'response': response_text})
        
    except Exception as e:
        print(f"Error in chat: {e}")
        return jsonify({'response': f'エラーが発生しました: {str(e)}'})

def open_browser():
    """3秒後にブラウザを開く"""
    time.sleep(3)
    webbrowser.open('http://127.0.0.1:5000')

def main():
    print("Oracle 不具合情報チャットボット - スタンドアロン版")
    print("=" * 50)
    
    config = get_config()
    
    # 設定表示
    print(f"データベースエンジン: {config['DB_ENGINE']}")
    if config['DB_ENGINE'] == 'django.db.backends.oracle':
        print(f"データベースホスト: {config['DB_HOST']}")
        print(f"データベース名: {config['DB_NAME']}")
        print(f"ユーザー: {config['DB_USER']}")
    
    print("\\nサーバーを起動しています...")
    print("ブラウザで http://127.0.0.1:5000 にアクセスしてください")
    print("終了するには Ctrl+C を押してください")
    
    # ブラウザを自動で開く
    threading.Thread(target=open_browser, daemon=True).start()
    
    try:
        app.run(host='127.0.0.1', port=5000, debug=False)
    except KeyboardInterrupt:
        print("\\nアプリケーションを終了します...")

if __name__ == '__main__':
    main()