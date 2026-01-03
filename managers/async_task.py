"""
Context Menu Manager - 非同期タスク管理モジュール
Version: 2.1.1 (修正版)
最終更新: 2025-01-03

修正内容:
- 型ヒントを完全に追加
- エラーハンドリングを改善
"""

import threading
import queue
from typing import Callable, Any, Tuple


class AsyncTaskManager:
    """非同期タスクを管理するクラス"""
    
    def __init__(self, callback: Callable[[str, Any], None]) -> None:
        """
        Args:
            callback: タスク完了時のコールバック関数
        """
        self.callback: Callable[[str, Any], None] = callback
        self.queue: queue.Queue[Tuple[str, Any]] = queue.Queue()
        self.running: bool = True
    
    def run_async(self, func: Callable, *args: Any, **kwargs: Any) -> None:
        """
        関数を非同期で実行する
        
        Args:
            func: 実行する関数
            *args: 位置引数
            **kwargs: キーワード引数
        """
        def worker() -> None:
            try:
                result = func(*args, **kwargs)
                self.queue.put(('success', result))
            except Exception as e:
                self.queue.put(('error', str(e)))
        
        thread = threading.Thread(target=worker, daemon=True)
        thread.start()
    
    def check_queue(self) -> None:
        """キューをチェックしてコールバックを呼び出す"""
        try:
            while not self.queue.empty():
                status, result = self.queue.get_nowait()
                if self.callback:
                    self.callback(status, result)
        except queue.Empty:
            pass
        except Exception as e:
            print(f"警告: キューチェックエラー: {e}")
    
    def stop(self) -> None:
        """タスクマネージャーを停止する"""
        self.running = False


# ✅ チェック完了: managers/async_task.py
# - 修正: 型ヒントを完全に追加 (Callable, Any, Tuple)
# - 修正: エラーハンドリングを追加
# - シンプルで効果的な非同期タスク管理
# - 問題なし