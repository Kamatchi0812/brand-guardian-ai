from __future__ import annotations

from typing import Any

from backend.app.models import AnalysisResult, MemoryItem


class BrandAnalyzer:
    NEGATIVE_WORDS = {
        "bad",
        "worst",
        "broken",
        "hate",
        "angry",
        "scam",
        "fraud",
        "fake",
        "delay",
        "poor",
        "issue",
        "complaint",
        "refund",
        "damaged",
    }
    POSITIVE_WORDS = {"love", "great", "nice", "good", "happy", "excellent", "best"}
    MEME_WORDS = {"meme", "lol", "funny", "template", "sarcasm", "joke"}
    FAKE_NEWS_WORDS = {"fake", "rumor", "leak", "boycott", "scam", "fraud", "misleading"}
    COMPLAINT_WORDS = {"refund", "support", "issue", "broken", "late", "complaint", "angry"}

    def heuristic_analyze(
        self,
        *,
        text: str,
        has_image: bool,
        related_memories: list[MemoryItem],
    ) -> AnalysisResult:
        normalized = text.lower()
        tokens = set(normalized.split())

        sentiment = "neutral"
        if tokens & self.NEGATIVE_WORDS:
            sentiment = "negative"
        elif tokens & self.POSITIVE_WORDS:
            sentiment = "positive"

        category = "neutral"
        if tokens & self.FAKE_NEWS_WORDS:
            category = "fake_news"
        elif has_image and (tokens & self.MEME_WORDS or "meme" in normalized or "sarcasm" in normalized):
            category = "meme"
        elif tokens & self.COMPLAINT_WORDS:
            category = "complaint"

        risk_score = 0.2
        if category == "complaint":
            risk_score = 0.7
        elif category == "meme":
            risk_score = 0.6
        elif category == "fake_news":
            risk_score = 0.9
        elif sentiment == "negative":
            risk_score = 0.55

        summary = self._build_summary(category=category, sentiment=sentiment, has_image=has_image)
        reasoning = self._build_reasoning(category=category, sentiment=sentiment, related_memories=related_memories)
        suggested_response = self._build_response(category=category, sentiment=sentiment)

        return AnalysisResult(
            category=category,
            sentiment=sentiment,
            risk_score=risk_score,
            summary=summary,
            reasoning=reasoning,
            suggested_response=suggested_response,
            related_memories=related_memories,
            mode="heuristic",
        )

    def from_gemini(
        self,
        payload: dict[str, Any],
        related_memories: list[MemoryItem],
    ) -> AnalysisResult:
        category = str(payload.get("category", "neutral"))
        sentiment = str(payload.get("sentiment", "neutral"))
        risk_score = float(payload.get("risk_score", 0.2))

        return AnalysisResult(
            category=category,  # type: ignore[arg-type]
            sentiment=sentiment,  # type: ignore[arg-type]
            risk_score=max(0.0, min(1.0, risk_score)),
            summary=str(payload.get("summary", "No summary available.")),
            reasoning=str(payload.get("reasoning", "No reasoning available.")),
            suggested_response=str(
                payload.get(
                    "suggested_response",
                    self._build_response(category=category, sentiment=sentiment),
                )
            ),
            related_memories=related_memories,
            mode="gemini",
        )

    def _build_summary(self, *, category: str, sentiment: str, has_image: bool) -> str:
        image_clause = " with visual context" if has_image else ""
        return f"Detected {category.replace('_', ' ')} content with {sentiment} sentiment{image_clause}."

    def _build_reasoning(
        self,
        *,
        category: str,
        sentiment: str,
        related_memories: list[MemoryItem],
    ) -> str:
        memory_clause = ""
        if related_memories:
            memory_clause = f" Found {len(related_memories)} related past interaction(s)."
        return (
            f"The content matches patterns commonly associated with {category.replace('_', ' ')} "
            f"and carries a {sentiment} tone.{memory_clause}"
        )

    def _build_response(self, *, category: str, sentiment: str) -> str:
        if category == "complaint":
            return (
                "We’re sorry to hear about your experience. Please share your order or case details "
                "via direct message so our support team can help quickly."
            )
        if category == "fake_news":
            return (
                "We want to clarify that this information appears inaccurate. Please refer to our "
                "official channels for verified updates, and feel free to contact us with questions."
            )
        if category == "meme":
            return (
                "Thanks for sharing this post. We’re listening closely and always working to improve "
                "how people experience our brand."
            )
        if sentiment == "positive":
            return "Thanks for the support. We appreciate you sharing your experience with our brand."
        return "Thank you for sharing this. We’re monitoring feedback carefully and appreciate the context."
