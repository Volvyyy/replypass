/**
 * Email Confirmation Page for Reply Pass
 * Compatible with Next.js 15 and Supabase Auth
 *
 * @description Email confirmation instructions after user registration
 * @security Part of secure registration flow with Supabase
 */

"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";

import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";

export default function ConfirmEmailPage() {
  const router = useRouter();

  return (
    <div className="bg-background flex min-h-screen items-center justify-center px-4 py-12 sm:px-6 lg:px-8">
      <div className="w-full max-w-md space-y-8">
        {/* Header */}
        <div className="text-center">
          <h1 className="text-foreground text-3xl font-bold tracking-tight">
            Reply Pass
          </h1>
          <p className="text-muted-foreground mt-2 text-sm">
            メールアドレスの確認
          </p>
        </div>

        {/* Confirmation Message */}
        <Card className="p-6 text-center">
          <div className="space-y-4">
            {/* Success Icon */}
            <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-green-100">
              <svg
                className="h-6 w-6 text-green-600"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
                xmlns="http://www.w3.org/2000/svg"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M5 13l4 4L19 7"
                />
              </svg>
            </div>

            {/* Main Message */}
            <div className="space-y-2">
              <h2 className="text-foreground text-xl font-semibold">
                確認メールを送信しました
              </h2>
              <p className="text-muted-foreground text-sm">
                ご登録いただいたメールアドレスに確認メールを送信しました。
                メール内のリンクをクリックしてアカウントを有効化してください。
              </p>
            </div>

            {/* Instructions */}
            <div className="rounded-md bg-blue-50 p-4 text-left">
              <h3 className="mb-2 text-sm font-medium text-blue-900">
                次の手順：
              </h3>
              <ol className="list-inside list-decimal space-y-1 text-sm text-blue-800">
                <li>メールボックスをご確認ください</li>
                <li>Reply Passからの確認メールを開いてください</li>
                <li>メール内の「アカウントを確認」ボタンをクリック</li>
                <li>確認完了後、ログインしてサービスをご利用ください</li>
              </ol>
            </div>

            {/* Troubleshooting */}
            <div className="space-y-2 text-left">
              <p className="text-muted-foreground text-xs">
                メールが届かない場合：
              </p>
              <ul className="text-muted-foreground list-inside list-disc space-y-1 text-xs">
                <li>迷惑メールフォルダをご確認ください</li>
                <li>メールアドレスが正しく入力されているかご確認ください</li>
                <li>数分お待ちいただいてから再度ご確認ください</li>
              </ul>
            </div>

            {/* Action Buttons */}
            <div className="space-y-3 pt-4">
              <Button onClick={() => router.push("/login")} className="w-full">
                ログイン画面に戻る
              </Button>

              <Button
                variant="outline"
                onClick={() => router.push("/signup")}
                className="w-full"
              >
                別のメールアドレスで登録
              </Button>
            </div>
          </div>
        </Card>

        {/* Additional Links */}
        <div className="space-y-2 text-center">
          <Link
            href="/"
            className="text-muted-foreground hover:text-foreground block text-sm"
          >
            ← ホームに戻る
          </Link>
          <Link
            href="/support"
            className="text-muted-foreground hover:text-foreground block text-sm"
          >
            サポートが必要ですか？
          </Link>
        </div>
      </div>
    </div>
  );
}
