from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, List
from uuid import uuid4

from chromadb import PersistentClient

from backend.app.config import Settings
from backend.app.models import MemoryItem


class MemoryService:
    def __init__(self, settings: Settings) -> None:
        self._items: list[MemoryItem] = []
        self._collection: Any | None = None
        self._use_chroma = True

        try:
            client = PersistentClient(path=settings.chroma_persist_directory)
            self._collection = client.get_or_create_collection(
                name=settings.chroma_collection_name
            )
        except Exception:
            self._use_chroma = False

    def add_memory(
        self,
        *,
        content: str,
        category: str,
        sentiment: str,
        response: str,
    ) -> MemoryItem:
        item = MemoryItem(
            id=str(uuid4()),
            content=content,
            category=category,
            sentiment=sentiment,
            response=response,
            created_at=datetime.now(timezone.utc).isoformat(),
        )

        self._items.insert(0, item)

        if self._use_chroma and self._collection is not None:
            try:
                self._collection.add(
                    ids=[item.id],
                    documents=[content],
                    metadatas=[
                        {
                            "category": category,
                            "sentiment": sentiment,
                            "response": response,
                            "created_at": item.created_at,
                        }
                    ],
                )
            except Exception:
                self._use_chroma = False

        return item

    def query(self, text: str, limit: int = 3) -> List[MemoryItem]:
        if self._use_chroma and self._collection is not None:
            try:
                result = self._collection.query(query_texts=[text], n_results=limit)
                ids = result.get("ids", [[]])[0]
                docs = result.get("documents", [[]])[0]
                metas = result.get("metadatas", [[]])[0]
                distances = result.get("distances", [[]])[0]
                memories: list[MemoryItem] = []
                for item_id, doc, meta, distance in zip(ids, docs, metas, distances):
                    memories.append(
                        MemoryItem(
                            id=item_id,
                            content=doc,
                            category=str(meta.get("category", "unknown")),
                            sentiment=str(meta.get("sentiment", "neutral")),
                            response=str(meta.get("response", "")),
                            created_at=str(meta.get("created_at", "")),
                            similarity=1 - float(distance) if distance is not None else None,
                        )
                    )
                if memories:
                    return memories
            except Exception:
                self._use_chroma = False

        query_terms = set(text.lower().split())
        ranked: list[tuple[float, MemoryItem]] = []
        for item in self._items:
            item_terms = set(item.content.lower().split())
            overlap = len(query_terms & item_terms)
            score = overlap / max(len(query_terms), 1)
            ranked.append((score, item))
        ranked.sort(key=lambda entry: entry[0], reverse=True)
        return [
            item.model_copy(update={"similarity": score})
            for score, item in ranked[:limit]
            if score > 0 or not text.strip()
        ]

    def list_items(self, limit: int = 20) -> List[MemoryItem]:
        return self._items[:limit]
