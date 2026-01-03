"""
Context Menu Manager - システム互換性モジュールのユニットテスト
Version: 1.0.0
最終更新: 2025-01-03
"""

import sys
import os
import unittest

# パス設定
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from core.compatibility import SystemCompatibility


class TestSystemCompatibility(unittest.TestCase):
    """SystemCompatibilityクラスのテスト"""

    # ===========================
    # Windowsバージョン取得テスト
    # ===========================

    def test_get_windows_version_returns_tuple(self):
        """Windowsバージョン取得が正しい形式で返されるかのテスト"""
        major, build = SystemCompatibility.get_windows_version()

        self.assertIsInstance(major, int, "メジャーバージョンが整数ではありません")
        self.assertIsInstance(build, int, "ビルド番号が整数ではありません")

    def test_get_windows_version_valid_range(self):
        """Windowsバージョンが妥当な範囲内かのテスト"""
        major, build = SystemCompatibility.get_windows_version()

        # Windows 10以上を想定
        self.assertGreaterEqual(major, 10, "Windows 10未満はサポート外です")

        # ビルド番号が正の値
        self.assertGreater(build, 0, "ビルド番号が不正です")

    def test_windows_11_detection(self):
        """Windows 11の検出テスト"""
        major, build = SystemCompatibility.get_windows_version()

        # ビルド22000以上はWindows 11として検出されるべき
        if build >= 22000:
            self.assertEqual(major, 11, "Windows 11が正しく検出されていません")
        else:
            self.assertLess(major, 11, "Windows 10がWindows 11として誤検出されています")

    # ===========================
    # Windows 11互換性チェックテスト
    # ===========================

    def test_is_win11_compatible_returns_bool(self):
        """Windows 11互換性チェックがboolを返すかのテスト"""
        result = SystemCompatibility.is_win11_compatible()
        self.assertIsInstance(result, bool, "戻り値がboolではありません")

    def test_is_win11_compatible_consistency(self):
        """Windows 11互換性チェックの一貫性テスト"""
        major, _ = SystemCompatibility.get_windows_version()
        is_compatible = SystemCompatibility.is_win11_compatible()

        if major >= 11:
            self.assertTrue(is_compatible, "Windows 11以上なのに互換性がFalseです")
        else:
            self.assertFalse(is_compatible, "Windows 10なのに互換性がTrueです")

    # ===========================
    # レジストリパス取得テスト
    # ===========================

    def test_get_registry_base_path_all_files(self):
        """すべてのファイル用のレジストリパス取得テスト"""
        path = SystemCompatibility.get_registry_base_path('all_files')
        self.assertEqual(path, r'Software\Classes\*\shell')

    def test_get_registry_base_path_folder(self):
        """フォルダー用のレジストリパス取得テスト"""
        path = SystemCompatibility.get_registry_base_path('folder')
        self.assertEqual(path, r'Software\Classes\Directory\shell')

    def test_get_registry_base_path_background(self):
        """背景用のレジストリパス取得テスト"""
        path = SystemCompatibility.get_registry_base_path('background')
        self.assertEqual(path, r'Software\Classes\Directory\Background\shell')

    def test_get_registry_base_path_extension(self):
        """拡張子指定のレジストリパス取得テスト"""
        extensions = ['.txt', '.py', '.jpg', '.pdf']

        for ext in extensions:
            path = SystemCompatibility.get_registry_base_path(ext)
            expected_path = f'Software\\Classes\\{ext}\\shell'
            self.assertEqual(path, expected_path, f"拡張子 {ext} のパスが正しくありません")

    def test_get_registry_base_path_unknown_type(self):
        """未知のターゲットタイプのデフォルトパステスト"""
        path = SystemCompatibility.get_registry_base_path('unknown_type')
        # デフォルトは all_files と同じ
        self.assertEqual(path, r'Software\Classes\*\shell')

    # ===========================
    # レジストリ競合チェックテスト
    # ===========================

    def test_check_registry_conflict_nonexistent(self):
        """存在しないレジストリキーの競合チェックテスト"""
        exists, command = SystemCompatibility.check_registry_conflict(
            "NonexistentShortcut_XYZ123",
            "all_files"
        )

        self.assertFalse(exists, "存在しないキーが存在すると判定されました")
        self.assertIsNone(command, "存在しないキーのコマンドが返されました")

    # ===========================
    # レジストリバックアップテスト
    # ===========================

    def test_backup_registry_key_nonexistent(self):
        """存在しないレジストリキーのバックアップテスト"""
        backup = SystemCompatibility.backup_registry_key(
            r"Software\Classes\*\shell\NonexistentKey_ABC123"
        )

        self.assertIsNotNone(backup, "バックアップデータがNoneです")
        self.assertIn('path', backup, "バックアップに'path'キーがありません")
        self.assertIn('values', backup, "バックアップに'values'キーがありません")
        self.assertIn('timestamp', backup, "バックアップに'timestamp'キーがありません")

        # 存在しないキーの場合、valuesは空
        self.assertEqual(len(backup['values']), 0, "存在しないキーのvaluesが空ではありません")

    def test_backup_registry_key_structure(self):
        """レジストリバックアップの構造テスト"""
        backup = SystemCompatibility.backup_registry_key(
            r"Software\Classes\*\shell\TestKey"
        )

        # 基本構造の確認
        self.assertIsInstance(backup, dict, "バックアップが辞書ではありません")
        self.assertIsInstance(backup['values'], dict, "valuesが辞書ではありません")
        self.assertIsInstance(backup['timestamp'], str, "timestampが文字列ではありません")

        # タイムスタンプがISO形式か確認
        from datetime import datetime
        try:
            datetime.fromisoformat(backup['timestamp'])
        except ValueError:
            self.fail("タイムスタンプがISO形式ではありません")


class TestSystemCompatibilityEdgeCases(unittest.TestCase):
    """SystemCompatibilityのエッジケーステスト"""

    def test_multiple_extension_types(self):
        """複数の拡張子タイプのテスト"""
        extensions = ['.txt', '.py', '.jpg', '.png', '.pdf', '.doc', '.zip']

        for ext in extensions:
            path = SystemCompatibility.get_registry_base_path(ext)
            self.assertTrue(path.startswith('Software\\Classes\\'), f"{ext}のパスが不正です")
            self.assertIn(ext, path, f"{ext}がパスに含まれていません")

    def test_case_sensitivity_target_type(self):
        """ターゲットタイプの大文字小文字テスト"""
        # 小文字
        path_lower = SystemCompatibility.get_registry_base_path('all_files')
        # 大文字（辞書にないため、デフォルトが返される）
        path_upper = SystemCompatibility.get_registry_base_path('ALL_FILES')

        # デフォルトパスが返される
        self.assertEqual(path_upper, r'Software\Classes\*\shell')


if __name__ == '__main__':
    unittest.main()
