from __future__ import annotations

import base64
import json
from typing import Any

import google.generativeai as genai

from backend.app.config import Settings


class GeminiClient:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._model = None
        self._enabled = False

        try:
            

            genai.configure(api_key=settings.google_api_key)

            model = genai.GenerativeModel("gemini-1.0-pro")

            self._enabled = True

            print("✅ Gemini Model Loaded Successfully")

        except Exception as e:
            print("❌ Gemini Error:", e)
            self._enabled = False
            self._model = None

    @property
    def enabled(self) -> bool:
        return self._enabled and self._model is not None

    def analyze(
        self,
        *,
        text: str,
        image_bytes: bytes | None,
        related_memories: list[dict[str, Any]],
    ) -> dict[str, Any]:

        if not self.enabled:
            raise RuntimeError("Gemini not enabled")

        prompt = {
            "task": "Analyze brand-related social content and classify risk.",
            "requirements": {
                "category": ["complaint", "meme", "fake_news", "neutral"],
                "sentiment": ["positive", "neutral", "negative"],
                "risk_score": "0 to 1",
                "summary": "short summary",
                "reasoning": "brief explanation",
                "suggested_response": "empathetic and concise response",
            },
            "content": text,
            "related_memories": related_memories,
        }

        parts: list[Any] = [json.dumps(prompt)]

        if image_bytes:
            parts.append(
                {
                    "mime_type": "image/png",
                    "data": base64.b64encode(image_bytes).decode("utf-8"),
                }
            )

        try:
            response = self._model.generate_content(parts)
            raw_text = response.text.strip()

            if raw_text.startswith("```"):
                raw_text = raw_text.strip("`")
                raw_text = raw_text.replace("json", "", 1).strip()

            return json.loads(raw_text)

        except Exception as e:
            print("❌ Gemini Runtime Error:", e)

            return {
                "category": "neutral",
                "sentiment": "neutral",
                "risk_score": 0.5,
                "summary": "Fallback due to Gemini error",
                "reasoning": str(e),
                "suggested_response": "We are reviewing this content.",
            }