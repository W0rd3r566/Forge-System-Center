from __future__ import annotations

import platform
import sys
from pathlib import Path
from typing import Any

from PySide6.QtCore import QByteArray, Qt, QTimer, QSize
from PySide6.QtGui import QColor, QFont, QIcon, QPainter, QPixmap
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QFrame, QLabel, QPushButton,
    QToolButton, QLineEdit, QComboBox, QStackedWidget, QVBoxLayout,
    QHBoxLayout, QGridLayout, QTableWidget, QTableWidgetItem, QHeaderView,
    QMessageBox, QFileDialog, QProgressBar, QSizePolicy, QAbstractItemView,
    QSplitter, QScrollArea,
)

from . import __version__, system

APP_ROOT = Path(__file__).resolve().parent.parent
BG = "#111218"
SIDEBAR = "#15161d"
PANEL = "#1a1b24"
PANEL_HOVER = "#22232e"
BORDER = "#2b2c38"
TEXT = "#f2f1f8"
MUTED = "#a09fb2"
SOFT = "#6f7083"
PURPLE = "#a99bff"
PURPLE_DARK = "#28243e"
GREEN = "#83d6b0"
AMBER = "#e9c27a"
RED = "#f08a9a"

# Tabler-style outline icons, rendered locally. No network or icon-font dependency.
ICON_PATHS = {
    "overview": '<path d="M5 4h4a1 1 0 0 1 1 1v6a1 1 0 0 1 -1 1h-4a1 1 0 0 1 -1 -1v-6a1 1 0 0 1 1 -1" /><path d="M5 16h4a1 1 0 0 1 1 1v2a1 1 0 0 1 -1 1h-4a1 1 0 0 1 -1 -1v-2a1 1 0 0 1 1 -1" /><path d="M15 12h4a1 1 0 0 1 1 1v6a1 1 0 0 1 -1 1h-4a1 1 0 0 1 -1 -1v-6a1 1 0 0 1 1 -1" /><path d="M15 4h4a1 1 0 0 1 1 1v2a1 1 0 0 1 -1 1h-4a1 1 0 0 1 -1 -1v-2a1 1 0 0 1 1 -1" />',
    "process": '<path d="M13 5h8" /><path d="M13 9h5" /><path d="M13 15h8" /><path d="M13 19h5" /><path d="M3 5a1 1 0 0 1 1 -1h4a1 1 0 0 1 1 1v4a1 1 0 0 1 -1 1h-4a1 1 0 0 1 -1 -1l0 -4" /><path d="M3 15a1 1 0 0 1 1 -1h4a1 1 0 0 1 1 1v4a1 1 0 0 1 -1 1h-4a1 1 0 0 1 -1 -1l0 -4" />',
    "disk": '<path d="M4 6a8 3 0 1 0 16 0a8 3 0 1 0 -16 0" /><path d="M4 6v6a8 3 0 0 0 16 0v-6" /><path d="M4 12v6a8 3 0 0 0 16 0v-6" />',
    "services": '<path d="M3 7a3 3 0 0 1 3 -3h12a3 3 0 0 1 3 3v2a3 3 0 0 1 -3 3h-12a3 3 0 0 1 -3 -3v-2" /><path d="M3 15a3 3 0 0 1 3 -3h12a3 3 0 0 1 3 3v2a3 3 0 0 1 -3 3h-12a3 3 0 0 1 -3 -3l0 -2" /><path d="M7 8l0 .01" /><path d="M7 16l0 .01" />',
    "startup": '<path d="M4 13a8 8 0 0 1 7 7a6 6 0 0 0 3 -5a9 9 0 0 0 6 -8a3 3 0 0 0 -3 -3a9 9 0 0 0 -8 6a6 6 0 0 0 -5 3" /><path d="M7 14a6 6 0 0 0 -3 6a6 6 0 0 0 6 -3" /><path d="M14 9a1 1 0 1 0 2 0a1 1 0 1 0 -2 0" />',
    "cleanup": '<path d="M4 7l16 0" /><path d="M10 11l0 6" /><path d="M14 11l0 6" /><path d="M5 7l1 12a2 2 0 0 0 2 2h8a2 2 0 0 0 2 -2l1 -12" /><path d="M9 7v-3a1 1 0 0 1 1 -1h4a1 1 0 0 1 1 1v3" />',
    "settings": '<path d="M10.325 4.317c.426 -1.756 2.924 -1.756 3.35 0a1.724 1.724 0 0 0 2.573 1.066c1.543 -.94 3.31 .826 2.37 2.37a1.724 1.724 0 0 0 1.065 2.572c1.756 .426 1.756 2.924 0 3.35a1.724 1.724 0 0 0 -1.066 2.573c.94 1.543 -.826 3.31 -2.37 2.37a1.724 1.724 0 0 0 -2.572 1.065c-.426 1.756 -2.924 1.756 -3.35 0a1.724 1.724 0 0 0 -2.573 -1.066c-1.543 .94 -3.31 -.826 -2.37 -2.37a1.724 1.724 0 0 0 -1.065 -2.572c-1.756 -.426 -1.756 -2.924 0 -3.35a1.724 1.724 0 0 0 1.066 -2.573c-.94 -1.543 .826 -3.31 2.37 -2.37c1 .608 2.296 .07 2.572 -1.065" /><path d="M9 12a3 3 0 1 0 6 0a3 3 0 0 0 -6 0" />',
    "info": '<path d="M3 12a9 9 0 1 0 18 0a9 9 0 0 0 -18 0" /><path d="M12 9h.01" /><path d="M11 12h1v4h1" />',
    "refresh": '<path d="M20 11a8.1 8.1 0 0 0 -15.5 -2m-.5 -4v4h4" /><path d="M4 13a8.1 8.1 0 0 0 15.5 2m.5 4v-4h-4" />',
    "search": '<path d="M3 10a7 7 0 1 0 14 0a7 7 0 0 0 -14 0" /><path d="M21 21l-6 -6" />',
    "cpu": '<path d="M5 6a1 1 0 0 1 1 -1h12a1 1 0 0 1 1 1v12a1 1 0 0 1 -1 1h-12a1 1 0 0 1 -1 -1l0 -12" /><path d="M9 9h6v6h-6l0 -6" /><path d="M3 10h2" /><path d="M3 14h2" /><path d="M10 3v2" /><path d="M14 3v2" /><path d="M21 10h-2" /><path d="M21 14h-2" /><path d="M14 21v-2" /><path d="M10 21v-2" />',
    "memory": '<path d="M4 6a8 3 0 1 0 16 0a8 3 0 1 0 -16 0" /><path d="M4 6v6a8 3 0 0 0 16 0v-6" /><path d="M4 12v6a8 3 0 0 0 16 0v-6" />',
    "check": '<path d="M5 12l5 5l10 -10" />',
    "folder": '<path d="M5 4h4l3 3h7a2 2 0 0 1 2 2v8a2 2 0 0 1 -2 2h-14a2 2 0 0 1 -2 -2v-11a2 2 0 0 1 2 -2" />',
}


def icon(name: str, color: str = MUTED, size: int = 18) -> QIcon:
    paths = ICON_PATHS.get(name, ICON_PATHS["info"])
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24"><g fill="none" stroke="{color}" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round">{paths}</g></svg>'
    renderer = QSvgRenderer(QByteArray(svg.encode("utf-8")))
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    renderer.render(painter)
    painter.end()
    return QIcon(pixmap)


def fmt_bytes(value: int | float) -> str:
    return system.format_bytes(value)


class MetricCard(QFrame):
    def __init__(self, title: str, icon_name: str, color: str) -> None:
        super().__init__()
        self.setObjectName("metricCard")
        self.setMinimumHeight(156)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 17, 18, 16)
        layout.setSpacing(12)
        top = QHBoxLayout()
        mark = QLabel()
        mark.setPixmap(icon(icon_name, color, 19).pixmap(19, 19))
        top.addWidget(mark)
        name = QLabel(title)
        name.setObjectName("muted")
        top.addWidget(name)
        top.addStretch(1)
        self.pill = QLabel("LIVE")
        self.pill.setObjectName("livePill")
        top.addWidget(self.pill)
        layout.addLayout(top)
        self.value = QLabel("—")
        self.value.setObjectName("metricValue")
        layout.addWidget(self.value)
        self.detail = QLabel("Получение данных…")
        self.detail.setObjectName("mutedSmall")
        layout.addWidget(self.detail)
        self.bar = QProgressBar()
        self.bar.setTextVisible(False)
        self.bar.setFixedHeight(5)
        self.bar.setRange(0, 100)
        self.bar.setValue(0)
        self.bar.setStyleSheet(f"QProgressBar{{background:{BORDER};border:0;border-radius:2px}} QProgressBar::chunk{{background:{color};border-radius:2px}}")
        layout.addWidget(self.bar)

    def update_value(self, value: str, detail: str, percent: float) -> None:
        self.value.setText(value)
        self.detail.setText(detail)
        self.bar.setValue(max(0, min(100, round(percent))))


class Heading(QWidget):
    def __init__(self, title: str, subtitle: str, action: QWidget | None = None) -> None:
        super().__init__()
        row = QHBoxLayout(self)
        row.setContentsMargins(0, 0, 0, 8)
        row.setSpacing(16)
        text_col = QVBoxLayout()
        text_col.setSpacing(5)
        title_label = QLabel(title)
        title_label.setObjectName("pageTitle")
        subtitle_label = QLabel(subtitle)
        subtitle_label.setObjectName("pageSubtitle")
        subtitle_label.setWordWrap(True)
        text_col.addWidget(title_label)
        text_col.addWidget(subtitle_label)
        row.addLayout(text_col, 1)
        if action is not None:
            row.addWidget(action, 0, Qt.AlignmentFlag.AlignBottom)


class ForgeWindow(QMainWindow):
    NAV = [
        ("Обзор", "overview", "Обзор"),
        ("Процессы", "process", "Процессы"),
        ("Накопители", "disk", "Накопители"),
        ("Службы", "services", "Службы"),
        ("Автозапуск", "startup", "Автозапуск"),
        ("Очистка", "cleanup", "Очистка"),
    ]

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Forge · Центр системы")
        self.setMinimumSize(1040, 700)
        self.resize(1360, 860)
        self.setWindowIcon(QIcon(str(APP_ROOT / "assets" / "forge.svg")))
        self.process_rows: list[dict[str, Any]] = []
        self.service_rows: list[dict[str, Any]] = []
        self.startup_rows: list[dict[str, Any]] = []
        self._build_ui()
        self._apply_theme()
        self.refresh_dashboard()
        self.refresh_processes()
        self.timer = QTimer(self)
        self.timer.setInterval(2500)
        self.timer.timeout.connect(self.refresh_dashboard)
        self.timer.start()
        self.statusBar().showMessage("Данные остаются на этом компьютере", 5000)

    def _build_ui(self) -> None:
        shell = QWidget()
        shell_layout = QHBoxLayout(shell)
        shell_layout.setContentsMargins(0, 0, 0, 0)
        shell_layout.setSpacing(0)

        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(238)
        side = QVBoxLayout(sidebar)
        side.setContentsMargins(18, 22, 18, 18)
        side.setSpacing(7)

        brand = QHBoxLayout()
        brand.setSpacing(11)
        logo = QLabel()
        logo.setObjectName("logoMark")
        logo.setFixedSize(43, 43)
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo.setPixmap(QIcon(str(APP_ROOT / "assets" / "forge.svg")).pixmap(43, 43))
        brand.addWidget(logo)
        brand_copy = QVBoxLayout()
        brand_copy.setSpacing(1)
        brand_name = QLabel("FORGE")
        brand_name.setObjectName("brandName")
        brand_sub = QLabel("ЦЕНТР СИСТЕМЫ")
        brand_sub.setObjectName("brandSub")
        brand_copy.addWidget(brand_name)
        brand_copy.addWidget(brand_sub)
        brand.addLayout(brand_copy)
        brand.addStretch(1)
        side.addLayout(brand)
        side.addSpacing(27)
        section = QLabel("УПРАВЛЕНИЕ")
        section.setObjectName("sectionLabel")
        side.addWidget(section)

        self.stack = QStackedWidget()
        self.pages: dict[str, QWidget] = {}
        self.nav_buttons: dict[str, QPushButton] = {}
        for title, icon_name, key in self.NAV:
            button = QPushButton(title)
            button.setObjectName("navButton")
            button.setIcon(icon(icon_name))
            button.setIconSize(QSize(19, 19))
            button.setCheckable(True)
            button.setCursor(Qt.CursorShape.PointingHandCursor)
            button.setMinimumHeight(43)
            button.clicked.connect(lambda checked=False, page=key: self.navigate(page))
            self.nav_buttons[key] = button
            side.addWidget(button)

        side.addStretch(1)
        system_chip = QFrame()
        system_chip.setObjectName("systemChip")
        chip_layout = QVBoxLayout(system_chip)
        chip_layout.setContentsMargins(12, 12, 12, 12)
        chip_layout.setSpacing(6)
        chip_head = QHBoxLayout()
        status_dot = QLabel("●")
        status_dot.setObjectName("greenDot")
        chip_head.addWidget(status_dot)
        chip_head.addWidget(QLabel("ЛОКАЛЬНЫЙ РЕЖИМ"))
        chip_head.addStretch(1)
        chip_layout.addLayout(chip_head)
        os_label = QLabel(f"{platform.system()} · {platform.machine()}")
        os_label.setObjectName("mutedSmall")
        os_label.setWordWrap(True)
        chip_layout.addWidget(os_label)
        side.addWidget(system_chip)
        version = QLabel(f"Forge {__version__}")
        version.setObjectName("mutedSmall")
        version.setContentsMargins(4, 8, 0, 0)
        side.addWidget(version)

        main = QWidget()
        main_layout = QVBoxLayout(main)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        topbar = QFrame()
        topbar.setObjectName("topbar")
        topbar.setFixedHeight(64)
        top = QHBoxLayout(topbar)
        top.setContentsMargins(28, 0, 28, 0)
        self.breadcrumb = QLabel("Обзор")
        self.breadcrumb.setObjectName("breadcrumb")
        top.addWidget(self.breadcrumb)
        top.addStretch(1)
        self.top_status = QLabel("●  СИСТЕМА ДОСТУПНА")
        self.top_status.setObjectName("statusTag")
        top.addWidget(self.top_status)
        main_layout.addWidget(topbar)
        content = QWidget()
        self.content_layout = QVBoxLayout(content)
        self.content_layout.setContentsMargins(28, 24, 28, 22)
        self.content_layout.addWidget(self.stack)
        main_layout.addWidget(content, 1)
        shell_layout.addWidget(sidebar)
        shell_layout.addWidget(main, 1)
        self.setCentralWidget(shell)

        self._page_overview()
        self._page_processes()
        self._page_disks()
        self._page_services()
        self._page_startup()
        self._page_cleanup()
        self.navigate("Обзор")

    def _scroll_page(self) -> tuple[QWidget, QVBoxLayout]:
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        inner = QWidget()
        layout = QVBoxLayout(inner)
        layout.setContentsMargins(0, 0, 4, 0)
        layout.setSpacing(16)
        scroll.setWidget(inner)
        return scroll, layout

    def _card(self, title: str, body: str = "") -> tuple[QFrame, QVBoxLayout]:
        frame = QFrame()
        frame.setObjectName("panel")
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(18, 17, 18, 17)
        layout.setSpacing(10)
        label = QLabel(title)
        label.setObjectName("panelTitle")
        layout.addWidget(label)
        if body:
            text = QLabel(body)
            text.setObjectName("muted")
            text.setWordWrap(True)
            layout.addWidget(text)
        return frame, layout

    def _button(self, text: str, kind: str = "secondary", icon_name: str | None = None) -> QPushButton:
        button = QPushButton(text)
        button.setObjectName({"primary": "primaryButton", "danger": "dangerButton"}.get(kind, "secondaryButton"))
        button.setCursor(Qt.CursorShape.PointingHandCursor)
        button.setMinimumHeight(36)
        if icon_name:
            button.setIcon(icon(icon_name, "#ffffff" if kind == "primary" else PURPLE))
        return button

    def _page_overview(self) -> None:
        page, layout = self._scroll_page()
        refresh = self._button("Обновить", icon_name="refresh")
        refresh.clicked.connect(self.refresh_dashboard)
        layout.addWidget(Heading("Обзор системы", "Главное о состоянии компьютера в одном месте.", refresh))
        hero = QFrame()
        hero.setObjectName("hero")
        hero_layout = QHBoxLayout(hero)
        hero_layout.setContentsMargins(22, 20, 22, 20)
        hero_copy = QVBoxLayout()
        hero_copy.setSpacing(7)
        overline = QLabel("ВАШ КОМПЬЮТЕР")
        overline.setObjectName("heroOverline")
        hero_title = QLabel("Всё под контролем.")
        hero_title.setObjectName("heroTitle")
        self.hero_subtitle = QLabel("Forge собирает показатели локально и не отправляет их в сеть.")
        self.hero_subtitle.setObjectName("heroSubtitle")
        self.hero_subtitle.setWordWrap(True)
        hero_copy.addWidget(overline)
        hero_copy.addWidget(hero_title)
        hero_copy.addWidget(self.hero_subtitle)
        hero_layout.addLayout(hero_copy, 1)
        hero_logo = QLabel()
        hero_logo.setPixmap(QIcon(str(APP_ROOT / "assets" / "forge.svg")).pixmap(92, 92))
        hero_layout.addWidget(hero_logo)
        layout.addWidget(hero)

        metrics = QGridLayout()
        metrics.setSpacing(12)
        self.cpu_card = MetricCard("Процессор", "cpu", PURPLE)
        self.ram_card = MetricCard("Оперативная память", "memory", GREEN)
        self.disk_card = MetricCard("Системный диск", "disk", AMBER)
        self.proc_card = MetricCard("Процессы", "process", "#82b7ff")
        for i, card in enumerate((self.cpu_card, self.ram_card, self.disk_card, self.proc_card)):
            metrics.addWidget(card, 0, i)
        layout.addLayout(metrics)

        lower = QGridLayout()
        lower.setSpacing(12)
        machine, machine_layout = self._card("Сведения об устройстве")
        self.machine_rows: dict[str, QLabel] = {}
        for key in ("Устройство", "Операционная система", "Архитектура", "Графика", "Время работы"):
            row = QHBoxLayout()
            k = QLabel(key)
            k.setObjectName("muted")
            v = QLabel("—")
            v.setObjectName("infoValue")
            v.setWordWrap(True)
            v.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
            row.addWidget(k)
            row.addStretch(1)
            row.addWidget(v)
            machine_layout.addLayout(row)
            self.machine_rows[key] = v
        actions, action_layout = self._card("Быстрые действия", "Переход к нужному разделу без поиска по меню.")
        quick_actions = [
            ("Открыть процессы", "Посмотреть нагрузку приложений", "Процессы"),
            ("Проверить диски", "Свободное место и папки", "Накопители"),
            ("Настроить автозапуск", "Приложения при входе в систему", "Автозапуск"),
        ]
        for title, desc, page_key in quick_actions:
            btn = QPushButton(f"{title}   ›")
            btn.setObjectName("quickButton")
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setToolTip(desc)
            btn.clicked.connect(lambda checked=False, key=page_key: self.navigate(key))
            action_layout.addWidget(btn)
        lower.addWidget(machine, 0, 0)
        lower.addWidget(actions, 0, 1)
        lower.setColumnStretch(0, 3)
        lower.setColumnStretch(1, 2)
        layout.addLayout(lower)
        note = QLabel("Forge не требует аккаунта. Опасные действия не выполняются автоматически.")
        note.setObjectName("mutedSmall")
        layout.addWidget(note)
        layout.addStretch(1)
        self.pages["Обзор"] = page
        self.stack.addWidget(page)

    def _table(self, headers: list[str]) -> QTableWidget:
        table = QTableWidget(0, len(headers))
        table.setHorizontalHeaderLabels(headers)
        table.setAlternatingRowColors(False)
        table.setShowGrid(False)
        table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        table.verticalHeader().setVisible(False)
        table.verticalHeader().setDefaultSectionSize(39)
        table.horizontalHeader().setHighlightSections(False)
        table.horizontalHeader().setStretchLastSection(True)
        table.setSortingEnabled(True)
        table.setObjectName("dataTable")
        return table

    def _page_processes(self) -> None:
        page, layout = self._scroll_page()
        layout.addWidget(Heading("Процессы", "Запущенные программы, их нагрузка и идентификаторы."))
        controls = QHBoxLayout()
        self.process_search = QLineEdit()
        self.process_search.setPlaceholderText("Поиск по названию, PID или пользователю…")
        self.process_search.addAction(icon("search"), QLineEdit.ActionPosition.LeadingPosition)
        self.process_search.textChanged.connect(self._render_processes)
        refresh = self._button("Обновить", icon_name="refresh")
        refresh.clicked.connect(self.refresh_processes)
        end = self._button("Завершить процесс", "danger")
        end.clicked.connect(self.terminate_selected_process)
        controls.addWidget(self.process_search, 1)
        controls.addWidget(refresh)
        controls.addWidget(end)
        layout.addLayout(controls)
        self.process_table = self._table(["PID", "ПРОЦЕСС", "ПОЛЬЗОВАТЕЛЬ", "CPU", "ПАМЯТЬ"])
        self.process_table.setColumnWidth(0, 85)
        self.process_table.setColumnWidth(1, 280)
        self.process_table.setColumnWidth(2, 210)
        layout.addWidget(self.process_table)
        self.process_status = QLabel("Загрузка списка процессов…")
        self.process_status.setObjectName("mutedSmall")
        layout.addWidget(self.process_status)
        self.pages["Процессы"] = page
        self.stack.addWidget(page)

    def _page_disks(self) -> None:
        page, layout = self._scroll_page()
        choose = self._button("Анализировать папку", "primary", "folder")
        choose.clicked.connect(self.choose_scan_folder)
        layout.addWidget(Heading("Накопители", "Свободное место на дисках и анализ размера папок.", choose))
        self.disk_summary = QGridLayout()
        self.disk_summary.setSpacing(12)
        disk_panel = QFrame()
        disk_panel.setObjectName("panel")
        disk_layout = QVBoxLayout(disk_panel)
        disk_layout.setContentsMargins(18, 17, 18, 17)
        title = QLabel("Подключённые диски")
        title.setObjectName("panelTitle")
        disk_layout.addWidget(title)
        self.disk_table = self._table(["ТОЧКА МОНТИРОВАНИЯ", "ФАЙЛОВАЯ СИСТЕМА", "ЗАНЯТО", "СВОБОДНО", "ИСПОЛЬЗОВАНО"])
        self.disk_table.setColumnWidth(0, 230)
        disk_layout.addWidget(self.disk_table)
        layout.addWidget(disk_panel)
        scan, scan_layout = self._card("Анализ папки", "Выбери каталог, чтобы увидеть самые крупные элементы. Сканирование только читает файлы и не следует по символическим ссылкам.")
        self.scan_result = QLabel("Папка ещё не выбрана.")
        self.scan_result.setObjectName("muted")
        self.scan_result.setWordWrap(True)
        scan_layout.addWidget(self.scan_result)
        layout.addWidget(scan)
        self.pages["Накопители"] = page
        self.stack.addWidget(page)
        self.refresh_disks()

    def _page_services(self) -> None:
        page, layout = self._scroll_page()
        layout.addWidget(Heading("Службы", "Управление фоновыми службами. Изменения требуют подтверждения."))
        if platform.system() != "Linux":
            frame, card = self._card("Недоступно в Windows", "Этот раздел использует systemd и работает только в Linux. На Windows используйте системную оснастку «Службы».")
            layout.addWidget(frame)
            layout.addStretch(1)
        else:
            controls = QHBoxLayout()
            self.service_scope = QComboBox()
            self.service_scope.addItems(["Службы пользователя", "Системные службы"])
            self.service_scope.currentIndexChanged.connect(self.refresh_services)
            refresh = self._button("Обновить", icon_name="refresh")
            refresh.clicked.connect(self.refresh_services)
            controls.addWidget(self.service_scope)
            controls.addStretch(1)
            controls.addWidget(refresh)
            layout.addLayout(controls)
            self.service_table = self._table(["СЛУЖБА", "СОСТОЯНИЕ", "ЗАГРУЗКА", "ОПИСАНИЕ"])
            self.service_table.setColumnWidth(0, 270)
            self.service_table.setColumnWidth(1, 120)
            self.service_table.setColumnWidth(2, 100)
            layout.addWidget(self.service_table)
            buttons = QHBoxLayout()
            for label, action in [("Запустить", "start"), ("Остановить", "stop"), ("Перезапустить", "restart")]:
                button = self._button(label, "primary" if action == "start" else "secondary")
                button.clicked.connect(lambda checked=False, act=action: self.service_action(act))
                buttons.addWidget(button)
            buttons.addStretch(1)
            layout.addLayout(buttons)
            self.service_status = QLabel("Выбери службу в таблице.")
            self.service_status.setObjectName("mutedSmall")
            layout.addWidget(self.service_status)
        self.pages["Службы"] = page
        self.stack.addWidget(page)

    def _page_startup(self) -> None:
        page, layout = self._scroll_page()
        refresh = self._button("Обновить", icon_name="refresh")
        refresh.clicked.connect(self.refresh_startup)
        layout.addWidget(Heading("Автозапуск", "Приложения, которые запускаются при входе в учётную запись.", refresh))
        frame, card = self._card("Элементы автозапуска", "Отключение скрывает запись из автозапуска, не удаляя её. Можно включить её обратно.")
        self.startup_table = self._table(["ПРИЛОЖЕНИЕ", "СОСТОЯНИЕ", "РАСПОЛОЖЕНИЕ"])
        self.startup_table.setColumnWidth(0, 250)
        self.startup_table.setColumnWidth(1, 120)
        card.addWidget(self.startup_table)
        buttons = QHBoxLayout()
        disable = self._button("Отключить", "danger")
        disable.clicked.connect(lambda: self.toggle_startup(False))
        enable = self._button("Включить")
        enable.clicked.connect(lambda: self.toggle_startup(True))
        buttons.addWidget(enable)
        buttons.addWidget(disable)
        buttons.addStretch(1)
        card.addLayout(buttons)
        self.startup_status = QLabel("Загрузка списка…")
        self.startup_status.setObjectName("mutedSmall")
        card.addWidget(self.startup_status)
        layout.addWidget(frame)
        layout.addStretch(1)
        self.pages["Автозапуск"] = page
        self.stack.addWidget(page)
        self.refresh_startup()

    def _page_cleanup(self) -> None:
        page, layout = self._scroll_page()
        layout.addWidget(Heading("Очистка", "Освободи место, предварительно проверив, что именно будет удалено."))
        frame, card = self._card("Кэш текущего пользователя", "Forge может удалить содержимое пользовательского кэша. Документы, загрузки и системные файлы не затрагиваются.")
        self.cache_path = QLabel("—")
        self.cache_path.setObjectName("pathLabel")
        self.cache_path.setWordWrap(True)
        card.addWidget(QLabel("Папка"))
        card.addWidget(self.cache_path)
        self.cache_size = QLabel("—")
        self.cache_size.setObjectName("bigNumber")
        card.addWidget(self.cache_size)
        self.cache_items = QLabel("")
        self.cache_items.setObjectName("muted")
        card.addWidget(self.cache_items)
        buttons = QHBoxLayout()
        refresh = self._button("Пересчитать размер", icon_name="refresh")
        refresh.clicked.connect(self.refresh_cache_info)
        clear = self._button("Очистить кэш…", "danger", "cleanup")
        clear.clicked.connect(self.clear_cache)
        buttons.addWidget(refresh)
        buttons.addWidget(clear)
        buttons.addStretch(1)
        card.addLayout(buttons)
        self.cache_note = QLabel("")
        self.cache_note.setObjectName("mutedSmall")
        self.cache_note.setWordWrap(True)
        card.addWidget(self.cache_note)
        layout.addWidget(frame)
        if platform.system() == "Windows":
            self.cache_note.setText("Очистка пользовательского кэша в этой версии доступна только на Linux.")
            clear.setEnabled(False)
            refresh.setEnabled(False)
        layout.addStretch(1)
        self.pages["Очистка"] = page
        self.stack.addWidget(page)
        self.refresh_cache_info()

    def navigate(self, page: str) -> None:
        if page not in self.pages:
            return
        self.stack.setCurrentWidget(self.pages[page])
        self.breadcrumb.setText(page)
        for key, button in self.nav_buttons.items():
            button.setChecked(key == page)
        if page == "Процессы":
            self.refresh_processes()
        elif page == "Накопители":
            self.refresh_disks()
        elif page == "Службы":
            self.refresh_services()
        elif page == "Автозапуск":
            self.refresh_startup()
        elif page == "Очистка":
            self.refresh_cache_info()

    def refresh_dashboard(self) -> None:
        try:
            data = system.get_system_snapshot()
            self.cpu_card.update_value(f"{data['cpu']:.0f}%", "Текущая загрузка", data["cpu"])
            self.ram_card.update_value(f"{data['memory_percent']:.0f}%", f"{fmt_bytes(data['memory_used'])} из {fmt_bytes(data['memory_total'])}", data["memory_percent"])
            self.disk_card.update_value(f"{data['disk_percent']:.0f}%", f"{fmt_bytes(data['disk_used'])} из {fmt_bytes(data['disk_total'])}", data["disk_percent"])
            self.proc_card.update_value(str(data["process_count"]), "Активных процессов", min(100, data["process_count"] / 4))
            self.machine_rows["Устройство"].setText(data["hostname"])
            self.machine_rows["Операционная система"].setText(data["os"])
            self.machine_rows["Архитектура"].setText(data["machine"])
            self.machine_rows["Графика"].setText(data["gpu"])
            self.machine_rows["Время работы"].setText(data["uptime"])
            self.top_status.setText("●  СИСТЕМА ДОСТУПНА")
        except Exception as exc:
            self.top_status.setText("●  НЕТ ДАННЫХ")
            self.statusBar().showMessage(f"Не удалось прочитать состояние системы: {exc}", 6000)

    def refresh_processes(self) -> None:
        try:
            self.process_rows = system.list_processes()
            self._render_processes()
        except Exception as exc:
            self.process_status.setText(f"Не удалось получить процессы: {exc}")

    def _render_processes(self) -> None:
        if not hasattr(self, "process_table"):
            return
        query = self.process_search.text().strip().lower()
        rows = [row for row in self.process_rows if query in str(row["name"]).lower() or query in str(row["pid"]) or query in str(row["user"]).lower()]
        self.process_table.setSortingEnabled(False)
        self.process_table.setRowCount(len(rows))
        for i, row in enumerate(rows):
            values = [str(row["pid"]), str(row["name"]), str(row["user"]), f"{row['cpu_percent']:.1f}%", f"{row['memory_percent']:.1f}%"]
            for j, value in enumerate(values):
                item = QTableWidgetItem(value)
                if j in (0, 3, 4):
                    item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                if j == 0:
                    item.setData(Qt.ItemDataRole.UserRole, int(row["pid"]))
                self.process_table.setItem(i, j, item)
        self.process_table.setSortingEnabled(True)
        self.process_status.setText(f"Показано {len(rows)} из {len(self.process_rows)} процессов. Завершение отправляет обычный сигнал и не повышает права.")

    def terminate_selected_process(self) -> None:
        row = self.process_table.currentRow()
        if row < 0:
            QMessageBox.information(self, "Процесс не выбран", "Сначала выбери процесс в таблице.")
            return
        pid_item = self.process_table.item(row, 0)
        if not pid_item:
            return
        pid = int(pid_item.data(Qt.ItemDataRole.UserRole) or pid_item.text())
        name = self.process_table.item(row, 1).text()
        answer = QMessageBox.question(self, "Завершить процесс?", f"Отправить обычный сигнал завершения процессу «{name}» (PID {pid})?")
        if answer != QMessageBox.StandardButton.Yes:
            return
        try:
            system.terminate_process(pid)
            self.statusBar().showMessage(f"Сигнал отправлен процессу {pid}", 4000)
            QTimer.singleShot(500, self.refresh_processes)
        except Exception as exc:
            QMessageBox.warning(self, "Не удалось завершить процесс", str(exc))

    def refresh_disks(self) -> None:
        if not hasattr(self, "disk_table"):
            return
        try:
            rows = system.list_disks()
            self.disk_table.setSortingEnabled(False)
            self.disk_table.setRowCount(len(rows))
            for i, row in enumerate(rows):
                values = [row["mountpoint"], row["fstype"], fmt_bytes(row["used"]), fmt_bytes(row["free"]), f"{row['percent']:.0f}%"]
                for j, value in enumerate(values):
                    item = QTableWidgetItem(value)
                    if j >= 2:
                        item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                    self.disk_table.setItem(i, j, item)
            self.disk_table.setSortingEnabled(True)
        except Exception as exc:
            self.statusBar().showMessage(f"Не удалось получить диски: {exc}", 6000)

    def choose_scan_folder(self) -> None:
        folder = QFileDialog.getExistingDirectory(self, "Выбери папку для анализа", str(Path.home()))
        if not folder:
            return
        self.scan_result.setText("Сканирование…")
        QApplication.processEvents()
        try:
            result = system.scan_directory(folder)
            top = result["entries"][:8]
            lines = [f"{entry['name']}   ·   {fmt_bytes(entry['size'])}" for entry in top]
            summary = f"{result['root']}\nВсего учтено: {fmt_bytes(result['total'])} · файлов: {result['files_counted']}"
            if lines:
                summary += "\n\n" + "\n".join(lines)
            self.scan_result.setText(summary)
        except Exception as exc:
            QMessageBox.warning(self, "Ошибка анализа папки", str(exc))
            self.scan_result.setText("Не удалось завершить анализ.")

    def refresh_services(self) -> None:
        if platform.system() != "Linux" or not hasattr(self, "service_table"):
            return
        scope = "user" if self.service_scope.currentIndex() == 0 else "system"
        try:
            self.service_rows = system.list_services(scope)
            self.service_table.setSortingEnabled(False)
            self.service_table.setRowCount(len(self.service_rows))
            for i, row in enumerate(self.service_rows):
                values = [row["unit"], row["active"], row["load"], row["description"]]
                for j, value in enumerate(values):
                    item = QTableWidgetItem(value)
                    if j == 0:
                        item.setData(Qt.ItemDataRole.UserRole, row["unit"])
                    if j == 1:
                        item.setForeground(QColor(GREEN if value == "active" else AMBER if value == "activating" else MUTED))
                    self.service_table.setItem(i, j, item)
            self.service_table.setSortingEnabled(True)
            if hasattr(self, "service_status"):
                self.service_status.setText(f"Найдено служб: {len(self.service_rows)} · область: {'пользователь' if scope == 'user' else 'система'}")
        except Exception as exc:
            if hasattr(self, "service_status"):
                self.service_status.setText(f"Не удалось прочитать службы: {exc}")

    def service_action(self, action: str) -> None:
        if not hasattr(self, "service_table"):
            return
        row = self.service_table.currentRow()
        if row < 0:
            QMessageBox.information(self, "Служба не выбрана", "Сначала выбери службу в таблице.")
            return
        unit = self.service_table.item(row, 0).data(Qt.ItemDataRole.UserRole)
        scope = "user" if self.service_scope.currentIndex() == 0 else "system"
        verb = {"start": "запустить", "stop": "остановить", "restart": "перезапустить"}[action]
        if QMessageBox.question(self, "Подтверждение", f"Точно {verb} службу «{unit}»?") != QMessageBox.StandardButton.Yes:
            return
        try:
            result = system.service_action(unit, scope, action)
            QMessageBox.information(self, "Готово", result)
            self.refresh_services()
        except Exception as exc:
            QMessageBox.warning(self, "Не удалось изменить службу", str(exc))

    def refresh_startup(self) -> None:
        if not hasattr(self, "startup_table"):
            return
        try:
            self.startup_rows = system.list_startup_apps()
            self.startup_table.setSortingEnabled(False)
            self.startup_table.setRowCount(len(self.startup_rows))
            for i, row in enumerate(self.startup_rows):
                values = [str(row["name"]), "Включено" if row["enabled"] else "Отключено", str(row["path"])]
                for j, value in enumerate(values):
                    item = QTableWidgetItem(value)
                    if j == 0:
                        item.setData(Qt.ItemDataRole.UserRole, str(row["path"]))
                    if j == 1:
                        item.setForeground(QColor(GREEN if row["enabled"] else AMBER))
                    self.startup_table.setItem(i, j, item)
            self.startup_table.setSortingEnabled(True)
            self.startup_status.setText(f"Найдено записей: {len(self.startup_rows)}")
        except Exception as exc:
            self.startup_status.setText(f"Не удалось прочитать автозапуск: {exc}")

    def toggle_startup(self, enabled: bool) -> None:
        row = self.startup_table.currentRow()
        if row < 0:
            QMessageBox.information(self, "Запись не выбрана", "Выбери элемент автозапуска.")
            return
        item = self.startup_table.item(row, 0)
        if not item:
            return
        path = str(item.data(Qt.ItemDataRole.UserRole))
        if QMessageBox.question(self, "Изменить автозапуск", f"{'Включить' if enabled else 'Отключить'} запись?\n\n{path}") != QMessageBox.StandardButton.Yes:
            return
        try:
            message = system.toggle_startup(path, enabled)
            self.startup_status.setText(message)
            self.refresh_startup()
        except Exception as exc:
            QMessageBox.warning(self, "Не удалось изменить автозапуск", str(exc))

    def refresh_cache_info(self) -> None:
        if not hasattr(self, "cache_size") or platform.system() != "Linux":
            return
        try:
            data = system.get_cache_info()
            self.cache_path.setText(data["path"])
            self.cache_size.setText(fmt_bytes(data["size"]))
            self.cache_items.setText(f"Элементов в папке: {data['items']}")
            self.cache_note.setText("Ничего не удалено. Перед очисткой появится отдельный запрос подтверждения.")
        except Exception as exc:
            self.cache_note.setText(f"Не удалось проверить кэш: {exc}")

    def clear_cache(self) -> None:
        if platform.system() != "Linux":
            return
        data = system.get_cache_info()
        question = (
            "Forge удалит содержимое пользовательской папки кэша.\n\n"
            f"Путь: {data['path']}\n"
            f"Объём: {fmt_bytes(data['size'])}\n"
            f"Элементов: {data['items']}\n\n"
            "Закрой приложения, если они сейчас используют кэш. Продолжить?"
        )
        if QMessageBox.warning(self, "Очистить пользовательский кэш", question, QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No) != QMessageBox.StandardButton.Yes:
            return
        try:
            result = system.clear_user_cache()
            text = f"Обработано элементов: {result['removed']}."
            if result["errors"]:
                text += "\n\nНе удалось удалить:\n" + "\n".join(result["errors"][:8])
            QMessageBox.information(self, "Результат очистки", text)
            self.refresh_cache_info()
        except Exception as exc:
            QMessageBox.warning(self, "Очистка не выполнена", str(exc))

    def _apply_theme(self) -> None:
        self.setStyleSheet(f"""
            QWidget {{ background: transparent; color: {TEXT}; font-family: 'Inter', 'Noto Sans', 'Segoe UI', sans-serif; font-size: 13px; }}
            QMainWindow, QWidget#root {{ background: {BG}; }}
            #sidebar {{ background: {SIDEBAR}; border-right: 1px solid {BORDER}; }}
            #logoMark {{ background: transparent; }}
            #brandName {{ font-size: 17px; font-weight: 800; letter-spacing: 2px; color: {TEXT}; }}
            #brandSub, #sectionLabel {{ color: {SOFT}; font-size: 9px; font-weight: 700; letter-spacing: 1.2px; }}
            #sectionLabel {{ padding-left: 9px; padding-bottom: 5px; }}
            #navButton {{ text-align: left; padding: 0 12px; border: 1px solid transparent; border-radius: 9px; color: {MUTED}; background: transparent; font-weight: 500; }}
            #navButton:hover {{ color: {TEXT}; background: {PANEL_HOVER}; }}
            #navButton:checked {{ color: {TEXT}; background: {PURPLE_DARK}; border: 1px solid #403960; font-weight: 700; }}
            #systemChip {{ background: #1b1c25; border: 1px solid {BORDER}; border-radius: 10px; }}
            #greenDot {{ color: {GREEN}; font-size: 9px; }}
            #systemChip QLabel {{ font-size: 9px; font-weight: 700; color: {MUTED}; }}
            #topbar {{ background: {BG}; border-bottom: 1px solid {BORDER}; }}
            #breadcrumb {{ color: {TEXT}; font-size: 13px; font-weight: 650; }}
            #statusTag {{ color: {GREEN}; background: #1c2b27; border: 1px solid #2c4940; padding: 7px 10px; border-radius: 7px; font-size: 10px; font-weight: 700; }}
            #pageTitle {{ font-size: 25px; font-weight: 750; color: {TEXT}; }}
            #pageSubtitle {{ font-size: 12px; color: {MUTED}; }}
            #hero {{ background: qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 #24213a,stop:0.55 #1b1b27,stop:1 #20202c); border: 1px solid #3b3555; border-radius: 14px; }}
            #heroOverline {{ color: {PURPLE}; font-size: 9px; font-weight: 800; letter-spacing: 1.5px; }}
            #heroTitle {{ font-size: 25px; font-weight: 750; }}
            #heroSubtitle {{ color: #b9b5d0; font-size: 12px; }}
            #metricCard, #panel {{ background: {PANEL}; border: 1px solid {BORDER}; border-radius: 12px; }}
            #panelTitle {{ font-size: 14px; font-weight: 700; color: {TEXT}; }}
            #muted {{ color: {MUTED}; font-size: 12px; }}
            #mutedSmall {{ color: {SOFT}; font-size: 10px; }}
            #metricValue {{ color: {TEXT}; font-size: 28px; font-weight: 750; }}
            #livePill {{ color: {GREEN}; background: #1b2c27; padding: 3px 6px; border-radius: 4px; font-size: 8px; font-weight: 800; }}
            #infoValue {{ color: {TEXT}; font-size: 11px; font-weight: 600; }}
            #bigNumber {{ color: {TEXT}; font-size: 32px; font-weight: 750; }}
            #pathLabel {{ color: {PURPLE}; font-family: monospace; font-size: 11px; }}
            #quickButton {{ background: transparent; color: {TEXT}; border: 1px solid {BORDER}; border-radius: 8px; text-align: left; padding: 10px 12px; }}
            #quickButton:hover {{ background: {PANEL_HOVER}; border-color: #4a4568; }}
            #primaryButton {{ color: #111018; background: {PURPLE}; border: 1px solid {PURPLE}; border-radius: 8px; padding: 0 14px; font-weight: 700; }}
            #primaryButton:hover {{ background: #b9adff; }}
            #secondaryButton {{ color: {TEXT}; background: #22232d; border: 1px solid #353643; border-radius: 8px; padding: 0 13px; }}
            #secondaryButton:hover {{ background: #2a2b37; border-color: #514b70; }}
            #dangerButton {{ color: #ffdce2; background: #3a2029; border: 1px solid #60313e; border-radius: 8px; padding: 0 13px; }}
            #dangerButton:hover {{ background: #49252f; }}
            QLineEdit, QComboBox {{ background: {PANEL}; color: {TEXT}; border: 1px solid {BORDER}; border-radius: 8px; padding: 9px 10px; selection-background-color: {PURPLE_DARK}; min-height: 18px; }}
            QLineEdit:focus, QComboBox:focus {{ border-color: #665a99; }}
            QComboBox QAbstractItemView {{ background: {PANEL}; border: 1px solid {BORDER}; selection-background-color: {PURPLE_DARK}; }}
            #dataTable {{ background: {PANEL}; alternate-background-color: #1d1e28; border: 1px solid {BORDER}; border-radius: 9px; selection-background-color: #393252; selection-color: {TEXT}; outline: 0; }}
            #dataTable::item {{ padding: 7px 8px; border-bottom: 1px solid #242530; }}
            #dataTable::item:selected {{ background: #393252; }}
            QHeaderView::section {{ background: #20212b; color: {SOFT}; border: 0; border-bottom: 1px solid {BORDER}; padding: 10px 9px; font-size: 9px; font-weight: 800; }}
            QScrollArea {{ border: 0; background: transparent; }}
            QScrollBar:vertical {{ background: {BG}; width: 9px; margin: 2px; }}
            QScrollBar::handle:vertical {{ background: #363746; border-radius: 4px; min-height: 24px; }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
            QStatusBar {{ background: {SIDEBAR}; color: {MUTED}; border-top: 1px solid {BORDER}; font-size: 10px; }}
            QMessageBox {{ background: {PANEL}; }}
        """)


def main() -> int:
    app = QApplication(sys.argv)
    app.setApplicationName("Forge")
    app.setOrganizationName("W0rd3r566")
    app.setStyle("Fusion")
    font = QFont("Inter", 10)
    if not font.exactMatch():
        font = QFont("Noto Sans", 10)
    app.setFont(font)
    window = ForgeWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
