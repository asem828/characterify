from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QButtonGroup,
    QFrame,
    QHBoxLayout,
    QLabel,
    QRadioButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)


def H1(text: str) -> QLabel:
    lbl = QLabel(text)
    lbl.setObjectName("H1")
    lbl.setWordWrap(True)
    return lbl


def H2(text: str) -> QLabel:
    lbl = QLabel(text)
    lbl.setObjectName("H2")
    lbl.setWordWrap(True)
    return lbl


def Muted(text: str) -> QLabel:
    lbl = QLabel(text)
    lbl.setObjectName("Muted")
    lbl.setWordWrap(True)
    return lbl


class Divider(QFrame):
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setFixedHeight(1)
        self.setObjectName("Divider")


class Card(QFrame):
    """Kartu UI sederhana ala Spotify."""

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setObjectName("Card")
        self.setFrameShape(QFrame.NoFrame)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Maximum)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)
        self.body = layout


class LikertScale(QWidget):
    """Skala Likert 1–5 (radio)."""

    LABELS = {
        1: "Sangat tidak setuju",
        2: "Tidak setuju",
        3: "Netral",
        4: "Setuju",
        5: "Sangat setuju",
    }

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._group = QButtonGroup(self)
        self._group.setExclusive(True)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(14)

        for v in range(1, 6):
            rb = QRadioButton(str(v))
            rb.setToolTip(self.LABELS[v])
            self._group.addButton(rb, v)
            layout.addWidget(rb)

        layout.addStretch(1)

    def is_answered(self) -> bool:
        return self._group.checkedId() in (1, 2, 3, 4, 5)

    def value(self) -> int:
        cid = self._group.checkedId()
        return int(cid) if cid != -1 else 0

    def set_value(self, v: int) -> None:
        btn = self._group.button(int(v))
        if btn:
            btn.setChecked(True)


class QuestionBlock(Card):
    """Satu blok pertanyaan + pilihan jawaban."""

    def __init__(self, number: int, text: str, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        top = QHBoxLayout()
        top.setContentsMargins(0, 0, 0, 0)
        top.setSpacing(10)

        num = QLabel(str(number))
        num.setFixedSize(28, 28)
        num.setAlignment(Qt.AlignCenter)
        num.setStyleSheet(
            "background: rgba(29,185,84,0.18); border: 1px solid rgba(29,185,84,0.30);"
            "border-radius: 10px; color: #E8FFE8; font-weight: 700;"
        )
        top.addWidget(num)

        q = QLabel(text)
        q.setWordWrap(True)
        q.setStyleSheet("font-weight: 600;")
        top.addWidget(q, 1)

        self.body.addLayout(top)
        self.scale = LikertScale()
        self.body.addWidget(self.scale)
