import Link from "next/link";

import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";

export default function DesignTestPage() {
  return (
    <div className="bg-background min-h-screen space-y-8 p-8">
      <div className="mx-auto max-w-4xl">
        {/* Header */}
        <div className="mb-12 space-y-4 text-center">
          <h1 className="text-foreground text-4xl font-bold">
            Reply Pass Design System
          </h1>
          <p className="text-muted-foreground text-lg">
            デザインシステムのテストページ
          </p>
        </div>

        {/* Color Palette */}
        <section className="space-y-6">
          <h2 className="text-2xl font-semibold">カラーパレット</h2>
          <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
            <div className="case-card">
              <div className="bg-primary mb-3 h-16 w-full rounded-lg"></div>
              <p className="font-medium">Primary</p>
              <p className="text-muted-foreground text-sm">--primary</p>
            </div>
            <div className="case-card">
              <div className="bg-secondary mb-3 h-16 w-full rounded-lg"></div>
              <p className="font-medium">Secondary</p>
              <p className="text-muted-foreground text-sm">--secondary</p>
            </div>
            <div className="case-card">
              <div className="bg-success mb-3 h-16 w-full rounded-lg"></div>
              <p className="font-medium">Success</p>
              <p className="text-muted-foreground text-sm">--success</p>
            </div>
            <div className="case-card">
              <div className="bg-warning mb-3 h-16 w-full rounded-lg"></div>
              <p className="font-medium">Warning</p>
              <p className="text-muted-foreground text-sm">--warning</p>
            </div>
          </div>
        </section>

        {/* Status Badges */}
        <section className="space-y-6">
          <h2 className="text-2xl font-semibold">ステータスバッジ</h2>
          <div className="flex flex-wrap gap-4">
            <span className="status-badge success">完了</span>
            <span className="status-badge warning">警告</span>
            <span className="status-badge error">エラー</span>
            <span className="status-badge info">情報</span>
          </div>
        </section>

        {/* Reply Cards */}
        <section className="space-y-6">
          <h2 className="text-2xl font-semibold">返信カード</h2>
          <div className="grid gap-4 md:grid-cols-2">
            <div className="reply-card">
              <h3 className="mb-2 font-medium">丁寧な返信</h3>
              <p className="text-muted-foreground mb-3 text-sm">
                承知いたしました。会議室Aで問題ございません。
              </p>
              <Button size="sm" variant="outline">
                選択する
              </Button>
            </div>
            <div className="reply-card">
              <h3 className="mb-2 font-medium">カジュアルな返信</h3>
              <p className="text-muted-foreground mb-3 text-sm">
                了解です！会議室Aで大丈夫ですよ〜
              </p>
              <Button size="sm" variant="outline">
                選択する
              </Button>
            </div>
          </div>
        </section>

        {/* Typography */}
        <section className="space-y-6">
          <h2 className="text-2xl font-semibold">タイポグラフィ</h2>
          <Card className="space-y-4 p-6">
            <h1 className="text-4xl">見出し1 (H1)</h1>
            <h2 className="text-3xl">見出し2 (H2)</h2>
            <h3 className="text-2xl">見出し3 (H3)</h3>
            <h4 className="text-xl">見出し4 (H4)</h4>
            <p className="text-base">
              これは本文のテキストです。Interフォントが適用されているはずです。
              日本語と英語が混在したテキストでも美しく表示されることを確認します。
            </p>
            <p className="text-muted-foreground text-sm">
              補足テキスト・キャプション用のスタイルです。
            </p>
          </Card>
        </section>

        {/* Buttons */}
        <section className="space-y-6">
          <h2 className="text-2xl font-semibold">ボタン</h2>
          <div className="flex flex-wrap gap-4">
            <Button>プライマリボタン</Button>
            <Button variant="secondary">セカンダリボタン</Button>
            <Button variant="outline">アウトラインボタン</Button>
            <Button variant="ghost">ゴーストボタン</Button>
          </div>
        </section>

        {/* New Components */}
        <section className="space-y-6">
          <h2 className="text-2xl font-semibold">新しいコンポーネント</h2>
          <div className="grid gap-4 md:grid-cols-2">
            <Card className="p-6">
              <h3 className="mb-3 text-lg font-semibold">
                パスワード強度インジケーター
              </h3>
              <p className="text-muted-foreground mb-4 text-sm">
                リアルタイムパスワード強度評価とUX最適化
              </p>
              <Button asChild variant="outline">
                <Link href="/design-test/password">デモを見る</Link>
              </Button>
            </Card>

            <Card className="p-6">
              <h3 className="mb-3 text-lg font-semibold">
                サインアップフォーム例
              </h3>
              <p className="text-muted-foreground mb-4 text-sm">
                React Hook Form統合とバリデーション
              </p>
              <Button asChild variant="outline">
                <Link href="/design-test/signup-form">デモを見る</Link>
              </Button>
            </Card>
          </div>
        </section>
      </div>
    </div>
  );
}
