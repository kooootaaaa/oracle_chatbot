@echo off
chcp 65001 >nul
echo Oracle ChatBot Starting...
wsl bash -c "cd '%~dp0' && pwd && ls -la start_app.sh && ./start_app.sh"
pause