/**
 * Authentication Error Page
 * 
 * @description Displays authentication errors with user-friendly messages
 * @security Provides helpful guidance without exposing sensitive details
 */

import Link from "next/link";

import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";

interface AuthErrorPageProps {
  searchParams: {
    error?: string;
  };
}

export default function AuthErrorPage({ searchParams }: AuthErrorPageProps) {
  const errorCode = searchParams.error || "unknown";

  // Map error codes to user-friendly messages
  const errorMessages: Record<string, {
    title: string;
    description: string;
    action: {
      label: string;
      href: string;
    };
  }> = {
    missing_parameters: {
      title: "リンクが無効です",
      description: "必要なパラメータが不足しています。メールから再度リンクをクリックしてください。",
      action: {
        label: "パスワードリセットをやり直す",
        href: "/auth/reset-password",
      },
    },
    invalid_token: {
      title: "無効なトークンです",
      description: "リンクが無効または既に使用されています。新しいリセットリンクを要求してください。",
      action: {
        label: "新しいリンクを要求する",
        href: "/auth/reset-password",
      },
    },
    token_expired: {
      title: "リンクの有効期限が切れています",
      description: "パスワードリセットリンクの有効期限が切れました。新しいリンクを要求してください。",
      action: {
        label: "新しいリンクを要求する",
        href: "/auth/reset-password",
      },
    },
    verification_failed: {
      title: "認証に失敗しました",
      description: "認証プロセスでエラーが発生しました。しばらく待ってから再度お試しください。",
      action: {
        label: "ログインページに戻る",
        href: "/login",
      },
    },
    auth_session_missing: {
      title: "認証セッションが見つかりません",
      description: "認証セッションが失効しています。別のデバイスやブラウザからリンクをクリックした可能性があります。",
      action: {
        label: "パスワードリセットをやり直す",
        href: "/auth/reset-password",
      },
    },
    signup_disabled: {
      title: "新規登録が無効です",
      description: "現在、新規登録を受け付けていません。しばらく待ってから再度お試しください。",
      action: {
        label: "ログインページに戻る",
        href: "/login",
      },
    },
    unexpected_error: {
      title: "予期しないエラーが発生しました",
      description: "システムエラーが発生しました。問題が続く場合は、サポートにお問い合わせください。",
      action: {
        label: "ホームページに戻る",
        href: "/",
      },
    },
    unknown: {
      title: "エラーが発生しました",
      description: "不明なエラーが発生しました。もう一度お試しください。",
      action: {
        label: "ログインページに戻る",
        href: "/login",
      },
    },
  };

  const errorInfo = errorMessages[errorCode] ?? errorMessages.unknown!;

  return (
    <div className="flex min-h-screen items-center justify-center px-4 py-12 sm:px-6 lg:px-8">
      <div className="w-full max-w-md space-y-8">
        {/* Header */}
        <div className="text-center">
          <div className="text-6xl mb-4">⚠️</div>
          <h1 className="text-3xl font-bold tracking-tight text-destructive">
            {errorInfo.title}
          </h1>
        </div>

        {/* Error Card */}
        <Card className="p-6">
          <div className="space-y-6 text-center">
            <p className="text-sm text-muted-foreground">
              {errorInfo.description}
            </p>

            {/* Debug Info (development only) */}
            {process.env.NODE_ENV === "development" && (
              <div className="rounded-md bg-muted p-3 text-left">
                <p className="text-xs text-muted-foreground font-mono">
                  Error Code: {errorCode}
                </p>
              </div>
            )}

            {/* Action Button */}
            <div className="space-y-3">
              <Link href={errorInfo.action.href}>
                <Button className="w-full">
                  {errorInfo.action.label}
                </Button>
              </Link>

              {/* Alternative Actions */}
              <div className="flex flex-col space-y-2 text-sm">
                <Link
                  href="/login"
                  className="text-primary hover:text-primary/80"
                >
                  ログインページに戻る
                </Link>
                <Link
                  href="/"
                  className="text-muted-foreground hover:text-foreground"
                >
                  ホームページに戻る
                </Link>
              </div>
            </div>
          </div>
        </Card>

        {/* Support Information */}
        <div className="text-center">
          <p className="text-xs text-muted-foreground">
            問題が解決しない場合は、
            <Link
              href="/contact"
              className="text-primary hover:text-primary/80"
            >
              サポートチーム
            </Link>
            までお問い合わせください。
          </p>
        </div>
      </div>
    </div>
  );
}