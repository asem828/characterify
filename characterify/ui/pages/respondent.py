from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Optional

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QButtonGroup,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from characterify.app_context import AppContext
from characterify.ui.widgets.common import Card, H1, H2, Muted
from characterify.ui.widgets.dialogs import show_error


@dataclass
class RespondentInfo:
    name: str
    gender: str


class RespondentPage(QWidget):
    def __init__(
        self,
        ctx: AppContext,
        on_continue: Callable[[str, RespondentInfo], None],
        on_back: Callable[[], None],
    ) -> None:
        super().__init__()
        self.ctx = ctx
        self.on_continue = on_continue
        self.on_back = on_back

        self.current_test_id: str = "mbti"

        root = QVBoxLayout(self)
        root.setContentsMargins(18, 18, 18, 18)
        root.setSpacing(12)

        root.addWidget(H1("Data Peserta"))
        root.addWidget(Muted("Sebelum mulai tes, isi nama dan pilih jenis kelamin."))

        card = Card()
        root.addWidget(card, 0)

        card.body.addWidget(H2("Nama"))
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Masukkan nama Anda")
        self.name_input.setMinimumHeight(38)
        card.body.addWidget(self.name_input)

        card.body.addWidget(H2("Jenis Kelamin"))

        row = QHBoxLayout()
        row.setSpacing(12)

        self.gender_group = QButtonGroup(self)
        self.gender_group.setExclusive(True)

        self.btn_male = QPushButton("Laki-laki")
        self.btn_male.setCheckable(True)
        self.btn_male.setObjectName("ChoiceCard")
        self.btn_male.setMinimumHeight(56)

        self.btn_female = QPushButton("Perempuan")
        self.btn_female.setCheckable(True)
        self.btn_female.setObjectName("ChoiceCard")
        self.btn_female.setMinimumHeight(56)

        self.gender_group.addButton(self.btn_male, 1)
        self.gender_group.addButton(self.btn_female, 2)

        row.addWidget(self.btn_male, 1)
        row.addWidget(self.btn_female, 1)
        card.body.addLayout(row)

        # Buttons
        btn_row = QHBoxLayout()
        btn_row.addStretch(1)

        back = QPushButton("Kembali")
        back.clicked.connect(self.on_back)
        btn_row.addWidget(back)

        start = QPushButton("Mulai Tes")
        start.setObjectName("PrimaryButton")
        start.clicked.connect(self._continue)
        btn_row.addWidget(start)

        card.body.addLayout(btn_row)

        root.addStretch(1)

    def load(self, test_id: str) -> None:
        self.current_test_id = test_id
        self.name_input.setText("")
        self.btn_male.setChecked(False)
        self.btn_female.setChecked(False)
        self.name_input.setFocus(Qt.OtherFocusReason)

    def _continue(self) -> None:
        name = (self.name_input.text() or "").strip()
        gender = self._selected_gender()

        if not name:
            show_error(self, "Belum Lengkap", "Nama wajib diisi sebelum memulai tes.")
            return
        if not gender:
            show_error(self, "Belum Lengkap", "Silakan pilih jenis kelamin.")
            return

        self.on_continue(self.current_test_id, RespondentInfo(name=name, gender=gender))

    def _selected_gender(self) -> str:
        if self.btn_male.isChecked():
            return "Laki-laki"
        if self.btn_female.isChecked():
            return "Perempuan"
        return ""
