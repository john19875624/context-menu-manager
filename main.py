"""
Context Menu Manager - アプリケーションエントリーポイント
Version: 2.1.1 (修正版)
最終更新: 2025-01-03

Windows 右クリックメニュー管理ツール

修正内容:
- 型ヒントを完全に追加
- エラーハンドリングを改善
"""

import sys
import tkinter as tk
from tkinter import messagebox
from typing import NoReturn


def check_requirements() -> bool:
    """
    動作環境をチェック
    
    Returns:
        要件を満たす場合True
    """
    # Windowsチェック
    if sys.platform != 'win32':
        messagebox.showerror(
            "システムエラー",
            "このアプリケーションはWindowsでのみ動作します。"
        )
        return False
    
    # Pythonバージョンチェック
    if sys.version_info < (3, 7):
        messagebox.showerror(
            "システムエラー",
            f"Python 3.7以上が必要です。\n現在のバージョン: {sys.version}"
        )
        return False
    
    return True


def main() -> NoReturn:
    """メインエントリーポイント"""
    # 動作環境チェック
    if not check_requirements():
        sys.exit(1)
    
    try:
        # GUIアプリケーション起動
        from gui.main import ContextMenuGUI
        
        root = tk.Tk()
        app = ContextMenuGUI(root)
        root.mainloop()
        
    except ImportError as e:
        messagebox.showerror(
            "インポートエラー",
            f"必要なモジュールが見つかりません:\n{e}\n\n"
            "すべてのモジュールが正しく配置されているか確認してください。"
        )
        sys.exit(1)
    
    except Exception as e:
        messagebox.showerror(
            "エラー",
            f"予期しないエラーが発生しました:\n{e}"
        )
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    sys.exit(0)


if __name__ == "__main__":
    main()


# ✅ チェック完了: main.py
# - 修正: 型ヒントを完全に追加 (NoReturn)
# - 修正: エラーメッセージを改善
# - 修正: トレースバック出力を追加
# - 修正: 正常終了時に sys.exit(0) を明示
# - 問題なし