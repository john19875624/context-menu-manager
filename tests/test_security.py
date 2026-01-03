"""
Context Menu Manager - セキュリティモジュールのユニットテスト
Version: 1.0.0
最終更新: 2025-01-03
"""

import sys
import os
import unittest

# パス設定
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from core.security import SecurityValidator


class TestSecurityValidator(unittest.TestCase):
    """SecurityValidatorクラスのテスト"""

    def setUp(self):
        """テストのセットアップ"""
        self.validator = SecurityValidator()

    # ===========================
    # コマンド検証テスト
    # ===========================

    def test_validate_command_safe(self):
        """安全なコマンドのテスト"""
        valid, msg = self.validator.validate_command("notepad.exe %1")
        self.assertTrue(valid, f"安全なコマンドが拒否されました: {msg}")

    def test_validate_command_empty(self):
        """空のコマンドのテスト"""
        valid, msg = self.validator.validate_command("")
        self.assertFalse(valid, "空のコマンドが許可されました")
        self.assertIn("空", msg)

    def test_validate_command_whitespace_only(self):
        """空白のみのコマンドのテスト"""
        valid, msg = self.validator.validate_command("   ")
        self.assertFalse(valid, "空白のみのコマンドが許可されました")

    def test_validate_command_too_long(self):
        """長すぎるコマンドのテスト"""
        long_command = "a" * 3000
        valid, msg = self.validator.validate_command(long_command)
        self.assertFalse(valid, "長すぎるコマンドが許可されました")
        self.assertIn("長すぎます", msg)

    def test_validate_command_null_character(self):
        """NULL文字を含むコマンドのテスト"""
        valid, msg = self.validator.validate_command("cmd.exe\x00/c dir")
        self.assertFalse(valid, "NULL文字を含むコマンドが許可されました")

    def test_validate_command_dangerous_delete(self):
        """危険な削除コマンドのテスト"""
        dangerous_commands = [
            "del C:\\*.*",
            "rd C:\\Windows",
            "format C:"
        ]
        for cmd in dangerous_commands:
            valid, msg = self.validator.validate_command(cmd)
            self.assertFalse(valid, f"危険なコマンドが許可されました: {cmd}")

    def test_validate_command_dangerous_shutdown(self):
        """シャットダウンコマンドのテスト"""
        valid, msg = self.validator.validate_command("shutdown /s /t 0")
        self.assertFalse(valid, "シャットダウンコマンドが許可されました")

    def test_validate_command_dangerous_registry(self):
        """危険なレジストリ操作のテスト"""
        valid, msg = self.validator.validate_command("reg delete HKLM\\Software")
        self.assertFalse(valid, "レジストリ削除コマンドが許可されました")

    def test_validate_command_network_path(self):
        """ネットワークパスのテスト"""
        valid, msg = self.validator.validate_command("\\\\server\\share\\file.exe")
        self.assertFalse(valid, "ネットワークパスが許可されました")

    def test_validate_command_whitelist_safe_executables(self):
        """ホワイトリストの安全な実行ファイルのテスト"""
        safe_commands = [
            "notepad.exe test.txt",
            "code.exe .",
            "python.exe script.py",
            "explorer.exe C:\\"
        ]
        for cmd in safe_commands:
            valid, msg = self.validator.validate_command(cmd)
            self.assertTrue(valid, f"安全なコマンドが拒否されました: {cmd} - {msg}")

    def test_validate_command_non_whitelisted_executable(self):
        """ホワイトリストにない実行ファイルのテスト"""
        valid, msg = self.validator.validate_command("malware.exe")
        self.assertFalse(valid, "ホワイトリストにない実行ファイルが許可されました")

    # ===========================
    # 名前検証テスト
    # ===========================

    def test_validate_name_normal(self):
        """正常な名前のテスト"""
        valid, msg = self.validator.validate_name("テストショートカット")
        self.assertTrue(valid, f"正常な名前が拒否されました: {msg}")

    def test_validate_name_empty(self):
        """空の名前のテスト"""
        valid, msg = self.validator.validate_name("")
        self.assertFalse(valid, "空の名前が許可されました")

    def test_validate_name_whitespace_only(self):
        """空白のみの名前のテスト"""
        valid, msg = self.validator.validate_name("   ")
        self.assertFalse(valid, "空白のみの名前が許可されました")

    def test_validate_name_too_long(self):
        """長すぎる名前のテスト"""
        long_name = "あ" * 200
        valid, msg = self.validator.validate_name(long_name)
        self.assertFalse(valid, "長すぎる名前が許可されました")

    def test_validate_name_invalid_characters(self):
        """禁止文字を含む名前のテスト"""
        invalid_chars = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']
        for char in invalid_chars:
            name = f"テスト{char}名前"
            valid, msg = self.validator.validate_name(name)
            self.assertFalse(valid, f"禁止文字 '{char}' を含む名前が許可されました")

    def test_validate_name_reserved_words(self):
        """予約語のテスト"""
        reserved_names = ['CON', 'PRN', 'AUX', 'NUL', 'COM1', 'LPT1']
        for name in reserved_names:
            valid, msg = self.validator.validate_name(name)
            self.assertFalse(valid, f"予約語 '{name}' が許可されました")

    # ===========================
    # アイコンパス検証テスト
    # ===========================

    def test_validate_icon_path_empty(self):
        """空のアイコンパス(省略可能)のテスト"""
        valid, msg = self.validator.validate_icon_path("")
        self.assertTrue(valid, "空のアイコンパスが拒否されました")

    def test_validate_icon_path_nonexistent(self):
        """存在しないファイルのテスト"""
        valid, msg = self.validator.validate_icon_path("C:\\nonexistent\\file.ico")
        self.assertFalse(valid, "存在しないファイルが許可されました")

    def test_validate_icon_path_network(self):
        """ネットワークパスのテスト"""
        valid, msg = self.validator.validate_icon_path("\\\\server\\share\\icon.ico")
        self.assertFalse(valid, "ネットワークパスが許可されました")

    def test_validate_icon_path_invalid_extension(self):
        """サポートされていない拡張子のテスト"""
        # 一時ファイルを作成してテスト
        import tempfile
        with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as tmp:
            tmp_path = tmp.name

        try:
            valid, msg = self.validator.validate_icon_path(tmp_path)
            self.assertFalse(valid, "サポートされていない拡張子が許可されました")
        finally:
            os.unlink(tmp_path)

    # ===========================
    # JSONインポートのサニタイズテスト
    # ===========================

    def test_sanitize_json_import_valid(self):
        """正常なJSONインポートのテスト"""
        data = {
            "shortcuts": [
                {
                    "name": "テスト1",
                    "command": "notepad.exe %1",
                    "target_type": "all_files",
                    "icon_path": ""
                }
            ]
        }

        is_valid, message, sanitized = self.validator.sanitize_json_import(data)
        self.assertTrue(is_valid, f"正常なJSONが拒否されました: {message}")
        self.assertEqual(len(sanitized['shortcuts']), 1)

    def test_sanitize_json_import_invalid_format(self):
        """不正なJSON形式のテスト"""
        data = "invalid"
        is_valid, message, sanitized = self.validator.sanitize_json_import(data)
        self.assertFalse(is_valid, "不正なJSON形式が許可されました")

    def test_sanitize_json_import_missing_shortcuts_key(self):
        """shortcutsキーが存在しないテスト"""
        data = {"other": []}
        is_valid, message, sanitized = self.validator.sanitize_json_import(data)
        self.assertFalse(is_valid, "'shortcuts'キーがないJSONが許可されました")

    def test_sanitize_json_import_too_many_items(self):
        """インポート件数が多すぎるテスト"""
        data = {
            "shortcuts": [{"name": f"test{i}", "command": "notepad.exe", "target_type": "all_files"}
                         for i in range(2000)]
        }
        is_valid, message, sanitized = self.validator.sanitize_json_import(data)
        self.assertFalse(is_valid, "インポート件数が多すぎるデータが許可されました")

    def test_sanitize_json_import_invalid_items(self):
        """不正なショートカット項目を含むテスト"""
        data = {
            "shortcuts": [
                {
                    "name": "正常",
                    "command": "notepad.exe",
                    "target_type": "all_files"
                },
                {
                    "name": "",  # 不正（空の名前）
                    "command": "notepad.exe",
                    "target_type": "all_files"
                }
            ]
        }

        is_valid, message, sanitized = self.validator.sanitize_json_import(data)
        self.assertTrue(is_valid, "部分的に有効なデータが完全に拒否されました")
        self.assertEqual(len(sanitized['shortcuts']), 1, "不正な項目がフィルタリングされていません")


if __name__ == '__main__':
    unittest.main()
