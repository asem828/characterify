from __future__ import annotations

from PySide6.QtWidgets import QScrollArea, QVBoxLayout, QWidget

from characterify.app_context import AppContext
from characterify.ui.widgets.common import Card, H1, H2, Muted


class InformationPage(QWidget):
    def __init__(self, ctx: AppContext) -> None:
        super().__init__()
        self.ctx = ctx

        root = QVBoxLayout(self)
        root.setContentsMargins(18, 18, 18, 18)
        root.setSpacing(12)

        root.addWidget(H1("Informasi"))
        root.addWidget(Muted("Tentang aplikasi Characterify dan disclaimer penggunaan."))

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.NoFrame)
        root.addWidget(scroll, 1)

        body = QWidget()
        scroll.setWidget(body)
        layout = QVBoxLayout(body)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        about = Card()
        about.body.addWidget(H2("Tentang Characterify"))
        about.body.addWidget(
            Muted(
                "Characterify adalah aplikasi desktop tes kepribadian yang menyatukan beberapa model populer "
                "(MBTI, Big Five/OCEAN, Enneagram, dan 4 Temperaments) untuk membantu refleksi diri dan pembelajaran. "
                "Aplikasi ini dirancang dengan antarmuka modern agar nyaman dipakai untuk eksplorasi personal."
            )
        )
        layout.addWidget(about)

        privacy = Card()
        privacy.body.addWidget(H2("Privasi & Data"))
        privacy.body.addWidget(
            Muted(
                "Versi aplikasi ini tidak menggunakan login ataupun penyimpanan riwayat. Jawaban dan hasil hanya "
                "diproses di memori selama sesi berjalan (tidak disimpan ke database)."
            )
        )
        layout.addWidget(privacy)

        disclaimer = Card()
        disclaimer.body.addWidget(H2("Disclaimer"))
        disclaimer.body.addWidget(
            Muted(
                "Hasil tes bersifat informatif dan bukan diagnosis klinis. Gunakan hasil untuk refleksi, "
                "komunikasi, dan pengembangan diri. Jika Anda membutuhkan bantuan psikologis profesional, "
                "silakan berkonsultasi dengan psikolog/psikiater."
            )
        )
        layout.addWidget(disclaimer)

        version = Card()
        version.body.addWidget(H2("Versi"))
        version.body.addWidget(Muted("Characterify Simplified v2 • PySide6"))
        layout.addWidget(version)

        layout.addStretch(1)
