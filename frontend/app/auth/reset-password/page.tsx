/**
 * Password Reset Request Page
 * 
 * @description Allows users to request a password reset email
 * @security Prevents email enumeration attacks
 */

"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import Link from "next/link";
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
import {
  resetPasswordSchema,
  type ResetPasswordFormData,
} from "@/lib/validations/auth";

export default function ResetPasswordPage() {
  const { resetPassword, loading } = useAuth();
  const [isSubmitted, setIsSubmitted] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const form = useForm<ResetPasswordFormData>({
    resolver: zodResolver(resetPasswordSchema),
    mode: "onBlur",
    defaultValues: {
      email: "",
    },
  });

  const onSubmit = async (data: ResetPasswordFormData) => {
    setError(null);

    try {
      const { error } = await resetPassword(data.email);

      if (error) {
        // Log error but show generic message to prevent email enumeration
        console.error("Password reset error:", error);
      }

      // Always show success message to prevent email enumeration
      setIsSubmitted(true);
    } catch (error) {
      console.error("Password reset failed:", error);
      setError("エラーが発生しました。もう一度お試しください。");
    }
  };

  // Show success message after submission
  if (isSubmitted) {
    return (
      <div className="flex min-h-screen items-center justify-center px-4 py-12 sm:px-6 lg:px-8">
        <div className="w-full max-w-md space-y-8">
          <div className="text-center">
            <h1 className="text-3xl font-bold tracking-tight">
              メールを送信しました
            </h1>
            <p className="mt-2 text-sm text-muted-foreground">
              パスワードリセットのメールを送信しました
            </p>
          </div>

          <Card className="p-6">
            <div className="space-y-4 text-center">
              <p className="text-sm text-muted-foreground">
                入力されたメールアドレスが登録されている場合、パスワードリセットのリンクを含むメールをお送りしました。
              </p>
              <p className="text-sm text-muted-foreground">
                メールが届かない場合は、迷惑メールフォルダをご確認ください。
              </p>
              <div className="pt-4">
                <Link href="/login">
                  <Button variant="default" className="w-full">
                    ログインに戻る
                  </Button>
                </Link>
              </div>
            </div>
          </Card>
        </div>
      </div>
    );
  }

  return (
    <div className="flex min-h-screen items-center justify-center px-4 py-12 sm:px-6 lg:px-8">
      <div className="w-full max-w-md space-y-8">
        {/* Header */}
        <div className="text-center">
          <h1 className="text-3xl font-bold tracking-tight">
            パスワードリセット
          </h1>
          <p className="mt-2 text-sm text-muted-foreground">
            登録したメールアドレスを入力してください
          </p>
        </div>

        {/* Reset Form */}
        <Card className="p-6">
          <Form {...form}>
            <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
              {/* Error Message */}
              {error && (
                <div className="rounded-md bg-destructive/15 p-3 text-sm text-destructive">
                  {error}
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

              {/* Submit Button */}
              <Button
                type="submit"
                className="w-full"
                disabled={loading || form.formState.isSubmitting}
              >
                {loading || form.formState.isSubmitting
                  ? "送信中..."
                  : "リセットメールを送信"}
              </Button>
            </form>
          </Form>

          {/* Login Link */}
          <div className="mt-6 text-center">
            <Link
              href="/login"
              className="text-sm text-primary hover:text-primary/80"
            >
              ← ログインに戻る
            </Link>
          </div>
        </Card>
      </div>
    </div>
  );
}