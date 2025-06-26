# **Reply Pass API仕様書 v1.0**

## **目次**
1. [概要](#1-概要)
2. [認証](#2-認証)
3. [共通仕様](#3-共通仕様)
4. [エンドポイント一覧](#4-エンドポイント一覧)
5. [エンドポイント詳細](#5-エンドポイント詳細)
6. [Webhookエンドポイント](#6-webhookエンドポイント)
7. [エラーハンドリング](#7-エラーハンドリング)
8. [レート制限](#8-レート制限)

## **1. 概要**

### 1.1. API基本情報
- **ベースURL**: `https://api.replypass.ai/v1`
- **プロトコル**: HTTPS only
- **データ形式**: JSON
- **文字エンコーディング**: UTF-8
- **日時形式**: ISO 8601 (UTC)
- **APIバージョニング**: URLパス (`/v1/`)

### 1.2. HTTPメソッド
- `GET`: リソースの取得
- `POST`: リソースの作成
- `PUT`: リソースの完全な更新
- `PATCH`: リソースの部分更新
- `DELETE`: リソースの削除

## **2. 認証**

### 2.1. 認証方式
Supabase Authから発行されるJWTトークンを使用

### 2.2. 認証ヘッダー
```http
Authorization: Bearer <jwt_token>
```

### 2.3. トークン取得フロー
```typescript
// Frontend実装例
const { data: { session } } = await supabase.auth.getSession();
const token = session?.access_token;

// APIリクエスト
const response = await fetch('https://api.replypass.ai/v1/cases', {
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  }
});
```

## **3. 共通仕様**

### 3.1. リクエストヘッダー
| ヘッダー名 | 必須 | 説明 |
|:---|:---:|:---|
| Authorization | Yes | Bearer token |
| Content-Type | Yes* | application/json (*POSTリクエスト時) |
| X-Request-ID | No | リクエスト追跡用ID |
| Accept-Language | No | レスポンス言語 (デフォルト: ja) |

### 3.2. レスポンスヘッダー
| ヘッダー名 | 説明 |
|:---|:---|
| X-Request-ID | リクエスト追跡用ID |
| X-RateLimit-Limit | レート制限の上限 |
| X-RateLimit-Remaining | 残りリクエスト数 |
| X-RateLimit-Reset | リセット時刻(Unix timestamp) |

### 3.3. ページネーション
```json
{
  "data": [...],
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total": 100,
    "total_pages": 5,
    "has_next": true,
    "has_prev": false
  }
}
```

### 3.4. ソート・フィルタリング
- ソート: `?sort=created_at:desc`
- フィルタ: `?status=active&created_after=2024-01-01`

## **4. エンドポイント一覧**

### 4.1. 認証関連
| メソッド | パス | 説明 |
|:---|:---|:---|
| POST | /auth/refresh | トークンリフレッシュ |
| POST | /auth/logout | ログアウト |

### 4.2. ユーザー関連
| メソッド | パス | 説明 |
|:---|:---|:---|
| GET | /users/me | 自分の情報取得 |
| PATCH | /users/me | プロフィール更新 |
| GET | /users/me/usage | 利用状況取得 |
| DELETE | /users/me | アカウント削除 |

### 4.3. ケース関連
| メソッド | パス | 説明 |
|:---|:---|:---|
| GET | /cases | ケース一覧取得 |
| POST | /cases | ケース作成 |
| GET | /cases/{id} | ケース詳細取得 |
| PATCH | /cases/{id} | ケース更新 |
| DELETE | /cases/{id} | ケース削除 |

### 4.4. ペルソナ関連
| メソッド | パス | 説明 |
|:---|:---|:---|
| GET | /cases/{id}/persona | ペルソナ取得 |
| PUT | /cases/{id}/persona | ペルソナ設定 |
| POST | /cases/{id}/persona/analyze | AI分析実行 |

### 4.5. 会話ログ関連
| メソッド | パス | 説明 |
|:---|:---|:---|
| GET | /cases/{id}/conversations | 会話ログ一覧 |
| POST | /cases/{id}/conversations | 会話ログ作成 |
| GET | /conversations/{id}/messages | メッセージ一覧 |
| POST | /conversations/{id}/messages | メッセージ追加 |
| POST | /conversations/{id}/messages/ocr | スクリーンショット解析 |

### 4.6. 返信生成関連
| メソッド | パス | 説明 |
|:---|:---|:---|
| POST | /cases/{id}/generate | 返信生成 |
| GET | /generated-replies/{id} | 生成履歴取得 |
| POST | /suggestions/{id}/send | 送信済みマーク |
| POST | /suggestions/{id}/feedback | フィードバック送信 |

### 4.7. サブスクリプション関連
| メソッド | パス | 説明 |
|:---|:---|:---|
| GET | /subscriptions/plans | プラン一覧取得 |
| GET | /subscriptions/current | 現在のサブスクリプション |
| POST | /subscriptions/checkout | Checkoutセッション作成 |
| POST | /subscriptions/cancel | サブスクリプション解約 |
| POST | /subscriptions/reactivate | サブスクリプション再開 |

## **5. エンドポイント詳細**

### 5.1. ケース作成
**POST** `/cases`

#### リクエスト
```json
{
  "name": "A社 鈴木様",
  "partner_name": "鈴木さん",
  "partner_type": "取引先",
  "my_position": "受注側",
  "conversation_purpose": "定期MTGの日程調整"
}
```

#### レスポンス (201 Created)
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "user_id": "098f6bcd-4621-3373-8ade-4e832627b4f6",
  "name": "A社 鈴木様",
  "partner_name": "鈴木さん",
  "partner_type": "取引先",
  "my_position": "受注側",
  "conversation_purpose": "定期MTGの日程調整",
  "created_at": "2024-06-01T10:00:00Z",
  "updated_at": "2024-06-01T10:00:00Z"
}
```

### 5.2. ペルソナ設定
**PUT** `/cases/{case_id}/persona`

#### リクエスト
```json
{
  "casualness_level": 3,
  "emoji_usage": "normal",
  "reference_texts": "こんにちは！今日も一日頑張りましょう〜😊\n昨日の件、確認しました。問題ないと思います！",
  "quick_settings": {
    "use_honorifics": true,
    "response_length": "medium",
    "thinking_style": "logical",
    "humor_level": 2
  }
}
```

#### レスポンス (200 OK)
```json
{
  "id": "456e7890-e89b-12d3-a456-426614174000",
  "case_id": "123e4567-e89b-12d3-a456-426614174000",
  "casualness_level": 3,
  "emoji_usage": "normal",
  "reference_texts": "こんにちは！今日も一日頑張りましょう〜😊\n昨日の件、確認しました。問題ないと思います！",
  "quick_settings": {
    "use_honorifics": true,
    "response_length": "medium",
    "thinking_style": "logical",
    "humor_level": 2
  },
  "created_at": "2024-06-01T10:00:00Z",
  "updated_at": "2024-06-01T10:05:00Z"
}
```

### 5.3. スクリーンショット解析
**POST** `/conversations/{conversation_id}/messages/ocr`

#### リクエスト (multipart/form-data)
```
Content-Type: multipart/form-data; boundary=----WebKitFormBoundary7MA4YWxkTrZu0gW

------WebKitFormBoundary7MA4YWxkTrZu0gW
Content-Disposition: form-data; name="images"; filename="screenshot1.png"
Content-Type: image/png

[Binary data]
------WebKitFormBoundary7MA4YWxkTrZu0gW
Content-Disposition: form-data; name="images"; filename="screenshot2.png"
Content-Type: image/png

[Binary data]
------WebKitFormBoundary7MA4YWxkTrZu0gW--
```

#### レスポンス (200 OK)
```json
{
  "messages": [
    {
      "id": "789a1234-e89b-12d3-a456-426614174000",
      "speaker": "assistant",
      "content": "お疲れ様です！明日の会議の件ですが、14時からで大丈夫でしょうか？",
      "message_timestamp": "2024-06-01T09:30:00Z",
      "metadata": {
        "extracted_from": "screenshot1.png",
        "confidence": 0.98
      }
    },
    {
      "id": "789a5678-e89b-12d3-a456-426614174000",
      "speaker": "user",
      "content": "14時了解です。場所は会議室Aでいいですか？",
      "message_timestamp": "2024-06-01T09:32:00Z",
      "metadata": {
        "extracted_from": "screenshot1.png",
        "confidence": 0.97
      }
    }
  ],
  "processing_time_ms": 2341
}
```

### 5.4. 返信生成
**POST** `/cases/{case_id}/generate`

#### リクエスト
```json
{
  "conversation_log_id": "abc12345-e89b-12d3-a456-426614174000",
  "user_goal": "会議の場所を確定させたい",
  "options": {
    "suggestion_count": 3,
    "model_override": null
  }
}
```

#### レスポンス (200 OK)
```json
{
  "generated_reply_id": "def45678-e89b-12d3-a456-426614174000",
  "suggestions": [
    {
      "id": "111a2222-e89b-12d3-a456-426614174000",
      "category": "丁寧",
      "suggestion": "承知いたしました。会議室Aで問題ございません。14時にお待ちしております。"
    },
    {
      "id": "333b4444-e89b-12d3-a456-426614174000",
      "category": "カジュアル",
      "suggestion": "はい、会議室Aで大丈夫です！14時に伺いますね〜"
    },
    {
      "id": "555c6666-e89b-12d3-a456-426614174000",
      "category": "確認重視",
      "suggestion": "会議室Aで承知しました。念のため確認ですが、6月2日（金）14時〜15時、会議室Aということでよろしいでしょうか？"
    }
  ],
  "llm_model": "gemini-2.0-flash",
  "processing_time_ms": 3456,
  "tokens_used": {
    "input": 1234,
    "output": 567
  }
}
```

### 5.5. フィードバック送信
**POST** `/suggestions/{suggestion_id}/feedback`

#### リクエスト
```json
{
  "feedback_type": "partner_reaction",
  "partner_reaction": "positive",
  "details": {
    "additional_context": "相手から「ありがとうございます」と返信がきた"
  }
}
```

#### レスポンス (200 OK)
```json
{
  "id": "777d8888-e89b-12d3-a456-426614174000",
  "reply_suggestion_id": "111a2222-e89b-12d3-a456-426614174000",
  "feedback_type": "partner_reaction",
  "created_at": "2024-06-01T11:00:00Z"
}
```

### 5.6. Checkoutセッション作成
**POST** `/subscriptions/checkout`

#### リクエスト
```json
{
  "price_id": "price_1234567890abcdef",
  "success_url": "https://app.replypass.ai/settings/subscription?success=true",
  "cancel_url": "https://app.replypass.ai/settings/subscription"
}
```

#### レスポンス (200 OK)
```json
{
  "checkout_url": "https://checkout.stripe.com/c/pay/cs_test_a1b2c3d4...",
  "session_id": "cs_test_a1b2c3d4..."
}
```

## **6. Webhookエンドポイント**

### 6.1. Stripe Webhook
**POST** `/webhooks/stripe`

#### ヘッダー
```http
Stripe-Signature: t=1614556800,v1=abc123...
```

#### イベントタイプ
- `checkout.session.completed`
- `customer.subscription.created`
- `customer.subscription.updated`
- `customer.subscription.deleted`
- `invoice.payment_succeeded`
- `invoice.payment_failed`

#### レスポンス
```json
{
  "received": true
}
```

## **7. エラーハンドリング**

### 7.1. エラーレスポンス形式
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "入力値が不正です",
    "details": {
      "field": "casualness_level",
      "constraint": "1-5の整数を指定してください"
    },
    "request_id": "req_123abc456def"
  }
}
```

### 7.2. HTTPステータスコード

| コード | 説明 | エラーコード例 |
|:---|:---|:---|
| 400 | Bad Request | VALIDATION_ERROR, INVALID_FORMAT |
| 401 | Unauthorized | INVALID_TOKEN, TOKEN_EXPIRED |
| 403 | Forbidden | INSUFFICIENT_PERMISSIONS, PLAN_LIMIT_EXCEEDED |
| 404 | Not Found | RESOURCE_NOT_FOUND |
| 409 | Conflict | DUPLICATE_RESOURCE, CONCURRENT_UPDATE |
| 422 | Unprocessable Entity | BUSINESS_LOGIC_ERROR |
| 429 | Too Many Requests | RATE_LIMIT_EXCEEDED |
| 500 | Internal Server Error | INTERNAL_ERROR |
| 502 | Bad Gateway | EXTERNAL_SERVICE_ERROR |
| 503 | Service Unavailable | SERVICE_MAINTENANCE |

### 7.3. エラーコード一覧

| エラーコード | 説明 | 対処法 |
|:---|:---|:---|
| VALIDATION_ERROR | 入力値検証エラー | エラー詳細を確認し、正しい値を送信 |
| INVALID_TOKEN | 無効なトークン | 再ログインしてトークンを更新 |
| TOKEN_EXPIRED | トークン期限切れ | リフレッシュトークンで更新 |
| PLAN_LIMIT_EXCEEDED | プラン上限超過 | プランアップグレードを検討 |
| RESOURCE_NOT_FOUND | リソースが存在しない | IDを確認 |
| RATE_LIMIT_EXCEEDED | レート制限超過 | 時間をおいて再試行 |
| INSUFFICIENT_BALANCE | 残高不足 | 支払い方法を更新 |
| OCR_FAILED | 画像解析失敗 | 画像品質を確認して再送信 |
| LLM_TIMEOUT | LLM応答タイムアウト | 再試行またはサポート連絡 |

## **8. レート制限**

### 8.1. 制限値

| エンドポイント | Free | Pro | Unlimited |
|:---|:---:|:---:|:---:|
| 返信生成 (/generate) | 5回/日 | 100回/日 | 1000回/日 |
| OCR解析 (/ocr) | 10回/日 | 100回/日 | 500回/日 |
| その他のAPI | 60回/分 | 300回/分 | 600回/分 |

### 8.2. レート制限の仕組み
- **ウィンドウ方式**: スライディングウィンドウ
- **識別単位**: ユーザーID
- **リセット**: 日次制限は日本時間0時にリセット

### 8.3. レート制限時のレスポンス
```http
HTTP/1.1 429 Too Many Requests
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 1622505600
Retry-After: 3600

{
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "API利用制限を超過しました",
    "details": {
      "limit_type": "daily",
      "reset_at": "2024-06-02T00:00:00+09:00"
    }
  }
}
```

### 8.4. ベストプラクティス
1. **指数バックオフ**: 429エラー時は指数的に待機時間を増やす
2. **ヘッダー監視**: X-RateLimit-Remainingを確認
3. **バッチ処理**: 可能な限りリクエストをまとめる
4. **キャッシュ活用**: 同じデータの重複取得を避ける

---

このAPI仕様書は、Reply PassのすべてのAPI機能を網羅しています。開発時はこの仕様書に従って実装を進めてください。