from __future__ import annotations

import os
import sys
from pathlib import Path


def _load_qss() -> str:
    here = Path(__file__).resolve().parent
    qss_path = here / "assets" / "style.qss"
    try:
        return qss_path.read_text(encoding="utf-8")
    except Exception:
        return ""


def main() -> int:

    try:
        from PySide6.QtGui import QFont, QIcon
        from PySide6.QtWidgets import QApplication
    except Exception as exc:
        print("PySide6 belum terpasang. Install dulu:")
        print("  pip install -r requirements.txt")
        print(f"\nError: {exc}")
        return 1

    # High DPI
    os.environ.setdefault("QT_ENABLE_HIGHDPI_SCALING", "1")
    os.environ.setdefault("QT_SCALE_FACTOR_ROUNDING_POLICY", "PassThrough")

    app = QApplication(sys.argv)
    app.setApplicationName("Characterify")
    app.setFont(QFont("Segoe UI", 10))

    # Icon (optional)
    try:
        icon_path = Path(__file__).resolve().parent / "assets" / "brand.png"
        if icon_path.exists():
            app.setWindowIcon(QIcon(str(icon_path)))
    except Exception:
        pass

    # Global stylesheet
    qss = _load_qss()
    if qss:
        app.setStyleSheet(qss)

    from characterify.app_context import AppContext
    from characterify.services.articles import ArticleService
    from characterify.services.pdf_report import PdfReportService
    from characterify.services.scoring import ScoringService
    from characterify.ui.main_window import MainWindow

    ctx = AppContext(
        scoring=ScoringService(),
        articles=ArticleService(),
        pdf=PdfReportService(),
    )

    window = MainWindow(ctx=ctx)
    window.resize(1240, 760)
    window.show()

    return app.exec()


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
