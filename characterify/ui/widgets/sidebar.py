from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QFrame, QLabel, QPushButton, QVBoxLayout, QWidget


@dataclass(frozen=True)
class NavItem:
    key: str
    label: str
    emoji: str = "•"


class Sidebar(QFrame):
    navigated = Signal(str)

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setObjectName("Sidebar")
        self.setFixedWidth(260)

        self._buttons: dict[str, QPushButton] = {}

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(10)

        brand = QLabel("Characterify")
        brand.setStyleSheet("font-size: 18px; font-weight: 900; color: #FFFFFF;")
        layout.addWidget(brand)

        sub = QLabel("Tes Kepribadian • Belajar • Refleksi")
        sub.setObjectName("Muted")
        sub.setWordWrap(True)
        layout.addWidget(sub)

        layout.addSpacing(6)

        self.group1_label = QLabel("MENU")
        self.group1_label.setObjectName("GroupLabel")
        layout.addWidget(self.group1_label)

        self.group1_container = QWidget()
        self.group1_layout = QVBoxLayout(self.group1_container)
        self.group1_layout.setContentsMargins(0, 0, 0, 0)
        self.group1_layout.setSpacing(6)
        layout.addWidget(self.group1_container)

        layout.addSpacing(8)

        self.group2_label = QLabel("LAINNYA")
        self.group2_label.setObjectName("GroupLabel")
        layout.addWidget(self.group2_label)

        self.group2_container = QWidget()
        self.group2_layout = QVBoxLayout(self.group2_container)
        self.group2_layout.setContentsMargins(0, 0, 0, 0)
        self.group2_layout.setSpacing(6)
        layout.addWidget(self.group2_container)

        layout.addStretch(1)

    def set_items(self, group1: List[NavItem], group2: List[NavItem]) -> None:
        self._clear_layout(self.group1_layout)
        self._clear_layout(self.group2_layout)
        self._buttons.clear()

        for item in group1:
            self.group1_layout.addWidget(self._make_button(item))
        for item in group2:
            self.group2_layout.addWidget(self._make_button(item))

        self.group1_layout.addStretch(1)
        self.group2_layout.addStretch(1)

    def set_active(self, key: str) -> None:
        for k, btn in self._buttons.items():
            btn.setProperty("active", "true" if k == key else "false")
            btn.style().unpolish(btn)
            btn.style().polish(btn)

    def _make_button(self, item: NavItem) -> QPushButton:
        btn = QPushButton(f"{item.emoji}  {item.label}")
        btn.setObjectName("NavButton")
        btn.setCursor(Qt.PointingHandCursor)
        btn.clicked.connect(lambda _=False, k=item.key: self.navigated.emit(k))
        self._buttons[item.key] = btn
        return btn

    @staticmethod
    def _clear_layout(layout) -> None:
        while layout.count():
            it = layout.takeAt(0)
            w = it.widget()
            if w:
                w.deleteLater()
