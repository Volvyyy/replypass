/**
 * Authentication Test Page
 * テスト用の認証状態確認ページ
 */

"use client";

import { useAuth } from "@/hooks/use-auth";

export default function TestAuthPage() {
  const {
    user,
    session,
    loading,
    initialized,
    isAuthenticated,
    isEmailVerified,
    signIn,
    signUp,
    signOut,
  } = useAuth();

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <div className="text-center">
          <div className="mx-auto h-32 w-32 animate-spin rounded-full border-b-2 border-blue-600"></div>
          <p className="mt-4 text-gray-600">認証状態を確認中...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto max-w-4xl p-8">
      <h1 className="mb-8 text-3xl font-bold">認証システム テスト</h1>

      {/* 認証状態表示 */}
      <div className="mb-8 grid grid-cols-1 gap-6 md:grid-cols-2">
        <div className="rounded-lg border bg-white p-6 shadow-md">
          <h2 className="mb-4 text-xl font-semibold text-gray-800">認証状態</h2>
          <div className="space-y-2">
            <p>
              <strong>初期化完了:</strong>{" "}
              <span className={initialized ? "text-green-600" : "text-red-600"}>
                {initialized ? "はい" : "いいえ"}
              </span>
            </p>
            <p>
              <strong>読み込み中:</strong>{" "}
              <span className={loading ? "text-yellow-600" : "text-green-600"}>
                {loading ? "はい" : "いいえ"}
              </span>
            </p>
            <p>
              <strong>認証済み:</strong>{" "}
              <span
                className={isAuthenticated ? "text-green-600" : "text-red-600"}
              >
                {isAuthenticated ? "はい" : "いいえ"}
              </span>
            </p>
            <p>
              <strong>メール確認済み:</strong>{" "}
              <span
                className={isEmailVerified ? "text-green-600" : "text-red-600"}
              >
                {isEmailVerified ? "はい" : "いいえ"}
              </span>
            </p>
          </div>
        </div>

        <div className="rounded-lg border bg-white p-6 shadow-md">
          <h2 className="mb-4 text-xl font-semibold text-gray-800">
            ユーザー情報
          </h2>
          {user ? (
            <div className="space-y-2">
              <p>
                <strong>ID:</strong>{" "}
                <span className="rounded bg-gray-100 px-2 py-1 font-mono text-sm">
                  {user.id}
                </span>
              </p>
              <p>
                <strong>メール:</strong> {user.email}
              </p>
              <p>
                <strong>作成日時:</strong>{" "}
                {new Date(user.created_at).toLocaleString("ja-JP")}
              </p>
              {user.updated_at && (
                <p>
                  <strong>最終更新:</strong>{" "}
                  {new Date(user.updated_at).toLocaleString("ja-JP")}
                </p>
              )}
              {user.email_confirmed_at && (
                <p>
                  <strong>メール確認日時:</strong>{" "}
                  {new Date(user.email_confirmed_at).toLocaleString("ja-JP")}
                </p>
              )}
            </div>
          ) : (
            <p className="text-gray-500">ログインしていません</p>
          )}
        </div>
      </div>

      {/* セッション情報 */}
      <div className="mb-8 rounded-lg border bg-white p-6 shadow-md">
        <h2 className="mb-4 text-xl font-semibold text-gray-800">
          セッション情報
        </h2>
        {session ? (
          <div className="space-y-2">
            <p>
              <strong>アクセストークン:</strong>{" "}
              <span className="rounded bg-gray-100 px-2 py-1 font-mono text-sm">
                {session.access_token.substring(0, 50)}...
              </span>
            </p>
            <p>
              <strong>有効期限:</strong>{" "}
              {session.expires_at
                ? new Date(session.expires_at * 1000).toLocaleString("ja-JP")
                : "未設定"}
            </p>
            <p>
              <strong>トークンタイプ:</strong> {session.token_type}
            </p>
            <p>
              <strong>リフレッシュトークン:</strong>{" "}
              <span className="rounded bg-gray-100 px-2 py-1 font-mono text-sm">
                {session.refresh_token ? "設定済み" : "未設定"}
              </span>
            </p>
          </div>
        ) : (
          <p className="text-gray-500">セッションが存在しません</p>
        )}
      </div>

      {/* 認証操作ボタン */}
      <div className="rounded-lg border bg-white p-6 shadow-md">
        <h2 className="mb-4 text-xl font-semibold text-gray-800">認証操作</h2>
        <div className="flex flex-wrap gap-4">
          {!isAuthenticated ? (
            <>
              <button
                onClick={() => signIn("test@example.com", "password123")}
                className="rounded-lg bg-blue-600 px-6 py-2 text-white transition-colors hover:bg-blue-700"
                disabled={loading}
              >
                テストログイン
              </button>
              <button
                onClick={() => signUp("test@example.com", "password123")}
                className="rounded-lg bg-green-600 px-6 py-2 text-white transition-colors hover:bg-green-700"
                disabled={loading}
              >
                テストサインアップ
              </button>
            </>
          ) : (
            <button
              onClick={signOut}
              className="rounded-lg bg-red-600 px-6 py-2 text-white transition-colors hover:bg-red-700"
              disabled={loading}
            >
              ログアウト
            </button>
          )}
        </div>
      </div>

      {/* 技術情報 */}
      <div className="mt-8 rounded-lg border bg-gray-50 p-6">
        <h2 className="mb-4 text-xl font-semibold text-gray-800">技術情報</h2>
        <div className="grid grid-cols-1 gap-4 text-sm md:grid-cols-3">
          <div>
            <h3 className="mb-2 font-semibold">状態管理</h3>
            <ul className="space-y-1 text-gray-600">
              <li>✅ Zustand Store</li>
              <li>✅ React Context</li>
              <li>✅ Custom Hook</li>
            </ul>
          </div>
          <div>
            <h3 className="mb-2 font-semibold">Supabase統合</h3>
            <ul className="space-y-1 text-gray-600">
              <li>✅ @supabase/ssr</li>
              <li>✅ クライアント/サーバー</li>
              <li>✅ 自動状態同期</li>
            </ul>
          </div>
          <div>
            <h3 className="mb-2 font-semibold">セキュリティ</h3>
            <ul className="space-y-1 text-gray-600">
              <li>✅ PKCE フロー</li>
              <li>✅ JWT 検証</li>
              <li>✅ 自動リフレッシュ</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}
