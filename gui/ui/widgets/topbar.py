from __future__ import annotations

from typing import Optional

from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QWidget


class TopBar(QFrame):
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setObjectName("TopBar")

        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(10)

        self.title = QLabel("Beranda")
        self.title.setObjectName("TopTitle")
        layout.addWidget(self.title)

        layout.addStretch(1)

        hint = QLabel("Offline • Bahasa Indonesia")
        hint.setObjectName("Muted")
        layout.addWidget(hint)

    def set_title(self, text: str) -> None:
        self.title.setText(text)
