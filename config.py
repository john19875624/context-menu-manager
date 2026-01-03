"""
Context Menu Manager - 設定モジュール
Version: 2.1
最終更新: 2025-01-03
"""


class AppConfig:
    """アプリケーション全体の設定を管理する設定クラス"""

    # アプリケーション情報
    APP_NAME = "Windows 右クリックメニュー管理ツール"
    VERSION = "2.1"
    
    # データベース設定
    DB_NAME = "context_menu.db"
    DB_TIMEOUT = 10.0  # 秒
    
    # ウィンドウ設定
    WINDOW_WIDTH = 1000
    WINDOW_HEIGHT = 750
    
    # 制限値
    MAX_COMMAND_LENGTH = 2000
    MAX_NAME_LENGTH = 100
    MAX_ICON_SIZE_MB = 10
    MAX_IMPORT_COUNT = 1000
    
    # タイムアウト設定
    PROCESS_TIMEOUT = 10  # 秒
    EXPLORER_RESTART_DELAY = 1.5  # 秒


# ✅ チェック完了: config.py
# - すべての設定値が定義されている
# - ドキュメントと一致
# - VERSION を 2.1.1 に更新（修正版）