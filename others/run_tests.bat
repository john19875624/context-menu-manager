@echo off
chcp 65001 > nul
echo ========================================
echo Context Menu Manager - テストランナー
echo ========================================
echo.
echo GUIテストランナーを起動します...
echo.

python test_runner.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo エラー: テストランナーの起動に失敗しました
    echo Python 3.7以上がインストールされているか確認してください
    pause
)
