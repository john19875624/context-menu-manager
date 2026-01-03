"""
Context Menu Manager - メインGUIアプリケーション
Version: 2.1.1 (修正版)
最終更新: 2025-01-03

修正内容:
- 🔴 修正3: SecurityValidatorのインポート位置を修正
- 🟡 修正4: プログレスバーの確実な停止を実装
- 型ヒントを完全に追加
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import Optional, Any
from config import AppConfig
from models.database import ContextMenuDatabase
from managers.menu import ContextMenuManager
from managers.async_task import AsyncTaskManager
from core.compatibility import SystemCompatibility
from core.security import SecurityValidator  # 🔴 修正3: __init__でインポート
from utils import TARGET_TYPES


class ContextMenuGUI:
    """メインGUIアプリケーションクラス"""
    
    def __init__(self, root: tk.Tk) -> None:
        """
        GUIを初期化する
        
        Args:
            root: tkinter.Tk ルートウィンドウ
        """
        self.root = root
        self.root.title(f"{AppConfig.APP_NAME} v{AppConfig.VERSION}")
        self.root.geometry(f"{AppConfig.WINDOW_WIDTH}x{AppConfig.WINDOW_HEIGHT}")
        
        # データベースとマネージャー初期化
        self.db = ContextMenuDatabase(AppConfig.DB_NAME)
        self.menu_manager = ContextMenuManager()
        self.async_manager = AsyncTaskManager(self.async_callback)
        self.validator = SecurityValidator()  # 🔴 修正3: 初期化時に作成
        
        # UI変数
        self.name_var = tk.StringVar()
        self.command_var = tk.StringVar()
        self.target_var = tk.StringVar(value=TARGET_TYPES[0])
        self.icon_var = tk.StringVar()
        
        # UI作成
        self.create_menu()
        self.create_widgets()
        self.update_style_status()
        self.refresh_shortcut_list()
        
        # 定期的なキューチェック
        self.root.after(100, self.check_async_queue)
    
    def create_menu(self) -> None:
        """メニューバーを作成する"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # ファイルメニュー
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="ファイル", menu=file_menu)
        file_menu.add_command(label="設定をエクスポート", command=self.export_settings)
        file_menu.add_command(label="設定をインポート", command=self.import_settings)
        file_menu.add_separator()
        file_menu.add_command(label="終了", command=self.root.quit)
        
        # メニュースタイル
        style_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="メニュースタイル", menu=style_menu)
        style_menu.add_command(label="Windows 10スタイルに変更", command=self.switch_to_win10)
        style_menu.add_command(label="Windows 11スタイルに変更", command=self.switch_to_win11)
        style_menu.add_separator()
        style_menu.add_command(label="エクスプローラーを再起動", command=self.restart_explorer_async)
        
        # ツールメニュー
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="ツール", menu=tools_menu)
        tools_menu.add_command(label="システム情報", command=self.show_system_info)
        tools_menu.add_command(label="監査ログ", command=self.show_audit_log)
        tools_menu.add_command(label="データベース最適化", command=self.optimize_database)
        
        # ヘルプメニュー
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="ヘルプ", menu=help_menu)
        help_menu.add_command(label="使い方", command=self.show_help)
        help_menu.add_command(label="セキュリティについて", command=self.show_security_info)
        help_menu.add_separator()
        help_menu.add_command(label="バージョン情報", command=self.show_about)
    
    def create_widgets(self) -> None:
        """ウィジェット（UI部品）を作成する"""
        # ステータスフレーム
        status_frame = ttk.LabelFrame(self.root, text="ステータス", padding=10)
        status_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.status_label = ttk.Label(status_frame, text="準備完了")
        self.status_label.pack(side=tk.LEFT)
        
        self.style_label = ttk.Label(status_frame, text="")
        self.style_label.pack(side=tk.RIGHT)
        
        # 入力フレーム
        input_frame = ttk.LabelFrame(self.root, text="新しいショートカット", padding=10)
        input_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # 名前
        ttk.Label(input_frame, text="名前:").grid(row=0, column=0, sticky=tk.W, pady=2)
        ttk.Entry(input_frame, textvariable=self.name_var, width=50).grid(
            row=0, column=1, columnspan=2, sticky=tk.EW, pady=2, padx=5
        )
        
        # コマンド
        ttk.Label(input_frame, text="コマンド:").grid(row=1, column=0, sticky=tk.W, pady=2)
        ttk.Entry(input_frame, textvariable=self.command_var, width=50).grid(
            row=1, column=1, columnspan=2, sticky=tk.EW, pady=2, padx=5
        )
        
        # ターゲットタイプ
        ttk.Label(input_frame, text="対象:").grid(row=2, column=0, sticky=tk.W, pady=2)
        ttk.Combobox(input_frame, textvariable=self.target_var, 
                     values=TARGET_TYPES, state='readonly', width=20).grid(
            row=2, column=1, sticky=tk.W, pady=2, padx=5
        )
        
        # アイコン
        ttk.Label(input_frame, text="アイコン:").grid(row=3, column=0, sticky=tk.W, pady=2)
        ttk.Entry(input_frame, textvariable=self.icon_var, width=40).grid(
            row=3, column=1, sticky=tk.EW, pady=2, padx=5
        )
        ttk.Button(input_frame, text="参照...", command=self.browse_icon).grid(
            row=3, column=2, pady=2
        )
        
        # ボタン
        button_frame = ttk.Frame(input_frame)
        button_frame.grid(row=4, column=0, columnspan=3, pady=10)
        
        ttk.Button(button_frame, text="検証", command=self.validate_input).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="追加", command=self.add_shortcut).pack(side=tk.LEFT, padx=5)
        
        input_frame.columnconfigure(1, weight=1)
        
        # リストフレーム
        list_frame = ttk.LabelFrame(self.root, text="登録済みショートカット", padding=10)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Treeview
        columns = ('ID', '名前', 'コマンド', '対象', '状態', '適用済み')
        self.tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=15)
        
        # カラム設定
        self.tree.heading('ID', text='ID')
        self.tree.heading('名前', text='名前')
        self.tree.heading('コマンド', text='コマンド')
        self.tree.heading('対象', text='対象')
        self.tree.heading('状態', text='状態')
        self.tree.heading('適用済み', text='適用済み')
        
        self.tree.column('ID', width=50)
        self.tree.column('名前', width=150)
        self.tree.column('コマンド', width=300)
        self.tree.column('対象', width=100)
        self.tree.column('状態', width=80)
        self.tree.column('適用済み', width=80)
        
        # スクロールバー
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 操作ボタン
        action_frame = ttk.Frame(self.root)
        action_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(action_frame, text="適用", command=self.apply_selected).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="削除", command=self.delete_selected).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="有効/無効切替", command=self.toggle_selected).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="更新", command=self.refresh_shortcut_list).pack(side=tk.LEFT, padx=5)
        
        # プログレスバー
        self.progress = ttk.Progressbar(self.root, mode='indeterminate')
        self.progress.pack(fill=tk.X, padx=10, pady=5)
    
    def update_style_status(self) -> None:
        """メニュースタイル状態を更新する"""
        style = self.menu_manager.get_current_style()
        self.style_label.config(text=f"現在: {style}")
    
    def validate_input(self) -> None:
        """入力内容を検証してダイアログ表示する"""
        # 🔴 修正3: self.validator を使用（インポート文を削除）
        
        # 名前検証
        is_valid, msg = self.validator.validate_name(self.name_var.get())
        if not is_valid:
            messagebox.showerror("検証エラー", f"名前: {msg}")
            return
        
        # コマンド検証
        is_valid, msg = self.validator.validate_command(self.command_var.get())
        if not is_valid:
            messagebox.showerror("検証エラー", f"コマンド: {msg}")
            return
        
        # アイコン検証
        if self.icon_var.get():
            is_valid, msg = self.validator.validate_icon_path(self.icon_var.get())
            if not is_valid:
                messagebox.showerror("検証エラー", f"アイコン: {msg}")
                return
        
        messagebox.showinfo("検証結果", "すべての入力が正常です")
    
    def browse_icon(self) -> None:
        """アイコンファイル選択ダイアログを表示する"""
        filename = filedialog.askopenfilename(
            title="アイコンファイルを選択",
            filetypes=[
                ("アイコンファイル", "*.ico"),
                ("実行ファイル", "*.exe"),
                ("DLLファイル", "*.dll"),
                ("すべてのファイル", "*.*")
            ]
        )
        if filename:
            self.icon_var.set(filename)
    
    def add_shortcut(self) -> None:
        """ショートカットをデータベースに追加する"""
        name = self.name_var.get().strip()
        command = self.command_var.get().strip()
        target_type = self.target_var.get()
        icon_path = self.icon_var.get().strip()
        
        if not name or not command:
            messagebox.showwarning("入力エラー", "名前とコマンドは必須です")
            return
        
        result = self.db.add_shortcut(name, command, target_type, icon_path)
        
        if result:
            messagebox.showinfo("成功", f"ショートカット '{name}' を追加しました")
            self.name_var.set("")
            self.command_var.set("")
            self.icon_var.set("")
            self.refresh_shortcut_list()
        else:
            messagebox.showerror("エラー", "ショートカットの追加に失敗しました")
    
    def refresh_shortcut_list(self) -> None:
        """ショートカット一覧を更新する"""
        # 既存項目をクリア
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # データベースから取得
        shortcuts = self.db.get_all_shortcuts()
        
        for s in shortcuts:
            status = "有効" if s['is_active'] else "無効"
            applied = "適用済み" if s['is_system_applied'] else "未適用"
            
            self.tree.insert('', tk.END, values=(
                s['id'],
                s['name'],
                s['command'][:50] + '...' if len(s['command']) > 50 else s['command'],
                s['target_type'],
                status,
                applied
            ))
        
        self.status_label.config(text=f"ショートカット数: {len(shortcuts)}")
    
    def apply_selected(self) -> None:
        """選択されたショートカットをシステムに適用する"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("選択エラー", "ショートカットを選択してください")
            return
        
        item = self.tree.item(selection[0])
        shortcut_id = item['values'][0]
        
        # データベースから詳細取得
        shortcuts = self.db.get_all_shortcuts()
        shortcut = next((s for s in shortcuts if s['id'] == shortcut_id), None)
        
        if not shortcut:
            messagebox.showerror("エラー", "ショートカット情報が見つかりません")
            return
        
        # 適用
        success, message = self.menu_manager.apply_shortcut(
            name=shortcut['name'],
            command=shortcut['command'],
            target_type=shortcut['target_type'],
            icon_path=shortcut['icon_path'],
            db=self.db
        )
        
        if success:
            self.db.update_system_applied(shortcut_id, True)
            messagebox.showinfo("成功", message)
            self.refresh_shortcut_list()
        else:
            messagebox.showerror("エラー", message)
    
    def delete_selected(self) -> None:
        """選択されたショートカットを削除する"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("選択エラー", "ショートカットを選択してください")
            return
        
        item = self.tree.item(selection[0])
        shortcut_id = item['values'][0]
        name = item['values'][1]
        
        if not messagebox.askyesno("確認", f"ショートカット '{name}' を削除しますか?"):
            return
        
        if self.db.delete_shortcut(shortcut_id):
            messagebox.showinfo("成功", "ショートカットを削除しました")
            self.refresh_shortcut_list()
        else:
            messagebox.showerror("エラー", "削除に失敗しました")
    
    def toggle_selected(self) -> None:
        """選択されたショートカットの有効/無効を切り替える"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("選択エラー", "ショートカットを選択してください")
            return
        
        item = self.tree.item(selection[0])
        shortcut_id = item['values'][0]
        
        if self.db.toggle_active(shortcut_id):
            self.refresh_shortcut_list()
    
    def switch_to_win10(self) -> None:
        """Windows 10スタイルに切り替える"""
        success, message = self.menu_manager.switch_to_win10_style()
        
        if success:
            messagebox.showinfo("成功", message)
            self.update_style_status()
        else:
            messagebox.showerror("エラー", message)
    
    def switch_to_win11(self) -> None:
        """Windows 11スタイルに切り替える"""
        success, message = self.menu_manager.switch_to_win11_style()
        
        if success:
            messagebox.showinfo("成功", message)
            self.update_style_status()
        else:
            messagebox.showerror("エラー", message)
    
    # 🟡 修正4: プログレスバーの確実な停止を実装
    def restart_explorer_async(self) -> None:
        """エクスプローラーを非同期で再起動する"""
        if not messagebox.askyesno("確認", "エクスプローラーを再起動しますか?"):
            return
        
        try:
            self.progress.start()
            self.status_label.config(text="エクスプローラーを再起動中...")
            self.async_manager.run_async(self.menu_manager.restart_explorer)
        except Exception as e:
            # エラー時もプログレスバーを確実に停止
            self.progress.stop()
            self.status_label.config(text="準備完了")
            messagebox.showerror("エラー", f"処理開始エラー: {e}")
    
    def export_settings(self) -> None:
        """設定をJSONファイルにエクスポートする"""
        filename = filedialog.asksaveasfilename(
            title="エクスポート先を選択",
            defaultextension=".json",
            filetypes=[("JSON", "*.json"), ("すべて", "*.*")]
        )
        
        if filename:
            try:
                self.db.export_to_json(filename)
                messagebox.showinfo("成功", "設定をエクスポートしました")
            except Exception as e:
                messagebox.showerror("エラー", f"エクスポート失敗: {e}")
    
    def import_settings(self) -> None:
        """JSONファイルから設定をインポートする"""
        filename = filedialog.askopenfilename(
            title="インポートファイルを選択",
            filetypes=[("JSON", "*.json"), ("すべて", "*.*")]
        )
        
        if filename:
            success, skip, errors = self.db.import_from_json(filename)
            
            message = f"成功: {success}件\nスキップ: {skip}件"
            if errors:
                message += f"\nエラー: {len(errors)}件\n" + "\n".join(errors[:3])
            
            messagebox.showinfo("インポート結果", message)
            self.refresh_shortcut_list()
    
    def show_system_info(self) -> None:
        """システム情報ダイアログを表示する"""
        major, build = SystemCompatibility.get_windows_version()
        
        info = f"""
システム情報

Windows バージョン: {major}
ビルド番号: {build}
アプリバージョン: {AppConfig.VERSION}
データベース: {AppConfig.DB_NAME}
        """
        
        messagebox.showinfo("システム情報", info.strip())
    
    def show_audit_log(self) -> None:
        """監査ログウィンドウを表示する"""
        log_window = tk.Toplevel(self.root)
        log_window.title("監査ログ")
        log_window.geometry("800x400")
        
        # Treeview作成
        columns = ('時刻', 'アクション', 'ショートカット', '詳細')
        tree = ttk.Treeview(log_window, columns=columns, show='headings')
        
        tree.heading('時刻', text='時刻')
        tree.heading('アクション', text='アクション')
        tree.heading('ショートカット', text='ショートカット')
        tree.heading('詳細', text='詳細')
        
        tree.column('時刻', width=150)
        tree.column('アクション', width=100)
        tree.column('ショートカット', width=150)
        tree.column('詳細', width=300)
        
        # スクロールバー
        scrollbar = ttk.Scrollbar(log_window, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # ログ取得
        logs = self.db.get_audit_log()
        for log in logs:
            tree.insert('', tk.END, values=(
                log['timestamp'],
                log['action'],
                log.get('shortcut_name', ''),
                log.get('details', '')
            ))
    
    def optimize_database(self) -> None:
        """データベースを最適化する（VACUUM実行）"""
        try:
            from core.database import DatabaseManager
            with DatabaseManager(self.db.db_path) as conn:
                conn.execute('VACUUM')
            messagebox.showinfo("成功", "データベースを最適化しました")
        except Exception as e:
            messagebox.showerror("エラー", f"最適化失敗: {e}")
    
    def show_help(self) -> None:
        """使い方ヘルプダイアログを表示する"""
        help_text = """
使い方

1. 新しいショートカットを追加
   - 名前、コマンド、対象を入力
   - 「検証」で入力内容を確認
   - 「追加」でデータベースに保存

2. システムに適用
   - 一覧からショートカットを選択
   - 「適用」をクリック
   - エクスプローラーで確認

3. メニュースタイル変更
   - メニューバーから選択
   - エクスプローラー再起動が必要

4. エクスポート/インポート
   - 設定をJSON形式で保存/復元可能
        """
        
        messagebox.showinfo("使い方", help_text.strip())
    
    def show_security_info(self) -> None:
        """セキュリティ機能説明ダイアログを表示する"""
        security_text = """
セキュリティ機能

✓ コマンド検証
  - 危険なコマンドパターンを検出
  - ホワイトリストによる実行ファイルチェック

✓ 入力検証
  - 名前の文字制限と予約語チェック
  - パス検証とファイル存在確認

✓ バックアップ
  - レジストリ変更前に自動バックアップ
  - データベースに保存

✓ 監査ログ
  - すべての操作を記録
  - トレーサビリティ確保
        """
        
        messagebox.showinfo("セキュリティについて", security_text.strip())
    
    def show_about(self) -> None:
        """バージョン情報ダイアログを表示する"""
        about_text = f"""
{AppConfig.APP_NAME}

バージョン: {AppConfig.VERSION}
作成日: 2025年1月

Windowsの右クリックメニューを
安全かつ簡単に管理できるツールです。

ライセンス: MIT License
        """
        
        messagebox.showinfo("バージョン情報", about_text.strip())
    
    def async_callback(self, status: str, result: Any) -> None:
        """非同期タスクのコールバック"""
        # 🟡 修正4: プログレスバーを確実に停止
        self.progress.stop()
        
        if status == 'success':
            success, message = result
            if success:
                messagebox.showinfo("成功", message)
                self.update_style_status()
            else:
                messagebox.showerror("エラー", message)
        else:
            messagebox.showerror("エラー", f"処理エラー: {result}")
        
        self.status_label.config(text="準備完了")
    
    def check_async_queue(self) -> None:
        """非同期タスクキューを定期チェック"""
        self.async_manager.check_queue()
        self.root.after(100, self.check_async_queue)


# ✅ チェック完了: gui/main.py
# - 🔴 修正3: SecurityValidator を __init__ でインポート・初期化
# - 🟡 修正4: restart_explorer_async() でtry-except追加
# - 🟡 修正4: async_callback() でプログレスバーを確実に停止
# - 修正: 型ヒントを完全に追加 (Optional, Any)
# - すべてのGUIメソッドが実装されている