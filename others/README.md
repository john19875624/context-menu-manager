# Windows 右クリックメニュー管理ツール

[![Python Version](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-Windows-lightgrey.svg)](https://www.microsoft.com/windows)

Windows のエクスプローラーの右クリックメニュー（コンテキストメニュー）をGUIで簡単に管理できるツールです。

## 🌟 主な機能

- ✨ **GUIで簡単操作** - 直感的なインターフェースでメニュー項目を管理
- 🔒 **セキュリティ検証** - 危険なコマンドを自動検出して拒否
- 💾 **データベース管理** - SQLiteでショートカットを永続化
- 📊 **監査ログ** - すべての操作を記録
- 🔄 **エクスポート/インポート** - JSON形式で設定を共有
- 🎨 **Windows 11対応** - Windows 10/11スタイルの切り替え
- 🧪 **テストツール付き** - GUIテストランナーで動作確認

## 📋 必要要件

- Windows 10/11
- Python 3.7以上
- tkinter（Pythonに標準搭載）

## 🚀 インストール

### 1. リポジトリのクローン

```bash
git clone https://github.com/YOUR_USERNAME/context_menu_manager.git
cd context_menu_manager
```

### 2. 依存パッケージのインストール

標準ライブラリのみを使用しているため、追加のパッケージインストールは不要です。

## 💻 使い方

### メインアプリケーションの起動

```bash
python main.py
```

### テストランナーの起動

```bash
python test_runner.py
```

または、Windowsバッチファイルで起動:

```bash
run_tests.bat
```

## 📁 プロジェクト構造

```
context_menu_manager/
├── main.py                 # アプリケーションエントリーポイント
├── config.py              # 設定モジュール
├── utils.py               # ユーティリティ定数
│
├── core/                  # コア機能
│   ├── compatibility.py   # システム互換性
│   ├── database.py        # データベース管理
│   └── security.py        # セキュリティ検証
│
├── models/                # データモデル
│   └── database.py        # データベースモデル
│
├── managers/              # 管理クラス
│   ├── menu.py           # メニュー管理
│   └── async_task.py     # 非同期タスク
│
├── gui/                   # GUI関連
│   └── main.py           # メインGUI
│
├── tests/                 # ユニットテスト
│   ├── test_security.py
│   ├── test_database.py
│   └── test_compatibility.py
│
├── test_runner.py         # GUIテストランナー
├── run_tests.bat          # テスト起動用バッチ
├── TEST_README.md         # テストドキュメント
└── README.md              # このファイル
```

## 🎯 使用例

### ショートカットの追加

1. メインアプリケーションを起動
2. 「名前」「コマンド」「ターゲットタイプ」を入力
3. 「追加」ボタンをクリック
4. 一覧から選択して「適用」をクリック
5. エクスプローラーを再起動して反映

### コマンドの例

- メモ帳で開く: `notepad "%1"`
- VS Codeで開く: `code "%1"`
- コマンドプロンプト: `cmd /k cd /d "%V"`

## 🔒 セキュリティ機能

このツールは以下のセキュリティ検証を実行します:

- ✅ コマンドのホワイトリストチェック
- ✅ 危険なパターンの検出（削除、シャットダウン等）
- ✅ NULL文字やネットワークパスの検出
- ✅ ファイル存在確認
- ✅ 予約語チェック
- ✅ 文字数制限

## 🧪 テスト

### すべてのテストを実行

```bash
# GUIテストランナー
python test_runner.py

# コマンドライン
python -m unittest discover -s tests -p "test_*.py"
```

### 個別のテスト実行

```bash
python -m unittest tests.test_security
python -m unittest tests.test_database
python -m unittest tests.test_compatibility
```

詳細は [TEST_README.md](TEST_README.md) を参照してください。

## 📖 ドキュメント

- [API ドキュメント](docs/API.md) - 詳細なAPI仕様
- [テストガイド](TEST_README.md) - テストツールの使い方

## 🤝 貢献

プルリクエストを歓迎します！大きな変更の場合は、まずissueを開いて変更内容を議論してください。

## 📝 ライセンス

[MIT License](LICENSE)

## ⚠️ 注意事項

1. **レジストリ操作**: このツールはWindowsレジストリを変更します。使用前にバックアップを推奨します。
2. **管理者権限**: 一部の操作には管理者権限が必要な場合があります。
3. **自己責任**: このツールの使用により生じた損害について、作者は一切の責任を負いません。

## 📧 お問い合わせ

バグ報告や機能要望は [Issues](https://github.com/YOUR_USERNAME/context_menu_manager/issues) までお願いします。

## 🙏 謝辞

このプロジェクトは、Windowsのレジストリ操作とPythonのtkinterライブラリを活用して開発されました。

---

**Version**: 2.1
**最終更新**: 2025年1月
