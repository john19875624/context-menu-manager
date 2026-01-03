"""
Context Menu Manager - データベースモデル
Version: 2.1.1 (修正版)
最終更新: 2025-01-03

修正内容:
- 🔴 修正1: updated_at の自動更新トリガーを追加
- 🟡 修正5: JSONインポートの重複チェックを最適化
- 型ヒントを完全に追加
"""

import json
from typing import Optional, List, Dict, Tuple, Set
from datetime import datetime
from core.database import DatabaseManager
from core.security import SecurityValidator


class ContextMenuDatabase:
    """ショートカット情報をSQLiteデータベースで管理するクラス"""
    
    def __init__(self, db_path: str = "context_menu.db") -> None:
        """
        Args:
            db_path: データベースファイルパス
        """
        self.db_path: str = db_path
        self.init_database()
    
    def init_database(self) -> None:
        """データベーステーブルを初期化する"""
        with DatabaseManager(self.db_path) as conn:
            cursor = conn.cursor()
            
            # ショートカットテーブル
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS shortcuts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    command TEXT NOT NULL,
                    target_type TEXT NOT NULL,
                    icon_path TEXT DEFAULT '',
                    is_active INTEGER DEFAULT 1,
                    is_system_applied INTEGER DEFAULT 0,
                    apply_count INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 🔴 修正1: updated_at 自動更新トリガーを追加
            cursor.execute('''
                CREATE TRIGGER IF NOT EXISTS update_shortcuts_timestamp 
                AFTER UPDATE ON shortcuts
                FOR EACH ROW
                BEGIN
                    UPDATE shortcuts SET updated_at = CURRENT_TIMESTAMP
                    WHERE id = NEW.id;
                END
            ''')
            
            # 設定テーブル
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS settings (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 監査ログテーブル
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS audit_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    action TEXT NOT NULL,
                    shortcut_name TEXT,
                    details TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # レジストリバックアップテーブル
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS registry_backups (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    shortcut_name TEXT NOT NULL,
                    backup_data TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # インデックス作成
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_shortcuts_name 
                ON shortcuts(name)
            ''')
            
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_audit_timestamp 
                ON audit_log(timestamp)
            ''')
    
    def add_shortcut(self, name: str, command: str, target_type: str, 
                     icon_path: str = "") -> Optional[int]:
        """
        新しいショートカットを追加する
        
        Args:
            name: ショートカット名
            command: 実行コマンド
            target_type: ターゲットタイプ
            icon_path: アイコンパス
            
        Returns:
            追加されたショートカットのID (失敗時はNone)
        """
        try:
            with DatabaseManager(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO shortcuts (name, command, target_type, icon_path)
                    VALUES (?, ?, ?, ?)
                ''', (name, command, target_type, icon_path))
                
                shortcut_id = cursor.lastrowid
                
                # 監査ログ記録
                cursor.execute('''
                    INSERT INTO audit_log (action, shortcut_name, details)
                    VALUES (?, ?, ?)
                ''', ('ADD', name, f'Target: {target_type}'))
                
                return shortcut_id
                
        except Exception as e:
            print(f"エラー: ショートカット追加失敗: {e}")
            return None
    
    def get_all_shortcuts(self) -> List[Dict]:
        """
        すべてのショートカット情報を取得する
        
        Returns:
            ショートカット情報のリスト
        """
        try:
            with DatabaseManager(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT id, name, command, target_type, icon_path,
                           is_active, is_system_applied, apply_count, created_at
                    FROM shortcuts
                    ORDER BY created_at DESC
                ''')
                
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
                
        except Exception as e:
            print(f"エラー: ショートカット取得失敗: {e}")
            return []
    
    def update_system_applied(self, shortcut_id: int, applied: bool) -> None:
        """
        ショートカットのシステム適用状態を更新する
        
        Args:
            shortcut_id: ショートカットID
            applied: 適用状態
        """
        try:
            with DatabaseManager(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE shortcuts 
                    SET is_system_applied = ?,
                        apply_count = apply_count + ?
                    WHERE id = ?
                ''', (1 if applied else 0, 1 if applied else 0, shortcut_id))
                
        except Exception as e:
            print(f"エラー: 適用状態更新失敗: {e}")
    
    def delete_shortcut(self, shortcut_id: int) -> bool:
        """
        ショートカットを削除する
        
        Args:
            shortcut_id: 削除するショートカットID
            
        Returns:
            削除成功時True
        """
        try:
            with DatabaseManager(self.db_path) as conn:
                cursor = conn.cursor()
                
                # ショートカット名取得
                cursor.execute('SELECT name FROM shortcuts WHERE id = ?', 
                             (shortcut_id,))
                row = cursor.fetchone()
                if not row:
                    return False
                
                name = row['name']
                
                # 削除実行
                cursor.execute('DELETE FROM shortcuts WHERE id = ?', 
                             (shortcut_id,))
                
                # 監査ログ記録
                cursor.execute('''
                    INSERT INTO audit_log (action, shortcut_name)
                    VALUES (?, ?)
                ''', ('DELETE', name))
                
                return True
                
        except Exception as e:
            print(f"エラー: ショートカット削除失敗: {e}")
            return False
    
    def toggle_active(self, shortcut_id: int) -> bool:
        """
        ショートカットの有効/無効を切り替える
        
        Args:
            shortcut_id: ショートカットID
            
        Returns:
            切り替え成功時True
        """
        try:
            with DatabaseManager(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE shortcuts 
                    SET is_active = 1 - is_active
                    WHERE id = ?
                ''', (shortcut_id,))
                
                return True
                
        except Exception as e:
            print(f"エラー: 状態切り替え失敗: {e}")
            return False
    
    def save_registry_backup(self, name: str, backup_data: dict) -> None:
        """
        レジストリバックアップをデータベースに保存する
        
        Args:
            name: ショートカット名
            backup_data: バックアップデータ
        """
        try:
            with DatabaseManager(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO registry_backups (shortcut_name, backup_data)
                    VALUES (?, ?)
                ''', (name, json.dumps(backup_data, ensure_ascii=False)))
                
        except Exception as e:
            print(f"エラー: バックアップ保存失敗: {e}")
    
    def get_audit_log(self, limit: int = 100) -> List[Dict]:
        """
        監査ログを取得する
        
        Args:
            limit: 取得件数
            
        Returns:
            監査ログのリスト
        """
        try:
            with DatabaseManager(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT id, action, shortcut_name, details, timestamp
                    FROM audit_log
                    ORDER BY timestamp DESC
                    LIMIT ?
                ''', (limit,))
                
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
                
        except Exception as e:
            print(f"エラー: 監査ログ取得失敗: {e}")
            return []
    
    def export_to_json(self, filepath: str) -> None:
        """
        設定をJSONファイルにエクスポートする
        
        Args:
            filepath: エクスポート先ファイルパス
        """
        try:
            shortcuts = self.get_all_shortcuts()
            
            export_data = {
                'export_date': datetime.now().isoformat(),
                'version': '2.1',
                'app': 'Context Menu Manager',
                'shortcuts': [
                    {
                        'name': s['name'],
                        'command': s['command'],
                        'target_type': s['target_type'],
                        'icon_path': s['icon_path']
                    }
                    for s in shortcuts if s['is_active']
                ]
            }
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            raise Exception(f"エラー: エクスポート失敗: {e}")
    
    def import_from_json(self, filepath: str) -> Tuple[int, int, List[str]]:
        """
        JSONファイルから設定をインポートする
        
        Args:
            filepath: インポート元ファイルパス
            
        Returns:
            (成功件数, スキップ件数, エラーリスト)
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # セキュリティ検証
            is_valid, message, sanitized_data = SecurityValidator.sanitize_json_import(data)
            
            if not is_valid:
                return 0, 0, [message]
            
            success_count = 0
            skip_count = 0
            errors: List[str] = []
            
            # 🟡 修正5: 重複チェックを一括実行（パフォーマンス改善）
            with DatabaseManager(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT name, target_type FROM shortcuts')
                existing: Set[Tuple[str, str]] = {(row['name'], row['target_type']) 
                                                   for row in cursor.fetchall()}
            
            for shortcut in sanitized_data['shortcuts']:
                # 重複チェック
                if (shortcut['name'], shortcut['target_type']) in existing:
                    skip_count += 1
                    continue
                
                # 追加
                result = self.add_shortcut(
                    name=shortcut['name'],
                    command=shortcut['command'],
                    target_type=shortcut['target_type'],
                    icon_path=shortcut.get('icon_path', '')
                )
                
                if result:
                    success_count += 1
                    # 成功したアイテムを既存セットに追加
                    existing.add((shortcut['name'], shortcut['target_type']))
                else:
                    errors.append(f"{shortcut['name']}: 追加失敗")
            
            return success_count, skip_count, errors
            
        except Exception as e:
            return 0, 0, [f"エラー: インポート失敗: {e}"]


# ✅ チェック完了: models/database.py
# - 🔴 修正1: updated_at の自動更新トリガーを追加
# - 🟡 修正5: JSONインポートの重複チェックを一括実行に最適化
# - 修正: 型ヒントを完全に追加 (Set[Tuple[str, str]])
# - 修正: エラーメッセージを統一
# - すべてのメソッドが実装されている