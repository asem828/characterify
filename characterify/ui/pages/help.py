from __future__ import annotations

from PySide6.QtWidgets import QScrollArea, QVBoxLayout, QWidget

from characterify.app_context import AppContext
from characterify.ui.widgets.common import Card, Divider, H1, H2, Muted


class HelpPage(QWidget):
    """Halaman Bantuan (tanpa database/login)."""

    def __init__(self, ctx: AppContext) -> None:
        super().__init__()
        self.ctx = ctx

        root = QVBoxLayout(self)
        root.setContentsMargins(18, 18, 18, 18)
        root.setSpacing(12)

        root.addWidget(H1("Bantuan"))
        root.addWidget(Muted("Panduan penggunaan dan FAQ singkat."))

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.NoFrame)
        root.addWidget(scroll, 1)

        body = QWidget()
        scroll.setWidget(body)
        layout = QVBoxLayout(body)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        usage = Card()
        usage.body.addWidget(H2("Cara Menggunakan"))
        usage.body.addWidget(Muted("1) Buka menu Tes di sidebar."))
        usage.body.addWidget(Muted("2) Pilih salah satu tes, lalu baca petunjuk."))
        usage.body.addWidget(Muted("3) Jawab pertanyaan (5 pertanyaan per halaman)."))
        usage.body.addWidget(Muted("4) Klik Next sampai selesai, lalu lihat hasil dan rekomendasi."))
        usage.body.addWidget(Muted("5) Jika ingin belajar lebih lanjut, buka menu Belajar."))
        layout.addWidget(usage)

        faq = Card()
        faq.body.addWidget(H2("FAQ"))
        faq.body.addWidget(Divider())

        items = [
            ("Apakah hasil tes ini akurat?", 
             "Tes membantu memetakan kecenderungan, bukan label mutlak. Hasil bisa berubah tergantung konteks, "
             "pengalaman, dan kondisi emosional saat menjawab."),
            ("Apakah ini diagnosis klinis?", 
             "Tidak. Characterify ditujukan untuk refleksi diri dan edukasi. Untuk kebutuhan klinis, konsultasikan "
             "dengan profesional kesehatan mental."),
            ("Kenapa pakai skala 1–5?", 
             "Skala Likert memudahkan pengguna menilai tingkat kesesuaian per pernyataan, bukan memilih benar/salah."),
            ("Bagaimana cara menjawab yang benar?", 
             "Tidak ada benar/salah. Jawab jujur sesuai kebiasaan umum Anda, jangan terlalu lama berpikir."),
            ("Bagaimana jika saya ragu pada sebuah pertanyaan?", 
             "Pilih jawaban yang paling mendekati. Fokus pada pola yang sering terjadi, bukan kejadian sekali-sekali."),
        ]

        for q, a in items:
            faq.body.addWidget(H2(q))
            faq.body.addWidget(Muted(a))
            faq.body.addWidget(Divider())

        layout.addWidget(faq)
        layout.addStretch(1)
