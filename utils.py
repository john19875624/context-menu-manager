"""
Context Menu Manager - ユーティリティモジュール
Version: 2.1.1 (修正版)
最終更新: 2025-01-03
"""

# ターゲットタイプの定義
TARGET_TYPES = (
    'all_files',     # すべてのファイル
    'folder',        # フォルダー
    'background',    # 背景（空白部分）
    '.txt',          # テキストファイル
    '.py',           # Pythonファイル
    '.jpg',          # JPG画像
    '.png',          # PNG画像
    '.pdf'           # PDFファイル
)

# 安全な実行ファイルのホワイトリスト
SAFE_EXECUTABLES = {
    'notepad.exe',    # メモ帳
    'code.exe',       # VS Code
    'cmd.exe',        # コマンドプロンプト
    'powershell.exe', # PowerShell
    'explorer.exe',   # エクスプローラー
    'mspaint.exe',    # ペイント
    'calc.exe',       # 電卓
    'wordpad.exe',    # ワードパッド
    'python.exe',     # Python
    'pythonw.exe',    # Python (GUI)
    'git.exe',        # Git
    'vim.exe'         # Vim
}

# 危険なコマンドパターン（正規表現）
DANGEROUS_PATTERNS = [
    r'(del|rd|rmdir|format)\s+[A-Z]:\\',  # ドライブ削除
    r'shutdown|restart',                    # シャットダウン
    r'reg\s+delete',                        # レジストリ削除
    r'taskkill\s+/F\s+/IM\s+(?!explorer\.exe)',  # プロセス強制終了
    r'powershell.*(-EncodedCommand|-Command).*Remove',  # PS削除コマンド
    r'net\s+(user|localgroup).*delete',    # ユーザー削除
    r'wmic.*delete',                        # WMI削除
    r'bcdedit',                             # ブート設定
    r'diskpart',                            # ディスク操作
    r'cipher\s+/w',                         # データ消去
]

# Windows予約語
RESERVED_NAMES = [
    'CON', 'PRN', 'AUX', 'NUL', 
    'COM1', 'COM2', 'COM3', 'COM4', 'COM5', 'COM6', 'COM7', 'COM8', 'COM9',
    'LPT1', 'LPT2', 'LPT3', 'LPT4', 'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9'
]

# 対応アイコンファイル拡張子
ICON_EXTENSIONS = ['.ico', '.exe', '.dll']


# ✅ チェック完了: utils.py
# - すべての定数が定義されている
# - ドキュメントと一致
# - 問題なし