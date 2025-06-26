# Reply Pass (AlterEgo AI)

**AIが、あなたの言葉と心を再現する。**

Reply Passは、ユーザーの人格とコミュニケーションスタイルを学習し、あらゆる会話でパーソナライズされた返信案を生成するAIサービスです。

## 🚀 主な機能

- **圧倒的な手軽さ**: スクリーンショットを投げ込むだけで会話を記録
- **究極の自分らしさ**: 独自のペルソナエンジンにより思考のクセまで模倣
- **無限の応用性**: ケースごとにペルソナを切り替え、あらゆる対人関係をサポート

## 📋 開発状況

現在MVP開発中（Phase 1 of 3）

詳細は以下のドキュメントを参照：
- [要件定義書 詳細版](./要件定義書_詳細版.md)
- [開発Todoリスト書](./開発Todoリスト書.md)
- [API仕様書](./API仕様書.md)
- [データベース設計書](./データベース設計書.md)
- [画面設計書](./画面設計書.md)

## 🛠 技術スタック

### Frontend
- Next.js 14+ (App Router)
- TypeScript
- Tailwind CSS + Shadcn/ui
- Zustand + TanStack Query

### Backend
- Python 3.11+ + FastAPI
- SQLAlchemy 2.0+
- Supabase (PostgreSQL + Auth)
- Google Gemini API

### Infrastructure
- Vercel (Frontend)
- Ubuntu VPS (Backend)
- Stripe (Payment)

## 🚦 開発環境セットアップ

### 必要なツール
- Node.js 20.x LTS
- Python 3.11+
- Docker & Docker Compose
- Git

### セットアップ手順

1. **リポジトリのクローン**
```bash
git clone https://github.com/yourusername/replypass.git
cd replypass
```

2. **フロントエンド**
```bash
cd frontend
npm install
npm run dev
```

3. **バックエンド**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## 📝 開発原則

プロジェクトの詳細な開発原則は [CLAUDE.md](./CLAUDE.md) を参照してください。

## 📄 ライセンス

このプロジェクトはプライベートリポジトリです。

---

Generated with Claude Code 🤖