/**
 * Signup Form Example with Password Strength
 * Demonstrates integration with React Hook Form and Zod validation
 *
 * @description Complete signup form with password strength validation
 * @route /design-test/signup-form
 */

"use client";

import { zodResolver } from "@hookform/resolvers/zod";
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
import { signUpSchema, type SignUpFormData } from "@/lib/validations/auth";

export default function SignupFormTestPage() {
  const [isSubmitting, setIsSubmitting] = useState(false);

  const form = useForm<SignUpFormData>({
    resolver: zodResolver(signUpSchema),
    mode: "onChange", // Real-time validation for better UX
    defaultValues: {
      email: "",
      password: "",
      confirmPassword: "",
      terms: false,
    },
  });

  const onSubmit = async (data: SignUpFormData) => {
    setIsSubmitting(true);

    // Simulate API call
    await new Promise((resolve) => setTimeout(resolve, 2000));

    // eslint-disable-next-line no-console
    console.log("Sign up data:", data);
    // eslint-disable-next-line no-alert
    alert("サインアップが完了しました！（テストモード）");

    setIsSubmitting(false);
  };

  const watchedPassword = form.watch("password");

  return (
    <div className="container mx-auto max-w-2xl px-4 py-8">
      <div className="space-y-8">
        {/* Header */}
        <div className="space-y-2 text-center">
          <h1 className="text-foreground text-3xl font-bold">
            サインアップフォーム
          </h1>
          <p className="text-muted-foreground">
            パスワード強度インジケーター統合デモ
          </p>
        </div>

        {/* Signup Form */}
        <Card className="p-6">
          <Form {...form}>
            <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
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
                        disabled={isSubmitting}
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
                        placeholder="新しいパスワードを入力"
                        autoComplete="new-password"
                        disabled={isSubmitting}
                        showStrengthIndicator={true}
                        compactStrength={false}
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
                        disabled={isSubmitting}
                        showStrengthIndicator={false}
                        {...field}
                      />
                    </FormControl>
                    <FormMessage />
                    {/* Password Match Indicator */}
                    {field.value && watchedPassword && (
                      <div className="mt-1 text-sm">
                        {watchedPassword === field.value ? (
                          <span className="flex items-center gap-1 text-green-600">
                            ✓ パスワードが一致しています
                          </span>
                        ) : (
                          <span className="flex items-center gap-1 text-red-600">
                            ✗ パスワードが一致しません
                          </span>
                        )}
                      </div>
                    )}
                  </FormItem>
                )}
              />

              {/* Terms Checkbox */}
              <FormField
                control={form.control}
                name="terms"
                render={({ field }) => (
                  <FormItem className="flex flex-row items-start space-y-0 space-x-3">
                    <FormControl>
                      <Checkbox
                        checked={field.value}
                        onCheckedChange={field.onChange}
                        disabled={isSubmitting}
                      />
                    </FormControl>
                    <div className="space-y-1 leading-none">
                      <FormLabel className="cursor-pointer text-sm font-normal">
                        利用規約とプライバシーポリシーに同意します
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
                disabled={isSubmitting || !form.formState.isValid}
              >
                {isSubmitting ? "アカウント作成中..." : "アカウントを作成"}
              </Button>
            </form>
          </Form>
        </Card>

        {/* Form State Debug Info */}
        <Card className="p-4">
          <h3 className="mb-3 font-medium">フォーム状態（デバッグ用）</h3>
          <div className="space-y-2 text-sm">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <span className="font-medium">有効性:</span>{" "}
                <span
                  className={
                    form.formState.isValid ? "text-green-600" : "text-red-600"
                  }
                >
                  {form.formState.isValid ? "有効" : "無効"}
                </span>
              </div>
              <div>
                <span className="font-medium">エラー数:</span>{" "}
                <span>{Object.keys(form.formState.errors).length}</span>
              </div>
            </div>

            {Object.keys(form.formState.errors).length > 0 && (
              <div className="mt-3">
                <span className="font-medium">エラー:</span>
                <ul className="mt-1 space-y-1">
                  {Object.entries(form.formState.errors).map(
                    ([field, error]) => (
                      <li key={field} className="text-red-600">
                        • {field}: {error?.message}
                      </li>
                    )
                  )}
                </ul>
              </div>
            )}

            <div className="mt-3 border-t pt-3">
              <span className="font-medium">現在の値:</span>
              <pre className="bg-muted mt-1 overflow-auto rounded p-2 text-xs">
                {JSON.stringify(form.getValues(), null, 2)}
              </pre>
            </div>
          </div>
        </Card>

        {/* Alternative Compact Version */}
        <Card className="p-6">
          <h3 className="mb-4 font-medium">コンパクト版の例</h3>
          <div className="space-y-4">
            <div className="space-y-2">
              <FormLabel>パスワード（コンパクト表示）</FormLabel>
              <PasswordInputWithStrength
                placeholder="パスワード"
                showStrengthIndicator={true}
                compactStrength={true}
                value={watchedPassword}
                onChange={(e) => form.setValue("password", e.target.value)}
              />
            </div>
          </div>
        </Card>

        {/* Integration Guide */}
        <Card className="p-6">
          <h3 className="mb-4 font-medium">統合ガイド</h3>
          <div className="space-y-4 text-sm">
            <div>
              <h4 className="font-medium">基本的な使用方法:</h4>
              <pre className="bg-muted mt-2 overflow-auto rounded p-3 text-xs">
                {`<PasswordInputWithStrength
  placeholder="パスワードを入力"
  showStrengthIndicator={true}
  compactStrength={false}
  showToggle={true}
  {...field}
/>`}
              </pre>
            </div>

            <div>
              <h4 className="font-medium">主要なプロパティ:</h4>
              <ul className="mt-2 space-y-1">
                <li>
                  • <code>showStrengthIndicator</code>:
                  強度インジケーターの表示/非表示
                </li>
                <li>
                  • <code>compactStrength</code>: コンパクト表示モード
                </li>
                <li>
                  • <code>showToggle</code>: パスワード表示/非表示ボタン
                </li>
                <li>
                  • <code>strengthClassName</code>:
                  強度インジケーターのカスタムスタイル
                </li>
              </ul>
            </div>
          </div>
        </Card>

        {/* Navigation */}
        <div className="text-center">
          <Button asChild variant="outline">
            <a href="/design-test">← デザインテストに戻る</a>
          </Button>
        </div>
      </div>
    </div>
  );
}
