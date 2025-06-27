/**
 * Login Page for Reply Pass
 * Compatible with Next.js 15, React Hook Form 7.58.1, and Zod 3.25.67
 *
 * @description User login interface with form validation and authentication
 * @security Implements secure authentication flow with Supabase
 */

"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { useForm } from "react-hook-form";

import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { useAuth } from "@/hooks/use-auth";
import { loginSchema, type LoginFormData } from "@/lib/validations/auth";

export default function LoginPage() {
  const router = useRouter();
  const { signIn, loading } = useAuth();
  const [authError, setAuthError] = useState<string | null>(null);

  const form = useForm<LoginFormData>({
    resolver: zodResolver(loginSchema),
    mode: "onBlur", // Better UX than onSubmit
    defaultValues: {
      email: "",
      password: "",
    },
  });

  const onSubmit = async (data: LoginFormData) => {
    setAuthError(null);

    try {
      const { error } = await signIn(data.email, data.password);

      if (error) {
        // Handle Supabase authentication errors
        const errorMessage = getErrorMessage(error.message);
        setAuthError(errorMessage);
        return;
      }

      // Successful login - redirect to dashboard
      router.push("/dashboard");
    } catch (error) {
      console.error("Login failed:", error);
      setAuthError("ログインに失敗しました。もう一度お試しください。");
    }
  };

  /**
   * Convert Supabase error messages to user-friendly Japanese messages
   */
  const getErrorMessage = (errorMessage: string): string => {
    const errorMap: Record<string, string> = {
      "Invalid login credentials":
        "メールアドレスまたはパスワードが正しくありません",
      "Email not confirmed":
        "メールアドレスが確認されていません。確認メールをご確認ください。",
      "Too many requests":
        "ログイン試行回数が上限に達しました。しばらく待ってからお試しください。",
      "User not found": "アカウントが見つかりません",
      "Signup disabled": "新規登録が無効になっています",
    };

    return (
      errorMap[errorMessage] ||
      "ログインエラーが発生しました。もう一度お試しください。"
    );
  };

  return (
    <div className="bg-background flex min-h-screen items-center justify-center px-4 py-12 sm:px-6 lg:px-8">
      <div className="w-full max-w-md space-y-8">
        {/* Header */}
        <div className="text-center">
          <h1 className="text-foreground text-3xl font-bold tracking-tight">
            Reply Pass
          </h1>
          <p className="text-muted-foreground mt-2 text-sm">
            アカウントにログインしてください
          </p>
        </div>

        {/* Login Form */}
        <Card className="p-6">
          <Form {...form}>
            <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
              {/* Global Error Message */}
              {authError && (
                <div className="bg-destructive/15 text-destructive rounded-md p-3 text-sm">
                  {authError}
                </div>
              )}

              {/* Email Field */}
              <FormField
                control={form.control}
                name="email"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>メールアドレス</FormLabel>
                    <FormControl>
                      <Input
                        type="email"
                        placeholder="your@example.com"
                        autoComplete="email"
                        disabled={loading}
                        {...field}
                      />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />

              {/* Password Field */}
              <FormField
                control={form.control}
                name="password"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>パスワード</FormLabel>
                    <FormControl>
                      <Input
                        type="password"
                        placeholder="パスワードを入力"
                        autoComplete="current-password"
                        disabled={loading}
                        {...field}
                      />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />

              {/* Forgot Password Link */}
              <div className="flex justify-end">
                <Link
                  href="/auth/reset-password"
                  className="text-primary hover:text-primary/80 text-sm"
                >
                  パスワードを忘れましたか？
                </Link>
              </div>

              {/* Submit Button */}
              <Button
                type="submit"
                className="w-full"
                disabled={loading || form.formState.isSubmitting}
              >
                {loading || form.formState.isSubmitting
                  ? "ログイン中..."
                  : "ログイン"}
              </Button>
            </form>
          </Form>

          {/* Sign Up Link */}
          <div className="mt-6 text-center">
            <p className="text-muted-foreground text-sm">
              アカウントをお持ちでないですか？{" "}
              <Link
                href="/signup"
                className="text-primary hover:text-primary/80 font-medium"
              >
                新規登録
              </Link>
            </p>
          </div>
        </Card>

        {/* Additional Links */}
        <div className="text-center">
          <Link
            href="/"
            className="text-muted-foreground hover:text-foreground text-sm"
          >
            ← ホームに戻る
          </Link>
        </div>
      </div>
    </div>
  );
}
