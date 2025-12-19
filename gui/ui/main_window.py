from __future__ import annotations

from typing import Any, Dict, Optional

from PySide6.QtCore import QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QMainWindow,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from characterify.app_context import AppContext
from characterify.ui.pages.home import HomePage
from characterify.ui.pages.information import InformationPage
from characterify.ui.pages.learn import ArticleReaderPage, LearnPage
from characterify.ui.pages.result import ResultPage
from characterify.ui.pages.help import HelpPage
from characterify.ui.pages.respondent import RespondentInfo, RespondentPage
from characterify.ui.pages.test_flow import TestIntroPage, TestListPage, TestRunnerPage
from characterify.ui.widgets.sidebar import NavItem, Sidebar
from characterify.ui.widgets.topbar import TopBar


class MainWindow(QMainWindow):


    def __init__(self, ctx: AppContext) -> None:
        super().__init__()
        self.ctx = ctx
        self.setWindowTitle("Characterify")
        self.setObjectName("AppRoot")

        self._current_key: str = "home"
        self._respondent: Optional[RespondentInfo] = None

        root = QWidget()
        self.setCentralWidget(root)

        main_layout = QHBoxLayout(root)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Sidebar
        self.sidebar = Sidebar()
        self.sidebar.set_items(
            group1=[
                NavItem("home", "Beranda", "🏠"),
                NavItem("test", "Tes", "🧪"),
                NavItem("learn", "Belajar", "📚"),
            ],
            group2=[
                NavItem("help", "Bantuan", "❓"),
                NavItem("information", "Informasi", "ℹ️"),
                NavItem("web", "Web version", "🌐"),
            ],
        )
        self.sidebar.navigated.connect(self.navigate)
        main_layout.addWidget(self.sidebar)

        # Right: topbar + pages
        right = QFrame()
        right.setObjectName("ContentArea")
        right_layout = QVBoxLayout(right)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(0)

        self.topbar = TopBar()
        right_layout.addWidget(self.topbar)

        self.pages = QStackedWidget()
        right_layout.addWidget(self.pages, 1)

        main_layout.addWidget(right, 1)

        self._page_map: Dict[str, QWidget] = {}
        self._register_pages()

        self.navigate("home")

    def _register_pages(self) -> None:
        self._add_page("home", HomePage(self.ctx, on_start_test=lambda: self.navigate("test")))
        self._add_page("test", TestListPage(self.ctx, on_select_test=lambda tid: self.navigate("test_intro", test_id=tid)))
        self._add_page("test_intro", TestIntroPage(self.ctx, on_start=lambda tid: self.navigate("respondent", test_id=tid)))
        self._add_page(
            "respondent",
            RespondentPage(
                self.ctx,
                on_continue=self._on_respondent_ready,
                on_back=lambda: self.navigate("test_intro", test_id=getattr(self, "_pending_test_id", "mbti")),
            ),
        )
        self._add_page("test_run", TestRunnerPage(self.ctx, on_finished=self._on_test_finished, on_cancel=lambda: self.navigate("test")))
        self._add_page("result", ResultPage(self.ctx, on_done=lambda: self.navigate("test")))
        self._add_page("learn", LearnPage(self.ctx, on_open_article=lambda aid: self.navigate("article", article_id=aid)))
        self._add_page("article", ArticleReaderPage(self.ctx, on_back=lambda: self.navigate("learn")))
        self._add_page("help", HelpPage(self.ctx))
        self._add_page("information", InformationPage(self.ctx))

        self.pages.setCurrentWidget(self._page_map["home"])

    def _add_page(self, key: str, page: QWidget) -> None:
        self._page_map[key] = page
        self.pages.addWidget(page)

    def navigate(self, key: str, **kwargs: Any) -> None:
        if key == "web":
            QDesktopServices.openUrl(QUrl("https://characterify.pythonanywhere.com/"))
            return

        self._current_key = key

        if key in ("home", "test", "learn", "help", "information"):
            self.sidebar.set_active(key)

        # dynamic pages
        if key == "test_intro":
            page: TestIntroPage = self._page_map[key]  # type: ignore
            test_id = kwargs.get("test_id", "mbti")
            self._pending_test_id = test_id
            page.load_test(test_id)
        elif key == "respondent":
            page: RespondentPage = self._page_map[key] 
            test_id = kwargs.get("test_id", getattr(self, "_pending_test_id", "mbti"))
            self._pending_test_id = test_id
            page.load(test_id)
        elif key == "test_run":
            page: TestRunnerPage = self._page_map[key] 
            page.start_test(kwargs.get("test_id", "mbti"))
        elif key == "result":
            page: ResultPage = self._page_map[key]   
            page.show_result(kwargs["payload"])
        elif key == "article":
            page: ArticleReaderPage = self._page_map[key]  
            page.open_article(kwargs.get("article_id", ""))

        self._apply_title_for_key(key)

        w = self._page_map.get(key)
        if w is not None:
            self.pages.setCurrentWidget(w)

    def _apply_title_for_key(self, key: str) -> None:
        mapping = {
            "home": "Beranda",
            "test": "Tes",
            "test_intro": "Tes",
            "respondent": "Data Peserta",
            "test_run": "Tes",
            "result": "Hasil Tes",
            "learn": "Belajar",
            "article": "Belajar",
            "help": "Bantuan",
            "information": "Informasi",
        }
        self.topbar.set_title(mapping.get(key, "Characterify"))

    def _on_test_finished(self, payload: Dict[str, Any]) -> None:
        if self._respondent is not None:
            payload = dict(payload)
            payload["respondent"] = {"name": self._respondent.name, "gender": self._respondent.gender}
        self.navigate("result", payload=payload)

    def _on_respondent_ready(self, test_id: str, info: RespondentInfo) -> None:
        self._respondent = info
        self.navigate("test_run", test_id=test_id)
