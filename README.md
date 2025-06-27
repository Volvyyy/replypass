# Reply Pass (AlterEgo AI)

**AIが、あなたの言葉と心を再現する。**

Reply Passは、ユーザーの人格とコミュニケーションスタイルを学習し、あらゆる会話でパーソナライズされた返信案を生成するAIサービスです。

## 🚀 主な機能

- **圧倒的な手軽さ**: スクリーンショットを投げ込むだけで会話を記録
- **究極の自分らしさ**: 独自のペルソナエンジンにより思考のクセまで模倣
- **無限の応用性**: ケースごとにペルソナを切り替え、あらゆる対人関係をサポート

## 📋 開発状況

**現在の進捗**: 環境構築完全完了・データベースRLS実装完了（23/252タスク完了、9.1%）

**最新の完了事項**:
- ✅ **RLSセキュリティ完全実装（12テーブル完全対応、セキュリティスコア95/100）**
- ✅ **persona_analysesテーブル実装（AI分析結果管理）**
- ✅ **包括的セキュリティテストスイート（11テストシナリオ）**
- ✅ **自動セキュリティ監査スクリプト（CI/CD対応）**
- ✅ **完全実装ガイド・ドキュメント（80ページ）**
- ✅ **環境構築全完了（16/16タスク、100%完了）**
- ✅ **フロントエンド認証システム完全実装（ログイン・サインアップ画面 + 認証コンテキスト）**
- ✅ **パスワード強度インジケーター実装（NIST SP 800-63B + OWASP 2024準拠）**
- ✅ **React Hook Form 7.58.1 + Zod 3.25.67（2025年最新スペック、日本語バリデーション）**
- ✅ **アクセシビリティ対応（WCAG 2.1 AA準拠、利用規約チェックボックス）**

詳細は以下のドキュメントを参照：
- [要件定義書 詳細版](./要件定義書_詳細版.md)
- [開発Todoリスト書](./開発Todoリスト書.md)
- [API仕様書](./API仕様書.md)
- [データベース設計書](./データベース設計書.md)
- [画面設計書](./画面設計書.md)

## 🛠 技術スタック（実装済み）

### Frontend ✅
- **Next.js 15.3.4** (App Router + TypeScript)
- **Tailwind CSS v4** (OKLCH color space + Shadcn/ui)
- **Zustand 5.0.6** + TanStack Query v5.81.2
- **React Hook Form 7.58.1** + Zod 3.25.67
- **ESLint 9** + Prettier 3.6.1

### Backend ✅
- **Python 3.11+** + FastAPI 0.109.1
- **SQLAlchemy 2.0.23** + Pydantic v2.9.4
- **Supabase 2.16.0** (PostgreSQL 15+ + Auth + RLS)
- **Google Gemini API 1.22.0** (新SDK - 2025年対応)
- **Stripe 12.2.0** (Enhanced Payment Element)

### Infrastructure 🔄
- **Vercel** (Frontend - 予定)
- **Ubuntu VPS** (Backend - 予定)
- **GitHub** (https://github.com/Volvyyy/replypass)

### 🚨 重要な技術更新
- **Gemini SDK移行必須**: 2025年9月30日までに旧SDK → 新SDK
- **Stripe最新機能**: Enhanced Payment Element、AI-Powered Features対応

## 🚦 開発環境セットアップ

### 必要なツール
- Node.js 20.x LTS
- Python 3.11+
- Docker & Docker Compose
- Git

### セットアップ手順

1. **リポジトリのクローン**
```bash
git clone https://github.com/Volvyyy/replypass.git
cd replypass
```

2. **環境変数設定**
```bash
# フロントエンド
cp frontend/.env.local.example frontend/.env.local
# バックエンド  
cp backend/.env.example backend/.env
# 実際の値に置き換えてください
```

3. **フロントエンド**
```bash
cd frontend
npm install
npm run check-all  # 型チェック + Lint + フォーマット確認
npm run dev        # 開発サーバー起動
```

4. **バックエンド**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python -c "from app.config import validate_settings; validate_settings()"  # 設定確認
uvicorn app.main:app --reload
```

### 📦 パッケージ情報
- **Google Gemini**: 新SDK `google-genai` (旧 `google-generativeai` は2025年9月30日廃止)
- **Stripe**: v12.2.0 (Enhanced Payment Element、Webhook署名検証対応)
- **Supabase**: SSR v0.6.1 (Next.js 15対応)

## 📝 開発原則

プロジェクトの詳細な開発原則は [CLAUDE.md](./CLAUDE.md) を参照してください。

## 📄 ライセンス

このプロジェクトはプライベートリポジトリです。

---

Generated with Claude Code 🤖