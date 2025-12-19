from __future__ import annotations

from dataclasses import dataclass

from characterify.services.articles import ArticleService
from characterify.services.scoring import ScoringService


@dataclass
class AppContext:

    scoring: ScoringService
    articles: ArticleService
