/**
 * Sign Up Page for Reply Pass
 * Compatible with Next.js 15, React Hook Form 7.58.1, and Zod 3.25.67
 *
 * @description User registration interface with password strength and form validation
 * @security Implements secure registration flow with Supabase
 */

"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { useForm } from "react-hook-form";

import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Checkbox } from "@/components/ui/checkbox";
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { PasswordInputWithStrength } from "@/components/ui/password-input-with-strength";
import { useAuth } from "@/hooks/use-auth";
import { signUpSchema, type SignUpFormData } from "@/lib/validations/auth";

export default function SignUpPage() {
  const router = useRouter();
  const { signUp, loading } = useAuth();
  const [authError, setAuthError] = useState<string | null>(null);

  const form = useForm<SignUpFormData>({
    resolver: zodResolver(signUpSchema),
    mode: "onBlur", // Better UX than onSubmit
    defaultValues: {
      email: "",
      password: "",
      confirmPassword: "",
      terms: false,
    },
  });

  const onSubmit = async (data: SignUpFormData) => {
    setAuthError(null);

    try {
      const { error } = await signUp(data.email, data.password);

      if (error) {
        // Handle Supabase authentication errors
        const errorMessage = getErrorMessage(error.message);
        setAuthError(errorMessage);
        return;
      }

      // Successful signup - redirect to email confirmation page
      router.push("/auth/confirm-email");
    } catch (error) {
      console.error("Sign up failed:", error);
      setAuthError("アカウント作成に失敗しました。もう一度お試しください。");
    }
  };

  /**
   * Convert Supabase error messages to user-friendly Japanese messages
   */
  const getErrorMessage = (errorMessage: string): string => {
    const errorMap: Record<string, string> = {
      "User already registered": "このメールアドレスは既に登録されています",
      "Password should be at least 6 characters":
        "パスワードは6文字以上で入力してください",
      "Unable to validate email address: invalid format":
        "有効なメールアドレスを入力してください",
      "Signup disabled": "新規登録が無効になっています",
      "Email rate limit exceeded":
        "メール送信回数が上限に達しました。しばらく待ってからお試しください。",
      "Invalid email or password": "メールアドレスまたはパスワードが無効です",
    };

    return (
      errorMap[errorMessage] ||
      "アカウント作成エラーが発生しました。もう一度お試しください。"
    );
  };

  // Get current password value for validation display
  const passwordValue = form.watch("password");
  const confirmPasswordValue = form.watch("confirmPassword");

  return (
    <div className="bg-background flex min-h-screen items-center justify-center px-4 py-12 sm:px-6 lg:px-8">
      <div className="w-full max-w-md space-y-8">
        {/* Header */}
        <div className="text-center">
          <h1 className="text-foreground text-3xl font-bold tracking-tight">
            Reply Pass
          </h1>
          <p className="text-muted-foreground mt-2 text-sm">
            新しいアカウントを作成してください
          </p>
        </div>

        {/* Sign Up Form */}
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

              {/* Password Field with Strength Indicator */}
              <FormField
                control={form.control}
                name="password"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>パスワード</FormLabel>
                    <FormControl>
                      <PasswordInputWithStrength
                        placeholder="パスワードを入力"
                        autoComplete="new-password"
                        disabled={loading}
                        compactStrength={true}
                        {...field}
                      />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />

              {/* Confirm Password Field */}
              <FormField
                control={form.control}
                name="confirmPassword"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>パスワード確認</FormLabel>
                    <FormControl>
                      <Input
                        type="password"
                        placeholder="パスワードを再入力"
                        autoComplete="new-password"
                        disabled={loading}
                        {...field}
                      />
                    </FormControl>
                    <FormMessage />
                    {/* Password Match Indicator */}
                    {passwordValue &&
                      confirmPasswordValue &&
                      passwordValue === confirmPasswordValue && (
                        <div className="text-sm text-green-600">
                          ✓ パスワードが一致しています
                        </div>
                      )}
                  </FormItem>
                )}
              />

              {/* Terms of Service Agreement */}
              <FormField
                control={form.control}
                name="terms"
                render={({ field }) => (
                  <FormItem className="flex flex-row items-start space-y-0 space-x-3">
                    <FormControl>
                      <Checkbox
                        checked={field.value}
                        onCheckedChange={field.onChange}
                        disabled={loading}
                      />
                    </FormControl>
                    <div className="space-y-1 leading-none">
                      <FormLabel className="text-sm font-normal">
                        <Link
                          href="/terms"
                          className="text-primary hover:text-primary/80 underline"
                          target="_blank"
                          rel="noopener noreferrer"
                        >
                          利用規約
                        </Link>
                        および
                        <Link
                          href="/privacy"
                          className="text-primary hover:text-primary/80 underline"
                          target="_blank"
                          rel="noopener noreferrer"
                        >
                          プライバシーポリシー
                        </Link>
                        に同意します
                      </FormLabel>
                      <FormMessage />
                    </div>
                  </FormItem>
                )}
              />

              {/* Submit Button */}
              <Button
                type="submit"
                className="w-full"
                disabled={loading || form.formState.isSubmitting}
              >
                {loading || form.formState.isSubmitting
                  ? "アカウント作成中..."
                  : "アカウントを作成"}
              </Button>
            </form>
          </Form>

          {/* Login Link */}
          <div className="mt-6 text-center">
            <p className="text-muted-foreground text-sm">
              すでにアカウントをお持ちですか？{" "}
              <Link
                href="/login"
                className="text-primary hover:text-primary/80 font-medium"
              >
                ログイン
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
