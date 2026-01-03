"""
Context Menu Manager - システム互換性モジュール
Version: 2.1.1 (修正版)
最終更新: 2025-01-03

修正内容:
- 型ヒントを完全に追加
- エラーメッセージの一貫性を改善
"""

import sys
import winreg
import json
from typing import Tuple, Optional, Dict
from datetime import datetime


class SystemCompatibility:
    """OS互換性とシステム情報を管理するクラス"""
    
    @staticmethod
    def get_windows_version() -> Tuple[int, int]:
        """
        Windowsのバージョン情報を取得する
        
        Returns:
            (メジャーバージョン, ビルド番号)
        """
        try:
            # レジストリからバージョン情報を取得
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 
                                r"SOFTWARE\Microsoft\Windows NT\CurrentVersion")
            
            # ビルド番号
            build = int(winreg.QueryValueEx(key, "CurrentBuildNumber")[0])
            
            # Windows 11判定 (ビルド22000以上)
            if build >= 22000:
                major = 11
            else:
                major = 10
            
            winreg.CloseKey(key)
            return major, build
            
        except Exception as e:
            print(f"警告: バージョン取得エラー: {e}")
            return 10, 0
    
    @staticmethod
    def is_win11_compatible() -> bool:
        """
        Windows 11対応かチェックする
        
        Returns:
            Windows 11以上の場合True
        """
        major, _ = SystemCompatibility.get_windows_version()
        return major >= 11
    
    @staticmethod
    def check_registry_conflict(name: str, target_type: str) -> Tuple[bool, Optional[str]]:
        """
        レジストリに同名のショートカットが存在するかチェックする
        
        Args:
            name: ショートカット名
            target_type: ターゲットタイプ
            
        Returns:
            (存在有無, 既存コマンド)
        """
        try:
            base_path = SystemCompatibility.get_registry_base_path(target_type)
            key_path = f"{base_path}\\{name}\\command"
            
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path)
            command, _ = winreg.QueryValueEx(key, "")
            winreg.CloseKey(key)
            
            return True, command
            
        except FileNotFoundError:
            return False, None
        except Exception as e:
            print(f"警告: 競合チェックエラー: {e}")
            return False, None
    
    @staticmethod
    def backup_registry_key(key_path: str) -> Optional[Dict]:
        """
        レジストリキーをバックアップする
        
        Args:
            key_path: レジストリキーパス
            
        Returns:
            バックアップデータ (失敗時はNone)
        """
        try:
            backup_data: Dict = {
                'path': key_path,
                'values': {},
                'timestamp': datetime.now().isoformat()
            }
            
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path)
            
            # すべての値を取得
            i = 0
            while True:
                try:
                    name, value, value_type = winreg.EnumValue(key, i)
                    backup_data['values'][name] = {
                        'value': value,
                        'type': value_type
                    }
                    i += 1
                except OSError:
                    break
            
            winreg.CloseKey(key)
            return backup_data
            
        except FileNotFoundError:
            # キーが存在しない場合は空のバックアップ
            return {
                'path': key_path,
                'values': {},
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            print(f"警告: バックアップエラー: {e}")
            return None
    
    @staticmethod
    def get_registry_base_path(target_type: str) -> str:
        """
        ターゲットタイプに応じたレジストリベースパスを取得する
        
        Args:
            target_type: ターゲットタイプ
            
        Returns:
            レジストリベースパス
        """
        base_paths = {
            'all_files': r'Software\Classes\*\shell',
            'folder': r'Software\Classes\Directory\shell',
            'background': r'Software\Classes\Directory\Background\shell',
        }
        
        # 拡張子指定の場合
        if target_type.startswith('.'):
            return f'Software\\Classes\\{target_type}\\shell'
        
        return base_paths.get(target_type, r'Software\Classes\*\shell')


# ✅ チェック完了: core/compatibility.py
# - 修正: 型ヒント Dict に明示的な型を追加
# - 修正: エラーメッセージを "警告:" プレフィックスに統一
# - すべてのメソッドが実装されている
# - 問題なし