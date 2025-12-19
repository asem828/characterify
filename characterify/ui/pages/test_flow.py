from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Dict

from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QPushButton,
    QProgressBar,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from characterify.app_context import AppContext
from characterify.ui.widgets.common import Card, H1, H2, Muted, QuestionBlock
from characterify.ui.widgets.dialogs import ask_yes_no, show_error, show_info


class TestListPage(QWidget):
    def __init__(self, ctx: AppContext, on_select_test: Callable[[str], None]) -> None:
        super().__init__()
        self.ctx = ctx
        self.on_select_test = on_select_test

        root = QVBoxLayout(self)
        root.setContentsMargins(18, 18, 18, 18)
        root.setSpacing(12)

        root.addWidget(H1("Perpustakaan Tes"))
        root.addWidget(Muted("Pilih salah satu tes di bawah untuk memulai."))

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
            item = self.body_layout.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()

        tests = self.ctx.scoring.get_tests()

        for t in tests:
            c = Card()
            c.body.addWidget(H2(f"{t.title} — {t.subtitle}"))
            c.body.addWidget(Muted(t.description))
            c.body.addWidget(Muted(f"Jumlah pertanyaan: {len(t.questions)}"))

            row = QHBoxLayout()
            row.addStretch(1)
            btn = QPushButton("Lihat Petunjuk")
            btn.clicked.connect(lambda _=False, tid=t.id: self.on_select_test(tid))
            row.addWidget(btn)

            btn2 = QPushButton("Mulai")
            btn2.setObjectName("PrimaryButton")
            btn2.clicked.connect(lambda _=False, tid=t.id: self.on_select_test(tid))
            row.addWidget(btn2)

            c.body.addLayout(row)
            self.body_layout.addWidget(c)

        self.body_layout.addStretch(1)


class TestIntroPage(QWidget):
    def __init__(self, ctx: AppContext, on_start: Callable[[str], None]) -> None:
        super().__init__()
        self.ctx = ctx
        self.on_start = on_start
        self.current_test_id: str = "mbti"

        root = QVBoxLayout(self)
        root.setContentsMargins(18, 18, 18, 18)
        root.setSpacing(12)

        self.title = H1("Tes")
        root.addWidget(self.title)
        self.subtitle = Muted("")
        root.addWidget(self.subtitle)

        self.card = Card()
        root.addWidget(self.card, 1)

        self.desc = Muted("")
        self.card.body.addWidget(self.desc)

        self.card.body.addWidget(H2("Petunjuk"))
        self.rules_container = QWidget()
        self.rules_layout = QVBoxLayout(self.rules_container)
        self.rules_layout.setContentsMargins(0, 0, 0, 0)
        self.rules_layout.setSpacing(6)
        self.card.body.addWidget(self.rules_container)

        row = QHBoxLayout()
        row.addStretch(1)
        self.btn_start = QPushButton("Mulai Tes")
        self.btn_start.setObjectName("PrimaryButton")
        self.btn_start.clicked.connect(lambda: self.on_start(self.current_test_id))
        row.addWidget(self.btn_start)
        self.card.body.addLayout(row)

    def load_test(self, test_id: str) -> None:
        self.current_test_id = test_id
        t = next((x for x in self.ctx.scoring.get_tests() if x.id == test_id), None)
        if not t:
            return
        self.title.setText(f"{t.title}")
        self.subtitle.setText(t.subtitle)
        self.desc.setText(t.description)

        while self.rules_layout.count():
            it = self.rules_layout.takeAt(0)
            w = it.widget()
            if w:
                w.deleteLater()

        for rule in t.instructions:
            lbl = QLabel(f"• {rule}")
            lbl.setWordWrap(True)
            self.rules_layout.addWidget(lbl)


class TestRunnerPage(QWidget):
    def __init__(self, ctx: AppContext, on_finished: Callable[[Dict], None], on_cancel: Callable[[], None]) -> None:
        super().__init__()
        self.ctx = ctx
        self.on_finished = on_finished
        self.on_cancel = on_cancel

        self.current_test_id: str = "mbti"
        self.current_index: int = 0
        self.answers: Dict[int, int] = {}
        self._question_widgets: Dict[int, QuestionBlock] = {}

        root = QVBoxLayout(self)
        root.setContentsMargins(18, 18, 18, 18)
        root.setSpacing(12)

        header = QHBoxLayout()
        self.title = H1("Tes")
        header.addWidget(self.title)
        header.addStretch(1)

        btn_cancel = QPushButton("Kembali")
        btn_cancel.clicked.connect(self._cancel)
        header.addWidget(btn_cancel)
        root.addLayout(header)

        self.progress = QProgressBar()
        root.addWidget(self.progress)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.NoFrame)
        root.addWidget(scroll, 1)

        body = QWidget()
        scroll.setWidget(body)
        self.body_layout = QVBoxLayout(body)
        self.body_layout.setContentsMargins(0, 0, 0, 0)
        self.body_layout.setSpacing(10)

        controls = QHBoxLayout()
        self.btn_back = QPushButton("Back")
        self.btn_back.clicked.connect(self._back)
        controls.addWidget(self.btn_back)

        controls.addStretch(1)

        self.btn_next = QPushButton("Next")
        self.btn_next.setObjectName("PrimaryButton")
        self.btn_next.clicked.connect(self._next)
        controls.addWidget(self.btn_next)

        root.addLayout(controls)

    def start_test(self, test_id: str) -> None:
        self.current_test_id = test_id
        self.current_index = 0
        self.answers = {}
        self._question_widgets.clear()

        t = next((x for x in self.ctx.scoring.get_tests() if x.id == test_id), None)
        if not t:
            return
        self.title.setText(f"{t.title} — {t.subtitle}")
        self._render_page()

    def _render_page(self) -> None:
        while self.body_layout.count():
            it = self.body_layout.takeAt(0)
            w = it.widget()
            if w:
                w.deleteLater()
        self._question_widgets.clear()

        t = next((x for x in self.ctx.scoring.get_tests() if x.id == self.current_test_id), None)
        if not t:
            return

        total = len(t.questions)
        start = self.current_index
        end = min(start + 5, total)

        answered_count = sum(1 for i in range(total) if int(self.answers.get(i, 0)) > 0)
        self.progress.setMaximum(total)
        self.progress.setValue(answered_count)
        self.progress.setFormat(f"{answered_count}/{total} terjawab")

        self.btn_back.setEnabled(start > 0)
        self.btn_next.setText("Selesai" if end >= total else "Next")

        info = Muted(f"Pertanyaan {start + 1}–{end} dari {total}")
        self.body_layout.addWidget(info)

        for idx in range(start, end):
            q = t.questions[idx]
            qb = QuestionBlock(number=idx + 1, text=q.text)
            if idx in self.answers:
                qb.scale.set_value(int(self.answers[idx]))
            self._question_widgets[idx] = qb
            self.body_layout.addWidget(qb)

        self.body_layout.addStretch(1)

    def _collect_current_answers(self) -> bool:
        for idx, qb in self._question_widgets.items():
            if not qb.scale.is_answered():
                return False
        for idx, qb in self._question_widgets.items():
            self.answers[idx] = qb.scale.value()
        return True

    def _next(self) -> None:
        if not self._collect_current_answers():
            show_error(self, "Belum Lengkap", "Mohon jawab semua pertanyaan di halaman ini sebelum lanjut.")
            return

        t = next((x for x in self.ctx.scoring.get_tests() if x.id == self.current_test_id), None)
        if not t:
            return

        total = len(t.questions)
        if self.current_index + 5 >= total:
            self._finish()
            return

        self.current_index += 5
        self._render_page()

    def _back(self) -> None:
        if not self._collect_current_answers():
            if not ask_yes_no(self, "Konfirmasi", "Ada jawaban di halaman ini yang belum diisi. Tetap kembali?"):
                return
        self.current_index = max(0, self.current_index - 5)
        self._render_page()

    def _finish(self) -> None:
        payload = self.ctx.scoring.score_test(self.current_test_id, self.answers)
        show_info(self, "Selesai", "Tes selesai. Menampilkan hasil...")
        self.on_finished(payload)

    def _cancel(self) -> None:
        if ask_yes_no(self, "Kembali", "Kembali ke daftar tes? Jawaban yang sudah diisi tidak disimpan."):
            self.on_cancel()
