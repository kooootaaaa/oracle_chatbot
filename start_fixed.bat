@echo off
chcp 65001 >nul
echo Oracle ChatBot Starting...
echo Current directory: %CD%
wsl bash -c "cd '/mnt/c/Users/k_yam/Dropbox/PC/Desktop/システム関連/Study/Oracle_ChatBot' && pwd && ./quick_start.sh"
pause