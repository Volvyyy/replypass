/**
 * Password Update Page
 * 
 * @description Allows users to set a new password after reset
 * @security Validates recovery session and password strength
 */

"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { useRouter } from "next/navigation";
import { useState, useEffect } from "react";
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
import { PasswordInputWithStrength } from "@/components/ui/password-input-with-strength";
import {
  updatePasswordSchema,
  type UpdatePasswordFormData,
} from "@/lib/validations/auth";
import { useSupabase } from "@/providers/auth-provider";

export default function UpdatePasswordPage() {
  const router = useRouter();
  const { supabase } = useSupabase();
  const [isLoading, setIsLoading] = useState(false);
  const [isRecoveryMode, setIsRecoveryMode] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const form = useForm<UpdatePasswordFormData>({
    resolver: zodResolver(updatePasswordSchema),
    mode: "onBlur",
    defaultValues: {
      password: "",
      confirmPassword: "",
    },
  });

  useEffect(() => {
    // Listen for PASSWORD_RECOVERY event
    const { data: authListener } = supabase.auth.onAuthStateChange(
      (event, _session) => {
        if (event === "PASSWORD_RECOVERY") {
          setIsRecoveryMode(true);
        }
      }
    );

    // Check URL hash for recovery token
    if (typeof window !== "undefined") {
      const hash = window.location.hash;
      if (hash && hash.includes("type=recovery")) {
        setIsRecoveryMode(true);
      }
    }

    return () => {
      authListener.subscription.unsubscribe();
    };
  }, [supabase.auth]);

  const onSubmit = async (data: UpdatePasswordFormData) => {
    setIsLoading(true);
    setError(null);

    try {
      const { error } = await supabase.auth.updateUser({
        password: data.password,
      });

      if (error) {
        console.error("Password update error:", error.message);
        setError("パスワードの更新に失敗しました。もう一度お試しください。");
        return;
      }

      // Success - redirect to dashboard
      router.push("/dashboard");
    } catch (error) {
      console.error("Password update failed:", error);
      setError("予期しないエラーが発生しました。");
    } finally {
      setIsLoading(false);
    }
  };

  // Show access denied if not in recovery mode
  if (!isRecoveryMode) {
    return (
      <div className="flex min-h-screen items-center justify-center px-4 py-12 sm:px-6 lg:px-8">
        <div className="w-full max-w-md space-y-8">
          <Card className="p-6">
            <div className="text-center">
              <h1 className="text-2xl font-bold text-destructive mb-4">
                アクセス権限がありません
              </h1>
              <p className="text-sm text-muted-foreground mb-6">
                このページにアクセスするには、パスワードリセットのメールからアクセスしてください。
              </p>
              <Button
                onClick={() => router.push("/auth/reset-password")}
                className="w-full"
              >
                パスワードリセットに戻る
              </Button>
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
            新しいパスワードを設定
          </h1>
          <p className="mt-2 text-sm text-muted-foreground">
            新しいパスワードを入力してください
          </p>
        </div>

        {/* Update Form */}
        <Card className="p-6">
          <Form {...form}>
            <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
              {/* Error Message */}
              {error && (
                <div className="rounded-md bg-destructive/15 p-3 text-sm text-destructive">
                  {error}
                </div>
              )}

              {/* Password Field with Strength Indicator */}
              <FormField
                control={form.control}
                name="password"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>新しいパスワード</FormLabel>
                    <FormControl>
                      <PasswordInputWithStrength
                        placeholder="新しいパスワードを入力"
                        autoComplete="new-password"
                        disabled={isLoading}
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
                      <PasswordInputWithStrength
                        placeholder="パスワードを再入力"
                        autoComplete="new-password"
                        disabled={isLoading}
                        showStrengthIndicator={false}
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
                disabled={isLoading || form.formState.isSubmitting}
              >
                {isLoading || form.formState.isSubmitting
                  ? "更新中..."
                  : "パスワードを更新"}
              </Button>
            </form>
          </Form>

          {/* Password Requirements */}
          <div className="mt-6 text-sm text-muted-foreground">
            <p className="font-medium mb-2">パスワードの要件:</p>
            <ul className="space-y-1 list-disc list-inside">
              <li>8文字以上</li>
              <li>大文字を1文字以上含む</li>
              <li>小文字を1文字以上含む</li>
              <li>数字を1文字以上含む</li>
            </ul>
          </div>
        </Card>
      </div>
    </div>
  );
}