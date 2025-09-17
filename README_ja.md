# AIROA メタデータ

[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![PyPI version](https://badge.fury.io/py/airoa-metadata.svg)](https://badge.fury.io/py/airoa-metadata)

> ロボットデータ収集のためのバージョン管理されたメタデータスキーマを扱うPythonライブラリ。バージョン間のシームレスな変換と堅牢な検証機能を提供します。

## 概要

AIROA メタデータは、ロボットデータ収集のための**統一されたバージョン管理可能なメタデータスキーマシステム**を提供します。研究者や開発者が異なるバージョン間でメタデータを管理し、自動変換機能により後方互換性とロボット学習パイプライン全体でのデータ一貫性を確保できます。

## 主な機能

- 🔄 **バージョン管理** - 複数のスキーマバージョン（0.0, 1.0, 1.1, 1.2, 1.3）をサポート
- 🔀 **自動変換** - 異なるメタデータバージョン間でのシームレスな変換
- ✅ **JSON スキーマ検証** - 定義されたJSONスキーマに対する堅牢な検証
- 🔒 **型安全性** - 完全な型ヒントとデータクラスベースの実装
- 🐍 **Python 3.10+ 互換** - 最新のPythonバージョンで動作
- 📦 **拡張可能なアーキテクチャ** - 新しいバージョンや機能の追加が容易

## クイックスタート

### 前提条件

- Python 3.10 以上
- pip または uv パッケージマネージャー

### インストール

#### pip を使用

```bash
pip install airoa-metadata
```

#### ソースから

```bash
# リポジトリをクローン
git clone https://github.com/airoa-org/airoa-metadata.git
cd airoa-metadata

# uv でインストール（推奨）
uv sync

# または pip でインストール
pip install -e .
```

### 基本的な使い方

```python
from airoa_metadata import MetadataV1_3, MetadataLoader

# JSONファイルからメタデータを読み込む
metadata = MetadataLoader.load_from_file("metadata.json")

# または辞書から作成
data = {
    "uuid": "123e4567-e89b-12d3-a456-426614174000",
    "version": "1.3",
    "files": [{"type": "rosbag", "name": "data.bag"}],
    "context": {"entities": [], "components": []},
    "run": {"total_time_s": 10.0, "instructions": [], "segments": []}
}
metadata = MetadataV1_3.from_dict(data)

# バージョン間の変換
from airoa_metadata.versions import MetadataV1_2
v1_2_metadata = MetadataV1_2.convert(metadata)
```

## サポートバージョン

| バージョン | 機能 | ステータス |
|----------|------|-----------|
| 0.0 | 基本的なメタデータ構造 | ✅ 安定版 |
| 1.0 | タスクテンプレートで拡張 | ✅ 安定版 |
| 1.1 | セグメントトラッキングの改善 | ✅ 安定版 |
| 1.2 | タスクテンプレートとの統一されたエンティティ構造 | ✅ 安定版 |
| 1.3 | タスクエンティティを task-record と task-template に分割 | ✅ 安定版 |

## 使用例

### 特定のバージョンを扱う

```python
# 特定のバージョンをインポート
from airoa_metadata.versions import (
    MetadataV0_0, MetadataV1_0, MetadataV1_1, 
    MetadataV1_2, MetadataV1_3
)

# 最新バージョンを使用
from airoa_metadata import MetadataLatest, Metadata

# 特定のバージョンでメタデータを作成
metadata = MetadataV1_3.from_dict(data)
```

### スキーマ検証

```python
from airoa_metadata.core import MetadataLoader

# 読み込み時の自動検証
try:
    metadata = MetadataLoader.load_from_dict(data)
    print(f"有効な {metadata.version} メタデータを読み込みました")
except Exception as e:
    print(f"検証に失敗しました: {e}")
```

### バージョン変換

```python
# 古いバージョンから新しいバージョンへの変換
old_metadata = MetadataV1_0.from_dict(old_data)
new_metadata = MetadataV1_3.convert(old_metadata)

# 新しいバージョンから古いバージョンへの変換（データ損失の可能性あり）
latest_metadata = MetadataV1_3.from_dict(latest_data)
older_metadata = MetadataV1_1.convert(latest_metadata)
```

## 開発

### 開発環境のセットアップ

```bash
# リポジトリをクローン
git clone https://github.com/airoa-org/airoa-metadata.git
cd airoa-metadata

# サブモジュールの初期化と依存関係のインストール
git submodule update --init --recursive
GIT_LFS_SKIP_SMUDGE=1 uv sync
```

### コード品質

```bash
# コードのフォーマット
make format

# リンティング（ruff + mypy）
make lint

# テストの実行
make test

# カバレッジ付きテスト
make test-coverage
```

### 利用可能な Make コマンド

- `make format` - ruff でコードをフォーマット
- `make lint` - リンティングチェック（ruff + mypy）を実行
- `make test` - 全ユニットテストを実行
- `make test-coverage` - カバレッジレポート付きでテストを実行

### テスト

```bash
# 特定のテストを実行
uv run pytest airoa_metadata/tests/test_versions.py -v

# カバレッジ付きで実行
make test-coverage
```

## ライブラリ構造

```
airoa_metadata/
├── __init__.py              # メインパッケージのエクスポート
├── core/                    # コア機能
│   ├── base.py             # MetadataBase クラス
│   └── loader.py           # MetadataLoader クラス
├── versions/               # バージョン固有の実装
│   ├── v0_0.py            # MetadataV0_0
│   ├── v1_0.py            # MetadataV1_0
│   ├── v1_1.py            # MetadataV1_1
│   ├── v1_2.py            # MetadataV1_2
│   └── v1_3.py            # MetadataV1_3
├── schemas/               # JSON スキーマファイル
└── tests/                 # テストスイート
```

## トラブルシューティング

### よくある問題

1. **インポートエラー**: `uv sync` または `pip install -e .` でパッケージが正しくインストールされているか確認
2. **検証エラー**: メタデータがバージョンの正しいスキーマに従っているか確認
3. **バージョン変換エラー**: 古いバージョンへの変換時にデータが失われる可能性があります

### ヘルプ

- 🐛 [GitHub Issues](https://github.com/airoa-org/airoa-metadata/issues) で問題を報告
- 💬 [GitHub Discussions](https://github.com/airoa-org/airoa-metadata/discussions) で議論に参加
- 📖 [Read the Docs](https://airoa-metadata.readthedocs.io/) でドキュメントを確認

## コントリビューション

コントリビューションを歓迎します！バグ修正、機能追加、ドキュメント改善など、あなたの協力に感謝します。

**クイックスタート:**

1. リポジトリをフォーク
2. 機能ブランチを作成
3. 変更を行い、テストを追加
4. 品質チェックを実行: `make format && make lint && make test`
5. プルリクエストを開く

📋 **詳細な手順、開発セットアップ、ガイドラインについては、[コントリビューションガイド](CONTRIBUTING.md)をご覧ください。**

## ライセンス

このプロジェクトは Apache License 2.0 でライセンスされています - 詳細は [LICENSE](LICENSE) ファイルをご覧ください。

---

Made with ❤️ by the [AIRoA Team](https://github.com/airoa-org)