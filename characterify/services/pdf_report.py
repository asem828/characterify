from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class PdfReportService:

    app_name: str = "Characterify"

    def export_result(self, payload: Dict[str, Any], out_path: str | Path) -> Path:
    
        try:
            
            from reportlab.lib import colors
            from reportlab.lib.pagesizes import A4
            from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
            from reportlab.lib.units import cm
            from reportlab.platypus import Image, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
        except Exception as exc:  # pragma: no cover
            raise RuntimeError("ReportLab belum terpasang. Install: pip install reportlab") from exc

        out = Path(out_path)
        if out.suffix.lower() != ".pdf":
            out = out.with_suffix(".pdf")

        doc = SimpleDocTemplate(
            str(out),
            pagesize=A4,
            title=f"{self.app_name} - Laporan Hasil Tes",
            author=self.app_name,
            leftMargin=2.0 * cm,
            rightMargin=2.0 * cm,
            topMargin=2.0 * cm,
            bottomMargin=2.0 * cm,
        )

        styles = getSampleStyleSheet()
        title_style = styles["Title"]
        h2 = styles["Heading2"]
        normal = styles["BodyText"]
        normal.spaceAfter = 6

        muted = ParagraphStyle(
            "Muted",
            parent=normal,
            textColor=colors.HexColor("#444444"),
        )

        story: List[Any] = []

        # Header
        story.append(Paragraph(f"{self.app_name} — Laporan Hasil Tes", title_style))
        story.append(Paragraph("Dokumen ini dihasilkan otomatis dari aplikasi desktop.", muted))
        story.append(Spacer(1, 10))

        respondent = payload.get("respondent") or {}
        test_id = str(payload.get("test_id", "")).upper()
        result_type = str(payload.get("result_type", ""))

        # Summary table
        data = [
            ["Nama", str(respondent.get("name", "-"))],
            ["Jenis Kelamin", str(respondent.get("gender", "-"))],
            ["Tes", test_id or "-"],
            ["Hasil", result_type or "-"],
        ]

        tbl = Table(data, colWidths=[4.0 * cm, 11.5 * cm])
        tbl.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#F2F2F2")),
                    ("BOX", (0, 0), (-1, -1), 0.6, colors.HexColor("#CCCCCC")),
                    ("INNERGRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#DDDDDD")),
                    ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
                    ("FONTSIZE", (0, 0), (-1, -1), 10),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 8),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                    ("TOPPADDING", (0, 0), (-1, -1), 6),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ]
            )
        )
        story.append(tbl)
        story.append(Spacer(1, 12))

        # Optional chart
        chart_path = self._build_chart_image(payload)
        if chart_path:
            try:
                story.append(Paragraph("Visualisasi Skor", h2))
                story.append(Spacer(1, 6))
                story.append(Image(str(chart_path), width=16.0 * cm, height=7.5 * cm))
                story.append(Spacer(1, 12))
            except Exception:
                pass

        # Content (title/subtitle/summary/sections)
        content = payload.get("content") or {}
        c_title = str(content.get("title") or "Ringkasan")
        c_sub = str(content.get("subtitle") or "")
        c_summary = str(content.get("summary_md") or "")

        story.append(Paragraph(c_title, h2))
        if c_sub:
            story.append(Paragraph(c_sub, muted))
        story.append(Spacer(1, 6))

        if c_summary:
            story.append(Paragraph(self._to_plain_html(c_summary), normal))
            story.append(Spacer(1, 6))

        for sec in content.get("sections", []) or []:
            sec_title = str(sec.get("title") or "")
            items = sec.get("items") or []
            if sec_title:
                story.append(Paragraph(sec_title, h2))
            for it in items:
                story.append(Paragraph(f"• {self._escape(str(it))}", normal))
            story.append(Spacer(1, 6))

        doc.build(story)
        return out

    # Helpers

    @staticmethod
    def _escape(text: str) -> str:
        try:
            from xml.sax.saxutils import escape

            return escape(text)
        except Exception:
            return text

    def _to_plain_html(self, md: str) -> str:
        
        text = md.replace("**", "")
        text = text.replace("\n", "<br/>")
        return self._escape(text)

    def _build_chart_image(self, payload: Dict[str, Any]) -> Optional[Path]:
       
        try:
            import tempfile

            from matplotlib.figure import Figure
        except Exception:
            return None

        try:
            kind = payload.get("chart_kind")
            fig = Figure(figsize=(8, 3.2), dpi=140)
            ax = fig.add_subplot(111)

            if kind == "mbti_stacked":
                self._plot_mbti(ax, payload.get("percentages", []))
            else:
                self._plot_bars(ax, payload.get("percentages", {}), payload.get("scores", {}))

            fig.tight_layout()

            tmp_dir = Path(tempfile.gettempdir()) / "characterify"
            tmp_dir.mkdir(parents=True, exist_ok=True)
            out = tmp_dir / "chart.png"
            fig.savefig(str(out), facecolor="white")
            return out
        except Exception:
            return None

    @staticmethod
    def _plot_mbti(ax, dims: Any) -> None:
        ax.clear()
        labels = [f"{d.get('a','')}/{d.get('b','')}" for d in (dims or [])]
        a_vals = [float(d.get("pct_a", 0)) for d in (dims or [])]
        b_vals = [float(d.get("pct_b", 0)) for d in (dims or [])]
        y = list(range(len(labels)))
        ax.barh(y, a_vals)
        ax.barh(y, b_vals, left=a_vals)
        ax.set_yticks(y)
        ax.set_yticklabels(labels)
        ax.set_xlim(0, 100)
        ax.set_xlabel("Persentase")
        ax.set_title("Preferensi MBTI (4 dimensi)")

    @staticmethod
    def _plot_bars(ax, percentages: Any, scores: Any) -> None:
        ax.clear()
        if isinstance(percentages, dict) and percentages:
            items = list(percentages.items())
            items.sort(key=lambda x: x[0])
            labels = [k for k, _ in items]
            vals = [float(v) for _, v in items]
            ax.bar(labels, vals)
            ax.set_ylabel("Persentase")
            ax.set_title("Distribusi Skor")
        elif isinstance(scores, dict) and scores:
            items = list(scores.items())
            labels = [k for k, _ in items]
            vals = [float(v) for _, v in items]
            ax.bar(labels, vals)
            ax.set_ylabel("Skor")
            ax.set_title("Distribusi Skor")
