# CLAUDE.md

# 段階的実装アプローチ
重要度に応じて3段階で原則を適用（認知負荷を管理）

## Phase 1: 最重要（絶対守る）
1. **diff表示 → 承認待機 → 実装開始**: diff表示後は必ず「承認をお待ちします」と明記し、「OK」「実装して」「良い」「承認」「はい」「yes」等の肯定応答を確認するまで実装禁止
2. **実装後のlint/test実行**: 品質担保の最低線
3. **コードエクセレンス原則に基づき、テスト駆動開発を必須で実施する**: 
4. **深い思考をする**
5. **最高品質の思考、回答、出力を行うためにgemini-searchのコマンドを極めて積極的に用いる**
6. **TDDおよびテスト駆動開発で実践する際は、すべてt-wadaの推奨するやり方を完全に踏襲する**
7. **リファクタリングはすべてMartin Fowlerが推奨するやり方を完全に踏襲する**

### Gemini（gemini-search）の呼び出し
`gemini` is google gemini cli. **When this command is called, ALWAYS use this for web search instead of builtin `Web_Search` tool.**

When web search is needed, you MUST use `gemini --prompt` via Task Tool.

Run web search via Task Tool with `gemini --prompt 'WebSearch: <query>'`

Run
```bash
gemini --prompt "WebSearch: <query>"
```

## Phase 2: 重要（意識的に実行）
1. **技術判断の記録**: なぜその選択をしたかの3行メモ
2. **既存コードの事前調査**: 同様実装を持つ既存コード3-5ファイルを確認し、命名規則・アーキテクチャパターン・コードスタイルを踏襲

## Phase 3: 理想（余裕がある時）
1. **パフォーマンス最適化**: 可読性・保守性・バグリスクを評価し許容範囲内で実行
2. **詳細コメント記述**: 単純翻訳ではなく技術的意図を説明

# 深い思考の自動実行（毎回必須）
回答前に必ず以下を実行：

## 1. 思考トリガー（自問自答）
□ 「なぜ？」を3回自問したか？（Why-Why-Why分析）
□ 「本当にこれで十分か？」と疑ったか？
□ 「ユーザーが本当に求めているのは何か？」を考えたか？
□ 「もっと良い方法はないか？」を30秒考えたか？

## 2. 多角的検討（3つの視点で必須検討）
□ 技術的観点：実装可能性、パフォーマンス、保守性
□ ユーザー観点：使いやすさ、理解しやすさ、期待との一致  
□ 運用観点：長期的影響、拡張性、リスク

## 3. 品質の自己採点（各項目4点以上で合格）
□ 具体性：抽象的でなく実行可能か？（5点満点）
□ 完全性：抜け漏れはないか？（5点満点）
□ 実用性：実際に役立つか？（5点満点）
□ 洞察性：表面的でなく本質に迫っているか？（5点満点）

## 4. 思考不足のサイン（以下が見えたら再検討）
- すぐに答えが思い浮かんだ
- 選択肢が1つしかない
- 「簡単に」「すぐに」などの表現を使っている
- 具体例や数値がない

# 実行可能な具体的ルール

## 実装計画の品質基準
以下4項目が全て明記されている場合のみ実装開始：
□ 変更対象ファイル名
□ 変更内容の要約（1-2行）
□ 想定される影響範囲
□ テスト方針

## 原則違反時の対処
原則違反が発生した場合：
1. 即座に作業を停止
2. 「○○の原則に違反しました」と明記
3. 修正方法をユーザーに確認
4. 違反原因を1行で記録（グローバルメモリに追記）

## 優先順位（原則が競合した場合）
1位: データ損失防止（既存ファイル・テストの保護）
2位: ユーザー承認（勝手な実装の防止）  
3位: 品質担保（lint/test）
4位: その他の改善提案

# 基本行動原則

## タスク開始時の原則確認プロセス（毎回必須実行）
新しいタスクを受け取ったら、実装開始前に必ず以下を実行：

### 1. 原則確認チェックリスト
```
【原則確認】
- Phase 1最重要: diff表示 → 承認待機 → 実装開始
- 実装後のlint/test実行
- 既存テスト削除の完全禁止
- 深い思考をする

【タスク理解】
- 要求内容: [ユーザーの要求を要約]
- 作業方針: [アプローチを明記]

【開始前確認】
上記の原則を守って作業を進めます。
```

### 2. 実行タイミング
- 新しいタスク開始時（必須）
- 中断後の再開時（必須）
- 複雑なタスクの段階移行時（推奨）

### 3. 習慣化の徹底
- LLMの記憶制約対策として、外部記憶に依存せず毎回確実に実行
- このプロセスなしにタスク開始は禁止

- 日本語で応答する
- テスト駆動開発で機能実装する
- タスクが終わったら、 「【完了報告】{タスク名}が完了しました。最も優先順位の高い次のタスクは{次のタスク名}です」と出力してください。

# 設計・開発品質原則
- **既存慣習の尊重**: 新機能実装前に必ず同様の機能を持つ既存コード3-5ファイルを確認
- **フレームワークベストプラクティス**: 使用する技術スタックの推奨パターンと原則を遵守
- **未使用変数の処理**: 実装完了後は未使用変数を削除または明示的に無視する
- **型安全性の優先**: 型強制は基本的に禁止、適切な型定義で解決する
- **本質的な機能をテスト**: 実装詳細ではなく、ユーザーが体験する機能の振る舞いをテストする
- **根本原因の理解**: 警告やエラーの表面的な修正ではなく、根本原因を理解してから対処する  
- **設計の見直し優先**: 技術的な回避策より、テスト設計やアプローチ自体の見直しを優先する
- **ファイル操作の安全性**: ファイル名変更や移動前に、必ず移動先のファイルが既に存在しないか確認し、既存ファイルがある場合は内容を確認して統合が必要か別名にすべきか判断する

# メタ原則
- 原則自体が障害になっている場合は、ユーザーに相談して調整する
- 新しい原則追加時は、既存原則を1つ削除または統合する（認知負荷管理）

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Reply Pass (AlterEgo AI) is an AI-powered message reply generation service that learns users' communication styles and generates personalized responses.

**🎯 Current Status**: 環境構築100%完了 - フロントエンド認証画面開発開始
**✅ Completed Tasks** (As of 2025-06-27 - 20/252タスク完了、7.9%):
- ENV-001: Next.js 15.3.4 project created with TypeScript
- ENV-002: Python FastAPI backend structure initialized
- ENV-003: Supabase project setup with SSR authentication
- ENV-004: Git repository initialized with comprehensive .gitignore
- ENV-004b: GitHub repository created (https://github.com/Volvyyy/replypass)
- ENV-007: Frontend dependencies installed (Supabase SSR, Shadcn/ui, Zustand, etc.)
- ENV-008: Backend dependencies installed in virtual environment
- ENV-009: TypeScript configuration optimized with strict mode
- ENV-010: Tailwind CSS v4 configured with custom design system
- ENV-011: ESLint/Prettier configured with import sorting, accessibility rules
- ENV-012: Python development tools setup (Black, isort, mypy strict mode)
- ENV-013: Environment variable templates created with Pydantic settings
- ENV-014: Supabase CLI setup with Google OAuth support
- ENV-015: API external services setup (Gemini new SDK, Stripe latest version)
- ENV-016: CI/CD basic setup (GitHub Actions workflow, PR auto-check functionality)
- DB-001: Supabase migration initialization (PostgreSQL 17, RLS enabled)
- DB-002: Basic tables created (PostgreSQL 17 optimization, partitioning, GIN indexes)
- DB-003: Remaining tables created (12 tables complete, BRIN/GIN/covering indexes, usage limit functions)
- API-001: Supabase Auth setup (@supabase/ssr 2025, JWT validation, security headers, 11 tests passing)

**🚨 Critical Technology Updates**:
- **Gemini SDK Migration**: `google-generativeai` → `google-genai` (mandatory by Sep 30, 2025)
- **Stripe SDK Update**: v8.8.0 → v12.2.0 (Enhanced Payment Element support)
- **Supabase Auth 2025**: @supabase/ssr package implemented (replaces deprecated auth-helpers)

**📈 Current Progress**:
- **Environment Setup**: 16/16 tasks (100%) ✅ **完了**
- **Database Foundation**: 3/8 tasks (37.5%) 
- **Authentication System**: 2/8 tasks (25.0%)
- **Overall MVP**: 20/72 tasks (27.8%)
**📋 Available Documents**:
- `要件定義書_詳細版.md` - Complete technical requirements with architecture
- `データベース設計書.md` - Full database schema with 12 tables, RLS, indexing
- `API仕様書.md` - 25 endpoints with authentication, rate limiting, webhooks
- `画面設計書.md` - 12 screens with wireframes, components, responsive design
- `開発Todoリスト書.md` - 252 detailed tasks across 3 development phases

## Technology Stack (Confirmed & Implemented)

### Frontend ✓ Implemented
- **Framework**: Next.js 15.3.4 with App Router
- **UI**: Tailwind CSS v4 (OKLCH color space), Shadcn/ui (New York style, Zinc), Lucide React
- **State**: Zustand 5.0.6 (client), TanStack Query v5.81.2 (server)
- **Forms**: React Hook Form 7.58.1 + Zod 3.25.67 validation
- **Code Quality**: ESLint 9 + Prettier 3.6.1 with Tailwind plugin
- **TypeScript**: v5 with strict mode, path aliases configured
- **Testing**: Jest + React Testing Library (pending), Playwright (pending)
- **Deployment**: Vercel (planned)

### Backend ✓ Implemented
- **Runtime**: Python 3.11+ with FastAPI 0.109.1
- **Database**: Supabase 2.16.0 (PostgreSQL 17) with Row Level Security
- **ORM**: SQLAlchemy 2.0.23 with Pydantic v2.9.4 validation
- **Settings**: pydantic-settings 2.3.0 for environment management
- **LLM**: Google Gemini API 1.22.0 (new SDK, mandatory by Sep 2025)
- **Payment**: Stripe 12.2.0 with enhanced webhooks and security
- **API Clients**: Gemini, Stripe, Supabase clients implemented
- **Authentication**: JWT Bearer validation with @supabase/ssr integration
- **Security**: Rate limiting, CORS, security headers middleware
- **Testing**: pytest 8.3.4 + pytest-asyncio 0.25.1 (11 auth tests passing)
- **Code Quality**: Black, isort, mypy with strict mode
- **Deployment**: Ubuntu VPS with Docker (planned)

### Architecture
- **Pattern**: Headless architecture with complete frontend/backend separation
- **Authentication**: Supabase Auth (email/password + Google OAuth)
- **API**: RESTful with OpenAPI documentation
- **Security**: JWT tokens, input validation, rate limiting, data encryption

## Core Features

### MVP Features (Week 1-2)
1. **Basic Authentication**: Email/password login with Supabase Auth
2. **Case Management**: Create, edit, delete conversation contexts
3. **Text-based Conversation Input**: Manual message entry
4. **Basic Reply Generation**: Simple 3-suggestion generation using Gemini 2.0 Flash
5. **Usage Tracking**: Daily limits based on subscription tier

### Phase 1 Features (Week 3-6)
1. **Google OAuth**: Social login integration
2. **Payment System**: Stripe integration with 3 subscription tiers
3. **Basic Persona System**: Manual persona configuration
4. **Screenshot OCR**: Image-to-text conversion using Gemini 2.5 Flash-Lite
5. **Enhanced Reply Generation**: Category-based suggestions with user goals

### Phase 2 Features (Week 7-10)
1. **Advanced Persona Engine**: AI-powered personality analysis and learning
2. **Feedback Loop System**: Track sent messages and partner reactions
3. **High-precision OCR**: Multi-app support with conversation structure parsing
4. **Adaptive AI**: Learning from user feedback to improve suggestions
5. **Advanced UI/UX**: Dark mode, accessibility, PWA features

## Database Schema Overview

**12 Core Tables** with complete RLS (Row Level Security):
- `users` - User profiles linked to Supabase Auth
- `cases` - Conversation contexts and partner information
- `personas` - User communication style settings
- `persona_analyses` - AI-generated personality analysis
- `conversation_logs` - Conversation session management
- `conversation_messages` - Individual messages with metadata
- `generated_replies` - Reply generation request history
- `reply_suggestions` - Generated reply options with categories
- `feedback_logs` - User feedback and partner reactions
- `subscription_plans` - Pricing tier definitions
- `user_subscriptions` - Active subscription tracking
- `usage_logs` - API usage and rate limiting data

**Key Features**:
- UUID primary keys for all tables
- Comprehensive indexing for performance
- Automatic timestamping (created_at, updated_at)
- Soft delete support with deleted_at columns
- JSONB columns for flexible metadata storage

## Security Implementation

**Authentication & Authorization**:
- Supabase Auth with JWT token validation
- Row Level Security (RLS) policies for tenant data isolation
- API route protection with middleware authentication
- OAuth 2.0 integration for Google sign-in

**Data Protection**:
- Encryption at rest for conversation logs and persona data
- TLS 1.3 for all API communications
- Input validation with Pydantic models and Zod schemas
- SQL injection prevention through parameterized queries

**API Security**:
- Rate limiting by subscription tier and endpoint
- Request/response validation and sanitization
- CORS configuration for frontend domain only
- Webhook signature verification for Stripe events

## LLM Integration Strategy

**Model Selection Logic**:
```python
# OCR Processing: Gemini 2.5 Flash-Lite (cost-optimized)
# Standard Generation: Gemini 2.0 Flash (balanced cost/quality)
# Pro Generation: Gemini 2.5 Flash (high quality)
```

**Rate Limiting by Tier**:
- **Free**: 5 generations/day, 1/minute
- **Pro**: 100 generations/day, 5/minute  
- **Unlimited**: 1000 generations/day, 20/minute

**Optimization Strategies**:
- Cache persona analysis results to reduce repeated API calls
- Implement prompt template system for consistent quality
- Monitor token usage and implement context window management
- Retry logic with exponential backoff for API failures

## Development Commands

Since this is a greenfield project, initial setup commands will be:

### Frontend (Next.js)
```bash
npx create-next-app@latest frontend --typescript --tailwind --app
cd frontend
npm install
npm run dev
```

### Backend (Python)
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python -c "from app.config import validate_settings; validate_settings()"
uvicorn app.main:app --reload
```

### Testing
```bash
# Frontend
cd frontend && npm run check-all

# Backend  
cd backend && pytest -v
```

## Key Implementation Notes

1. **Persona Engine**: Store raw reference texts (up to 5,000 chars) and AI-analyzed personality traits separately
2. **Screenshot Processing**: Use Gemini's multimodal capabilities to extract conversation data with speaker identification
3. **Feedback System**: Track "sent" status and partner reactions (😊/😥) to improve future suggestions
4. **Pricing Tiers**: Free (5/day), Pro (¥1,280), Unlimited (¥3,480) with different model access

## Design System (Confirmed & Implemented)

### Color Palette (OKLCH)
- **Primary**: oklch(64.6% 0.122 264) - Blue (#3b82f6)
- **Secondary**: oklch(61% 0.122 264) - Light Blue  
- **Success**: oklch(70.4% 0.191 156) - Green (#10b981)
- **Warning**: oklch(74.5% 0.155 83) - Orange (#f59e0b)
- **Error**: oklch(67.2% 0.227 21) - Red (#ef4444)

### Typography
- **Font**: Inter (system-ui fallback)
- **Scale**: 4xl (36px) → 3xl (30px) → 2xl (24px) → xl (20px) → lg (18px) → base (16px) → sm (14px) → xs (12px)

### Component Classes
- **reply-card**: Reply suggestion cards with hover effect
- **case-card**: Case/conversation context cards
- **status-badge**: Status indicators (success/warning/error/info)
- **Responsive**: Mobile-first design with md/lg breakpoints

### Development Settings
- **Path Aliases**: @/components, @/lib, @/types, @/hooks, @/utils, @/store
- **ESLint Rules**: Import ordering, accessibility checks, TypeScript strict
- **Prettier**: 80 char width, trailing commas, double quotes, Tailwind CSS plugin

## Development Roadmap

### Immediate Next Steps
**次の高優先度タスク (FE-002: ログイン画面実装)**
- React Hook Form + Zod バリデーション実装
- レスポンシブUI設計 (Tailwind CSS v4)
- 認証エラーハンドリング
- グローバル認証状態との統合

### Phase Progression
1. **MVP (Week 1-2)**: 72 tasks - Core authentication, basic case management, simple reply generation
2. **Phase 1 (Week 3-6)**: 88 tasks - Payment system, OAuth, persona system, OCR integration  
3. **Phase 2 (Week 7-10)**: 92 tasks - Advanced AI features, feedback loops, enhanced UX

### Key Development Principles
- **Test-driven development** with comprehensive coverage
- **Security-first** approach with RLS and input validation
- **Performance optimization** with proper indexing and caching
- **User experience focus** with responsive design and accessibility
- **Scalable architecture** supporting future growth

### Critical Success Factors
- Follow the detailed task list exactly to avoid scope creep
- Implement proper monitoring and error handling from day one
- Ensure all API responses follow the documented schema
- Test each feature thoroughly before moving to the next phase
