"""
Stripe API クライアント設定
最新SDK (stripe==12.2.0) 対応版
"""

import json
import logging
from typing import Any, Dict, List, Optional

import stripe
from fastapi import HTTPException, Request

from .config import settings

logger = logging.getLogger(__name__)

# Stripe API設定
stripe.api_key = settings.stripe_secret_key


class StripeClient:
    """Stripe API クライアント"""

    def __init__(self):
        """Stripe クライアントの初期化"""
        if not settings.stripe_secret_key or settings.stripe_secret_key.startswith(
            "placeholder"
        ):
            logger.warning("Stripe secret key not configured properly")

    async def create_customer(
        self,
        email: str,
        name: Optional[str] = None,
        metadata: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """
        Stripe顧客作成

        Args:
            email: 顧客のメールアドレス
            name: 顧客名（オプション）
            metadata: 追加のメタデータ

        Returns:
            作成された顧客情報
        """
        try:
            customer = stripe.Customer.create(
                email=email, name=name, metadata=metadata or {}
            )

            return {
                "id": customer.id,
                "email": customer.email,
                "name": customer.name,
                "created": customer.created,
            }

        except stripe.error.StripeError as e:
            logger.error(f"Stripe customer creation failed: {str(e)}")
            raise HTTPException(
                status_code=400, detail=f"Customer creation failed: {str(e)}"
            )

    async def create_checkout_session(
        self,
        customer_id: str,
        price_id: str,
        success_url: str,
        cancel_url: str,
        metadata: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """
        Stripe Checkout セッション作成

        Args:
            customer_id: Stripe顧客ID
            price_id: 価格ID（pro/unlimited）
            success_url: 成功時のリダイレクトURL
            cancel_url: キャンセル時のリダイレクトURL
            metadata: 追加のメタデータ

        Returns:
            チェックアウトセッション情報
        """
        try:
            session = stripe.checkout.Session.create(
                customer=customer_id,
                payment_method_types=["card"],
                line_items=[
                    {
                        "price": price_id,
                        "quantity": 1,
                    }
                ],
                mode="subscription",
                success_url=success_url,
                cancel_url=cancel_url,
                metadata=metadata or {},
                allow_promotion_codes=True,
                billing_address_collection="auto",
                # 2025年新機能: Enhanced Payment Element
                payment_method_configuration=(
                    settings.stripe_payment_method_config
                    if hasattr(settings, "stripe_payment_method_config")
                    else None
                ),
            )

            return {
                "id": session.id,
                "url": session.url,
                "customer": session.customer,
                "subscription": session.subscription,
            }

        except stripe.error.StripeError as e:
            logger.error(f"Checkout session creation failed: {str(e)}")
            raise HTTPException(
                status_code=400, detail=f"Checkout session creation failed: {str(e)}"
            )

    async def create_billing_portal_session(
        self, customer_id: str, return_url: str
    ) -> Dict[str, Any]:
        """
        顧客ポータルセッション作成（サブスクリプション管理用）

        Args:
            customer_id: Stripe顧客ID
            return_url: 戻り先URL

        Returns:
            ポータルセッション情報
        """
        try:
            session = stripe.billing_portal.Session.create(
                customer=customer_id, return_url=return_url
            )

            return {"id": session.id, "url": session.url}

        except stripe.error.StripeError as e:
            logger.error(f"Billing portal creation failed: {str(e)}")
            raise HTTPException(
                status_code=400, detail=f"Billing portal creation failed: {str(e)}"
            )

    async def get_customer_subscription(
        self, customer_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        顧客のサブスクリプション情報取得

        Args:
            customer_id: Stripe顧客ID

        Returns:
            サブスクリプション情報（なければNone）
        """
        try:
            subscriptions = stripe.Subscription.list(
                customer=customer_id, status="active", limit=1
            )

            if subscriptions.data:
                subscription = subscriptions.data[0]
                return {
                    "id": subscription.id,
                    "status": subscription.status,
                    "current_period_start": subscription.current_period_start,
                    "current_period_end": subscription.current_period_end,
                    "cancel_at_period_end": subscription.cancel_at_period_end,
                    "items": [
                        {
                            "price_id": item.price.id,
                            "product_id": item.price.product,
                            "quantity": item.quantity,
                        }
                        for item in subscription.items.data
                    ],
                }

            return None

        except stripe.error.StripeError as e:
            logger.error(f"Subscription retrieval failed: {str(e)}")
            return None

    async def cancel_subscription(
        self, subscription_id: str, immediately: bool = False
    ) -> Dict[str, Any]:
        """
        サブスクリプションキャンセル

        Args:
            subscription_id: サブスクリプションID
            immediately: 即座にキャンセルするか（False: 期間終了時）

        Returns:
            キャンセル結果
        """
        try:
            if immediately:
                subscription = stripe.Subscription.cancel(subscription_id)
            else:
                subscription = stripe.Subscription.modify(
                    subscription_id, cancel_at_period_end=True
                )

            return {
                "id": subscription.id,
                "status": subscription.status,
                "cancel_at_period_end": subscription.cancel_at_period_end,
                "canceled_at": subscription.canceled_at,
            }

        except stripe.error.StripeError as e:
            logger.error(f"Subscription cancellation failed: {str(e)}")
            raise HTTPException(
                status_code=400, detail=f"Cancellation failed: {str(e)}"
            )

    async def verify_webhook_signature(
        self, payload: bytes, signature_header: str
    ) -> Dict[str, Any]:
        """
        Webhook署名検証（2025年セキュリティベストプラクティス）

        Args:
            payload: Webhookペイロード
            signature_header: Stripe-Signatureヘッダー

        Returns:
            検証済みイベントデータ
        """
        try:
            event = stripe.Webhook.construct_event(
                payload=payload,
                sig_header=signature_header,
                secret=settings.stripe_webhook_secret,
            )

            # 2025年新機能: タイムスタンプ検証の強化
            # construct_eventで自動的に実行されるが、追加のログを記録
            logger.info(f"Webhook verified: {event['type']} - {event['id']}")

            return event

        except ValueError as e:
            logger.error(f"Invalid webhook payload: {str(e)}")
            raise HTTPException(status_code=400, detail="Invalid payload")
        except stripe.error.SignatureVerificationError as e:
            logger.error(f"Invalid webhook signature: {str(e)}")
            raise HTTPException(status_code=400, detail="Invalid signature")

    async def handle_webhook_event(self, event: Dict[str, Any]) -> Dict[str, str]:
        """
        Webhook イベント処理

        Args:
            event: 検証済みStripeイベント

        Returns:
            処理結果
        """
        event_type = event["type"]
        data = event["data"]["object"]

        try:
            if event_type == "checkout.session.completed":
                await self._handle_checkout_completed(data)
            elif event_type == "customer.subscription.created":
                await self._handle_subscription_created(data)
            elif event_type == "customer.subscription.updated":
                await self._handle_subscription_updated(data)
            elif event_type == "customer.subscription.deleted":
                await self._handle_subscription_deleted(data)
            elif event_type == "invoice.payment_succeeded":
                await self._handle_payment_succeeded(data)
            elif event_type == "invoice.payment_failed":
                await self._handle_payment_failed(data)
            else:
                logger.info(f"Unhandled webhook event: {event_type}")

            return {"status": "success", "event_type": event_type}

        except Exception as e:
            logger.error(f"Webhook processing failed for {event_type}: {str(e)}")
            return {"status": "error", "message": str(e)}

    async def _handle_checkout_completed(self, session: Dict[str, Any]):
        """チェックアウト完了処理"""
        customer_id = session.get("customer")
        subscription_id = session.get("subscription")

        logger.info(
            f"Checkout completed: customer={customer_id}, subscription={subscription_id}"
        )

        # TODO: データベースにサブスクリプション情報を保存
        # TODO: ユーザーのプラン情報を更新

    async def _handle_subscription_created(self, subscription: Dict[str, Any]):
        """サブスクリプション作成処理"""
        customer_id = subscription.get("customer")
        subscription_id = subscription.get("id")

        logger.info(
            f"Subscription created: {subscription_id} for customer {customer_id}"
        )

        # TODO: user_subscriptionsテーブルに挿入

    async def _handle_subscription_updated(self, subscription: Dict[str, Any]):
        """サブスクリプション更新処理"""
        subscription_id = subscription.get("id")
        status = subscription.get("status")

        logger.info(f"Subscription updated: {subscription_id} - status: {status}")

        # TODO: user_subscriptionsテーブルを更新

    async def _handle_subscription_deleted(self, subscription: Dict[str, Any]):
        """サブスクリプション削除処理"""
        subscription_id = subscription.get("id")

        logger.info(f"Subscription deleted: {subscription_id}")

        # TODO: user_subscriptionsテーブルのステータスを更新

    async def _handle_payment_succeeded(self, invoice: Dict[str, Any]):
        """支払い成功処理"""
        customer_id = invoice.get("customer")
        amount_paid = invoice.get("amount_paid")

        logger.info(f"Payment succeeded: {amount_paid} for customer {customer_id}")

        # TODO: 支払い履歴を記録

    async def _handle_payment_failed(self, invoice: Dict[str, Any]):
        """支払い失敗処理"""
        customer_id = invoice.get("customer")

        logger.error(f"Payment failed for customer {customer_id}")

        # TODO: 支払い失敗の通知処理

    def get_plan_price_id(self, plan_name: str) -> str:
        """プラン名から価格IDを取得"""
        if plan_name == "pro":
            return settings.stripe_price_id_pro
        elif plan_name == "unlimited":
            return settings.stripe_price_id_unlimited
        else:
            raise ValueError(f"Invalid plan name: {plan_name}")

    def health_check(self) -> bool:
        """
        Health check for Stripe API

        Returns:
            True if API is accessible, False otherwise
        """
        try:
            # Simple account retrieval test
            account = stripe.Account.retrieve()
            return bool(account and account.id)
        except Exception:
            return False


def get_stripe_client() -> StripeClient:
    """Get Stripe client instance"""
    return stripe_client


# グローバルクライアントインスタンス
stripe_client = StripeClient()
