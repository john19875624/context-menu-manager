"""
Context Menu Manager - セキュリティ検証モジュール
Version: 2.1.1 (修正版)
最終更新: 2025-01-03

修正内容:
- 型ヒントを完全に追加
- エラーメッセージの一貫性を改善
"""

import re
import os
from typing import Tuple, Dict, List
from config import AppConfig
from utils import SAFE_EXECUTABLES, DANGEROUS_PATTERNS, RESERVED_NAMES, ICON_EXTENSIONS


class SecurityValidator:
    """セキュリティ検証を行うクラス"""
    
    @staticmethod
    def validate_command(command: str) -> Tuple[bool, str]:
        """
        コマンドの安全性を検証する
        
        Args:
            command: 検証するコマンド文字列
            
        Returns:
            (検証結果, メッセージ)
        """
        # 空チェック
        if not command or not command.strip():
            return False, "エラー: コマンドが空です"
        
        # 長さチェック
        if len(command) > AppConfig.MAX_COMMAND_LENGTH:
            return False, f"エラー: コマンドが長すぎます（最大{AppConfig.MAX_COMMAND_LENGTH}文字）"
        
        # NULL文字の検出
        if '\x00' in command:
            return False, "エラー: NULL文字が含まれています"
        
        # 危険なパターンマッチング
        for pattern in DANGEROUS_PATTERNS:
            if re.search(pattern, command, re.IGNORECASE):
                return False, f"エラー: 危険なコマンドパターンが検出されました"
        
        # ネットワークパスの検出
        if command.startswith('\\\\'):
            return False, "エラー: ネットワークパスは使用できません"
        
        # 実行ファイルのホワイトリストチェック
        parts = command.split()
        if parts:
            exe_name = os.path.basename(parts[0].strip('"')).lower()
            
            # ホワイトリストチェック
            if exe_name and not any(exe_name == safe for safe in SAFE_EXECUTABLES):
                # フルパスが指定されている場合は存在確認
                exe_path = parts[0].strip('"')
                if os.path.isabs(exe_path):
                    if not os.path.exists(exe_path):
                        return False, f"エラー: 指定された実行ファイルが見つかりません: {exe_path}"
                else:
                    return False, f"エラー: 実行ファイルがホワイトリストにありません: {exe_name}"
        
        return True, "OK"
    
    @staticmethod
    def validate_name(name: str) -> Tuple[bool, str]:
        """
        ショートカット名の安全性を検証する
        
        Args:
            name: 検証する名前
            
        Returns:
            (検証結果, メッセージ)
        """
        # 空文字チェック
        if not name or not name.strip():
            return False, "エラー: 名前が空です"
        
        # 長さチェック
        if len(name) > AppConfig.MAX_NAME_LENGTH:
            return False, f"エラー: 名前が長すぎます（最大{AppConfig.MAX_NAME_LENGTH}文字）"
        
        # 使用禁止文字チェック
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            if char in name:
                return False, f"エラー: 使用できない文字が含まれています: {char}"
        
        # 予約語チェック
        if name.upper() in RESERVED_NAMES:
            return False, f"エラー: 予約語は使用できません: {name}"
        
        return True, "OK"
    
    @staticmethod
    def validate_icon_path(path: str) -> Tuple[bool, str]:
        """
        アイコンファイルパスの安全性を検証する
        
        Args:
            path: 検証するファイルパス
            
        Returns:
            (検証結果, メッセージ)
        """
        # 空の場合はOK（省略可能）
        if not path:
            return True, "OK"
        
        # ネットワークパスチェック
        if path.startswith('\\\\'):
            return False, "エラー: ネットワークパスは使用できません"
        
        # ファイル存在確認
        if not os.path.exists(path):
            return False, f"エラー: ファイルが見つかりません: {path}"
        
        # 拡張子チェック
        _, ext = os.path.splitext(path)
        if ext.lower() not in ICON_EXTENSIONS:
            return False, f"エラー: サポートされていないファイル形式です: {ext}"
        
        # ファイルサイズチェック
        try:
            file_size_mb = os.path.getsize(path) / (1024 * 1024)
            if file_size_mb > AppConfig.MAX_ICON_SIZE_MB:
                return False, f"エラー: ファイルサイズが大きすぎます（最大{AppConfig.MAX_ICON_SIZE_MB}MB）"
        except OSError as e:
            return False, f"エラー: ファイルサイズの取得に失敗しました: {e}"
        
        return True, "OK"
    
    @staticmethod
    def sanitize_json_import(data: dict) -> Tuple[bool, str, dict]:
        """
        インポートJSONデータをサニタイズする
        
        Args:
            data: インポートするJSON辞書
            
        Returns:
            (成功, メッセージ, サニタイズ済みデータ)
        """
        if not isinstance(data, dict):
            return False, "エラー: 不正なJSON形式です", {}
        
        if 'shortcuts' not in data:
            return False, "エラー: 'shortcuts'キーが見つかりません", {}
        
        shortcuts = data.get('shortcuts', [])
        if not isinstance(shortcuts, list):
            return False, "エラー: 'shortcuts'はリストである必要があります", {}
        
        # 最大件数チェック
        if len(shortcuts) > AppConfig.MAX_IMPORT_COUNT:
            return False, f"エラー: インポート件数が多すぎます（最大{AppConfig.MAX_IMPORT_COUNT}件）", {}
        
        sanitized_shortcuts: List[Dict[str, str]] = []
        errors: List[str] = []
        
        for i, shortcut in enumerate(shortcuts):
            if not isinstance(shortcut, dict):
                errors.append(f"項目{i+1}: 不正な形式")
                continue
            
            # 必須フィールドチェック
            name = shortcut.get('name', '')
            command = shortcut.get('command', '')
            target_type = shortcut.get('target_type', '')
            
            # 検証
            valid_name, msg_name = SecurityValidator.validate_name(name)
            if not valid_name:
                errors.append(f"項目{i+1}: {msg_name}")
                continue
            
            valid_cmd, msg_cmd = SecurityValidator.validate_command(command)
            if not valid_cmd:
                errors.append(f"項目{i+1}: {msg_cmd}")
                continue
            
            # アイコンパス検証（オプション）
            icon_path = shortcut.get('icon_path', '')
            if icon_path:
                valid_icon, msg_icon = SecurityValidator.validate_icon_path(icon_path)
                if not valid_icon:
                    errors.append(f"項目{i+1}: {msg_icon}")
                    icon_path = ''  # エラー時は空にする
            
            sanitized_shortcuts.append({
                'name': name,
                'command': command,
                'target_type': target_type,
                'icon_path': icon_path
            })
        
        result_data = {
            'shortcuts': sanitized_shortcuts,
            'version': data.get('version', ''),
            'export_date': data.get('export_date', '')
        }
        
        if errors:
            error_msg = f"{len(sanitized_shortcuts)}件成功、{len(errors)}件エラー\n" + "\n".join(errors[:5])
            return True, error_msg, result_data
        
        return True, f"{len(sanitized_shortcuts)}件のショートカットをインポートしました", result_data


# ✅ チェック完了: core/security.py
# - 修正: 型ヒントを完全に追加 (List, Dict)
# - 修正: エラーメッセージに "エラー:" プレフィックスを統一
# - 修正: OSError の例外処理を追加
# - すべての検証メソッドが実装されている