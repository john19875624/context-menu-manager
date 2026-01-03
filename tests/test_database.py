"""
Context Menu Manager - データベースモジュールのユニットテスト
Version: 1.0.0
最終更新: 2025-01-03
"""

import sys
import os
import unittest
import tempfile
import json

# パス設定
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from models.database import ContextMenuDatabase
from core.database import DatabaseManager


class TestContextMenuDatabase(unittest.TestCase):
    """ContextMenuDatabaseクラスのテスト"""

    def setUp(self):
        """テストのセットアップ - 一時データベースを作成"""
        self.temp_db = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
        self.temp_db_path = self.temp_db.name
        self.temp_db.close()

        self.db = ContextMenuDatabase(self.temp_db_path)

    def tearDown(self):
        """テストのクリーンアップ - 一時データベースを削除"""
        if os.path.exists(self.temp_db_path):
            os.unlink(self.temp_db_path)

    # ===========================
    # データベース初期化テスト
    # ===========================

    def test_init_database_creates_tables(self):
        """データベーステーブルの作成テスト"""
        with DatabaseManager(self.temp_db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]

        required_tables = ['shortcuts', 'settings', 'audit_log', 'registry_backups']
        for table in required_tables:
            self.assertIn(table, tables, f"テーブル '{table}' が作成されていません")

    def test_init_database_creates_indexes(self):
        """インデックスの作成テスト"""
        with DatabaseManager(self.temp_db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='index'")
            indexes = [row[0] for row in cursor.fetchall()]

        # 最低限のインデックスが存在するか確認
        self.assertTrue(len(indexes) > 0, "インデックスが作成されていません")

    # ===========================
    # ショートカット追加テスト
    # ===========================

    def test_add_shortcut_success(self):
        """ショートカット追加の成功テスト"""
        shortcut_id = self.db.add_shortcut(
            name="テストショートカット",
            command="notepad.exe %1",
            target_type="all_files",
            icon_path=""
        )

        self.assertIsNotNone(shortcut_id, "ショートカットの追加に失敗しました")
        self.assertIsInstance(shortcut_id, int, "ショートカットIDが整数ではありません")

    def test_add_shortcut_with_icon(self):
        """アイコン付きショートカット追加のテスト"""
        shortcut_id = self.db.add_shortcut(
            name="アイコン付きショートカット",
            command="code.exe %1",
            target_type="folder",
            icon_path="C:\\icon.ico"
        )

        self.assertIsNotNone(shortcut_id)

        # 取得して確認
        shortcuts = self.db.get_all_shortcuts()
        self.assertEqual(shortcuts[0]['icon_path'], "C:\\icon.ico")

    def test_add_multiple_shortcuts(self):
        """複数ショートカット追加のテスト"""
        names = ["ショートカット1", "ショートカット2", "ショートカット3"]
        ids = []

        for name in names:
            shortcut_id = self.db.add_shortcut(
                name=name,
                command="notepad.exe",
                target_type="all_files"
            )
            ids.append(shortcut_id)

        self.assertEqual(len(ids), 3, "すべてのショートカットが追加されていません")
        self.assertEqual(len(set(ids)), 3, "ショートカットIDが重複しています")

    # ===========================
    # ショートカット取得テスト
    # ===========================

    def test_get_all_shortcuts_empty(self):
        """空のデータベースからのショートカット取得テスト"""
        shortcuts = self.db.get_all_shortcuts()
        self.assertEqual(len(shortcuts), 0, "空のデータベースからデータが取得されました")

    def test_get_all_shortcuts_with_data(self):
        """データ挿入後のショートカット取得テスト"""
        self.db.add_shortcut("テスト1", "notepad.exe", "all_files")
        self.db.add_shortcut("テスト2", "code.exe", "folder")

        shortcuts = self.db.get_all_shortcuts()
        self.assertEqual(len(shortcuts), 2, "ショートカット数が一致しません")

    def test_get_all_shortcuts_order(self):
        """ショートカット取得順序のテスト（created_at DESC）"""
        self.db.add_shortcut("最初", "notepad.exe", "all_files")
        self.db.add_shortcut("2番目", "code.exe", "all_files")
        self.db.add_shortcut("最後", "explorer.exe", "all_files")

        shortcuts = self.db.get_all_shortcuts()
        # 最新のものが最初に来る
        self.assertEqual(shortcuts[0]['name'], "最後")
        self.assertEqual(shortcuts[2]['name'], "最初")

    # ===========================
    # ショートカット削除テスト
    # ===========================

    def test_delete_shortcut_success(self):
        """ショートカット削除の成功テスト"""
        shortcut_id = self.db.add_shortcut("削除テスト", "notepad.exe", "all_files")
        result = self.db.delete_shortcut(shortcut_id)

        self.assertTrue(result, "ショートカットの削除に失敗しました")

        shortcuts = self.db.get_all_shortcuts()
        self.assertEqual(len(shortcuts), 0, "ショートカットが削除されていません")

    def test_delete_nonexistent_shortcut(self):
        """存在しないショートカットの削除テスト"""
        result = self.db.delete_shortcut(99999)
        self.assertFalse(result, "存在しないショートカットの削除が成功しました")

    # ===========================
    # システム適用状態更新テスト
    # ===========================

    def test_update_system_applied(self):
        """システム適用状態の更新テスト"""
        shortcut_id = self.db.add_shortcut("適用テスト", "notepad.exe", "all_files")

        # 適用状態を更新
        self.db.update_system_applied(shortcut_id, True)

        shortcuts = self.db.get_all_shortcuts()
        self.assertEqual(shortcuts[0]['is_system_applied'], 1)
        self.assertEqual(shortcuts[0]['apply_count'], 1)

    def test_update_system_applied_multiple_times(self):
        """複数回の適用状態更新テスト"""
        shortcut_id = self.db.add_shortcut("複数適用テスト", "notepad.exe", "all_files")

        # 3回適用
        for _ in range(3):
            self.db.update_system_applied(shortcut_id, True)

        shortcuts = self.db.get_all_shortcuts()
        self.assertEqual(shortcuts[0]['apply_count'], 3, "適用回数が正しくカウントされていません")

    # ===========================
    # 有効/無効切り替えテスト
    # ===========================

    def test_toggle_active(self):
        """有効/無効切り替えテスト"""
        shortcut_id = self.db.add_shortcut("切り替えテスト", "notepad.exe", "all_files")

        # デフォルトは有効(1)
        shortcuts = self.db.get_all_shortcuts()
        self.assertEqual(shortcuts[0]['is_active'], 1)

        # 無効に切り替え
        self.db.toggle_active(shortcut_id)
        shortcuts = self.db.get_all_shortcuts()
        self.assertEqual(shortcuts[0]['is_active'], 0)

        # 再び有効に切り替え
        self.db.toggle_active(shortcut_id)
        shortcuts = self.db.get_all_shortcuts()
        self.assertEqual(shortcuts[0]['is_active'], 1)

    # ===========================
    # レジストリバックアップテスト
    # ===========================

    def test_save_registry_backup(self):
        """レジストリバックアップ保存テスト"""
        backup_data = {
            'path': r'Software\Classes\*\shell\TestShortcut',
            'values': {
                'Icon': {'value': 'C:\\icon.ico', 'type': 1}
            }
        }

        self.db.save_registry_backup("テストショートカット", backup_data)

        # バックアップが保存されたか確認
        with DatabaseManager(self.temp_db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM registry_backups WHERE shortcut_name = ?",
                         ("テストショートカット",))
            row = cursor.fetchone()

        self.assertIsNotNone(row, "バックアップが保存されていません")

    # ===========================
    # 監査ログテスト
    # ===========================

    def test_audit_log_on_add(self):
        """ショートカット追加時の監査ログテスト"""
        self.db.add_shortcut("ログテスト", "notepad.exe", "all_files")

        logs = self.db.get_audit_log()
        self.assertTrue(len(logs) > 0, "監査ログが記録されていません")
        self.assertEqual(logs[0]['action'], 'ADD')
        self.assertEqual(logs[0]['shortcut_name'], "ログテスト")

    def test_audit_log_on_delete(self):
        """ショートカット削除時の監査ログテスト"""
        shortcut_id = self.db.add_shortcut("削除ログテスト", "notepad.exe", "all_files")
        self.db.delete_shortcut(shortcut_id)

        logs = self.db.get_audit_log()
        # 最新のログが削除ログ
        self.assertEqual(logs[0]['action'], 'DELETE')

    def test_get_audit_log_limit(self):
        """監査ログ取得件数制限のテスト"""
        # 5件追加
        for i in range(5):
            self.db.add_shortcut(f"ログ{i}", "notepad.exe", "all_files")

        # 3件のみ取得
        logs = self.db.get_audit_log(limit=3)
        self.assertEqual(len(logs), 3, "取得件数制限が機能していません")

    # ===========================
    # JSONエクスポート/インポートテスト
    # ===========================

    def test_export_to_json(self):
        """JSONエクスポートのテスト"""
        self.db.add_shortcut("エクスポート1", "notepad.exe", "all_files")
        self.db.add_shortcut("エクスポート2", "code.exe", "folder")

        export_path = tempfile.NamedTemporaryFile(suffix='.json', delete=False).name

        try:
            self.db.export_to_json(export_path)

            # ファイルが作成されたか確認
            self.assertTrue(os.path.exists(export_path), "エクスポートファイルが作成されていません")

            # 内容を確認
            with open(export_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            self.assertIn('shortcuts', data)
            self.assertEqual(len(data['shortcuts']), 2)
            self.assertEqual(data['version'], '2.1')

        finally:
            if os.path.exists(export_path):
                os.unlink(export_path)

    def test_import_from_json(self):
        """JSONインポートのテスト"""
        import_data = {
            "version": "2.1",
            "shortcuts": [
                {
                    "name": "インポート1",
                    "command": "notepad.exe %1",
                    "target_type": "all_files",
                    "icon_path": ""
                },
                {
                    "name": "インポート2",
                    "command": "code.exe .",
                    "target_type": "folder",
                    "icon_path": ""
                }
            ]
        }

        import_path = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8')
        json.dump(import_data, import_path, ensure_ascii=False)
        import_path.close()

        try:
            success_count, skip_count, errors = self.db.import_from_json(import_path.name)

            self.assertEqual(success_count, 2, "インポート成功数が一致しません")
            self.assertEqual(skip_count, 0, "スキップ数が一致しません")
            self.assertEqual(len(errors), 0, "エラーが発生しました")

            # インポートされたか確認
            shortcuts = self.db.get_all_shortcuts()
            self.assertEqual(len(shortcuts), 2)

        finally:
            if os.path.exists(import_path.name):
                os.unlink(import_path.name)

    def test_import_duplicate_shortcuts(self):
        """重複ショートカットのインポートテスト"""
        # 既存のショートカットを追加
        self.db.add_shortcut("重複テスト", "notepad.exe", "all_files")

        import_data = {
            "shortcuts": [
                {
                    "name": "重複テスト",
                    "command": "notepad.exe",
                    "target_type": "all_files",
                    "icon_path": ""
                }
            ]
        }

        import_path = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8')
        json.dump(import_data, import_path, ensure_ascii=False)
        import_path.close()

        try:
            success_count, skip_count, errors = self.db.import_from_json(import_path.name)

            self.assertEqual(skip_count, 1, "重複がスキップされていません")

        finally:
            if os.path.exists(import_path.name):
                os.unlink(import_path.name)


if __name__ == '__main__':
    unittest.main()
