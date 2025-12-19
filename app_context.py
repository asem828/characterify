from __future__ import annotations

from dataclasses import dataclass

from characterify.services.articles import ArticleService
from characterify.services.pdf_report import PdfReportService
from characterify.services.scoring import ScoringService


@dataclass
class AppContext:
    """Konteks aplikasi (tanpa database).

    Objek ini dibuat sekali saat aplikasi dijalankan, lalu dibagikan ke seluruh UI.
    """

    scoring: ScoringService
    articles: ArticleService
    pdf: PdfReportService
