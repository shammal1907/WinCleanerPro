@echo off
pip install -r requirements.txt
pyinstaller --onefile --windowed --uac-admin --name WinCleanerPro --collect-all customtkinter --collect-all matplotlib src\wincleaner_pro.py
echo Done! EXE in dist\WinCleanerPro.exe
pause
