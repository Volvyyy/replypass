"""
Google Gemini API クライアント設定
新SDK (google-genai) 対応版
"""

import asyncio
import logging
from typing import Any, Dict, List, Optional

from google import genai

from .config import settings

logger = logging.getLogger(__name__)


class GeminiClient:
    """Google Gemini API クライアント"""

    def __init__(self):
        """Geminiクライアントの初期化"""
        self.client = genai.Client(api_key=settings.gemini_api_key)

    async def generate_content(
        self,
        prompt: str,
        model: Optional[str] = None,
        max_tokens: int = 1000,
        temperature: float = 0.7,
    ) -> str:
        """
        コンテンツ生成（基本機能）

        Args:
            prompt: 生成用プロンプト
            model: モデル名（指定なしでデフォルト）
            max_tokens: 最大トークン数
            temperature: 生成の創造性（0.0-1.0）

        Returns:
            生成されたテキスト
        """
        try:
            # モデル選択ロジック
            selected_model = model or settings.default_gemini_model

            # API呼び出し
            response = await asyncio.to_thread(
                self.client.models.generate_content,
                model=selected_model,
                contents=[prompt],
                config=genai.GenerateContentConfig(
                    max_output_tokens=max_tokens, temperature=temperature
                ),
            )

            # レスポンス処理
            if response.candidates and len(response.candidates) > 0:
                content = response.candidates[0].content
                if content.parts and len(content.parts) > 0:
                    return content.parts[0].text

            logger.warning("Gemini API returned empty response")
            return ""

        except Exception as e:
            logger.error(f"Gemini API error: {str(e)}")
            raise

    async def generate_reply_suggestions(
        self,
        conversation_context: str,
        persona_info: Dict[str, Any],
        user_goal: Optional[str] = None,
        user_plan: str = "free",
    ) -> List[Dict[str, str]]:
        """
        返信提案生成（Reply Pass専用）

        Args:
            conversation_context: 会話の文脈
            persona_info: ペルソナ情報
            user_goal: ユーザーの目的（オプション）
            user_plan: ユーザープラン（free/pro/unlimited）

        Returns:
            返信提案のリスト
        """
        try:
            # プラン別モデル選択
            model = self._select_model_by_plan(user_plan)

            # プロンプト構築
            prompt = self._build_reply_prompt(
                conversation_context, persona_info, user_goal
            )

            # 生成実行
            response_text = await self.generate_content(
                prompt=prompt, model=model, max_tokens=800, temperature=0.8
            )

            # レスポンス解析
            suggestions = self._parse_reply_suggestions(response_text)

            return suggestions

        except Exception as e:
            logger.error(f"Reply suggestion generation failed: {str(e)}")
            return self._fallback_suggestions()

    async def analyze_persona(
        self, reference_texts: List[str], user_plan: str = "free"
    ) -> Dict[str, Any]:
        """
        ペルソナ分析（AI自動分析）

        Args:
            reference_texts: 参考テキストのリスト
            user_plan: ユーザープラン

        Returns:
            分析結果辞書
        """
        try:
            # プラン別モデル選択（高品質分析）
            model = (
                settings.high_quality_gemini_model
                if user_plan != "free"
                else settings.default_gemini_model
            )

            # プロンプト構築
            prompt = self._build_persona_analysis_prompt(reference_texts)

            # 分析実行
            response_text = await self.generate_content(
                prompt=prompt,
                model=model,
                max_tokens=1500,
                temperature=0.3,  # 分析は創造性低めで正確に
            )

            # 結果解析
            analysis = self._parse_persona_analysis(response_text)

            return analysis

        except Exception as e:
            logger.error(f"Persona analysis failed: {str(e)}")
            return self._fallback_persona_analysis()

    async def extract_text_from_image(
        self, image_data: bytes, context_hint: Optional[str] = None
    ) -> str:
        """
        画像からテキスト抽出（OCR機能）

        Args:
            image_data: 画像のバイナリデータ
            context_hint: 抽出のヒント（会話アプリ名など）

        Returns:
            抽出されたテキスト
        """
        try:
            # OCR専用モデル使用
            model = settings.ocr_gemini_model

            # プロンプト構築
            prompt = self._build_ocr_prompt(context_hint)

            # 画像付きコンテンツ生成
            response = await asyncio.to_thread(
                self.client.models.generate_content,
                model=model,
                contents=[prompt, {"mime_type": "image/jpeg", "data": image_data}],
            )

            # OCR結果処理
            if response.candidates and len(response.candidates) > 0:
                content = response.candidates[0].content
                if content.parts and len(content.parts) > 0:
                    return content.parts[0].text

            return ""

        except Exception as e:
            logger.error(f"OCR extraction failed: {str(e)}")
            return ""

    def _select_model_by_plan(self, user_plan: str) -> str:
        """プラン別モデル選択"""
        if user_plan == "unlimited":
            return settings.high_quality_gemini_model
        elif user_plan == "pro":
            return settings.default_gemini_model
        else:  # free
            return settings.default_gemini_model

    def _build_reply_prompt(
        self, context: str, persona: Dict[str, Any], goal: Optional[str]
    ) -> str:
        """返信生成用プロンプト構築"""
        casualness = persona.get("casualness_level", 5)
        emoji_usage = persona.get("emoji_usage", "moderate")

        goal_text = f"\n\n返信の目的: {goal}" if goal else ""

        return f"""
あなたは以下のペルソナでメッセージの返信を生成してください。

## ペルソナ設定
- カジュアルさレベル: {casualness}/10
- 絵文字使用頻度: {emoji_usage}
- コミュニケーションスタイル: {persona.get('communication_style', '自然')}

## 会話の文脈
{context}{goal_text}

## 指示
上記のペルソナに合わせて、3種類の返信案を生成してください：
1. 【丁寧】: より礼儀正しい返信
2. 【標準】: バランスの取れた返信  
3. 【カジュアル】: よりフランクな返信

各返信は JSON 形式で以下のように出力してください：
```json
[
  {{"category": "polite", "text": "返信内容1"}},
  {{"category": "standard", "text": "返信内容2"}},
  {{"category": "casual", "text": "返信内容3"}}
]
```
"""

    def _build_persona_analysis_prompt(self, texts: List[str]) -> str:
        """ペルソナ分析用プロンプト構築"""
        combined_text = "\n\n---\n\n".join(texts)

        return f"""
以下のテキストサンプルから、筆者の特徴を詳細に分析してください。

## 分析項目
1. 性格・価値観
   - 基本的な性格特性（外向的/内向的、論理的/感情的など）
   - 重視する価値観
   - コミュニケーションスタイル

2. 言語的特徴
   - よく使う表現・口癖
   - 文体（です・ます調/だ・である調/カジュアル）
   - 絵文字・顔文字の使用傾向
   - 句読点の使い方

3. 思考パターン
   - 論理展開の特徴
   - 話題の選び方
   - 相手への配慮の仕方

## サンプルテキスト
{combined_text}

## 出力形式
JSON形式で、各項目を構造化して出力してください：
```json
{{
  "personality": {{
    "traits": ["特性1", "特性2"],
    "values": ["価値観1", "価値観2"],
    "communication_style": "スタイル説明"
  }},
  "language": {{
    "common_expressions": ["表現1", "表現2"],
    "formality_level": "formal/casual/mixed",
    "emoji_usage": "frequent/moderate/rare",
    "punctuation_style": "説明"
  }},
  "thinking_patterns": {{
    "logic_style": "説明",
    "topic_preference": "説明",
    "consideration_level": "説明"
  }}
}}
```
"""

    def _build_ocr_prompt(self, context_hint: Optional[str]) -> str:
        """OCR用プロンプト構築"""
        hint_text = f"\n\nコンテキスト: {context_hint}" if context_hint else ""

        return f"""
この画像から会話のテキストを正確に抽出してください。

## 抽出ルール
1. 発言者を明確に区別してください
2. 時刻情報があれば含めてください
3. スタンプや画像の場合は [スタンプ] や [画像] と記載してください
4. 読み取れない文字は [不明] と記載してください

## 出力形式
発言者: メッセージ内容
の形式で、時系列順に出力してください。{hint_text}
"""

    def _parse_reply_suggestions(self, response_text: str) -> List[Dict[str, str]]:
        """返信提案のパース"""
        try:
            import json

            # JSONブロックを抽出
            start = response_text.find("[")
            end = response_text.rfind("]") + 1
            if start != -1 and end != 0:
                json_text = response_text[start:end]
                suggestions = json.loads(json_text)
                return suggestions
        except:
            pass

        return self._fallback_suggestions()

    def _parse_persona_analysis(self, response_text: str) -> Dict[str, Any]:
        """ペルソナ分析のパース"""
        try:
            import json

            start = response_text.find("{")
            end = response_text.rfind("}") + 1
            if start != -1 and end != 0:
                json_text = response_text[start:end]
                analysis = json.loads(json_text)
                return analysis
        except:
            pass

        return self._fallback_persona_analysis()

    def _fallback_suggestions(self) -> List[Dict[str, str]]:
        """フォールバック用の返信提案"""
        return [
            {
                "category": "polite",
                "text": "ありがとうございます。検討させていただきます。",
            },
            {"category": "standard", "text": "承知しました。"},
            {"category": "casual", "text": "了解です！"},
        ]

    def _fallback_persona_analysis(self) -> Dict[str, Any]:
        """フォールバック用のペルソナ分析"""
        return {
            "personality": {
                "traits": ["標準的", "バランス型"],
                "values": ["コミュニケーション重視"],
                "communication_style": "自然体",
            },
            "language": {
                "common_expressions": [],
                "formality_level": "mixed",
                "emoji_usage": "moderate",
                "punctuation_style": "標準的",
            },
            "thinking_patterns": {
                "logic_style": "バランス型",
                "topic_preference": "相手に合わせる",
                "consideration_level": "適度",
            },
        }


    async def health_check(self) -> bool:
        """
        Health check for Gemini API
        
        Returns:
            True if API is accessible, False otherwise
        """
        try:
            # Simple test generation request
            response = await self.generate_content("Hello", max_tokens=10, temperature=0.1)
            return bool(response.strip())
        except Exception:
            return False


def get_gemini_client() -> GeminiClient:
    """Get Gemini client instance"""
    return gemini_client


# グローバルクライアントインスタンس
gemini_client = GeminiClient()
