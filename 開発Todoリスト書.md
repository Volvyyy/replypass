# **Reply Pass 開発Todoリスト書 v1.0**

## **目次**
1. [概要](#1-概要)
2. [MVP開発タスク（週1-2）](#2-mvp開発タスク週1-2)
3. [Phase 1開発タスク（週3-6）](#3-phase-1開発タスク週3-6)
4. [Phase 2開発タスク（週7-10）](#4-phase-2開発タスク週7-10)
5. [タスク進行ガイドライン](#5-タスク進行ガイドライン)

## **1. 概要**

### 1.0. 進捗状況（2025-06-27時点）
**完了タスク数**: 26/237タスク（11.0%）
- **環境構築**: 15/16タスク完了（93.8%） ⚠️ **ENV-016（Google OAuth）未完了**
- **データベース基盤**: 4/13タスク完了（30.7%） ✅ **RLS完全実装**
- **フロントエンド**: 3/83タスク完了（3.6%） ✅ **認証システム完全実装**
- **バックエンド**: 3/57タスク完了（5.3%） ✅ **FastAPI 2025・ヘルスチェック・SQLAlchemy完了**
- **API実装**: 2/21タスク完了（9.5%） ✅ **Supabase Auth統合・ユーザー登録API完了**
- **テストシステム**: 0/27タスク完了（0%）
- **デプロイ基盤**: 0/12タスク完了（0%）
- **ドキュメント**: 0/9タスク完了（0%）
- **MVP開発**: 26/237タスク完了（11.0%）

**🚨 重要な技術更新**:
- **Gemini SDK移行**: `google-generativeai` → `google-genai` (2025年9月30日までに必須)
- **Stripe SDK更新**: v8.8.0 → v12.2.0 (Enhanced Payment Element対応)
- **RLSセキュリティ**: 12テーブル完全対応（セキュリティスコア95/100）
- **ユーザー登録API**: Pydantic V2、強力なパスワード検証、プロフィール作成完全実装

**次の高優先度タスク**（現在の基盤完成度に基づく最適順序）:
1. ✅ **BE-002: ヘルスチェックエンドポイント** （49番） - 基本API機能、サーバー稼働確認 **【完了】**
2. ✅ **BE-004: Userモデル・リポジトリ** （53番） - データアクセス層基盤（SQLAlchemy） **【完了】**
3. **BE-005: Caseモデル・リポジトリ** （54番） - ケース管理データ層
4. **API-003: ケース一覧取得API** （55番） - ユーザー登録後の基本機能  
5. **FE-004: パスワードリセット機能** （29番） - 認証システム完成

**重要**: Pydantic Settingsクラスは既に`backend/app/config.py`で完全実装済み

### 1.1. タスク表記規則
- **[ENV]**: 環境構築・設定
- **[FE]**: フロントエンド実装
- **[BE]**: バックエンド実装
- **[DB]**: データベース関連
- **[API]**: API実装
- **[TEST]**: テスト実装
- **[DEPLOY]**: デプロイ・インフラ
- **[DOC]**: ドキュメント作成

### 1.2. 優先度
- **1** : リリースブロッカー（致命的バグ・法的／セキュリティ要件）
- **2** : 極めて重要（主要ユーザーフローを阻害、他タスクをブロック）
- **3** : 非常に重要（ユーザー体験の核となる機能、期日厳守）
- **4** : 重要（ビジネス目標に直結、早期着手が望ましい）
- **5** : 中程度以上の優先度（MVP 必須だが多少順延可）
- **6** : 中程度（UX 改善・最適化、MVP 期間内に完了したい）
- **7** : 低〜中（便利機能・リファクタ・テスト拡充。後続スプリントでも可）
- **8** : 低（パフォーマンス改善・非機能強化。時間があれば実施）
- **9** : 非常に低（将来的拡張・実験的機能。バックログで管理）
- **10**: 最後に着手（Phase 1 以降に実装予定の拡張、大規模新機能）

### 1.3. 工数見積もり
- **XS**: 0.5日
- **S**: 1日
- **M**: 2-3日
- **L**: 4-5日
- **XL**: 1週間以上

### 1.4. MVP αロードマップ（更新: 2025-06-27）

以下はユーザーとの追加合意事項を反映した *最小実装スプリント*（α 版）ロードマップである。既存タスク ID を再利用しつつ、優先度を P0〜P2 ではなく 1〜10 の数値で付与した。

| 優先度 (1=最重要) | 新スプリントタスク | 既存タスク ID との対応 |
|---|---|---|
| 1 | Supabase Auth (メール+パスワード & Google OAuth) 統合 | API-001, FE-001, FE-002, FE-003 |
| 2 | Core DB & RLS 完全有効化 (users, cases, personas, messages) | DB-001〜DB-004, BE-004, BE-005, BE-015 |
| 3 | Persona ウィザード（ワンページ）詳細実装 | FE-037〜FE-040, FE-042, BE-012, BE-014, API-012 |
| 4 | 会話テキスト入力 UI + CRUD API | FE-046〜FE-048, API-014 |
| 5 | Gemini 返信生成 3 案 + 自由タグ付け | BE-020, API-018(縮), FE-055〜FE-058 |
| 6 | OCR パイプライン (PNG/JPEG, 10 枚=50MB, PC 画像対応) | FE-049, FE-050, BE-016, BE-017, API-015, API-016 |
| 7 | 全文検索 (本文 + 名前 + ケース名) 単一入力 | BE-018, API-017, FE-051 |
| 8 | 共通レイアウト / Dashboard / LP(骨格) / 状態管理 | FE-007, FE-019, FE-020, FE-012, FE-013 |
| 9 | 基本ユニットテスト + Apache デプロイ (next start リバプロ) | TEST-001, DEPLOY-001, DEPLOY-006 |
| 10 | 決済、A/B テスト、PWA 等 拡張 | Stripe 系, AB-test 系, PWA 系 |

> ⚠️ **注意:** これらの優先度は既存 *P0/P1/P2* ラベルに代えて **1〜10** を採用している。ブロッカーは **優先度 1** で管理する。

#### 合意済み仕様ハイライト
1. ペルソナ設定はワンページ式 UI。
2. スクリーンショット解析は PNG/JPEG (スマホ & PC) に対応し、1 回最大 10 枚 / 合計 50 MB。
3. 返信案 3 件 + LLM 自由生成タグ。
4. フィードバック (😊/😥) は MVP で誤タップ取り消し機能を実装。
5. データ暗号化は Supabase 透過暗号化のみ使用。
6. Apache リバースプロキシ + `next start` 構成でホスティング。

これに伴い、**Phase1/Phase2 の Stripe・A/B テスト等は優先度 10 とし、α 版完了後のスプリントで着手する。**

---

## **2. MVP開発タスク（週1-2）**

### **2.1. 環境構築・初期設定（16タスク）**

#### **プロジェクト初期化**
1. **[ENV-001]** Next.js 14プロジェクト作成 `1` `XS` ✅ **完了**
   - `npx create-next-app@latest frontend --typescript --tailwind --app`
   - ESLint、Prettier設定
   - **完了条件**: `npm run dev`で起動確認

2. **[ENV-002]** Python FastAPIプロジェクト作成 `1` `S` ✅ **完了**
   - ディレクトリ構造作成: `backend/app/`
   - `pyproject.toml`、`requirements.txt`作成
   - **ファイル**: `backend/app/main.py`、`backend/app/__init__.py`
   - **完了条件**: `uvicorn app.main:app --reload`で起動確認

3. **[ENV-003]** Supabaseプロジェクト作成・設定 `1` `S` ✅ **完了**
   - Supabaseダッシュボードでプロジェクト作成
   - 環境変数設定（URL、API Key）
   - **ファイル**: `frontend/.env.local`、`backend/.env`
   - **完了条件**: 管理画面へのアクセス確認

4. **[ENV-004]** Git/GitHub設定 `1` `XS` ✅ **完了** 
   - リポジトリ作成、初期コミット
   - ブランチ戦略設定（main, develop）
   - **ファイル**: `.gitignore`、`README.md`
   - **完了条件**: 初回push完了

5. **[ENV-005]** GitHubリポジトリ作成（gh auth必要） `1` `XS` ✅ **完了**
   - **リポジトリURL**: https://github.com/Volvyyy/replypass
   - GitHub CLI認証、リモートリポジトリ作成
   - **完了条件**: リモートリポジトリへのpush成功

#### **パッケージ・依存関係**
6. **[ENV-006]** Frontend依存関係インストール `1` `S` ✅ **完了**
   - Shadcn/ui、Zustand、TanStack Query
   - React Hook Form、Zod
   - **ファイル**: `frontend/package.json`、`frontend/components.json`
   - **コマンド**: `npx shadcn-ui@latest init`
   - **完了条件**: 全依存関係でビルド成功

7. **[ENV-007]** Backend依存関係インストール `1` `S` ✅ **完了**
   - FastAPI、SQLAlchemy、Pydantic
   - Google Generative AI、Stripe
   - **ファイル**: `backend/requirements.txt`
   - **完了条件**: 全依存関係でサーバー起動成功

#### **基本設定ファイル**
8. **[ENV-008]** TypeScript設定最適化 `4` `XS` ✅ **完了**
   - **ファイル**: `frontend/tsconfig.json`
   - strict mode有効化、パス設定
   - **完了条件**: 型エラーなしでビルド成功

9. **[ENV-009]** Tailwind CSS設定 `4` `XS` ✅ **完了**
    - **ファイル**: `frontend/tailwind.config.js`
    - カスタムカラー、フォント設定
    - **完了条件**: デザインシステムの色が適用確認

10. **[ENV-010]** ESLint/Prettier設定 `4` `XS` ✅ **完了**
    - **ファイル**: `frontend/.eslintrc.json`、`frontend/.prettierrc`
    - 統一コーディング規約
    - **完了条件**: 自動フォーマット機能確認

11. **[ENV-011]** Python設定（Black、isort、mypy） `4` `XS` ✅ **完了**
    - **ファイル**: `backend/pyproject.toml`
    - **完了条件**: `black . && isort . && mypy .`でエラーなし

#### **環境変数・シークレット管理**
12. **[ENV-012]** 環境変数テンプレート作成 `1` `XS` ✅ **完了**
    - **ファイル**: `frontend/.env.example`、`backend/.env.example`
    - 必要な環境変数の一覧化
    - **完了条件**: 新規開発者が設定手順に従って環境構築完了

13. **[ENV-013]** Supabase CLI設定 `4` `S` ✅ **完了**
    - **ファイル**: `supabase/config.toml`
    - ローカル開発環境のセットアップ
    - **コマンド**: `supabase init`、`supabase start`
    - **完了条件**: ローカルSupabase起動確認

14. **[ENV-014]** API外部サービス設定 `1` `M` ✅ **完了**
    - Google Gemini API設定（新SDK google-genai 1.22.0対応）
    - Stripe API設定（最新SDK 12.2.0、Webhook署名検証）
    - **実装ファイル**: `app/gemini_client.py`, `app/stripe_client.py`
    - **完了条件**: 各APIクライアントのインポート成功

15. **[ENV-015]** CI/CD基本設定 `4` `M` ✅ **完了**
    - **ファイル**: `.github/workflows/test.yml`
    - GitHub Actions workflow作成（フロントエンド・バックエンド並列チェック）
    - **完了条件**: プルリクエスト時の自動チェック機能確認

16. **[ENV-016]** Google OAuth設定 `4` `M`
    - **ファイル**: `frontend/.env.local`, `backend/.env`
    - Google ConsoleでOAuth2.0クライアント作成
    - SupabaseダッシュボードでGoogleプロバイダ設定
    - **完了条件**: Googleソーシャルログイン機能確認

### **2.2. データベース基盤（13タスク）**

17. **[DB-001]** Supabaseマイグレーション初期化 `1` `S` ✅ **完了**
    - **ファイル**: `supabase/migrations/20250627000001_initial_schema.sql`
    - usersテーブル作成、PostgreSQL 17対応RLS、パフォーマンスインデックス
    - **完了条件**: マイグレーション実行成功、テストユーザー3件投入確認

18. **[DB-002]** 基本テーブル作成 `1` `L` ✅ **完了**
    - **ファイル**: `supabase/migrations/20250627000002_core_tables.sql`
    - cases、personas、conversation_logs、conversation_messagesテーブル
    - PostgreSQL 17最適化、月次パーティション、GIN索引、階層的RLS
    - **完了条件**: 全テーブル作成、制約設定完了、パフォーマンステスト成功

19. **[DB-003]** 残りテーブル・インデックス作成 `1` `M` ✅ **完了**
    - **ファイル**: `supabase/migrations/20250627000003_remaining_tables.sql`
    - 6テーブル作成（generated_replies、reply_suggestions、feedback_logs、subscription_plans、user_subscriptions、usage_logs）
    - PostgreSQL 17最適化（BRIN・GIN・カバリングインデックス、利用制限関数）
    - **完了条件**: 全テーブル作成、11テーブル対応テスト成功、シードデータ投入完了

20. **[DB-004]** RLS（Row Level Security）設定 `1` `L` ✅ **完了**
    - **ファイル**: `supabase/migrations/20240601000004_rls_policies.sql`
    - 全テーブルのセキュリティポリシー
    - **完了条件**: テストユーザーでアクセス制御確認

21. **[DB-005]** 初期データ投入（seed） `4` `M`
    - **ファイル**: `supabase/seed.sql`
    - テスト用のサンプルデータ
    - **完了条件**: 各テーブルにサンプルデータ投入確認

22. **[DB-006]** データベース関数作成 `4` `M`
    - 使用量チェック関数
    - 日次制限チェック関数
    - **ファイル**: `supabase/migrations/20240601000005_functions.sql`
    - **完了条件**: 関数の動作テスト成功

23. **[DB-007]** バックアップ・復元手順確立 `4` `S`
    - **ファイル**: `docs/database-backup.md`
    - 手動・自動バックアップ手順
    - **完了条件**: バックアップ・復元テスト成功

24. **[DB-008]** パフォーマンスモニタリング設定 `7` `S`
    - スロークエリ検出
    - **完了条件**: 重いクエリの特定・最適化手順確立

### **2.3. 認証システム基盤（82タスク）**

26. **[API-001]** Supabase Auth設定 `1` `M` ✅ **完了**
    - **ファイル**: `frontend/lib/supabase/*.ts`、`backend/app/auth/*.py`、`backend/app/middleware/auth.py`
    - フロントエンド: @supabase/ssr 2025対応、セキュリティミドルウェア、SSRクライアント
    - バックエンド: JWT検証、ミドルウェア認証、レート制限、セキュリティヘッダー
    - **完了条件**: フロント・バック認証統合、11テスト成功、サーバー起動確認

27. **[FE-001]** 認証コンテキスト作成 `1` `M` ✅ **完了**
    - **ファイル**: `frontend/contexts/auth-context.tsx`
    - グローバル認証状態管理
    - **完了条件**: 認証状態の変更が全画面に反映

28. **[FE-002]** ログイン画面実装 `1` `M` ✅ **完了**
    - **ファイル**: `frontend/app/auth/login/page.tsx`
    - React Hook Form + Zodバリデーション
    - **完了条件**: メール/パスワードでログイン成功

28. **[FE-003]** サインアップ画面実装 `1` `M` ✅ **完了**
    - **ファイル**: `frontend/app/auth/signup/page.tsx`
    - 利用規約同意チェックボックス
    - **完了条件**: 新規アカウント作成・メール認証完了

29. **[FE-004]** パスワードリセット機能 `4` `M` ✅ **完了**
    - **ファイル**: `frontend/app/auth/reset-password/page.tsx`, `frontend/app/auth/update-password/page.tsx`, `frontend/app/auth/confirm/route.ts`, `frontend/app/auth/error/page.tsx`（実装済み）
    - メール送信・新パスワード設定・トークン検証・エラーハンドリング完全実装
    - **完了条件**: パスワード変更フロー完了 ✅（TDD準拠、658行テストコード、セキュリティ強化）

30. **[BE-001]** FastAPI基本設定（CORS、セキュリティミドルウェア） `1` `M` ✅ **完了**
    - **ファイル**: `backend/app/middleware/security.py`, `backend/app/middleware/cors_handler.py`, `backend/app/middleware/request_validator.py`, `backend/app/middleware/logging_middleware.py`, `backend/app/core/security.py`
    - 2025年セキュリティベストプラクティス：SecurityHeadersMiddleware、AdvancedCORSMiddleware、RequestValidationMiddleware、StructuredLoggingMiddleware
    - セキュリティ機能：CSP、HSTS、Permissions Policy、Cross-Origin policies、SQLインジェクション・XSS対策、構造化ログ、レート制限階層化
    - **完了条件**: 14テスト成功、セキュリティヘッダー完全実装、エンタープライズグレードの堅牢性実現

31. **[FE-005]** 認証ガード実装 `1` `M`
    - **ファイル**: `frontend/middleware.ts`
    - ページアクセス制御
    - **完了条件**: 未認証時の自動リダイレクト確認

32. **[FE-006]** ローディング・エラー状態管理 `4` `S`
    - **ファイル**: `frontend/components/auth/loading.tsx`
    - 認証中のUX改善
    - **完了条件**: スムーズな認証フロー確認

### **2.4. 基本UI/UXコンポーネント（12タスク）**

33. **[FE-007]** 共通レイアウトコンポーネント `1` `M`
    - **ファイル**: `frontend/components/layout/main-layout.tsx`
    - ヘッダー、サイドバー、フッター
    - **完了条件**: 全保護ページで共通レイアウト適用

34. **[FE-008]** ナビゲーションコンポーネント `1` `M`
    - **ファイル**: `frontend/components/nav/sidebar.tsx`
    - アクティブ状態、アイコン表示
    - **完了条件**: ページ間の移動確認

35. **[FE-009]** 基本Buttonコンポーネント拡張 `1` `S`
    - **ファイル**: `frontend/components/ui/button.tsx`
    - ローディング状態、アイコン対応
    - **完了条件**: 全パターンのボタン表示確認

36. **[FE-010]** Cardコンポーネント作成 `1` `S`
    - **ファイル**: `frontend/components/ui/card.tsx`
    - タイトル、説明、アクション領域
    - **完了条件**: 一貫性のあるカードデザイン確認

37. **[FE-011]** Modalコンポーネント作成 `1` `M`
    - **ファイル**: `frontend/components/ui/modal.tsx`
    - アクセシビリティ対応（フォーカス管理）
    - **完了条件**: キーボード操作でのモーダル制御確認

38. **[FE-012]** Toastコンポーネント作成 `4` `M`
    - **ファイル**: `frontend/components/ui/toast.tsx`
    - 成功・エラー・警告・情報の4種類
    - **完了条件**: 各タイプの通知表示確認

39. **[FE-013]** LoadingSpinnerコンポーネント `4` `S`
    - **ファイル**: `frontend/components/ui/loading.tsx`
    - 各サイズ対応
    - **完了条件**: 非同期処理中の表示確認

40. **[FE-014]** FormFieldコンポーネント `1` `M`
    - **ファイル**: `frontend/components/ui/form-field.tsx`
    - ラベル、エラー、ヘルプテキスト
    - **完了条件**: バリデーションエラーの表示確認

41. **[FE-015]** FileUploadコンポーネント `4` `L`
    - **ファイル**: `frontend/components/ui/file-upload.tsx`
    - ドラッグ&ドロップ、プログレスバー
    - **完了条件**: 画像ファイルのアップロード確認

42. **[FE-016]** ProgressBarコンポーネント `7` `S`
    - **ファイル**: `frontend/components/ui/progress.tsx`
    - 利用状況表示用
    - **完了条件**: パーセンテージ表示確認

43. **[FE-017]** Badgeコンポーネント `7` `S`
    - **ファイル**: `frontend/components/ui/badge.tsx`
    - ステータス表示用
    - **完了条件**: 各色・サイズの表示確認

44. **[FE-018]** Skeletonコンポーネント `7` `S`
    - **ファイル**: `frontend/components/ui/skeleton.tsx`
    - ローディング時のプレースホルダー
    - **完了条件**: 滑らかなロード体験確認

### **2.5. 基本ページ実装（8タスク）**

45. **[FE-019]** ランディングページ基本構造 `1` `L`
    - **ファイル**: `frontend/app/page.tsx`
    - ヒーロー、機能紹介、料金表
    - **完了条件**: レスポンシブデザイン確認

46. **[FE-020]** ダッシュボードページ基本構造 `1` `L`
    - **ファイル**: `frontend/app/dashboard/page.tsx`
    - ケース一覧、利用状況表示
    - **完了条件**: 認証後のダッシュボード表示確認

47. **[FE-021]** 404/500エラーページ `4` `M`
    - **ファイル**: `frontend/app/not-found.tsx`、`frontend/app/error.tsx`
    - ユーザーフレンドリーなエラー表示
    - **完了条件**: 各エラー状況での適切な表示確認

48. **[FE-022]** 利用規約・プライバシーポリシー `4` `M`
    - **ファイル**: `frontend/app/legal/terms/page.tsx`
    - 法的文書の表示
    - **完了条件**: 読みやすいフォーマットでの表示確認

49. ✅ **[BE-002]** ヘルスチェックエンドポイント `1` `S` **【完了】**
    - **ファイル**: `backend/app/main.py`, `backend/app/core/health.py`
    - `/health`, `/health/live`, `/health/ready`, `/health/detailed`エンドポイント
    - **完了条件**: サーバー稼働状況確認可能 ✅
    - **実装内容**: 2025年ベストプラクティス準拠（Kubernetes対応、30秒キャッシング、並行依存関係チェック）

50. **[BE-003]** CORS設定 `1` `S`
    - **ファイル**: `backend/app/main.py`
    - フロントエンドからのアクセス許可
    - **完了条件**: ブラウザでのAPI呼び出し成功

51. **[TEST-001]** 基本テスト環境構築 `4` `M`
    - **ファイル**: `frontend/jest.config.js`、`backend/tests/conftest.py`
    - Jest（FE）、pytest（BE）設定
    - **完了条件**: サンプルテストの実行成功

### **2.6. ケース管理MVP（12タスク）**

53. ✅ **[BE-004]** Userモデル・リポジトリ `1` `M` **【完了】**
    - **ファイル**: `backend/app/models/user.py`、`backend/app/repositories/user.py`、`backend/app/models/base.py`、`backend/app/repositories/base.py`、`backend/app/database.py`
    - SQLAlchemy 2.0モデル定義（非同期対応、型安全性、JSONフィールド）
    - **完了条件**: CRUD操作確認 ✅
    - **実装内容**: BaseModel/BaseRepository、Identity Mapパターン、12個のテスト全通過

54. **[BE-005]** Caseモデル・リポジトリ `1` `M`
    - **ファイル**: `backend/app/models/case.py`、`backend/app/repositories/case.py`
    - ケース情報の永続化
    - **完了条件**: ケースの作成・取得・更新・削除確認

55. **[API-003]** ケース一覧取得API `1` `M` ✅ **完了**
    - **ファイル**: `backend/app/api/cases.py`（実装済み）
    - `GET /api/cases`実装（ページネーション・フィルタリング・認証対応）
    - **完了条件**: ページネーション付きレスポンス確認 ✅

56. **[API-004]** ケース作成API `1` `M`
    - **ファイル**: `backend/app/routes/cases.py`
    - `POST /cases`実装、バリデーション
    - **完了条件**: 新規ケース作成確認

57. **[API-005]** ケース詳細取得API `1` `S`
    - **ファイル**: `backend/app/routes/cases.py`
    - `GET /cases/{id}`実装
    - **完了条件**: 存在確認、404エラー処理確認

58. **[API-006]** ケース更新・削除API `1` `M`
    - **ファイル**: `backend/app/routes/cases.py`
    - `PATCH /cases/{id}`、`DELETE /cases/{id}`実装
    - **完了条件**: 更新・論理削除確認

59. **[FE-023]** ケース一覧コンポーネント `1` `M`
    - **ファイル**: `frontend/components/cases/case-list.tsx`
    - カード形式、フィルタリング機能
    - **完了条件**: ケース一覧の表示・操作確認

60. **[FE-024]** ケース作成フォーム `1` `L`
    - **ファイル**: `frontend/components/cases/case-form.tsx`
    - React Hook Form、リアルタイムバリデーション
    - **完了条件**: フォーム送信・エラー処理確認

61. **[FE-025]** ケース詳細ページ `1` `L`
    - **ファイル**: `frontend/app/cases/[id]/page.tsx`
    - タブレイアウト（ペルソナ、会話ログ、履歴）
    - **完了条件**: 動的ルーティング、データ表示確認

62. **[FE-026]** ケース編集・削除機能 `4` `M`
    - **ファイル**: `frontend/components/cases/case-actions.tsx`
    - 編集モーダル、削除確認ダイアログ
    - **完了条件**: 編集・削除操作確認

63. **[TEST-002]** ケース管理テスト実装 `4` `L`
    - **ファイル**: `frontend/tests/cases.test.tsx`、`backend/tests/test_cases.py`
    - API、コンポーネントテスト
    - **完了条件**: 全テストケース通過

64. **[FE-027]** ローディング・エラー状態管理 `4` `M`
    - **ファイル**: `frontend/hooks/use-cases.ts`
    - TanStack Query活用
    - **完了条件**: スムーズなUX確認

### **2.7. MVP統合・テスト（8タスク）**

65. **[TEST-003]** 統合テスト環境構築 `1` `M`
    - **ファイル**: `tests/integration/`
    - E2Eテスト環境（Playwright）
    - **完了条件**: 基本フローのE2Eテスト実行

66. **[TEST-004]** 認証フローテスト `1` `L`
    - **ファイル**: `tests/integration/auth.spec.ts`
    - ログイン〜ダッシュボード表示まで
    - **完了条件**: 全認証パターンの自動テスト通過

67. **[TEST-005]** ケース管理フローテスト `1` `L`
    - **ファイル**: `tests/integration/cases.spec.ts`
    - 作成〜表示〜編集〜削除まで
    - **完了条件**: CRUD操作の自動テスト通過

68. **[DEPLOY-001]** 開発環境デプロイ `1` `L`
    - Vercel（FE）、Ubuntu VPS（BE）設定
    - **完了条件**: 外部アクセス可能な開発環境構築

69. **[DEPLOY-002]** 環境変数・シークレット管理 `1` `M`
    - 本番用環境変数設定
    - **完了条件**: セキュアな本番環境設定完了

70. **[TEST-006]** パフォーマンステスト `4` `M`
    - **ファイル**: `tests/performance/`
    - ページロード時間、API応答時間測定
    - **完了条件**: パフォーマンス目標達成確認

71. **[DOC-001]** 開発手順書作成 `4` `S`
    - **ファイル**: `docs/development-guide.md`
    - セットアップ〜デプロイまでの手順
    - **完了条件**: 新規開発者が手順通りに環境構築完了

72. **[TEST-007]** MVP受け入れテスト `1` `M`
    - ユーザー受け入れ基準の確認
    - **完了条件**: 全機能要件の動作確認完了

---

## **3. Phase 1開発タスク（週3-6）**

### **3.1. 決済システム統合（16タスク）**

#### **Stripe基盤構築**
73. **[API-007]** Stripe設定・Webhook実装 `1` `L`
    - **ファイル**: `backend/app/services/stripe.py`
    - Customer作成、Subscription管理
    - **完了条件**: Stripe Webhook受信・処理確認

74. **[DB-009]** サブスクリプション関連テーブル `1` `M`
    - **ファイル**: `supabase/migrations/20240615000001_subscription_tables.sql`
    - subscription_plans、user_subscriptions、usage_logsテーブル
    - **完了条件**: サブスクリプション情報の永続化確認

75. **[BE-006]** プラン管理システム `1` `L`
    - **ファイル**: `backend/app/models/subscription.py`
    - プラン作成・更新・無効化機能
    - **完了条件**: 管理画面からのプラン操作確認

76. **[API-008]** サブスクリプション管理API `1` `L`
    - **ファイル**: `backend/app/routes/subscriptions.py`
    - 現在プラン取得、変更、解約API
    - **完了条件**: 全サブスクリプション操作のAPI確認

#### **フロントエンド決済UI**
77. **[FE-028]** 料金表コンポーネント `1` `M`
    - **ファイル**: `frontend/components/pricing/pricing-table.tsx`
    - 3プラン比較、特徴一覧表示
    - **完了条件**: 動的プラン情報表示確認

78. **[FE-029]** Checkoutページ実装 `1` `L`
    - **ファイル**: `frontend/app/checkout/page.tsx`
    - Stripe Checkout統合
    - **完了条件**: テスト決済完了確認

79. **[FE-030]** サブスクリプション管理ページ `1` `L`
    - **ファイル**: `frontend/app/settings/subscription/page.tsx`
    - 現在プラン表示、変更・解約機能
    - **完了条件**: プラン変更フロー確認

80. **[FE-031]** 決済成功・失敗ページ `4` `M`
    - **ファイル**: `frontend/app/checkout/success/page.tsx`
    - 決済結果表示、次ステップ案内
    - **完了条件**: 各決済結果での適切な表示確認

#### **使用量制限システム**
81. **[BE-007]** 使用量トラッキングシステム `1` `L`
    - **ファイル**: `backend/app/services/usage_tracker.py`
    - API呼び出し回数記録・制限チェック
    - **完了条件**: プラン別制限の動作確認

82. **[API-009]** 使用量チェックミドルウェア `1` `M`
    - **ファイル**: `backend/app/middleware/rate_limit.py`
    - リクエスト前の制限チェック
    - **完了条件**: 制限超過時の429レスポンス確認

83. **[FE-032]** 使用量表示コンポーネント `4` `M`
    - **ファイル**: `frontend/components/usage/usage-meter.tsx`
    - プログレスバー、残り回数表示
    - **完了条件**: リアルタイム使用量更新確認

84. **[FE-033]** 制限超過時のUI処理 `4` `M`
    - **ファイル**: `frontend/components/usage/limit-exceeded.tsx`
    - アップグレード誘導、制限解除案内
    - **完了条件**: 制限超過時の適切なUX確認

#### **Webhookイベント処理**
85. **[BE-008]** Stripe Webhookハンドラー `1` `L`
    - **ファイル**: `backend/app/webhook/stripe.py`
    - payment_succeeded、subscription_updated等
    - **完了条件**: 全Webhookイベントの適切な処理確認

86. **[BE-009]** 決済失敗・チャージバック処理 `1` `M`
    - **ファイル**: `backend/app/services/payment_failure.py`
    - アカウント一時停止、通知送信
    - **完了条件**: 決済失敗時の適切な対応確認

    - **ファイル**: `backend/app/services/invoice.py`
    - PDF生成、メール送信
    - **完了条件**: 請求書の自動生成・送信確認

88. **[TEST-008]** 決済システム統合テスト `1` `L`
    - **ファイル**: `tests/integration/payment.spec.ts`
    - 決済フロー全体のテスト
    - **完了条件**: 決済関連全シナリオの自動テスト通過

### **3.2. Google OAuth統合（8タスク）**

89. **[FE-034]** Google OAuth設定 `1` `M`
    - Google Cloud Console設定
    - **完了条件**: OAuth認証フロー確認

90. **[FE-035]** Google OAuth ボタン実装 `1` `M`
    - **ファイル**: `frontend/components/auth/google-auth.tsx`
    - Supabase Auth統合
    - **完了条件**: Googleアカウントでのログイン確認

91. **[BE-010]** OAuth後のユーザー情報処理 `1` `M`
    - **ファイル**: `backend/app/services/oauth.py`
    - プロフィール情報の自動設定
    - **完了条件**: OAuth後の適切なユーザー情報設定確認

92. **[FE-036]** OAuth エラーハンドリング `4` `M`
    - **ファイル**: `frontend/components/auth/oauth-error.tsx`
    - 認証失敗時の適切な案内
    - **完了条件**: OAuth失敗時の適切なエラー表示確認

93. **[API-011]** プロフィール情報同期API `4` `S`
    - **ファイル**: `backend/app/routes/profile.py`
    - Googleプロフィールとの同期
    - **完了条件**: プロフィール情報の自動更新確認

94. **[TEST-009]** OAuth認証テスト `4` `M`
    - **ファイル**: `tests/integration/oauth.spec.ts`
    - OAuth認証フローのテスト
    - **完了条件**: OAuth関連シナリオの自動テスト通過

95. **[FE-037]** アカウント連携設定 `7` `M`
    - **ファイル**: `frontend/app/settings/accounts/page.tsx`
    - 複数アカウント連携管理
    - **完了条件**: アカウント連携・解除機能確認

96. **[BE-011]** アカウント統合・マイグレーション `7` `L`
    - **ファイル**: `backend/app/services/account_merge.py`
    - 既存アカウントとの統合処理
    - **完了条件**: アカウント統合の安全な実行確認

### **3.3. ペルソナシステム基盤（16タスク）**

#### **ペルソナデータモデル**
97. **[DB-010]** ペルソナ関連テーブル拡張 `1` `M`
    - **ファイル**: `supabase/migrations/20240620000001_persona_system.sql`
    - persona_analyses、reference_textsテーブル追加
    - **完了条件**: ペルソナ情報の完全な永続化確認

98. **[BE-012]** Personaモデル・リポジトリ `1` `M`
    - **ファイル**: `backend/app/models/persona.py`
    - ペルソナ設定の管理
    - **完了条件**: ペルソナCRUD操作確認

99. **[API-012]** ペルソナ取得・更新API `1` `M`
    - **ファイル**: `backend/app/routes/personas.py`
    - `GET/PUT /cases/{id}/persona`実装
    - **完了条件**: ペルソナ設定の保存・取得確認

#### **ペルソナ設定UI**
100. **[FE-038]** クイック設定コンポーネント `1` `L`
     - **ファイル**: `frontend/components/persona/quick-settings.tsx`
     - スライダー、ラジオボタン、トグル
     - **完了条件**: 設定値の保存・表示確認

101. **[FE-039]** スタイルインポートコンポーネント `1` `L`
     - **ファイル**: `frontend/components/persona/style-import.tsx`
     - テキストエリア、文字数カウント
     - **完了条件**: テキスト入力・保存確認

102. **[FE-040]** ペルソナ設定ページ統合 `1` `M`
     - **ファイル**: `frontend/app/cases/[id]/persona/page.tsx`
     - タブ形式での設定項目表示
     - **完了条件**: ペルソナ設定の総合的な操作確認

103. **[FE-041]** 設定精度メーター `4` `M`
     - **ファイル**: `frontend/components/persona/accuracy-meter.tsx`
     - 設定完了度の視覚的表示
     - **完了条件**: 設定に応じたメーター変動確認

#### **参考テキスト管理**
104. **[BE-013]** テキスト保存・取得サービス `1` `M`
     - **ファイル**: `backend/app/services/reference_text.py`
     - 5000文字制限、暗号化保存
     - **完了条件**: 機密テキストの安全な保存確認

105. **[FE-042]** テキストエディタコンポーネント `4` `L`
     - **ファイル**: `frontend/components/persona/text-editor.tsx`
     - シンタックスハイライト、文字数制限
     - **完了条件**: 使いやすいテキスト編集体験確認

106. **[API-013]** テキスト暗号化・復号化API `1` `M`
     - **ファイル**: `backend/app/services/encryption.py`
     - 参考テキストの暗号化
     - **完了条件**: テキストの暗号化保存・復号化表示確認

#### **バリデーション・エラーハンドリング**
107. **[BE-014]** ペルソナバリデーション `1` `M`
     - **ファイル**: `backend/app/validators/persona.py`
     - 入力値検証、ビジネスルール
     - **完了条件**: 不正な入力値の適切な拒否確認

108. **[FE-043]** ペルソナエラー表示 `4` `M`
     - **ファイル**: `frontend/components/persona/error-display.tsx`
     - フィールド別エラーメッセージ
     - **完了条件**: バリデーションエラーの適切な表示確認

109. **[TEST-010]** ペルソナシステムテスト `1` `L`
     - **ファイル**: `tests/integration/persona.spec.ts`
     - 設定保存〜表示までのテスト
     - **完了条件**: ペルソナ関連全機能の自動テスト通過

#### **UI/UX改善**
110. **[FE-043]** ペルソナプレビュー機能 `4` `L`
     - **ファイル**: `frontend/components/persona/preview.tsx`
     - 設定反映後の返信例表示
     - **完了条件**: 設定変更の即座な反映確認

111. **[FE-044]** 設定保存・復元機能 `7` `M`
     - **ファイル**: `frontend/components/persona/save-restore.tsx`
     - 設定テンプレート機能
     - **完了条件**: ペルソナ設定の保存・読み込み確認

112. **[FE-045]** ペルソナ設定ガイド `7` `M`
     - **ファイル**: `frontend/components/persona/guide.tsx`
     - 初回利用者向けのツアー
     - **完了条件**: わかりやすい設定手順の提供確認

### **3.4. 会話ログ管理システム（20タスク）**

#### **会話ログデータモデル**
113. **[DB-011]** 会話ログテーブル最適化 `1` `M`
     - **ファイル**: `supabase/migrations/20240625000001_conversation_optimization.sql`
     - パフォーマンス改善、インデックス追加
     - **完了条件**: 大量メッセージの高速検索確認

114. **[BE-015]** ConversationLogモデル `1` `M`
     - **ファイル**: `backend/app/models/conversation.py`
     - メッセージ、メタデータ管理
     - **完了条件**: 会話ログCRUD操作確認

115. **[API-014]** 会話ログ管理API `1` `L`
     - **ファイル**: `backend/app/routes/conversations.py`
     - 作成、取得、メッセージ追加API
     - **完了条件**: 会話ログ操作の全API確認

#### **テキスト入力機能**
116. **[FE-046]** テキストメッセージ入力コンポーネント `1` `M`
     - **ファイル**: `frontend/components/conversation/text-input.tsx`
     - 発言者選択、リアルタイム保存
     - **完了条件**: テキストメッセージの追加確認

117. **[FE-047]** 会話表示コンポーネント `1` `L`
     - **ファイル**: `frontend/components/conversation/conversation-view.tsx`
     - チャット形式、スクロール、タイムスタンプ
     - **完了条件**: 見やすい会話表示確認

118. **[FE-048]** メッセージ編集・削除機能 `4` `M`
     - **ファイル**: `frontend/components/conversation/message-actions.tsx`
     - インライン編集、削除確認
     - **完了条件**: メッセージ操作の確認

#### **スクリーンショット入力（基本）**
119. **[FE-049]** 画像アップロードコンポーネント `1` `L`
     - **ファイル**: `frontend/components/conversation/image-upload.tsx`
     - ドラッグ&ドロップ、プレビュー表示
     - **完了条件**: 画像ファイルのアップロード確認

120. **[BE-016]** 画像保存サービス `1` `M`
     - **ファイル**: `backend/app/services/image_storage.py`
     - Supabase Storage統合
     - **完了条件**: 画像の安全な保存確認

121. **[API-015]** 画像アップロードAPI `1` `M`
     - **ファイル**: `backend/app/routes/images.py`
     - マルチパートファイルアップロード
     - **完了条件**: 画像アップロードAPI確認

#### **OCR基盤（Phase 1では基本実装）**
122. **[BE-017]** Gemini OCRサービス基盤 `1` `L`
     - **ファイル**: `backend/app/services/ocr.py`
     - Gemini 2.5 Flash-Lite統合
     - **完了条件**: 基本的なOCR機能確認

123. **[API-016]** OCR解析API `1` `L`
     - **ファイル**: `backend/app/routes/ocr.py`
     - `POST /conversations/{id}/messages/ocr`実装
     - **完了条件**: スクリーンショットからテキスト抽出確認

124. **[FE-050]** OCR結果表示・編集 `4` `L`
     - **ファイル**: `frontend/components/conversation/ocr-result.tsx`
     - 抽出結果の確認・修正機能
     - **完了条件**: OCR結果の編集・確定確認

#### **会話ログ検索・フィルタリング**
125. **[BE-018]** 全文検索機能 `4` `L`
     - **ファイル**: `backend/app/services/search.py`
     - PostgreSQL全文検索
     - **完了条件**: メッセージ内容の高速検索確認

126. **[FE-051]** 検索・フィルタコンポーネント `4` `M`
     - **ファイル**: `frontend/components/conversation/search.tsx`
     - キーワード検索、日付フィルタ
     - **完了条件**: 検索機能の動作確認

127. **[API-017]** 検索API `4` `M`
     - **ファイル**: `backend/app/routes/search.py`
     - 検索クエリ処理、結果返却
     - **完了条件**: 検索API全パターン確認

#### **パフォーマンス最適化**
128. **[BE-019]** ページネーション実装 `1` `M`
     - **ファイル**: `backend/app/services/pagination.py`
     - 大量メッセージの効率的な取得
     - **完了条件**: 大量データの快適な表示確認

129. **[FE-052]** 仮想スクロール実装 `4` `L`
     - **ファイル**: `frontend/components/conversation/virtual-scroll.tsx`
     - 長い会話ログの快適な表示
     - **完了条件**: 数千件メッセージの滑らかなスクロール確認

130. **[TEST-011]** 会話ログシステムテスト `1` `L`
     - **ファイル**: `tests/integration/conversation.spec.ts`
     - テキスト・画像入力、OCR処理テスト
     - **完了条件**: 会話ログ関連全機能の自動テスト通過

#### **UI/UX改善**
131. **[FE-053]** 会話ログエクスポート機能 `7` `M`
     - **ファイル**: `frontend/components/conversation/export.tsx`
     - テキスト・CSV・PDFエクスポート
     - **完了条件**: 各形式でのエクスポート確認

132. **[FE-054]** 会話ログインポート機能 `7` `M`
     - **ファイル**: `frontend/components/conversation/import.tsx`
     - 他サービスからのデータ移行
     - **完了条件**: 外部データの取り込み確認

### **3.5. 基本返信生成システム（16タスク）**

#### **LLM統合基盤**
133. **[BE-020]** Gemini API統合サービス `1` `L`
     - **ファイル**: `backend/app/services/llm.py`
     - モデル選択、プロンプト管理
     - **完了条件**: 全Geminiモデルでの生成確認

134. **[BE-021]** プロンプトエンジニアリング基盤 `1` `L`
     - **ファイル**: `backend/app/services/prompt_builder.py`
     - コンテキスト構築、テンプレート管理
     - **完了条件**: 動的プロンプト生成確認

135. **[BE-022]** レート制限・エラーハンドリング `1` `M`
     - **ファイル**: `backend/app/services/llm_limiter.py`
     - API制限対応、リトライ処理
     - **完了条件**: API制限時の適切な処理確認

#### **返信生成API**
136. **[API-018]** 返信生成メインAPI `1` `L`
     - **ファイル**: `backend/app/routes/generate.py`
     - `POST /cases/{id}/generate`実装
     - **完了条件**: 3つの返信案生成確認

137. **[BE-023]** 生成履歴管理システム `1` `M`
     - **ファイル**: `backend/app/services/generation_history.py`
     - 生成結果の保存、取得
     - **完了条件**: 生成履歴の永続化確認

138. **[API-019]** 生成オプション処理 `4` `M`
     - **ファイル**: `backend/app/services/generation_options.py`
     - モデル選択、目的指定処理
     - **完了条件**: 各種オプションでの生成結果差異確認

#### **フロントエンド生成UI**
139. **[FE-055]** 返信生成フォーム `1` `L`
     - **ファイル**: `frontend/components/generate/generate-form.tsx`
     - 目的入力、生成ボタン
     - **完了条件**: 生成リクエストの送信確認

140. **[FE-056]** 生成結果表示コンポーネント `1` `L`
     - **ファイル**: `frontend/components/generate/result-display.tsx`
     - 3つの返信案、カテゴリー表示
     - **完了条件**: 生成結果の見やすい表示確認

141. **[FE-057]** 生成中ローディング状態 `4` `M`
     - **ファイル**: `frontend/components/generate/loading-state.tsx`
     - プログレスインジケーター、キャンセル機能
     - **完了条件**: 生成中の適切なフィードバック確認

142. **[FE-058]** 返信案アクション（いいね/送信） `1` `M`
     - **ファイル**: `frontend/components/generate/suggestion-actions.tsx`
     - 評価ボタン、送信済みマーク
     - **完了条件**: 各アクションの動作確認

#### **コンテキスト管理**
143. **[BE-024]** 会話コンテキスト構築 `1` `L`
     - **ファイル**: `backend/app/services/context_builder.py`
     - 会話履歴、ペルソナ情報統合
     - **完了条件**: 適切なコンテキストでの生成確認

144. **[BE-025]** トークン制限管理 `1` `M`
     - **ファイル**: `backend/app/services/token_manager.py`
     - コンテキスト長制限、優先順位付け
     - **完了条件**: トークン制限内での最適な生成確認

145. **[API-020]** コンテキスト最適化API `4` `M`
     - **ファイル**: `backend/app/routes/context.py`
     - コンテキスト詳細取得、調整
     - **完了条件**: コンテキスト内容の確認・調整確認

#### **品質管理・モニタリング**
146. **[BE-026]** 生成品質チェック `4` `M`
     - **ファイル**: `backend/app/services/quality_check.py`
     - 不適切コンテンツ検出
     - **完了条件**: 不適切な生成結果の自動検出確認

147. **[BE-027]** 生成メトリクス収集 `4` `M`
     - **ファイル**: `backend/app/services/metrics.py`
     - 生成時間、成功率、ユーザー評価
     - **完了条件**: 生成パフォーマンスの可視化確認

148. **[TEST-012]** 返信生成システムテスト `1` `L`
     - **ファイル**: `tests/integration/generation.spec.ts`
     - 生成フロー全体のテスト
     - **完了条件**: 返信生成関連全機能の自動テスト通過

### **3.6. Phase 1統合・品質保証（12タスク）**

149. **[TEST-013]** 決済統合テスト `1` `L`
     - **ファイル**: `tests/integration/payment-flow.spec.ts`
     - サインアップ〜決済〜機能制限解除まで
     - **完了条件**: 決済関連全フローの自動テスト通過

150. **[TEST-014]** ペルソナ・生成統合テスト `1` `L`
     - **ファイル**: `tests/integration/persona-generation.spec.ts`
     - ペルソナ設定〜返信生成まで
     - **完了条件**: メイン機能フローの自動テスト通過

151. **[TEST-015]** セキュリティテスト `1` `L`
     - **ファイル**: `tests/security/`
     - 認証、認可、入力検証テスト
     - **完了条件**: セキュリティ脆弱性の検証完了

152. **[DEPLOY-003]** ステージング環境構築 `1` `L`
     - 本番環境と同等のステージング環境
     - **完了条件**: ステージング環境での全機能動作確認

153. **[TEST-016]** 負荷テスト `4` `L`
     - **ファイル**: `tests/load/`
     - 同時接続、API負荷テスト
     - **完了条件**: 性能要件達成確認

154. **[DOC-002]** APIドキュメント更新 `4` `M`
     - **ファイル**: `docs/api-reference.md`
     - OpenAPI仕様書、利用例
     - **完了条件**: 全APIの詳細ドキュメント完成

155. **[DOC-003]** ユーザーマニュアル作成 `4` `L`
     - **ファイル**: `docs/user-manual.md`
     - 機能の使い方、トラブルシューティング
     - **完了条件**: ユーザーサポート用ドキュメント完成

156. **[DEPLOY-004]** 本番環境デプロイ準備 `1` `L`
     - SSL証明書、監視設定、バックアップ
     - **完了条件**: 本番リリース可能な状態確認

157. **[TEST-017]** 受け入れテスト実施 `1` `L`
     - **ファイル**: `tests/acceptance/`
     - ビジネス要件の確認
     - **完了条件**: 全要件の動作確認完了

158. **[DEPLOY-005]** Phase 1本番リリース `1` `M`
     - 本番環境へのデプロイ実行
     - **完了条件**: 本番環境での全機能動作確認

159. **[TEST-018]** 本番環境疎通確認 `1` `M`
     - 本番環境での動作確認
     - **完了条件**: 本番環境での問題なし確認

160. **[DOC-004]** Phase 1振り返り・Phase 2計画 `4` `S`
     - **ファイル**: `docs/phase1-retrospective.md`
     - 課題整理、改善点、次期計画
     - **完了条件**: Phase 2開発計画の確定

---

## **4. Phase 2開発タスク（週7-10）**

### **4.1. 高度なペルソナエンジン（20タスク）**

#### **AI分析システム**
161. **[BE-028]** ペルソナ自動分析エンジン `1` `XL`
     - **ファイル**: `backend/app/services/persona_analyzer.py`
     - Gemini 2.5を使った高度な分析
     - **完了条件**: 性格・価値観・言語パターンの自動抽出確認

162. **[BE-029]** 分析結果構造化処理 `1` `L`
     - **ファイル**: `backend/app/services/analysis_processor.py`
     - JSON形式での分析結果管理
     - **完了条件**: 構造化された分析データの保存確認

163. **[API-021]** ペルソナ分析API `1` `L`
     - **ファイル**: `backend/app/routes/persona_analysis.py`
     - `POST /cases/{id}/persona/analyze`実装
     - **完了条件**: 分析APIの動作確認

164. **[FE-059]** 分析実行・結果表示UI `1` `L`
     - **ファイル**: `frontend/components/persona/analysis-view.tsx`
     - 分析進行状況、結果の可視化
     - **完了条件**: 分析結果の見やすい表示確認

#### **動的ペルソナ調整**
165. **[BE-030]** ペルソナ学習システム `8` `XL`
     - **ファイル**: `backend/app/services/persona_learning.py`
     - フィードバックベースの自動調整
     - **完了条件**: 利用履歴に基づくペルソナ改善確認

     - **ファイル**: `backend/app/services/ab_testing.py`
     - 複数ペルソナパターンの比較
     - **完了条件**: ペルソナ効果測定確認

167. **[FE-060]** ペルソナ比較・調整UI `4` `L`
     - **ファイル**: `frontend/components/persona/comparison.tsx`
     - 分析前後の比較表示
     - **完了条件**: ペルソナ変化の可視化確認

#### **高度な参考テキスト処理**
     - **ファイル**: `backend/app/services/multilingual_analysis.py`
     - 言語検出、翻訳、分析
     - **完了条件**: 日本語以外のテキスト処理確認

169. **[BE-033]** テキスト品質評価 `4` `M`
     - **ファイル**: `backend/app/services/text_quality.py`
     - 分析に適したテキストの判定
     - **完了条件**: 不適切テキストの自動検出確認

170. **[FE-061]** 高度なテキストエディタ `4` `L`
     - **ファイル**: `frontend/components/persona/advanced-editor.tsx`
     - シンタックスハイライト、品質評価表示
     - **完了条件**: 使いやすいテキスト編集体験確認

#### **ペルソナテンプレート機能**
171. **[DB-012]** テンプレート管理テーブル `4` `M`
     - **ファイル**: `supabase/migrations/20240705000001_persona_templates.sql`
     - persona_templatesテーブル
     - **完了条件**: テンプレート情報の永続化確認

172. **[BE-034]** テンプレート管理サービス `4` `L`
     - **ファイル**: `backend/app/services/persona_templates.py`
     - 作成、共有、適用機能
     - **完了条件**: テンプレート機能の動作確認

173. **[FE-062]** テンプレート選択・適用UI `4` `M`
     - **ファイル**: `frontend/components/persona/templates.tsx`
     - テンプレート一覧、プレビュー機能
     - **完了条件**: テンプレート機能の使いやすさ確認

#### **性格診断・推奨機能**
     - **ファイル**: `backend/app/services/personality_test.py`
     - MBTI、Big5等の心理学的指標
     - **完了条件**: 科学的根拠のある性格分析確認

     - **ファイル**: `frontend/components/persona/personality-test.tsx`
     - 質問形式の診断フォーム
     - **完了条件**: 直感的な診断体験確認

176. **[BE-036]** ペルソナ推奨エンジン `7` `L`
     - **ファイル**: `backend/app/services/persona_recommendations.py`
     - 相手タイプ別のペルソナ推奨
     - **完了条件**: 適切なペルソナ推奨確認

#### **統合テスト・パフォーマンス**
177. **[TEST-019]** ペルソナエンジンテスト `1` `L`
     - **ファイル**: `tests/integration/persona-engine.spec.ts`
     - 分析〜学習〜推奨までの統合テスト
     - **完了条件**: ペルソナエンジン全機能の自動テスト通過

178. **[BE-037]** 分析処理最適化 `4` `M`
     - **ファイル**: `backend/app/services/analysis_optimization.py`
     - 分析速度向上、メモリ使用量削減
     - **完了条件**: 分析処理の高速化確認

179. **[FE-064]** ペルソナUX最適化 `4` `M`
     - **ファイル**: `frontend/components/persona/ux-improvements.tsx`
     - 操作性向上、視覚的改善
     - **完了条件**: ユーザビリティテスト結果良好確認

180. **[DOC-005]** ペルソナエンジン仕様書 `4` `M`
     - **ファイル**: `docs/persona-engine.md`
     - アルゴリズム詳細、利用方法
     - **完了条件**: 技術仕様の完全なドキュメント化完了

### **4.2. 高度なOCRシステム（16タスク）**

#### **OCR精度向上**
181. **[BE-038]** 画像前処理エンジン `1` `L`
     - **ファイル**: `backend/app/services/image_preprocessing.py`
     - 二値化、ノイズ除去、傾き補正
     - **完了条件**: OCR精度の大幅向上確認

182. **[BE-039]** 複数OCRエンジン統合 `4` `L`
     - **ファイル**: `backend/app/services/multi_ocr.py`
     - Gemini + Tesseract + Google Vision
     - **完了条件**: 最適OCRエンジンの自動選択確認

183. **[BE-040]** OCR結果検証・修正 `1` `M`
     - **ファイル**: `backend/app/services/ocr_validation.py`
     - 信頼度評価、自動修正
     - **完了条件**: OCR結果の品質保証確認

#### **高度な会話抽出**
184. **[BE-041]** 会話構造解析 `1` `L`
     - **ファイル**: `backend/app/services/conversation_parser.py`
     - 発言者識別、時系列順序付け
     - **完了条件**: 複雑なチャット画面の正確な解析確認

185. **[BE-042]** マルチアプリ対応 `4` `L`
     - **ファイル**: `backend/app/services/multi_app_parser.py`
     - LINE、Discord、Teams等の対応
     - **完了条件**: 主要チャットアプリの解析確認

186. **[FE-065]** OCR結果編集エディタ `1` `L`
     - **ファイル**: `frontend/components/ocr/result-editor.tsx`
     - 直感的な修正機能
     - **完了条件**: OCR結果の効率的な修正確認

#### **バッチ処理・大量画像対応**
187. **[BE-043]** バッチOCR処理 `4` `L`
     - **ファイル**: `backend/app/services/batch_ocr.py`
     - 複数画像の一括処理
     - **完了条件**: 大量画像の効率的な処理確認

188. **[BE-044]** 非同期処理システム `1` `M`
     - **ファイル**: `backend/app/services/async_ocr.py`
     - Celery/Redis使用の背景処理
     - **完了条件**: 長時間処理の非同期実行確認

189. **[FE-066]** 処理進行状況表示 `4` `M`
     - **ファイル**: `frontend/components/ocr/progress-display.tsx`
     - リアルタイム進捗、キューイング状況
     - **完了条件**: 処理状況の透明性確認

#### **OCR品質管理**
190. **[BE-045]** OCR精度メトリクス `4` `M`
     - **ファイル**: `backend/app/services/ocr_metrics.py`
     - 精度測定、品質レポート
     - **完了条件**: OCR性能の定量評価確認

191. **[BE-046]** 学習データ収集 `7` `L`
     - **ファイル**: `backend/app/services/training_data.py`
     - ユーザー修正データの活用
     - **完了条件**: OCR改善のためのデータ収集確認

195. **[TEST-020]** OCRシステム統合テスト `1` `L`
     - **ファイル**: `tests/integration/ocr-system.spec.ts`
     - 画像アップロード〜会話抽出〜編集まで
     - **完了条件**: OCR機能全体の自動テスト通過

196. **[DOC-006]** OCRシステム仕様書 `4` `M`
     - **ファイル**: `docs/ocr-system.md`
     - 対応形式、制限事項、最適化方法
     - **完了条件**: OCR機能の完全なドキュメント化完了

### **4.3. フィードバックループシステム（20タスク）**

#### **フィードバック収集基盤**
197. **[DB-013]** フィードバック関連テーブル `1` `M`
     - **ファイル**: `supabase/migrations/20240710000001_feedback_system.sql`
     - feedback_logs、partner_reactions、improvement_logsテーブル
     - **完了条件**: フィードバックデータの完全な記録確認

198. **[BE-049]** フィードバック管理サービス `1` `L`
     - **ファイル**: `backend/app/services/feedback_manager.py`
     - 収集、分類、分析機能
     - **完了条件**: フィードバックの系統的管理確認

199. **[API-022]** フィードバック送信API `1` `M`
     - **ファイル**: `backend/app/routes/feedback.py`
     - 返信評価、相手反応記録
     - **完了条件**: 各種フィードバックの記録確認

#### **返信評価システム**
200. **[FE-068]** 返信評価UI改善 `1` `M`
     - **ファイル**: `frontend/components/feedback/rating-system.tsx`
     - 5段階評価、詳細コメント
     - **完了条件**: 直感的な評価機能確認

201. **[FE-069]** 相手反応記録UI `1` `M`
     - **ファイル**: `frontend/components/feedback/reaction-tracker.tsx`
     - 😊😥以外の詳細な反応記録
     - **完了条件**: 詳細な反応データ収集確認

202. **[BE-050]** 評価重み付けシステム `4` `M`
     - **ファイル**: `backend/app/services/rating_weights.py`
     - 時間経過、重要度による重み調整
     - **完了条件**: 適切な評価重み付け確認

#### **学習・改善エンジン**
203. **[BE-051]** フィードバック学習エンジン `1` `XL`
     - **ファイル**: `backend/app/services/feedback_learning.py`
     - 成功パターン学習、失敗要因分析
     - **完了条件**: フィードバックベースの生成改善確認

204. **[BE-052]** パターン認識システム `4` `L`
     - **ファイル**: `backend/app/services/pattern_recognition.py`
     - 成功・失敗パターンの自動抽出
     - **完了条件**: 有効なパターンの発見確認

205. **[BE-053]** プロンプト動的最適化 `1` `L`
     - **ファイル**: `backend/app/services/prompt_optimization.py`
     - フィードバックベースのプロンプト改善
     - **完了条件**: 個人最適化されたプロンプト確認

#### **成功事例・失敗事例管理**
206. **[BE-054]** 事例データベース構築 `4` `L`
     - **ファイル**: `backend/app/services/case_database.py`
     - 成功・失敗事例の構造化保存
     - **完了条件**: 検索可能な事例データベース確認

207. **[FE-070]** 事例閲覧・学習UI `4` `M`
     - **ファイル**: `frontend/components/feedback/case-study.tsx`
     - 過去の成功・失敗事例表示
     - **完了条件**: 学習に役立つ事例表示確認

208. **[BE-055]** 類似状況検索 `4` `M`
     - **ファイル**: `backend/app/services/similarity_search.py`
     - 現在状況と類似の過去事例検索
     - **完了条件**: 関連性の高い事例推奨確認

#### **パーソナライズ機能**
209. **[BE-056]** 個人学習プロファイル `4` `L`
     - **ファイル**: `backend/app/services/personal_learning.py`
     - ユーザー固有の成功パターン学習
     - **完了条件**: 個人に最適化された提案確認

210. **[BE-057]** 適応的生成システム `1` `L`
     - **ファイル**: `backend/app/services/adaptive_generation.py`
     - 学習結果を反映した動的生成
     - **完了条件**: 継続利用による生成品質向上確認

211. **[FE-071]** 学習進捗表示 `4` `M`
     - **ファイル**: `frontend/components/feedback/learning-progress.tsx`
     - AIの学習状況、改善度の可視化
     - **完了条件**: 学習効果の透明性確認

#### **分析・レポート機能**
212. **[BE-058]** フィードバック分析エンジン `4` `L`
     - **ファイル**: `backend/app/services/feedback_analytics.py`
     - 統計分析、トレンド分析
     - **完了条件**: 詳細なフィードバック分析確認

213. **[FE-072]** 改善レポートUI `8` `M`
     - **ファイル**: `frontend/components/feedback/improvement-report.tsx`
     - 月次改善レポート、グラフ表示
     - **完了条件**: わかりやすい改善状況表示確認

     - **ファイル**: `backend/app/services/auto_ab_testing.py`
     - 新機能の自動A/Bテスト
     - **完了条件**: 自動的な機能改善確認

#### **高度なフィードバック機能**
     - **ファイル**: `frontend/components/feedback/voice-feedback.tsx`
     - 音声での詳細フィードバック
     - **完了条件**: 音声フィードバックの収集確認

216. **[TEST-021]** フィードバックシステムテスト `1` `L`
     - **ファイル**: `tests/integration/feedback-system.spec.ts`
     - フィードバック収集〜学習〜改善まで
     - **完了条件**: フィードバック機能全体の自動テスト通過

### **4.4. 高度なUI/UX機能（16タスク）**

#### **ダークモード・テーマ機能**
217. **[FE-074]** ダークモード実装 `4` `M`
     - **ファイル**: `frontend/components/theme/dark-mode.tsx`
     - システム設定連動、手動切替
     - **完了条件**: 完全なダークモード対応確認

218. **[FE-075]** カスタムテーマ機能 `7` `L`
     - **ファイル**: `frontend/components/theme/custom-theme.tsx`
     - 色調整、フォント選択
     - **完了条件**: ユーザーカスタマイズ可能な外観確認

#### **アクセシビリティ向上**
219. **[FE-076]** スクリーンリーダー対応強化 `4` `L`
     - **ファイル**: `frontend/components/accessibility/`
     - ARIA属性、セマンティック改善
     - **完了条件**: スクリーンリーダーでの完全操作確認

220. **[FE-077]** キーボードショートカット `4` `M`
     - **ファイル**: `frontend/hooks/use-keyboard-shortcuts.ts`
     - 主要機能のキーボード操作
     - **完了条件**: キーボードのみでの完全操作確認

221. **[FE-078]** 文字サイズ・コントラスト調整 `4` `M`
     - **ファイル**: `frontend/components/accessibility/display-settings.tsx`
     - ユーザー設定での表示調整
     - **完了条件**: 視覚障害者対応の表示設定確認

#### **高度なインタラクション**
222. **[FE-079]** ドラッグ&ドロップ改善 `8` `M`
     - **ファイル**: `frontend/components/interaction/drag-drop.tsx`
     - ケース並び替え、ファイル操作
     - **完了条件**: 直感的なドラッグ&ドロップ操作確認

     - **ファイル**: `frontend/components/interaction/context-menu.tsx`
     - 効率的な操作メニュー
     - **完了条件**: 作業効率向上の確認

     - **ファイル**: `frontend/components/mobile/gestures.tsx`
     - スワイプ、ピンチ操作
     - **完了条件**: モバイルでの快適なジェスチャー操作確認

#### **パフォーマンス最適化**
225. **[FE-082]** 仮想化リスト最適化 `4` `L`
     - **ファイル**: `frontend/components/optimization/virtual-list.tsx`
     - 大量データの効率表示
     - **完了条件**: 数万件データの滑らかな表示確認

226. **[FE-083]** 画像遅延読み込み `4` `M`
     - **ファイル**: `frontend/components/optimization/lazy-image.tsx`
     - Intersection Observer使用
     - **完了条件**: 画像読み込みの最適化確認

227. **[FE-084]** PWA機能実装 `7` `L`
     - **ファイル**: `frontend/app/manifest.json`、`frontend/sw.js`
     - オフライン対応、アプリインストール
     - **完了条件**: PWAとしての動作確認

#### **マイクロインタラクション**
228. **[FE-085]** アニメーション体系化 `4` `M`
     - **ファイル**: `frontend/components/animation/`
     - Framer Motion使用の統一アニメーション
     - **完了条件**: 滑らかで統一感のあるアニメーション確認

229. **[FE-086]** フィードバックアニメーション `4` `M`
     - **ファイル**: `frontend/components/feedback/micro-interactions.tsx`
     - ボタン押下、フォーム送信等の反応
     - **完了条件**: 操作に対する適切なフィードバック確認

     - **ファイル**: `frontend/components/loading/enhanced-loading.tsx`
     - スケルトンスクリーン、プログレス表示
     - **完了条件**: 待機時間の快適性向上確認

232. **[TEST-022]** UI/UX統合テスト `4` `L`
     - **ファイル**: `tests/integration/ui-ux.spec.ts`
     - アクセシビリティ、パフォーマンステスト
     - **完了条件**: UI/UX品質の自動検証確認

### **4.5. 運用・監視システム（12タスク）**

#### **ログ・監視基盤**
233. **[DEPLOY-006]** 構造化ログ実装 `1` `L`
     - **ファイル**: `backend/app/logging/structured_logging.py`
     - JSON形式ログ、トレーサビリティ
     - **完了条件**: 問題の迅速な特定可能確認

234. **[DEPLOY-007]** APM（Application Performance Monitoring） `1` `L`
     - New Relic、Datadog等の導入
     - **完了条件**: パフォーマンス問題の自動検出確認

235. **[DEPLOY-008]** エラー追跡システム `1` `M`
     - Sentry導入、エラー通知
     - **完了条件**: エラーの即座な検知・通知確認

#### **ビジネスメトリクス**
236. **[BE-060]** ビジネス指標収集 `1` `L`
     - **ファイル**: `backend/app/analytics/business_metrics.py`
     - DAU、チャーン率、LTV計算
     - **完了条件**: 重要ビジネス指標の自動計算確認

237. **[FE-089]** 管理者ダッシュボード `4` `L`
     - **ファイル**: `frontend/app/admin/dashboard/page.tsx`
     - リアルタイム指標表示
     - **完了条件**: ビジネス状況の一目での把握確認

238. **[BE-061]** 利用統計レポート自動生成 `4` `M`
     - **ファイル**: `backend/app/reports/usage_reports.py`
     - 日次・月次レポート自動作成
     - **完了条件**: 定期レポートの自動生成確認

#### **セキュリティ監視**
239. **[BE-062]** セキュリティログ監視 `1` `L`
     - **ファイル**: `backend/app/security/security_monitoring.py`
     - 不正アクセス検知、異常ログイン監視
     - **完了条件**: セキュリティ脅威の自動検知確認

240. **[BE-063]** API不正利用検知 `1` `M`
     - **ファイル**: `backend/app/security/api_abuse_detection.py`
     - レート制限超過、異常パターン検知
     - **完了条件**: API濫用の自動ブロック確認

#### **障害対応・復旧**
241. **[DEPLOY-009]** 自動バックアップシステム `1` `M`
     - データベース、ファイルの定期バックアップ
     - **完了条件**: データ損失リスクの最小化確認

242. **[DEPLOY-010]** 障害通知システム `1` `M`
     - Slack、メール通知の設定
     - **完了条件**: 障害の迅速な通知確認

243. **[DOC-007]** 運用手順書作成 `1` `L`
     - **ファイル**: `docs/operations-manual.md`
     - 障害対応、メンテナンス手順
     - **完了条件**: 運用チームでの手順書活用確認

244. **[TEST-023]** 運用監視テスト `4` `M`
     - **ファイル**: `tests/operations/`
     - 監視アラート、復旧手順のテスト
     - **完了条件**: 運用システムの信頼性確認

### **4.6. Phase 2統合・最終リリース（8タスク）**

245. **[TEST-024]** Phase 2機能統合テスト `1` `XL`
     - **ファイル**: `tests/integration/phase2-full.spec.ts`
     - 全機能の総合的な動作確認
     - **完了条件**: Phase 2全機能の完璧な動作確認

246. **[TEST-025]** パフォーマンス・負荷テスト `1` `L`
     - **ファイル**: `tests/performance/final-load-test.js`
     - 本番想定負荷での性能確認
     - **完了条件**: 性能要件の完全な達成確認

247. **[DEPLOY-011]** 本番環境最終調整 `1` `L`
     - SSL、CDN、セキュリティ設定最終確認
     - **完了条件**: 本番環境の完璧な準備確認

248. **[TEST-026]** セキュリティ監査 `1` `L`
     - **ファイル**: `tests/security/final-audit.md`
     - 外部セキュリティ監査の実施
     - **完了条件**: セキュリティ脆弱性ゼロ確認

249. **[DOC-008]** 最終ドキュメント整備 `1` `M`
     - API仕様書、運用手順書、ユーザーマニュアル最終版
     - **完了条件**: 全ドキュメントの完成確認

250. **[DEPLOY-012]** Phase 2本番リリース `1` `M`
     - 段階的リリース実行
     - **完了条件**: 問題なく本番リリース完了

251. **[TEST-027]** 本番環境総合確認 `1` `M`
     - 全機能の本番環境での動作確認
     - **完了条件**: 本番環境での全機能正常動作確認

252. **[DOC-009]** プロジェクト完了報告書 `4` `S`
     - **ファイル**: `docs/project-completion-report.md`
     - 成果物、課題、今後の展望
     - **完了条件**: ステークホルダーへの完了報告完了

---

## **5. タスク進行ガイドライン**

### **5.1. タスク実行時の原則**

#### **実装前の確認事項**
1. **要件理解**: タスクの目的と完了条件を明確に理解
2. **依存関係**: 前提となるタスクの完了確認
3. **技術調査**: 実装方法の事前調査（30分以内）
4. **アプローチ確認**: 実装方針をチームに共有

#### **実装中の品質保証**
1. **コード品質**: ESLint、Prettier、TypeScript型チェック
2. **テストカバレッジ**: 重要機能は80%以上
3. **セキュリティ**: 入力検証、認証・認可の確認
4. **パフォーマンス**: レスポンス時間、メモリ使用量の監視

#### **完了時の確認事項**
1. **動作確認**: 複数ブラウザ・デバイスでのテスト
2. **ドキュメント更新**: README、API仕様書の更新
3. **コードレビュー**: チームメンバーによる確認
4. **デプロイ確認**: ステージング環境での動作確認

### **5.2. 緊急度・優先度の判断基準**

#### **P0（必須）タスクの特徴**
- セキュリティに関わる
- 他のタスクをブロックする
- ユーザー体験に致命的な影響
- 法的要件に関わる

#### **P1（重要）タスクの特徴**
- ユーザビリティに大きく影響
- ビジネス目標達成に重要
- 技術的負債の解消
- パフォーマンスに影響

#### **P2（改善）タスクの特徴**
- 利便性の向上
- 運用効率の改善
- 将来の拡張性向上
- UXの細かい改善

### **5.3. リスク管理**

#### **技術的リスク**
- **新技術の採用**: プロトタイプでの事前検証
- **外部API依存**: 代替手段の準備
- **パフォーマンス問題**: 負荷テストの早期実施

#### **スケジュールリスク**
- **工数超過**: 定期的な進捗確認と調整
- **依存関係遅延**: クリティカルパスの明確化
- **品質問題**: 継続的なコードレビューとテスト

#### **ビジネスリスク**
- **要件変更**: アジャイルな対応体制
- **競合対応**: 差別化機能の優先実装
- **ユーザーフィードバック**: 早期のユーザーテスト実施

### **5.4. 成功指標**

#### **技術的成功指標**
- **テストカバレッジ**: 80%以上
- **バグ発見率**: 週次10件以下
- **ページ読み込み速度**: 2秒以内（P95）
- **API応答時間**: 500ms以内（P95）

#### **ビジネス成功指標**
- **ユーザー登録数**: 週次目標達成
- **利用継続率**: 月次70%以上
- **顧客満足度**: NPS 50以上
- **収益目標**: 月次売上目標達成

---

この開発Todoリスト書は、Reply Passの完全な実装を段階的に進めるための詳細なロードマップです。各タスクは具体的な実装内容、完了条件、優先度が明記されており、Claude Codeが迷うことなく開発を進められます。

実装時は必ずこのリストに従って進め、各タスクの完了後は進捗を更新してください。