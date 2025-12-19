from __future__ import annotations

from pathlib import Path
from typing import Callable, Optional

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget

from characterify.app_context import AppContext
from characterify.ui.widgets.common import Card, H1, H2, Muted


class HomePage(QWidget):
    def __init__(self, ctx: AppContext, on_start_test: Callable[[], None]) -> None:
        super().__init__()
        self.ctx = ctx
        self.on_start_test = on_start_test

        root = QVBoxLayout(self)
        root.setContentsMargins(18, 18, 18, 18)
        root.setSpacing(14)

        hero = Card()
        root.addWidget(hero)

        row = QHBoxLayout()
        hero.body.addLayout(row)

        # Left: text
        left = QVBoxLayout()
        left.setSpacing(10)
        row.addLayout(left, 3)

        left.addWidget(H1("Kenali Dirimu, Lebih Jelas."))
        left.addWidget(
            Muted(
                "Characterify membantu Anda mengeksplorasi kecenderungan kepribadian melalui beberapa tes populer "
                "(MBTI, Big Five/OCEAN, Enneagram, dan Temperament). Hasil ditampilkan dalam bentuk visual dan "
                "ringkasan yang mudah dipahami."
            )
        )

        btn = QPushButton("Mulai Tes")
        btn.setObjectName("PrimaryButton")
        btn.clicked.connect(self.on_start_test)
        left.addWidget(btn, alignment=Qt.AlignLeft)

        left.addWidget(Muted("Catatan: ini bukan diagnosis klinis—gunakan sebagai refleksi & pembelajaran."))

        # Right: brand image
        img = QLabel()
        img.setAlignment(Qt.AlignCenter)
        img.setMinimumWidth(320)
        img.setStyleSheet("background: rgba(255,255,255,0.04); border-radius: 14px;")
        row.addWidget(img, 2)

        try:
            brand = Path(__file__).resolve().parents[2] / "assets" / "brand.png"
            if brand.exists():
                pm = QPixmap(str(brand))
                img.setPixmap(pm.scaledToWidth(330, Qt.SmoothTransformation))
        except Exception:
            img.setText("Characterify")

        # Feature highlights
        features = QHBoxLayout()
        features.setSpacing(12)
        root.addLayout(features)

        for title, desc in [
            ("🧠 Hasil Terstruktur", "Ringkasan tipe, chart, dan rekomendasi pengembangan diri yang rapi."),
            ("📊 Visualisasi Skor", "Grafik membantu membaca kecenderungan dengan cepat dan jelas."),
            ("📚 Materi Belajar", "25 artikel psikologi & personality untuk memperdalam pemahaman."),
        ]:
            c = Card()
            c.body.addWidget(H2(title))
            c.body.addWidget(Muted(desc))
            features.addWidget(c)

        root.addStretch(1)
