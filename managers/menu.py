"""
Context Menu Manager - コンテキストメニュー管理モジュール
Version: 2.1.1 (修正版)
最終更新: 2025-01-03

修正内容:
- 🔴 修正2: レジストリキーの再帰的削除機能を追加
- 型ヒントを完全に追加
"""

import winreg
import subprocess
import time
from typing import Tuple, Optional
from config import AppConfig
from core.compatibility import SystemCompatibility
from core.security import SecurityValidator


class ContextMenuManager:
    """Windowsレジストリを操作してコンテキストメニューを管理するクラス"""
    
    def __init__(self) -> None:
        """ContextMenuManagerを初期化する"""
        self.compatibility = SystemCompatibility()
        self.validator = SecurityValidator()
    
    def get_current_style(self) -> str:
        """
        現在のメニュースタイルを取得する
        
        Returns:
            "Windows 10 スタイル" または "Windows 11 スタイル"
        """
        try:
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Classes\CLSID\{86ca1aa0-34aa-4e8b-a509-50c905bae2a2}\InprocServer32"
            )
            winreg.CloseKey(key)
            return "Windows 10 スタイル"
        except FileNotFoundError:
            return "Windows 11 スタイル"
        except Exception:
            return "不明"
    
    def switch_to_win10_style(self) -> Tuple[bool, str]:
        """
        Windows 10スタイルのコンテキストメニューに切り替える
        
        Returns:
            (成功, メッセージ)
        """
        if not self.compatibility.is_win11_compatible():
            return False, "このPCはWindows 11ではありません"
        
        try:
            # レジストリキーを作成
            key = winreg.CreateKeyEx(
                winreg.HKEY_CURRENT_USER,
                r"Software\Classes\CLSID\{86ca1aa0-34aa-4e8b-a509-50c905bae2a2}\InprocServer32"
            )
            winreg.SetValueEx(key, "", 0, winreg.REG_SZ, "")
            winreg.CloseKey(key)
            
            return True, "Windows 10スタイルに変更しました。エクスプローラーを再起動してください。"
            
        except Exception as e:
            return False, f"エラー: スタイル変更失敗: {e}"
    
    def switch_to_win11_style(self) -> Tuple[bool, str]:
        """
        Windows 11スタイルのコンテキストメニューに切り替える
        
        Returns:
            (成功, メッセージ)
        """
        if not self.compatibility.is_win11_compatible():
            return False, "このPCはWindows 11ではありません"
        
        try:
            # レジストリキーを削除
            winreg.DeleteKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Classes\CLSID\{86ca1aa0-34aa-4e8b-a509-50c905bae2a2}\InprocServer32"
            )
            
            return True, "Windows 11スタイルに変更しました。エクスプローラーを再起動してください。"
            
        except FileNotFoundError:
            return True, "既にWindows 11スタイルです"
        except Exception as e:
            return False, f"エラー: スタイル変更失敗: {e}"
    
    def restart_explorer(self, timeout: Optional[int] = None) -> Tuple[bool, str]:
        """
        エクスプローラーを再起動する
        
        Args:
            timeout: タイムアウト秒数
            
        Returns:
            (成功, メッセージ)
        """
        if timeout is None:
            timeout = AppConfig.PROCESS_TIMEOUT
        
        try:
            # エクスプローラーを終了
            subprocess.run(
                ['taskkill', '/F', '/IM', 'explorer.exe'],
                timeout=timeout,
                capture_output=True
            )
            
            # 待機
            time.sleep(AppConfig.EXPLORER_RESTART_DELAY)
            
            # エクスプローラーを起動
            subprocess.Popen('explorer.exe')
            
            return True, "エクスプローラーを再起動しました"
            
        except subprocess.TimeoutExpired:
            return False, "エラー: タイムアウト - エクスプローラーの再起動に失敗しました"
        except Exception as e:
            return False, f"エラー: 再起動失敗: {e}"
    
    # 🔴 修正2: レジストリキーの再帰的削除機能を追加
    def _delete_registry_key_recursive(self, hkey, key_path: str) -> bool:
        """
        レジストリキーを再帰的に削除する（内部メソッド）
        
        Args:
            hkey: レジストリハイブ
            key_path: キーパス
            
        Returns:
            成功時True
        """
        try:
            # サブキーを列挙して削除
            key = winreg.OpenKey(hkey, key_path, 0, winreg.KEY_ALL_ACCESS)
            
            subkeys = []
            i = 0
            while True:
                try:
                    subkey = winreg.EnumKey(key, i)
                    subkeys.append(subkey)
                    i += 1
                except OSError:
                    break
            
            winreg.CloseKey(key)
            
            # 再帰的にサブキーを削除
            for subkey in subkeys:
                self._delete_registry_key_recursive(hkey, f"{key_path}\\{subkey}")
            
            # 最後にキー自体を削除
            winreg.DeleteKey(hkey, key_path)
            return True
            
        except FileNotFoundError:
            # キーが存在しない場合は成功とみなす
            return True
        except Exception as e:
            print(f"警告: レジストリキー削除エラー: {key_path} - {e}")
            return False
    
    def apply_shortcut(self, name: str, command: str, target_type: str, 
                       icon_path: str = "", db=None) -> Tuple[bool, str]:
        """
        ショートカットをシステム（レジストリ）に適用する
        
        Args:
            name: ショートカット名
            command: 実行コマンド
            target_type: ターゲットタイプ
            icon_path: アイコンパス
            db: データベースインスタンス
            
        Returns:
            (成功, メッセージ)
        """
        # セキュリティ検証
        is_valid, msg = self.validator.validate_name(name)
        if not is_valid:
            return False, f"名前検証エラー: {msg}"
        
        is_valid, msg = self.validator.validate_command(command)
        if not is_valid:
            return False, f"コマンド検証エラー: {msg}"
        
        if icon_path:
            is_valid, msg = self.validator.validate_icon_path(icon_path)
            if not is_valid:
                return False, f"アイコン検証エラー: {msg}"
        
        # 競合チェック
        exists, existing_cmd = self.compatibility.check_registry_conflict(name, target_type)
        if exists:
            return False, f"エラー: 既に同名のショートカットが存在します: {name}"
        
        try:
            # レジストリベースパス取得
            base_path = self.compatibility.get_registry_base_path(target_type)
            menu_key_path = f"{base_path}\\{name}"
            
            # バックアップ
            if db:
                backup_data = self.compatibility.backup_registry_key(menu_key_path)
                if backup_data:
                    db.save_registry_backup(name, backup_data)
            
            # メニューキー作成
            menu_key = winreg.CreateKeyEx(
                winreg.HKEY_CURRENT_USER,
                menu_key_path
            )
            
            # アイコン設定
            if icon_path:
                winreg.SetValueEx(menu_key, "Icon", 0, winreg.REG_SZ, icon_path)
            
            winreg.CloseKey(menu_key)
            
            # コマンドキー作成
            command_key_path = f"{menu_key_path}\\command"
            command_key = winreg.CreateKeyEx(
                winreg.HKEY_CURRENT_USER,
                command_key_path
            )
            
            # コマンド設定
            winreg.SetValueEx(command_key, "", 0, winreg.REG_SZ, command)
            winreg.CloseKey(command_key)
            
            return True, f"ショートカット '{name}' を適用しました"
            
        except Exception as e:
            return False, f"エラー: 適用失敗: {e}"
    
    def remove_shortcut(self, name: str, target_type: str) -> Tuple[bool, str]:
        """
        レジストリからショートカットを削除する
        
        Args:
            name: ショートカット名
            target_type: ターゲットタイプ
            
        Returns:
            (成功, メッセージ)
        """
        try:
            base_path = self.compatibility.get_registry_base_path(target_type)
            menu_key_path = f"{base_path}\\{name}"
            
            # 🔴 修正2: 再帰的削除を使用
            success = self._delete_registry_key_recursive(
                winreg.HKEY_CURRENT_USER,
                menu_key_path
            )
            
            if success:
                return True, f"ショートカット '{name}' を削除しました"
            else:
                return False, f"エラー: ショートカット '{name}' の削除に失敗しました"
            
        except FileNotFoundError:
            return False, f"エラー: ショートカット '{name}' が見つかりません"
        except Exception as e:
            return False, f"エラー: 削除失敗: {e}"


# ✅ チェック完了: managers/menu.py
# - 🔴 修正2: _delete_registry_key_recursive() メソッドを追加
# - 修正: remove_shortcut() で再帰的削除を使用
# - 修正: 型ヒントを完全に追加 (Optional[int])
# - 修正: エラーメッセージを統一
# - すべてのメソッドが実装されている