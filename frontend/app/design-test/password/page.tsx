/**
 * Password Strength Indicator Test Page
 * Demonstrates various password strength scenarios and component usage
 *
 * @description Test page for password strength indicator component
 * @route /design-test/password
 */

"use client";

import { useState } from "react";

import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  PasswordStrength,
  PasswordStrengthCompact,
} from "@/components/ui/password-strength";

export default function PasswordTestPage() {
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");

  // Test scenarios for demonstration
  const testPasswords = [
    { label: "非常に弱い", value: "123" },
    { label: "弱い", value: "password" },
    { label: "普通", value: "Password123" },
    { label: "強い", value: "MyStr0ng!Pass" },
    { label: "非常に強い", value: "MyVeryStr0ng!P@ssw0rd2024" },
  ];

  return (
    <div className="container mx-auto max-w-4xl px-4 py-8">
      <div className="space-y-8">
        {/* Header */}
        <div className="space-y-2 text-center">
          <h1 className="text-foreground text-3xl font-bold">
            パスワード強度インジケーター
          </h1>
          <p className="text-muted-foreground">
            リアルタイムパスワード強度評価とUXベストプラクティス
          </p>
        </div>

        {/* Interactive Demo */}
        <Card className="p-6">
          <div className="space-y-6">
            <h2 className="text-xl font-semibold">インタラクティブデモ</h2>

            <div className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="test-password">
                  パスワードを入力して強度を確認
                </Label>
                <Input
                  id="test-password"
                  type="password"
                  placeholder="パスワードを入力してください"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="text-base"
                />
              </div>

              <PasswordStrength password={password} />
            </div>
          </div>
        </Card>

        {/* Password Confirmation Example */}
        <Card className="p-6">
          <div className="space-y-6">
            <h2 className="text-xl font-semibold">パスワード確認フォーム例</h2>

            <div className="grid gap-4 md:grid-cols-2">
              <div className="space-y-2">
                <Label htmlFor="password-1">パスワード</Label>
                <Input
                  id="password-1"
                  type="password"
                  placeholder="新しいパスワード"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                />
                <PasswordStrength password={password} showCriteria={false} />
              </div>

              <div className="space-y-2">
                <Label htmlFor="password-2">パスワード確認</Label>
                <Input
                  id="password-2"
                  type="password"
                  placeholder="パスワードを再入力"
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                />
                {confirmPassword && (
                  <div className="text-sm">
                    {password === confirmPassword ? (
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
              </div>
            </div>
          </div>
        </Card>

        {/* Test Scenarios */}
        <Card className="p-6">
          <div className="space-y-6">
            <h2 className="text-xl font-semibold">テストシナリオ</h2>
            <p className="text-muted-foreground">
              様々な強度のパスワード例をクリックして試してください
            </p>

            <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
              {testPasswords.map((test, index) => (
                <Button
                  key={index}
                  variant="outline"
                  onClick={() => setPassword(test.value)}
                  className="h-auto justify-start p-4 text-left"
                >
                  <div className="w-full space-y-2">
                    <div className="font-medium">{test.label}</div>
                    <div className="text-muted-foreground font-mono text-sm">
                      "{test.value}"
                    </div>
                    <PasswordStrengthCompact
                      password={test.value}
                      className="mt-2"
                    />
                  </div>
                </Button>
              ))}
            </div>
          </div>
        </Card>

        {/* Compact Version Demo */}
        <Card className="p-6">
          <div className="space-y-6">
            <h2 className="text-xl font-semibold">コンパクト版</h2>
            <p className="text-muted-foreground">
              スペースが限られた場所での使用例
            </p>

            <div className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="compact-password">
                  パスワード（コンパクト表示）
                </Label>
                <div className="space-y-2">
                  <Input
                    id="compact-password"
                    type="password"
                    placeholder="パスワード"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                  />
                  <PasswordStrengthCompact password={password} />
                </div>
              </div>
            </div>
          </div>
        </Card>

        {/* Features Overview */}
        <Card className="p-6">
          <div className="space-y-6">
            <h2 className="text-xl font-semibold">実装機能</h2>

            <div className="grid gap-4 md:grid-cols-2">
              <div className="space-y-3">
                <h3 className="font-medium">UX機能</h3>
                <ul className="text-muted-foreground space-y-1 text-sm">
                  <li>✓ リアルタイム強度評価</li>
                  <li>✓ 視覚的プログレスバー</li>
                  <li>✓ 詳細な要件チェックリスト</li>
                  <li>✓ 改善のためのヒント表示</li>
                  <li>✓ レスポンシブデザイン</li>
                  <li>✓ ダークモード対応</li>
                </ul>
              </div>

              <div className="space-y-3">
                <h3 className="font-medium">アクセシビリティ</h3>
                <ul className="text-muted-foreground space-y-1 text-sm">
                  <li>✓ WCAG 2.1 AA準拠</li>
                  <li>✓ スクリーンリーダー対応</li>
                  <li>✓ ARIA属性の適切な使用</li>
                  <li>✓ キーボードナビゲーション</li>
                  <li>✓ 色覚異常への配慮</li>
                  <li>✓ 十分なコントラスト比</li>
                </ul>
              </div>
            </div>
          </div>
        </Card>

        {/* Technical Details */}
        <Card className="p-6">
          <div className="space-y-6">
            <h2 className="text-xl font-semibold">技術仕様</h2>

            <div className="grid gap-6 md:grid-cols-2">
              <div>
                <h3 className="mb-3 font-medium">評価アルゴリズム</h3>
                <ul className="text-muted-foreground space-y-1 text-sm">
                  <li>• 長さ要件（8文字以上必須、12文字以上推奨）</li>
                  <li>• 文字種類の多様性（大文字、小文字、数字、記号）</li>
                  <li>• エントロピー計算による複雑性評価</li>
                  <li>• NIST SP 800-63B準拠のセキュリティ基準</li>
                  <li>• OWASP 2024パスワードガイドライン対応</li>
                </ul>
              </div>

              <div>
                <h3 className="mb-3 font-medium">パフォーマンス</h3>
                <ul className="text-muted-foreground space-y-1 text-sm">
                  <li>• useMemoによる計算最適化</li>
                  <li>• スムーズなアニメーション（300ms）</li>
                  <li>• クライアントサイド処理のみ</li>
                  <li>• TypeScript完全対応</li>
                  <li>• 軽量（バンドルサイズ最小化）</li>
                </ul>
              </div>
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
