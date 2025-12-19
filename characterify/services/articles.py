from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

from characterify.data.articles import ARTICLES


@dataclass(frozen=True)
class Article:
    id: str
    title: str
    category: str
    read_minutes: int
    summary: str
    content: str


class ArticleService:
    """Menyediakan konten artikel edukasi (offline)."""

    def list_articles(self) -> List[Article]:
        return [Article(**a) for a in ARTICLES]

    def get(self, article_id: str) -> Optional[Article]:
        for a in ARTICLES:
            if a.get("id") == article_id:
                return Article(**a)
        return None
