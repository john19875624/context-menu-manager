"""
Context Menu Manager - テストランナー (GUI版)
Version: 1.0.0
最終更新: 2025-01-03

テスト対象を一覧表示し、選択して実行できるGUIテストツール
"""

import sys
import os
import unittest
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from typing import List, Dict, Optional
from datetime import datetime
import traceback


# テストモジュールをインポートするためのパス設定
sys.path.insert(0, os.path.dirname(__file__))


class TestCase:
    """個別のテストケース情報を保持するクラス"""

    def __init__(self, name: str, description: str, test_func, category: str):
        """
        Args:
            name: テスト名
            description: テストの説明
            test_func: テスト関数
            category: カテゴリ
        """
        self.name = name
        self.description = description
        self.test_func = test_func
        self.category = category
        self.result: Optional[str] = None
        self.error_msg: Optional[str] = None


class TestRegistry:
    """テストケースを登録・管理するクラス"""

    def __init__(self):
        self.test_cases: List[TestCase] = []
        self._register_all_tests()

    def _register_all_tests(self):
        """すべてのテストを登録する"""

        # カテゴリ: セキュリティ検証
        self.register_test(
            "セキュリティ - コマンド検証",
            "危険なコマンドパターンの検出テスト",
            self._test_security_command_validation,
            "セキュリティ"
        )

        self.register_test(
            "セキュリティ - 名前検証",
            "ショートカット名の妥当性検証テスト",
            self._test_security_name_validation,
            "セキュリティ"
        )

        self.register_test(
            "セキュリティ - アイコンパス検証",
            "アイコンファイルパスの検証テスト",
            self._test_security_icon_validation,
            "セキュリティ"
        )

        # カテゴリ: データベース
        self.register_test(
            "データベース - 初期化",
            "データベーステーブルの作成テスト",
            self._test_database_init,
            "データベース"
        )

        self.register_test(
            "データベース - ショートカット追加",
            "ショートカットの追加・取得テスト",
            self._test_database_add_shortcut,
            "データベース"
        )

        self.register_test(
            "データベース - ショートカット削除",
            "ショートカットの削除テスト",
            self._test_database_delete_shortcut,
            "データベース"
        )

        # カテゴリ: システム互換性
        self.register_test(
            "システム - Windowsバージョン取得",
            "Windowsバージョン情報の取得テスト",
            self._test_system_version,
            "システム"
        )

        self.register_test(
            "システム - レジストリパス取得",
            "ターゲットタイプに応じたレジストリパスの取得テスト",
            self._test_system_registry_path,
            "システム"
        )

        # カテゴリ: 設定
        self.register_test(
            "設定 - アプリケーション設定",
            "AppConfigの設定値テスト",
            self._test_config_values,
            "設定"
        )

        # カテゴリ: ユーティリティ
        self.register_test(
            "ユーティリティ - 定数確認",
            "ユーティリティ定数の存在確認テスト",
            self._test_utils_constants,
            "ユーティリティ"
        )

    def register_test(self, name: str, description: str, test_func, category: str):
        """テストケースを登録する"""
        self.test_cases.append(TestCase(name, description, test_func, category))

    def get_categories(self) -> List[str]:
        """カテゴリ一覧を取得する"""
        categories = list(set(tc.category for tc in self.test_cases))
        return sorted(categories)

    def get_tests_by_category(self, category: str) -> List[TestCase]:
        """特定カテゴリのテストを取得する"""
        return [tc for tc in self.test_cases if tc.category == category]

    # ===============================
    # テスト実装
    # ===============================

    def _test_security_command_validation(self) -> Dict[str, any]:
        """セキュリティ - コマンド検証テスト"""
        from core.security import SecurityValidator

        results = []

        # 安全なコマンド
        valid, msg = SecurityValidator.validate_command("notepad.exe %1")
        results.append(f"安全なコマンド: {valid} ({msg})")
        assert valid, "安全なコマンドが拒否されました"

        # 危険なコマンド (削除)
        valid, msg = SecurityValidator.validate_command("del C:\\*.*")
        results.append(f"危険なコマンド(削除): {valid} ({msg})")
        assert not valid, "危険なコマンドが許可されました"

        # 空のコマンド
        valid, msg = SecurityValidator.validate_command("")
        results.append(f"空のコマンド: {valid} ({msg})")
        assert not valid, "空のコマンドが許可されました"

        return {
            "success": True,
            "message": "\n".join(results)
        }

    def _test_security_name_validation(self) -> Dict[str, any]:
        """セキュリティ - 名前検証テスト"""
        from core.security import SecurityValidator

        results = []

        # 正しい名前
        valid, msg = SecurityValidator.validate_name("テストショートカット")
        results.append(f"正常な名前: {valid} ({msg})")
        assert valid, "正常な名前が拒否されました"

        # 禁止文字を含む名前
        valid, msg = SecurityValidator.validate_name("テスト<>名前")
        results.append(f"禁止文字を含む名前: {valid} ({msg})")
        assert not valid, "禁止文字を含む名前が許可されました"

        # 予約語
        valid, msg = SecurityValidator.validate_name("CON")
        results.append(f"予約語: {valid} ({msg})")
        assert not valid, "予約語が許可されました"

        return {
            "success": True,
            "message": "\n".join(results)
        }

    def _test_security_icon_validation(self) -> Dict[str, any]:
        """セキュリティ - アイコンパス検証テスト"""
        from core.security import SecurityValidator

        results = []

        # 空のパス（省略可能）
        valid, msg = SecurityValidator.validate_icon_path("")
        results.append(f"空のパス: {valid} ({msg})")
        assert valid, "空のパスが拒否されました"

        # 存在しないファイル
        valid, msg = SecurityValidator.validate_icon_path("C:\\nonexistent.ico")
        results.append(f"存在しないファイル: {valid} ({msg})")
        assert not valid, "存在しないファイルが許可されました"

        return {
            "success": True,
            "message": "\n".join(results)
        }

    def _test_database_init(self) -> Dict[str, any]:
        """データベース - 初期化テスト"""
        import tempfile
        from models.database import ContextMenuDatabase

        # 一時ファイルでテスト
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            tmp_path = tmp.name

        try:
            db = ContextMenuDatabase(tmp_path)

            # テーブルが作成されているか確認
            from core.database import DatabaseManager
            with DatabaseManager(tmp_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = [row[0] for row in cursor.fetchall()]

            required_tables = ['shortcuts', 'settings', 'audit_log', 'registry_backups']
            missing_tables = [t for t in required_tables if t not in tables]

            assert not missing_tables, f"必要なテーブルが作成されていません: {missing_tables}"

            return {
                "success": True,
                "message": f"データベース初期化成功\n作成されたテーブル: {', '.join(tables)}"
            }
        finally:
            # クリーンアップ
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)

    def _test_database_add_shortcut(self) -> Dict[str, any]:
        """データベース - ショートカット追加テスト"""
        import tempfile
        from models.database import ContextMenuDatabase

        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            tmp_path = tmp.name

        try:
            db = ContextMenuDatabase(tmp_path)

            # ショートカット追加
            shortcut_id = db.add_shortcut(
                name="テストショートカット",
                command="notepad.exe %1",
                target_type="all_files",
                icon_path=""
            )

            assert shortcut_id is not None, "ショートカットの追加に失敗しました"

            # 取得して確認
            shortcuts = db.get_all_shortcuts()
            assert len(shortcuts) == 1, "ショートカットが取得できません"
            assert shortcuts[0]['name'] == "テストショートカット", "ショートカット名が一致しません"

            return {
                "success": True,
                "message": f"ショートカット追加成功 (ID: {shortcut_id})\n取得されたショートカット: {shortcuts[0]['name']}"
            }
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)

    def _test_database_delete_shortcut(self) -> Dict[str, any]:
        """データベース - ショートカット削除テスト"""
        import tempfile
        from models.database import ContextMenuDatabase

        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            tmp_path = tmp.name

        try:
            db = ContextMenuDatabase(tmp_path)

            # ショートカット追加
            shortcut_id = db.add_shortcut(
                name="削除テスト",
                command="notepad.exe",
                target_type="all_files"
            )

            # 削除
            result = db.delete_shortcut(shortcut_id)
            assert result, "ショートカットの削除に失敗しました"

            # 削除確認
            shortcuts = db.get_all_shortcuts()
            assert len(shortcuts) == 0, "ショートカットが削除されていません"

            return {
                "success": True,
                "message": "ショートカット削除成功"
            }
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)

    def _test_system_version(self) -> Dict[str, any]:
        """システム - Windowsバージョン取得テスト"""
        from core.compatibility import SystemCompatibility

        major, build = SystemCompatibility.get_windows_version()

        assert isinstance(major, int), "メジャーバージョンが整数ではありません"
        assert isinstance(build, int), "ビルド番号が整数ではありません"
        assert major >= 10, "Windows 10未満はサポート外です"

        return {
            "success": True,
            "message": f"Windowsバージョン: {major} (ビルド {build})"
        }

    def _test_system_registry_path(self) -> Dict[str, any]:
        """システム - レジストリパス取得テスト"""
        from core.compatibility import SystemCompatibility

        results = []

        # 各ターゲットタイプのパスを取得
        test_types = ['all_files', 'folder', 'background', '.txt']
        for target_type in test_types:
            path = SystemCompatibility.get_registry_base_path(target_type)
            results.append(f"{target_type}: {path}")
            assert path, f"{target_type}のパスが取得できません"

        return {
            "success": True,
            "message": "\n".join(results)
        }

    def _test_config_values(self) -> Dict[str, any]:
        """設定 - アプリケーション設定テスト"""
        from config import AppConfig

        results = []

        # 設定値の確認
        assert AppConfig.APP_NAME, "APP_NAMEが設定されていません"
        results.append(f"アプリ名: {AppConfig.APP_NAME}")

        assert AppConfig.VERSION, "VERSIONが設定されていません"
        results.append(f"バージョン: {AppConfig.VERSION}")

        assert AppConfig.DB_NAME, "DB_NAMEが設定されていません"
        results.append(f"DB名: {AppConfig.DB_NAME}")

        assert AppConfig.WINDOW_WIDTH > 0, "WINDOW_WIDTHが不正です"
        results.append(f"ウィンドウ幅: {AppConfig.WINDOW_WIDTH}")

        assert AppConfig.WINDOW_HEIGHT > 0, "WINDOW_HEIGHTが不正です"
        results.append(f"ウィンドウ高さ: {AppConfig.WINDOW_HEIGHT}")

        return {
            "success": True,
            "message": "\n".join(results)
        }

    def _test_utils_constants(self) -> Dict[str, any]:
        """ユーティリティ - 定数確認テスト"""
        from utils import TARGET_TYPES, SAFE_EXECUTABLES, DANGEROUS_PATTERNS

        results = []

        # TARGET_TYPESの確認
        assert len(TARGET_TYPES) > 0, "TARGET_TYPESが空です"
        results.append(f"TARGET_TYPES数: {len(TARGET_TYPES)}")

        # SAFE_EXECUTABLESの確認
        assert len(SAFE_EXECUTABLES) > 0, "SAFE_EXECUTABLESが空です"
        results.append(f"SAFE_EXECUTABLES数: {len(SAFE_EXECUTABLES)}")

        # DANGEROUS_PATTERNSの確認
        assert len(DANGEROUS_PATTERNS) > 0, "DANGEROUS_PATTERNSが空です"
        results.append(f"DANGEROUS_PATTERNS数: {len(DANGEROUS_PATTERNS)}")

        return {
            "success": True,
            "message": "\n".join(results)
        }


class TestRunnerGUI:
    """GUIテストランナー"""

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Context Menu Manager - テストランナー")
        self.root.geometry("900x700")

        self.registry = TestRegistry()
        self.selected_tests: List[TestCase] = []

        self._create_widgets()
        self._load_test_list()

    def _create_widgets(self):
        """ウィジェットを作成する"""

        # メインフレーム
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # タイトル
        title_label = ttk.Label(
            main_frame,
            text="テストランナー",
            font=("", 16, "bold")
        )
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 10))

        # 左側: テストリスト
        list_frame = ttk.LabelFrame(main_frame, text="テスト一覧", padding="10")
        list_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 5))

        # ツリービュー
        self.tree = ttk.Treeview(
            list_frame,
            columns=("description", "status"),
            height=20
        )
        self.tree.heading("#0", text="テスト名")
        self.tree.heading("description", text="説明")
        self.tree.heading("status", text="状態")

        self.tree.column("#0", width=200)
        self.tree.column("description", width=250)
        self.tree.column("status", width=80)

        # スクロールバー
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))

        # 右側: 実行結果
        result_frame = ttk.LabelFrame(main_frame, text="実行結果", padding="10")
        result_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))

        self.result_text = scrolledtext.ScrolledText(
            result_frame,
            width=40,
            height=25,
            wrap=tk.WORD
        )
        self.result_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # ボタンフレーム
        button_frame = ttk.Frame(main_frame, padding="10")
        button_frame.grid(row=2, column=0, columnspan=2, pady=(10, 0))

        # 実行ボタン
        run_selected_btn = ttk.Button(
            button_frame,
            text="選択したテストを実行",
            command=self._run_selected_tests
        )
        run_selected_btn.grid(row=0, column=0, padx=5)

        # すべて実行ボタン
        run_all_btn = ttk.Button(
            button_frame,
            text="すべて実行",
            command=self._run_all_tests
        )
        run_all_btn.grid(row=0, column=1, padx=5)

        # クリアボタン
        clear_btn = ttk.Button(
            button_frame,
            text="結果をクリア",
            command=self._clear_results
        )
        clear_btn.grid(row=0, column=2, padx=5)

        # グリッド設定
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        result_frame.columnconfigure(0, weight=1)
        result_frame.rowconfigure(0, weight=1)

    def _load_test_list(self):
        """テストリストを読み込む"""

        # カテゴリごとにテストを追加
        for category in self.registry.get_categories():
            category_id = self.tree.insert("", tk.END, text=category, values=("", ""))

            for test_case in self.registry.get_tests_by_category(category):
                self.tree.insert(
                    category_id,
                    tk.END,
                    text=test_case.name,
                    values=(test_case.description, "未実行"),
                    tags=(test_case.name,)
                )

    def _run_selected_tests(self):
        """選択したテストを実行する"""
        selected_items = self.tree.selection()

        if not selected_items:
            messagebox.showwarning("警告", "テストを選択してください")
            return

        # 選択されたテストを取得
        tests_to_run = []
        for item in selected_items:
            item_text = self.tree.item(item, "text")
            # カテゴリではなくテストケースのみを実行
            for test_case in self.registry.test_cases:
                if test_case.name == item_text:
                    tests_to_run.append(test_case)
                    break

        if not tests_to_run:
            messagebox.showwarning("警告", "実行可能なテストが選択されていません")
            return

        self._execute_tests(tests_to_run)

    def _run_all_tests(self):
        """すべてのテストを実行する"""
        self._execute_tests(self.registry.test_cases)

    def _execute_tests(self, tests: List[TestCase]):
        """テストを実行する"""
        self._clear_results()
        self._log(f"=== テスト実行開始: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===\n")
        self._log(f"実行テスト数: {len(tests)}\n\n")

        success_count = 0
        failure_count = 0

        for test_case in tests:
            self._log(f"▶ {test_case.name}\n")
            self._log(f"  説明: {test_case.description}\n")

            try:
                # テスト実行
                result = test_case.test_func()

                if result.get("success"):
                    success_count += 1
                    test_case.result = "成功"
                    self._log(f"  ✓ 成功\n")
                    if result.get("message"):
                        self._log(f"  {result['message']}\n")

                    # ツリービューを更新
                    self._update_tree_status(test_case.name, "成功", "success")
                else:
                    failure_count += 1
                    test_case.result = "失敗"
                    self._log(f"  ✗ 失敗\n")
                    if result.get("message"):
                        self._log(f"  {result['message']}\n")

                    self._update_tree_status(test_case.name, "失敗", "failure")

            except AssertionError as e:
                failure_count += 1
                test_case.result = "失敗"
                test_case.error_msg = str(e)
                self._log(f"  ✗ アサーションエラー: {e}\n")
                self._update_tree_status(test_case.name, "失敗", "failure")

            except Exception as e:
                failure_count += 1
                test_case.result = "エラー"
                test_case.error_msg = str(e)
                self._log(f"  ✗ エラー: {e}\n")
                self._log(f"  {traceback.format_exc()}\n")
                self._update_tree_status(test_case.name, "エラー", "error")

            self._log("\n")

        # サマリー
        self._log("=" * 50 + "\n")
        self._log(f"テスト完了\n")
        self._log(f"成功: {success_count} / 失敗: {failure_count} / 合計: {len(tests)}\n")
        self._log("=" * 50 + "\n")

        # 結果メッセージ
        if failure_count == 0:
            messagebox.showinfo("完了", f"すべてのテストが成功しました！\n成功: {success_count}")
        else:
            messagebox.showwarning("完了", f"一部のテストが失敗しました。\n成功: {success_count} / 失敗: {failure_count}")

    def _update_tree_status(self, test_name: str, status: str, tag: str):
        """ツリービューのステータスを更新する"""
        for item in self.tree.get_children():
            for child in self.tree.get_children(item):
                if self.tree.item(child, "text") == test_name:
                    self.tree.item(child, values=(self.tree.item(child, "values")[0], status))

                    # 色分け
                    if tag == "success":
                        self.tree.item(child, tags=(tag,))
                        self.tree.tag_configure("success", foreground="green")
                    elif tag == "failure":
                        self.tree.item(child, tags=(tag,))
                        self.tree.tag_configure("failure", foreground="red")
                    elif tag == "error":
                        self.tree.item(child, tags=(tag,))
                        self.tree.tag_configure("error", foreground="orange")

    def _log(self, message: str):
        """結果テキストエリアにログを出力する"""
        self.result_text.insert(tk.END, message)
        self.result_text.see(tk.END)
        self.root.update()

    def _clear_results(self):
        """結果をクリアする"""
        self.result_text.delete(1.0, tk.END)

        # すべてのステータスを「未実行」に戻す
        for item in self.tree.get_children():
            for child in self.tree.get_children(item):
                values = self.tree.item(child, "values")
                self.tree.item(child, values=(values[0], "未実行"))


def main():
    """メインエントリーポイント"""

    # Windowsチェック
    if sys.platform != 'win32':
        print("エラー: このツールはWindowsでのみ動作します")
        sys.exit(1)

    root = tk.Tk()
    app = TestRunnerGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
