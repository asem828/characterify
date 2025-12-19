from __future__ import annotations

from typing import Any, Callable, Dict, List, Optional

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from characterify.app_context import AppContext
from characterify.ui.widgets.common import Card, Divider, H1, H2, Muted


class ResultPage(QWidget):
    def __init__(self, ctx: AppContext, on_done: Callable[[], None]) -> None:
        super().__init__()
        self.ctx = ctx
        self.on_done = on_done
        self._payload: Dict[str, Any] = {}

        root = QVBoxLayout(self)
        root.setContentsMargins(18, 18, 18, 18)
        root.setSpacing(12)

        header = QHBoxLayout()
        self.title = H1("Hasil Tes")
        header.addWidget(self.title)
        header.addStretch(1)

        pdf_btn = QPushButton("Unduh PDF")
        pdf_btn.clicked.connect(self._download_pdf)
        header.addWidget(pdf_btn)

        done = QPushButton("Selesai")
        done.setObjectName("PrimaryButton")
        done.clicked.connect(self.on_done)
        header.addWidget(done)
        root.addLayout(header)

        root.addWidget(Muted("Ringkasan hasil dan rekomendasi pengembangan diri."))

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.NoFrame)
        root.addWidget(scroll, 1)

        body = QWidget()
        scroll.setWidget(body)
        self.body_layout = QVBoxLayout(body)
        self.body_layout.setContentsMargins(0, 0, 0, 0)
        self.body_layout.setSpacing(12)

    def show_result(self, payload: Dict[str, Any]) -> None:
        self._payload = payload or {}

        while self.body_layout.count():
            it = self.body_layout.takeAt(0)
            w = it.widget()
            if w:
                w.deleteLater()

        test_id = str(payload.get("test_id", ""))
        result_type = str(payload.get("result_type", ""))

        self.title.setText(f"Hasil Tes • {test_id.upper()}")

        # Data peserta
        respondent = payload.get("respondent") or {}
        if isinstance(respondent, dict) and respondent:
            rc = Card()
            rc.body.addWidget(H2("Data Peserta"))
            name = str(respondent.get("name", "-"))
            gender = str(respondent.get("gender", "-"))
            rc.body.addWidget(Muted(f"Nama: {name}"))
            rc.body.addWidget(Muted(f"Jenis kelamin: {gender}"))
            self.body_layout.addWidget(rc)

        # Chart card
        chart_card = Card()
        chart_card.body.addWidget(H2("Visualisasi Skor"))
        chart_card.body.addWidget(Muted("Grafik ini membantu melihat kecenderungan Anda secara cepat."))
        chart_widget = self._build_chart_widget(payload)
        chart_card.body.addWidget(chart_widget)
        self.body_layout.addWidget(chart_card)

        # Content card
        content = payload.get("content") or {}
        info = Card()
        info.body.addWidget(H2(content.get("title", "Ringkasan")))
        if content.get("subtitle"):
            info.body.addWidget(Muted(str(content.get("subtitle"))))
        info.body.addWidget(Divider())

        # Summary paragraph
        summary = str(content.get("summary_md") or "")
        if summary:
            lbl = QLabel(summary)
            lbl.setWordWrap(True)
            lbl.setTextInteractionFlags(Qt.TextSelectableByMouse)
            lbl.setStyleSheet("color: #EDEDED;")
            info.body.addWidget(lbl)

        for sec in content.get("sections", []):
            info.body.addWidget(Divider())
            info.body.addWidget(H2(str(sec.get("title", ""))))
            for item in sec.get("items", []):
                info.body.addWidget(Muted(f"• {item}"))

        self.body_layout.addWidget(info)
        self.body_layout.addStretch(1)

    def _download_pdf(self) -> None:
        if not self._payload:
            return

        default_name = "hasil_characterify.pdf"
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Simpan PDF",
            default_name,
            "PDF (*.pdf)",
        )
        if not path:
            return

        try:
            out = self.ctx.pdf.export_result(self._payload, path)
        except Exception as exc:
            from characterify.ui.widgets.dialogs import show_error

            show_error(self, "Gagal", f"Gagal membuat PDF.\n\n{exc}")
            return

        from characterify.ui.widgets.dialogs import show_info

        show_info(self, "Berhasil", f"PDF berhasil disimpan:\n{out}")

    def _build_chart_widget(self, payload: Dict[str, Any]) -> QWidget:
        try:
            from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
            from matplotlib.figure import Figure
        except Exception:
            lbl = QLabel("Matplotlib belum tersedia. Install: pip install matplotlib")
            lbl.setObjectName("Muted")
            lbl.setWordWrap(True)
            return lbl

        fig = Figure(figsize=(6, 2.6), dpi=100)
        canvas = FigureCanvas(fig)
        ax = fig.add_subplot(111)

        chart_kind = payload.get("chart_kind")
        if chart_kind == "mbti_stacked":
            self._plot_mbti(ax, payload.get("percentages", []))
        else:
            self._plot_bars(ax, payload.get("percentages", {}), payload.get("scores", {}))

        fig.tight_layout()
        canvas.setMinimumHeight(240)
        return canvas

    @staticmethod
    def _plot_mbti(ax, dims: List[Dict[str, Any]]) -> None:
        # dims: [{"a":"I","b":"E","pct_a":..,"pct_b":..,"name_a":..,"name_b":..}, ...]
        ax.clear()
        ax.set_facecolor("#181818")
        ax.tick_params(colors="#B3B3B3")
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.spines["left"].set_color("#2A2A2A")
        ax.spines["bottom"].set_color("#2A2A2A")

        labels = [f"{d['a']}/{d['b']}" for d in dims]
        a_vals = [float(d.get("pct_a", 0)) for d in dims]
        b_vals = [float(d.get("pct_b", 0)) for d in dims]

        y = list(range(len(labels)))
        ax.barh(y, a_vals, label="A", color="#1DB954")
        ax.barh(y, b_vals, left=a_vals, label="B", color="#2E2E2E")

        ax.set_yticks(y)
        ax.set_yticklabels(labels)
        ax.set_xlim(0, 100)
        ax.set_xlabel("Persentase", color="#B3B3B3")
        ax.set_title("Preferensi MBTI (4 dimensi)", color="#FFFFFF")

    @staticmethod
    def _plot_bars(ax, percentages: Any, scores: Any) -> None:
        ax.clear()
        ax.set_facecolor("#181818")
        ax.tick_params(colors="#B3B3B3")
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.spines["left"].set_color("#2A2A2A")
        ax.spines["bottom"].set_color("#2A2A2A")

        if isinstance(percentages, dict) and percentages:
            items = list(percentages.items())
            items.sort(key=lambda x: x[0])
            labels = [k for k, _ in items]
            vals = [float(v) for _, v in items]
            ax.bar(labels, vals, color="#1DB954")
            ax.set_ylabel("Persentase", color="#B3B3B3")
            ax.set_ylim(0, max(100.0, max(vals) + 10))
            ax.set_title("Distribusi Skor (Persentase)", color="#FFFFFF")
        else:
            # fallback to raw scores
            if isinstance(scores, dict) and scores:
                items = list(scores.items())
                labels = [k for k, _ in items]
                vals = [float(v) for _, v in items]
                ax.bar(labels, vals, color="#1DB954")
                ax.set_ylabel("Skor", color="#B3B3B3")
                ax.set_title("Distribusi Skor", color="#FFFFFF")
            else:
                ax.text(0.5, 0.5, "Tidak ada data chart", ha="center", va="center", color="#B3B3B3")
