@echo off
chcp 65001 >nul
echo Oracle ChatBotを起動します...
wsl -e bash -c "cd '/mnt/c/Users/k_yam/Dropbox/PC/Desktop/システム関連/Study/Oracle_ChatBot' && ./start_app.sh"
pause