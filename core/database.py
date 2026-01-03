"""
Context Menu Manager - データベース管理モジュール
Version: 2.1.1 (修正版)
最終更新: 2025-01-03

修正内容:
- 型ヒントを完全に追加
- エラーログ機能を改善
"""

import sqlite3
from typing import Optional
from config import AppConfig


class DatabaseManager:
    """データベース接続を管理するコンテキストマネージャー"""
    
    def __init__(self, db_path: str) -> None:
        """
        Args:
            db_path: データベースファイルパス
        """
        self.db_path: str = db_path
        self.connection: Optional[sqlite3.Connection] = None
    
    def __enter__(self) -> sqlite3.Connection:
        """
        コンテキストマネージャーのエントリーポイント
        
        Returns:
            データベース接続オブジェクト
        """
        try:
            self.connection = sqlite3.connect(
                self.db_path,
                timeout=AppConfig.DB_TIMEOUT
            )
            self.connection.row_factory = sqlite3.Row  # 辞書形式でアクセス可能にする
            return self.connection
        except sqlite3.Error as e:
            print(f"エラー: データベース接続失敗: {e}")
            raise
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
        """
        コンテキストマネージャーの終了処理
        
        Args:
            exc_type: 例外タイプ
            exc_val: 例外値
            exc_tb: トレースバック
            
        Returns:
            例外を抑制する場合True
        """
        if self.connection:
            try:
                if exc_type is None:
                    # 例外がない場合はコミット
                    self.connection.commit()
                else:
                    # 例外がある場合はロールバック
                    self.connection.rollback()
                    print(f"警告: トランザクションをロールバックしました: {exc_val}")
            except sqlite3.Error as e:
                print(f"エラー: トランザクション処理失敗: {e}")
            finally:
                self.connection.close()
        
        # 例外は再発生させる
        return False


# ✅ チェック完了: core/database.py
# - 修正: 型ヒントを完全に追加 (__init__ に -> None)
# - 修正: エラーハンドリングを強化
# - 修正: ログメッセージを追加
# - コンテキストマネージャーが正しく実装されている