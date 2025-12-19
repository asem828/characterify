from __future__ import annotations

from typing import Callable, List

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from characterify.app_context import AppContext
from characterify.services.articles import Article
from characterify.ui.widgets.common import Card, Divider, H1, H2, Muted


class LearnPage(QWidget):
   

    def __init__(self, ctx: AppContext, on_open_article: Callable[[str], None]) -> None:
        super().__init__()
        self.ctx = ctx
        self.on_open_article = on_open_article

        root = QVBoxLayout(self)
        root.setContentsMargins(18, 18, 18, 18)
        root.setSpacing(12)

        root.addWidget(H1("Belajar"))
        root.addWidget(Muted("Materi pembelajaran tentang personality dan psikologi. Gunakan pencarian untuk menemukan topik."))

        top = QHBoxLayout()
        self.search = QLineEdit()
        self.search.setPlaceholderText("Cari judul atau kategori…")
        self.search.textChanged.connect(self.refresh)
        top.addWidget(self.search, 1)

        btn_clear = QPushButton("Clear")
        btn_clear.clicked.connect(lambda: self.search.setText(""))
        top.addWidget(btn_clear)

        root.addLayout(top)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.NoFrame)
        root.addWidget(scroll, 1)

        body = QWidget()
        scroll.setWidget(body)
        self.body_layout = QVBoxLayout(body)
        self.body_layout.setContentsMargins(0, 0, 0, 0)
        self.body_layout.setSpacing(12)

        self.refresh()

    def refresh(self) -> None:
        while self.body_layout.count():
            it = self.body_layout.takeAt(0)
            w = it.widget()
            if w:
                w.deleteLater()

        q = (self.search.text() or "").strip().lower()
        items: List[Article] = self.ctx.articles.list_articles()

        if q:
            items = [a for a in items if q in a.title.lower() or q in a.category.lower()]

        for a in items:
            c = Card()
            c.body.addWidget(H2(a.title))
            c.body.addWidget(Muted(f"Kategori: {a.category} • Estimasi baca: {a.read_minutes} menit"))
            c.body.addWidget(Muted(a.summary))

            row = QHBoxLayout()
            row.addStretch(1)
            b = QPushButton("Baca")
            b.setObjectName("PrimaryButton")
            b.clicked.connect(lambda _=False, aid=a.id: self.on_open_article(aid))
            row.addWidget(b)
            c.body.addLayout(row)

            self.body_layout.addWidget(c)

        self.body_layout.addStretch(1)


class ArticleReaderPage(QWidget):
    def __init__(self, ctx: AppContext, on_back: Callable[[], None]) -> None:
        super().__init__()
        self.ctx = ctx
        self.on_back = on_back

        root = QVBoxLayout(self)
        root.setContentsMargins(18, 18, 18, 18)
        root.setSpacing(12)

        header = QHBoxLayout()
        back = QPushButton("← Kembali")
        back.clicked.connect(self.on_back)
        header.addWidget(back)

        header.addStretch(1)
        root.addLayout(header)

        self.card = Card()
        root.addWidget(self.card, 1)

        self.title = H1("")
        self.card.body.addWidget(self.title)

        self.meta = Muted("")
        self.card.body.addWidget(self.meta)

        self.card.body.addWidget(Divider())

        from PySide6.QtWidgets import QTextBrowser
        self.text = QTextBrowser()
        self.text.setOpenExternalLinks(True)
        self.text.setStyleSheet(
            "QTextBrowser { background: transparent; border: none; }"
        )
        self.card.body.addWidget(self.text, 1)

    def open_article(self, article_id: str) -> None:
        a = self.ctx.articles.get(article_id)
        if not a:
            self.title.setText("Artikel tidak ditemukan")
            self.meta.setText("")
            self.text.setPlainText("")
            return

        self.title.setText(a.title)
        self.meta.setText(f"Kategori: {a.category} • Estimasi baca: {a.read_minutes} menit")
        self.text.setPlainText(a.content)
