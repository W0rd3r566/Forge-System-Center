from __future__ import annotations

import os
import platform
import sys
import time
from pathlib import Path
from typing import Any, Callable

from PySide6.QtCore import QObject, QRunnable, Qt, QThreadPool, QTimer, Signal, QSize, QRectF
from PySide6.QtGui import QColor, QFont, QPainter, QPen, QBrush, QAction, QDesktopServices, QIcon, QKeySequence
from PySide6.QtCore import QUrl
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QFrame,
    QLabel,
    QPushButton,
    QToolButton,
    QLineEdit,
    QComboBox,
    QStackedWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QScrollArea,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QMessageBox,
    QFileDialog,
    QProgressBar,
    QSizePolicy,
    QAbstractItemView,
    QMenu,
    QSplitter,
    QStyle,
)

from . import __version__
from . import system

BG = "#171819"
SURFACE = "#202223"
SURFACE_ALT = "#252728"
BORDER = "#343738"
TEXT = "#F0F1F1"
MUTED = "#A2A7A8"
SOFT = "#767D7F"
ACCENT = "#D4D8D7"
GREEN = "#8DBAA6"
AMBER = "#D8B77C"
RED = "#D98D8D"


class WorkerSignals(QObject):
    result = Signal(object)
    error = Signal(str)
    finished = Signal()


class Worker(QRunnable):
    def __init__(self, function: Callable[..., Any], *args: Any, **kwargs: Any) -> None:
        super().__init__()
        self.function = function
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()

    def run(self) -> None:
        try:
            result = self.function(*self.args, **self.kwargs)
            self.signals.result.emit(result)
        except Exception as exc:  # The UI receives and displays expected OS errors.
            self.signals.error.emit(str(exc) or exc.__class__.__name__)
        finally:
            self.signals.finished.emit()


class Sparkline(QWidget):
    def __init__(self, color: str = ACCENT, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.values: list[float] = []
        self.color = QColor(color)
        self.setMinimumHeight(34)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

    def set_values(self, values: list[float]) -> None:
        self.values = values[-60:]
        self.update()

    def paintEvent(self, event: Any) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = self.rect().adjusted(2, 5, -2, -5)
        if len(self.values) < 2 or rect.width() <= 0 or rect.height() <= 0:
            painter.setPen(QPen(QColor(BORDER), 1))
            painter.drawLine(rect.bottomLeft(), rect.bottomRight())
            return
        points = []
        count = len(self.values)
        for index, value in enumerate(self.values):
            x = rect.left() + (rect.width() * index / max(1, count - 1))
            y = rect.bottom() - (max(0, min(100, value)) / 100) * rect.height()
            points.append((x, y))
        path = __import__("PySide6.QtGui", fromlist=["QPainterPath"]).QPainterPath()
        path.moveTo(points[0][0], points[0][1])
        for x, y in points[1:]:
            path.lineTo(x, y)
        pen = QPen(self.color, 1.7)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        painter.setPen(pen)
        painter.drawPath(path)


class MetricCard(QFrame):
    def __init__(self, label: str, accent: str = ACCENT, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("metricCard")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 16, 18, 14)
        layout.setSpacing(8)
        top = QHBoxLayout()
        self.title = QLabel(label.upper())
        self.title.setObjectName("eyebrow")
        self.dot = QLabel("●")
        self.dot.setStyleSheet(f"color: {accent}; font-size: 9px;")
        top.addWidget(self.title)
        top.addStretch(1)
        top.addWidget(self.dot)
        layout.addLayout(top)
        self.value = QLabel("—")
        self.value.setObjectName("metricValue")
        layout.addWidget(self.value)
        self.detail = QLabel("Waiting for system data")
        self.detail.setObjectName("muted")
        self.detail.setWordWrap(True)
        layout.addWidget(self.detail)
        self.chart = Sparkline(accent)
        layout.addWidget(self.chart)

    def update_metric(self, value: str, detail: str, history: list[float] | None = None) -> None:
        self.value.setText(value)
        self.detail.setText(detail)
        if history is not None:
            self.chart.set_values(history)


class SectionHeading(QWidget):
    def __init__(self, title: str, description: str, action: QWidget | None = None) -> None:
        super().__init__()
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 8)
        layout.setSpacing(14)
        copy = QVBoxLayout()
        copy.setSpacing(4)
        title_label = QLabel(title)
        title_label.setObjectName("pageTitle")
        desc = QLabel(description)
        desc.setObjectName("muted")
        desc.setWordWrap(True)
        copy.addWidget(title_label)
        copy.addWidget(desc)
        layout.addLayout(copy, 1)
        if action is not None:
            layout.addWidget(action, 0, Qt.AlignmentFlag.AlignBottom)


class ForgeWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Forge · System Center")
        self.setMinimumSize(QSize(1060, 700))
        self.resize(1320, 850)
        self.setWindowIcon(QIcon(str(Path(__file__).resolve().parent.parent / "assets" / "forge.svg")))
        self.thread_pool = QThreadPool.globalInstance()
        self._refresh_busy = False
        self._last_snapshot: dict[str, Any] = {}
        self._cpu_history: list[float] = []
        self._mem_history: list[float] = []
        self._disk_history: list[float] = []
        self._process_cache: list[dict[str, Any]] = []
        self._service_cache: list[dict[str, str]] = []
        self._startup_cache: list[dict[str, str | bool]] = []
        self._scan_path: str | None = None
        self._workers: list[Worker] = []
        self._build_ui()
        self._build_shortcuts()
        self._apply_theme()
        self.refresh_dashboard()
        self.refresh_processes()
        self.refresh_services()
        self.refresh_startup()
        self.refresh_cache_info()
        self.timer = QTimer(self)
        self.timer.setInterval(2200)
        self.timer.timeout.connect(self.refresh_dashboard)
        self.timer.start()
        self.statusBar().showMessage("Local-only mode · no account · no telemetry", 6000)

    def _build_ui(self) -> None:
        root = QWidget()
        root.setObjectName("root")
        shell = QHBoxLayout(root)
        shell.setContentsMargins(0, 0, 0, 0)
        shell.setSpacing(0)

        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(218)
        side = QVBoxLayout(sidebar)
        side.setContentsMargins(16, 20, 16, 16)
        side.setSpacing(7)

        brand = QHBoxLayout()
        logo = QLabel("F")
        logo.setObjectName("brandMark")
        logo.setFixedSize(36, 36)
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        brand_text = QVBoxLayout()
        brand_text.setSpacing(0)
        brand_name = QLabel("FORGE")
        brand_name.setObjectName("brandName")
        brand_sub = QLabel("SYSTEM CENTER")
        brand_sub.setObjectName("brandSub")
        brand_text.addWidget(brand_name)
        brand_text.addWidget(brand_sub)
        brand.addWidget(logo)
        brand.addSpacing(9)
        brand.addLayout(brand_text)
        brand.addStretch(1)
        side.addLayout(brand)

        side.addSpacing(25)
        nav_label = QLabel("WORKSPACE")
        nav_label.setObjectName("eyebrow")
        nav_label.setContentsMargins(8, 0, 0, 7)
        side.addWidget(nav_label)

        self.stack = QStackedWidget()
        self.pages: dict[str, QWidget] = {}
        self.nav_buttons: dict[str, QPushButton] = {}
        nav_items = [
            ("Overview", "Overview", "▦"),
            ("Processes", "Processes", "≋"),
            ("Storage", "Storage", "◫"),
            ("Services", "Services", "⌘"),
            ("Startup", "Startup", "↗"),
            ("Cleanup", "Cleanup", "⌁"),
        ]
        for key, title, glyph in nav_items:
            button = QPushButton(f"{glyph}    {title}")
            button.setObjectName("navButton")
            button.setCheckable(True)
            button.setCursor(Qt.CursorShape.PointingHandCursor)
            button.clicked.connect(lambda _checked=False, page_key=key: self.navigate(page_key))
            self.nav_buttons[key] = button
            side.addWidget(button)

        side.addStretch(1)
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setObjectName("separator")
        side.addWidget(line)
        local_label = QLabel("●  LOCAL INSTANCE")
        local_label.setObjectName("localStatus")
        side.addWidget(local_label)
        os_label = QLabel(f"{platform.system()} · {platform.machine()}")
        os_label.setObjectName("mutedSmall")
        side.addWidget(os_label)
        version = QLabel(f"Forge v{__version__}")
        version.setObjectName("mutedSmall")
        side.addWidget(version)

        main = QVBoxLayout()
        main.setContentsMargins(0, 0, 0, 0)
        main.setSpacing(0)
        topbar = QFrame()
        topbar.setObjectName("topbar")
        topbar.setFixedHeight(66)
        top_layout = QHBoxLayout(topbar)
        top_layout.setContentsMargins(26, 0, 26, 0)
        self.breadcrumb = QLabel("Overview")
        self.breadcrumb.setObjectName("breadcrumb")
        self.live_label = QLabel("●  LIVE SYSTEM DATA")
        self.live_label.setObjectName("liveTag")
        top_layout.addWidget(self.breadcrumb)
        top_layout.addStretch(1)
        top_layout.addWidget(self.live_label)
        main.addWidget(topbar)

        body = QWidget()
        body_layout = QVBoxLayout(body)
        body_layout.setContentsMargins(26, 22, 26, 22)
        body_layout.addWidget(self.stack)
        main.addWidget(body, 1)

        shell.addWidget(sidebar)
        main_widget = QWidget()
        main_widget.setLayout(main)
        shell.addWidget(main_widget, 1)
        self.setCentralWidget(root)

        self._build_dashboard()
        self._build_processes_page()
        self._build_storage_page()
        self._build_services_page()
        self._build_startup_page()
        self._build_cleanup_page()
        self.navigate("Overview")

    def _build_dashboard(self) -> None:
        page = self._make_scroll_page()
        layout = page.widget().layout()
        refresh = self._button("Refresh", secondary=True)
        refresh.clicked.connect(self.refresh_dashboard)
        heading = SectionHeading("System overview", "A live, local snapshot of your machine.", refresh)
        layout.addWidget(heading)

        cards = QGridLayout()
        cards.setSpacing(12)
        self.cpu_card = MetricCard("Processor", ACCENT)
        self.memory_card = MetricCard("Memory", GREEN)
        self.disk_card = MetricCard("System disk", AMBER)
        self.process_card = MetricCard("Processes", ACCENT)
        for index, card in enumerate((self.cpu_card, self.memory_card, self.disk_card, self.process_card)):
            cards.addWidget(card, 0, index)
        layout.addLayout(cards)

        lower = QGridLayout()
        lower.setSpacing(12)
        system_panel = QFrame()
        system_panel.setObjectName("panel")
        sys_layout = QVBoxLayout(system_panel)
        sys_layout.setContentsMargins(18, 18, 18, 18)
        sys_layout.setSpacing(12)
        sys_header = QHBoxLayout()
        sys_title = QLabel("Machine details")
        sys_title.setObjectName("panelTitle")
        sys_header.addWidget(sys_title)
        sys_header.addStretch(1)
        self.uptime_chip = QLabel("—")
        self.uptime_chip.setObjectName("miniChip")
        sys_header.addWidget(self.uptime_chip)
        sys_layout.addLayout(sys_header)
        self.info_rows: dict[str, QLabel] = {}
        for name in ("Device", "Operating system", "Architecture", "Graphics", "Python"):
            row = QHBoxLayout()
            label = QLabel(name)
            label.setObjectName("muted")
            value = QLabel("—")
            value.setObjectName("infoValue")
            value.setWordWrap(True)
            value.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
            row.addWidget(label)
            row.addStretch(1)
            row.addWidget(value)
            sys_layout.addLayout(row)
            self.info_rows[name] = value

        actions_panel = QFrame()
        actions_panel.setObjectName("panel")
        action_layout = QVBoxLayout(actions_panel)
        action_layout.setContentsMargins(18, 18, 18, 18)
        action_layout.setSpacing(12)
        actions_title = QLabel("Quick access")
        actions_title.setObjectName("panelTitle")
        action_layout.addWidget(actions_title)
        action_layout.addWidget(self._quick_action("Inspect running processes", "See CPU and memory usage by process", lambda: self.navigate("Processes")))
        action_layout.addWidget(self._quick_action("Review disk usage", "Inspect mounted volumes and scan a folder", lambda: self.navigate("Storage")))
        action_layout.addWidget(self._quick_action("Manage startup entries", "Enable or disable your own autostart items", lambda: self.navigate("Startup")))
        action_layout.addWidget(self._quick_action("Clear user cache", "Review cache size before removing anything", lambda: self.navigate("Cleanup")))
        action_layout.addStretch(1)
        lower.addWidget(system_panel, 0, 0)
        lower.addWidget(actions_panel, 0, 1)
        lower.setColumnStretch(0, 3)
        lower.setColumnStretch(1, 2)
        layout.addLayout(lower)
        note = QLabel("Forge reads system information locally. Privileged actions require explicit confirmation and system authentication.")
        note.setObjectName("mutedSmall")
        note.setWordWrap(True)
        layout.addWidget(note)
        self.pages["Overview"] = page
        self.stack.addWidget(page)

    def _build_processes_page(self) -> None:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        bar = QHBoxLayout()
        self.process_search = QLineEdit()
        self.process_search.setPlaceholderText("Filter by process name, PID or user…")
        self.process_search.textChanged.connect(self._render_processes)
        refresh = self._button("Refresh", secondary=True)
        refresh.clicked.connect(self.refresh_processes)
        terminate = self._button("End process", danger=True)
        terminate.clicked.connect(self.terminate_selected_process)
        bar.addWidget(self.process_search, 1)
        bar.addWidget(refresh)
        bar.addWidget(terminate)
        layout.addWidget(SectionHeading("Processes", "Review running processes. Forge only sends a normal termination signal and never escalates privileges."))
        layout.addLayout(bar)
        self.process_table = self._table(["PID", "PROCESS", "USER", "CPU", "MEMORY"])
        self.process_table.setColumnWidth(0, 86)
        self.process_table.setColumnWidth(1, 280)
        self.process_table.setColumnWidth(2, 190)
        self.process_table.setColumnWidth(3, 110)
        self.process_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.process_table, 1)
        self.process_status = QLabel("Processes are read from the current user context.")
        self.process_status.setObjectName("mutedSmall")
        layout.addWidget(self.process_status)
        self.pages["Processes"] = page
        self.stack.addWidget(page)

    def _build_storage_page(self) -> None:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        choose = self._button("Scan folder", secondary=True)
        choose.clicked.connect(self.choose_scan_folder)
        layout.addWidget(SectionHeading("Storage", "Mounted disks and a safe, read-only scan of a folder.", choose))
        self.disk_grid = QGridLayout()
        self.disk_grid.setSpacing(12)
        self.disk_grid_widget = QWidget()
        self.disk_grid_widget.setLayout(self.disk_grid)
        layout.addWidget(self.disk_grid_widget)
        scan_panel = QFrame()
        scan_panel.setObjectName("panel")
        scan_layout = QVBoxLayout(scan_panel)
        scan_layout.setContentsMargins(16, 16, 16, 16)
        scan_head = QHBoxLayout()
        self.scan_title = QLabel("Folder analysis")
        self.scan_title.setObjectName("panelTitle")
        self.scan_path_label = QLabel("Choose a directory to inspect its largest entries.")
        self.scan_path_label.setObjectName("mutedSmall")
        scan_head.addWidget(self.scan_title)
        scan_head.addStretch(1)
        scan_layout.addLayout(scan_head)
        scan_layout.addWidget(self.scan_path_label)
        self.scan_table = self._table(["ENTRY", "TYPE", "SIZE", "LOCATION"])
        self.scan_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.scan_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.scan_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.scan_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        self.scan_table.setMinimumHeight(220)
        scan_layout.addWidget(self.scan_table)
        self.scan_status = QLabel("Scanning reads file metadata only; it does not move or delete files.")
        self.scan_status.setObjectName("mutedSmall")
        scan_layout.addWidget(self.scan_status)
        layout.addWidget(scan_panel, 1)
        self.pages["Storage"] = page
        self.stack.addWidget(page)
        self.refresh_disks()

    def _build_services_page(self) -> None:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        controls = QHBoxLayout()
        self.service_scope = QComboBox()
        self.service_scope.addItem("User services", "user")
        self.service_scope.addItem("System services", "system")
        self.service_scope.currentIndexChanged.connect(self.refresh_services)
        refresh = self._button("Refresh", secondary=True)
        refresh.clicked.connect(self.refresh_services)
        self.service_action_buttons: list[QPushButton] = []
        for action, label, danger in (("start", "Start", False), ("restart", "Restart", False), ("stop", "Stop", True)):
            button = self._button(label, danger=danger, secondary=not danger)
            button.clicked.connect(lambda _checked=False, chosen=action: self.run_service_action(chosen))
            controls.addWidget(button)
            self.service_action_buttons.append(button)
        controls.insertWidget(0, self.service_scope)
        controls.insertWidget(1, refresh)
        layout.addWidget(SectionHeading("Services", "Inspect systemd services. System-level changes use your desktop authentication prompt."))
        layout.addLayout(controls)
        self.service_table = self._table(["UNIT", "STATE", "SUBSTATE", "DESCRIPTION"])
        self.service_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.service_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.service_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.service_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.service_table, 1)
        self.services_status = QLabel("Services are loaded on request; Forge does not change them automatically.")
        self.services_status.setObjectName("mutedSmall")
        layout.addWidget(self.services_status)
        self.pages["Services"] = page
        self.stack.addWidget(page)

    def _build_startup_page(self) -> None:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        refresh = self._button("Refresh", secondary=True)
        refresh.clicked.connect(self.refresh_startup)
        layout.addWidget(SectionHeading("Startup", "Enable or disable entries in your own autostart folder. Original files are preserved by renaming." , refresh))
        buttons = QHBoxLayout()
        enable = self._button("Enable selected", secondary=True)
        enable.clicked.connect(lambda: self.toggle_selected_startup(True))
        disable = self._button("Disable selected", secondary=True)
        disable.clicked.connect(lambda: self.toggle_selected_startup(False))
        buttons.addWidget(enable)
        buttons.addWidget(disable)
        buttons.addStretch(1)
        layout.addLayout(buttons)
        self.startup_table = self._table(["APPLICATION", "STATE", "ENTRY FILE"])
        self.startup_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.startup_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.startup_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.startup_table, 1)
        self.startup_status = QLabel("Only the current user's startup entries are managed.")
        self.startup_status.setObjectName("mutedSmall")
        layout.addWidget(self.startup_status)
        self.pages["Startup"] = page
        self.stack.addWidget(page)

    def _build_cleanup_page(self) -> None:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(SectionHeading("Cleanup", "Review your per-user cache before clearing it. System-level files and package archives outside this folder are not touched."))
        panel = QFrame()
        panel.setObjectName("panel")
        panel_layout = QVBoxLayout(panel)
        panel_layout.setContentsMargins(22, 22, 22, 22)
        panel_layout.setSpacing(12)
        self.cache_size_label = QLabel("Calculating cache size…")
        self.cache_size_label.setObjectName("heroValue")
        self.cache_path_label = QLabel(str(system.get_cache_directory()))
        self.cache_path_label.setObjectName("muted")
        self.cache_path_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.cache_detail_label = QLabel("Scanning cache directories in the background.")
        self.cache_detail_label.setObjectName("muted")
        self.cache_progress = QProgressBar()
        self.cache_progress.setRange(0, 0)
        self.cache_progress.setTextVisible(False)
        self.cache_progress.setFixedHeight(4)
        self.cache_progress.setMaximumWidth(300)
        row = QHBoxLayout()
        refresh = self._button("Recalculate", secondary=True)
        refresh.clicked.connect(self.refresh_cache_info)
        clear = self._button("Clear user cache", danger=True)
        clear.clicked.connect(self.clear_cache_confirmed)
        row.addWidget(refresh)
        row.addWidget(clear)
        row.addStretch(1)
        panel_layout.addWidget(QLabel("USER CACHE") , 0)
        panel_layout.addWidget(self.cache_size_label)
        panel_layout.addWidget(self.cache_path_label)
        panel_layout.addWidget(self.cache_progress, 0, Qt.AlignmentFlag.AlignLeft)
        panel_layout.addWidget(self.cache_detail_label)
        panel_layout.addSpacing(10)
        panel_layout.addLayout(row)
        layout.addWidget(panel)
        warning = QFrame()
        warning.setObjectName("noticePanel")
        warning_layout = QVBoxLayout(warning)
        warning_layout.setContentsMargins(16, 14, 16, 14)
        warning_title = QLabel("What this action does")
        warning_title.setObjectName("panelTitle")
        warning_text = QLabel("Forge removes the contents of ~/.cache for the current user only. This can include application caches and per-user tool caches such as pip. It does not delete your Downloads folder, personal documents, system files or system package archives outside this directory. Review the path before continuing.")
        warning_text.setObjectName("muted")
        warning_text.setWordWrap(True)
        warning_layout.addWidget(warning_title)
        warning_layout.addWidget(warning_text)
        layout.addWidget(warning)
        layout.addStretch(1)
        self.pages["Cleanup"] = page
        self.stack.addWidget(page)

    def _make_scroll_page(self) -> QWidget:
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setObjectName("pageScroll")
        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(0, 0, 4, 8)
        layout.setSpacing(16)
        layout.addStretch(0)
        scroll.setWidget(content)
        # The content widget is retained by the scroll area.
        return scroll

    def _quick_action(self, title: str, description: str, callback: Callable[[], None]) -> QPushButton:
        button = QPushButton()
        button.setObjectName("quickAction")
        button.setCursor(Qt.CursorShape.PointingHandCursor)
        box = QHBoxLayout(button)
        box.setContentsMargins(12, 10, 12, 10)
        box.setSpacing(12)
        icon = QLabel("↗")
        icon.setObjectName("quickArrow")
        copy = QVBoxLayout()
        copy.setSpacing(3)
        name = QLabel(title)
        name.setObjectName("quickTitle")
        desc = QLabel(description)
        desc.setObjectName("mutedSmall")
        desc.setWordWrap(True)
        copy.addWidget(name)
        copy.addWidget(desc)
        box.addLayout(copy, 1)
        box.addWidget(icon)
        button.clicked.connect(callback)
        return button

    def _button(self, label: str, secondary: bool = False, danger: bool = False) -> QPushButton:
        button = QPushButton(label)
        button.setCursor(Qt.CursorShape.PointingHandCursor)
        button.setMinimumHeight(36)
        button.setObjectName("dangerButton" if danger else ("secondaryButton" if secondary else "primaryButton"))
        return button

    def _table(self, headers: list[str]) -> QTableWidget:
        table = QTableWidget(0, len(headers))
        table.setHorizontalHeaderLabels(headers)
        table.setObjectName("dataTable")
        table.setAlternatingRowColors(True)
        table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        table.setShowGrid(False)
        table.verticalHeader().setVisible(False)
        table.verticalHeader().setDefaultSectionSize(38)
        table.horizontalHeader().setFixedHeight(38)
        table.horizontalHeader().setStretchLastSection(False)
        table.setSortingEnabled(True)
        return table

    def _build_shortcuts(self) -> None:
        shortcuts = {
            "Ctrl+1": "Overview",
            "Ctrl+2": "Processes",
            "Ctrl+3": "Storage",
            "Ctrl+4": "Services",
            "Ctrl+5": "Startup",
            "Ctrl+6": "Cleanup",
        }
        for sequence, page in shortcuts.items():
            action = QAction(self)
            action.setShortcut(QKeySequence(sequence))
            action.triggered.connect(lambda _checked=False, target=page: self.navigate(target))
            self.addAction(action)

    def _apply_theme(self) -> None:
        self.setStyleSheet(r"""
            QWidget { color: #F0F1F1; font-family: Inter, 'Noto Sans', sans-serif; font-size: 13px; }
            QMainWindow, QWidget#root { background: #171819; }
            QFrame#sidebar { background: #1B1D1E; border-right: 1px solid #303334; }
            QFrame#topbar { background: #1A1C1D; border-bottom: 1px solid #303334; }
            QLabel#brandMark { background: #D7DBDA; color: #161819; border-radius: 10px; font-weight: 900; font-size: 20px; }
            QLabel#brandName { color: #F3F4F4; font-size: 14px; font-weight: 800; letter-spacing: 2px; }
            QLabel#brandSub { color: #83898A; font-size: 8px; letter-spacing: 1.6px; }
            QLabel#eyebrow { color: #858B8C; font-size: 10px; font-weight: 700; letter-spacing: 1.4px; }
            QLabel#brandSub, QLabel#mutedSmall { font-size: 10px; }
            QLabel#muted, QLabel#mutedSmall { color: #9AA0A1; }
            QLabel#mutedSmall { color: #7D8485; }
            QLabel#localStatus { color: #A9C6B7; font-size: 10px; font-weight: 700; letter-spacing: 0.5px; }
            QLabel#breadcrumb { font-size: 13px; font-weight: 650; color: #DBDEDE; }
            QLabel#liveTag { color: #9FBDAF; font-size: 10px; font-weight: 700; letter-spacing: 0.7px; padding: 7px 10px; background: #24302B; border: 1px solid #33453D; border-radius: 8px; }
            QPushButton#navButton { text-align: left; padding: 11px 12px; border-radius: 8px; border: 1px solid transparent; background: transparent; color: #969C9D; font-weight: 550; }
            QPushButton#navButton:hover { background: #252829; color: #ECEEEE; }
            QPushButton#navButton:checked { background: #2A2D2E; border: 1px solid #3A3E3F; color: #F4F5F5; }
            QFrame#separator { color: #303334; background: #303334; max-height: 1px; border: none; }
            QLabel#pageTitle { font-size: 27px; font-weight: 700; letter-spacing: -0.6px; color: #F0F1F1; }
            QLabel#panelTitle { font-size: 14px; font-weight: 700; color: #ECEEEE; }
            QLabel#metricValue { font-size: 29px; font-weight: 720; letter-spacing: -0.8px; }
            QFrame#metricCard { background: #202223; border: 1px solid #323637; border-radius: 12px; }
            QFrame#panel { background: #202223; border: 1px solid #323637; border-radius: 12px; }
            QFrame#noticePanel { background: #242321; border: 1px solid #4A4235; border-radius: 10px; }
            QLabel#infoValue { color: #E3E5E5; font-size: 12px; font-weight: 550; }
            QLabel#miniChip { background: #2A2D2E; border: 1px solid #393D3E; border-radius: 7px; color: #BBC0C0; padding: 5px 8px; font-size: 10px; font-weight: 700; }
            QPushButton { background: #D7DBDA; color: #17191A; border: 1px solid #E4E7E7; border-radius: 8px; padding: 0 13px; font-weight: 650; }
            QPushButton:hover { background: #F0F2F1; }
            QPushButton:pressed { background: #B8BEBC; }
            QPushButton:disabled { background: #303334; color: #686E6F; border-color: #303334; }
            QPushButton#secondaryButton { background: #292C2D; border: 1px solid #3A3E3F; color: #E0E3E3; }
            QPushButton#secondaryButton:hover { background: #333738; border-color: #4A4F50; }
            QPushButton#dangerButton { background: #422A2B; border: 1px solid #664042; color: #F2CBCB; }
            QPushButton#dangerButton:hover { background: #573234; }
            QPushButton#quickAction { background: transparent; border: 1px solid transparent; border-radius: 8px; text-align: left; }
            QPushButton#quickAction:hover { background: #282B2C; border-color: #393D3E; }
            QLabel#quickTitle { color: #E4E6E6; font-size: 12px; font-weight: 650; }
            QLabel#quickArrow { color: #9AA0A1; font-size: 16px; padding: 0 3px; }
            QLineEdit, QComboBox { background: #202223; color: #E8EAEA; border: 1px solid #363A3B; border-radius: 8px; padding: 9px 11px; selection-background-color: #59615F; min-height: 18px; }
            QLineEdit:focus, QComboBox:focus { border-color: #787F7D; }
            QComboBox::drop-down { border: none; width: 25px; }
            QComboBox QAbstractItemView { background: #242728; color: #E8EAEA; selection-background-color: #3C4142; border: 1px solid #3B3F40; }
            QTableWidget#dataTable { background: #1D1F20; alternate-background-color: #222526; border: 1px solid #323637; border-radius: 10px; outline: none; selection-background-color: #383D3E; selection-color: #FFFFFF; }
            QTableWidget#dataTable::item { padding-left: 10px; padding-right: 8px; border: none; }
            QTableWidget#dataTable::item:selected { background: #383D3E; }
            QHeaderView::section { background: #242728; color: #969D9E; border: none; border-bottom: 1px solid #383C3D; padding: 0 9px; font-size: 10px; font-weight: 700; letter-spacing: 0.7px; }
            QScrollArea#pageScroll { background: transparent; border: none; }
            QScrollBar:vertical { background: transparent; width: 10px; margin: 2px; }
            QScrollBar::handle:vertical { background: #424748; border-radius: 4px; min-height: 25px; }
            QScrollBar::handle:vertical:hover { background: #555B5C; }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
            QProgressBar { background: #2E3233; border: none; border-radius: 2px; }
            QProgressBar::chunk { background: #A7C3B5; border-radius: 2px; }
            QStatusBar { background: #191B1C; color: #878E8F; border-top: 1px solid #303334; font-size: 10px; }
            QMessageBox { background: #202223; }
            QMenu { background: #242728; border: 1px solid #3A3E3F; padding: 5px; }
            QMenu::item { padding: 7px 22px; border-radius: 5px; }
            QMenu::item:selected { background: #3B4041; }
        """)

    def navigate(self, key: str) -> None:
        if key not in self.pages:
            return
        self.stack.setCurrentWidget(self.pages[key])
        self.breadcrumb.setText(key)
        for name, button in self.nav_buttons.items():
            button.setChecked(name == key)
        if key == "Storage":
            self.refresh_disks()
        elif key == "Processes":
            self.refresh_processes()
        elif key == "Services":
            self.refresh_services()
        elif key == "Startup":
            self.refresh_startup()
        elif key == "Cleanup":
            self.refresh_cache_info()

    def _run_worker(self, function: Callable[..., Any], args: tuple[Any, ...], on_result: Callable[[Any], None], on_error: Callable[[str], None]) -> None:
        worker = Worker(function, *args)
        self._workers.append(worker)
        worker.signals.result.connect(on_result)
        worker.signals.error.connect(on_error)
        worker.signals.finished.connect(lambda w=worker: self._discard_worker(w))
        self.thread_pool.start(worker)

    def _discard_worker(self, worker: Worker) -> None:
        try:
            self._workers.remove(worker)
        except ValueError:
            pass

    def refresh_dashboard(self) -> None:
        try:
            snapshot = system.get_system_snapshot()
        except Exception as exc:
            self.statusBar().showMessage(f"System read failed: {exc}", 5000)
            return
        self._last_snapshot = snapshot
        self._cpu_history.append(snapshot["cpu"])
        self._mem_history.append(snapshot["memory_percent"])
        self._disk_history.append(snapshot["disk_percent"])
        self._cpu_history = self._cpu_history[-60:]
        self._mem_history = self._mem_history[-60:]
        self._disk_history = self._disk_history[-60:]
        self.cpu_card.update_metric(f"{snapshot['cpu']:.0f}%", "Current total processor usage", self._cpu_history)
        self.memory_card.update_metric(f"{snapshot['memory_percent']:.0f}%", f"{system.format_bytes(snapshot['memory_used'])} of {system.format_bytes(snapshot['memory_total'])}", self._mem_history)
        self.disk_card.update_metric(f"{snapshot['disk_percent']:.0f}%", f"{system.format_bytes(snapshot['disk_used'])} used · {system.format_bytes(snapshot['disk_total'])} total", self._disk_history)
        self.process_card.update_metric(str(snapshot["process_count"]), "Processes visible to this user", [])
        self.uptime_chip.setText(f"UPTIME  {snapshot['uptime']}")
        self.info_rows["Device"].setText(snapshot["hostname"])
        self.info_rows["Operating system"].setText(snapshot["os"])
        self.info_rows["Architecture"].setText(snapshot["machine"])
        self.info_rows["Graphics"].setText(snapshot["gpu"])
        self.info_rows["Python"].setText(snapshot["python"])
        self.live_label.setText("●  LIVE SYSTEM DATA")
        self.live_label.setStyleSheet("color: #9FBDAF; font-size: 10px; font-weight: 700; letter-spacing: 0.7px; padding: 7px 10px; background: #24302B; border: 1px solid #33453D; border-radius: 8px;")

    def refresh_processes(self) -> None:
        try:
            self._process_cache = system.list_processes()
            self._render_processes()
            self.process_status.setText(f"Showing {len(self._process_cache)} process(es) · refresh to update usage samples")
        except Exception as exc:
            self.process_status.setText(f"Could not read processes: {exc}")

    def _render_processes(self) -> None:
        if not hasattr(self, "process_table"):
            return
        needle = self.process_search.text().strip().lower() if hasattr(self, "process_search") else ""
        self.process_table.setSortingEnabled(False)
        self.process_table.setRowCount(0)
        matches = [row for row in self._process_cache if not needle or needle in row["name"].lower() or needle in row["user"].lower() or needle in str(row["pid"])]
        for proc in matches:
            row = self.process_table.rowCount()
            self.process_table.insertRow(row)
            values = [str(proc["pid"]), proc["name"], proc["user"], f"{proc['cpu_percent']:.1f}%", f"{proc['memory_percent']:.1f}%"]
            for col, value in enumerate(values):
                item = QTableWidgetItem(value)
                item.setData(Qt.ItemDataRole.UserRole, proc["pid"])
                if col in {0, 3, 4}:
                    item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                self.process_table.setItem(row, col, item)
        self.process_table.setSortingEnabled(True)
        self.process_status.setText(f"{len(matches)} shown · {len(self._process_cache)} sampled · only normal termination is available")

    def terminate_selected_process(self) -> None:
        selected = self.process_table.selectionModel().selectedRows()
        if not selected:
            QMessageBox.information(self, "Select a process", "Choose a process row first.")
            return
        row = selected[0].row()
        pid_item = self.process_table.item(row, 0)
        try:
            pid = int(pid_item.text())
        except (ValueError, AttributeError):
            QMessageBox.warning(self, "Invalid selection", "Could not read the selected process ID.")
            return
        name = self.process_table.item(row, 1).text()
        answer = QMessageBox.question(
            self,
            "End process?",
            f"Send a normal termination signal to {name} (PID {pid})?\n\nUnsaved work in that application may be lost.",
            QMessageBox.StandardButton.Cancel | QMessageBox.StandardButton.Yes,
            QMessageBox.StandardButton.Cancel,
        )
        if answer != QMessageBox.StandardButton.Yes:
            return
        try:
            system.terminate_process(pid)
            self.statusBar().showMessage(f"Termination signal sent to {name} (PID {pid}).", 5000)
            QTimer.singleShot(450, self.refresh_processes)
        except Exception as exc:
            QMessageBox.warning(self, "Could not end process", str(exc))

    def refresh_disks(self) -> None:
        while self.disk_grid.count():
            item = self.disk_grid.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
        try:
            disks = system.list_disks()
        except Exception as exc:
            label = QLabel(f"Could not read mounted disks: {exc}")
            label.setObjectName("muted")
            self.disk_grid.addWidget(label, 0, 0)
            return
        if not disks:
            label = QLabel("No readable mounted disks were found.")
            label.setObjectName("muted")
            self.disk_grid.addWidget(label, 0, 0)
            return
        for i, disk in enumerate(disks):
            card = QFrame()
            card.setObjectName("metricCard")
            v = QVBoxLayout(card)
            v.setContentsMargins(15, 14, 15, 14)
            header = QHBoxLayout()
            path = QLabel(disk["mountpoint"])
            path.setObjectName("panelTitle")
            fs = QLabel(disk["fstype"])
            fs.setObjectName("miniChip")
            header.addWidget(path, 1)
            header.addWidget(fs)
            value = QLabel(f"{disk['percent']:.0f}% used")
            value.setObjectName("metricValue")
            value.setStyleSheet("font-size: 22px;")
            p = QProgressBar()
            p.setRange(0, 100)
            p.setValue(int(disk["percent"]))
            p.setTextVisible(False)
            p.setFixedHeight(5)
            v.addLayout(header)
            v.addWidget(value)
            v.addWidget(p)
            desc = QLabel(f"{system.format_bytes(disk['used'])} used · {system.format_bytes(disk['free'])} free")
            desc.setObjectName("mutedSmall")
            v.addWidget(desc)
            self.disk_grid.addWidget(card, i // 2, i % 2)
        for column in range(2):
            self.disk_grid.setColumnStretch(column, 1)

    def choose_scan_folder(self) -> None:
        start = str(Path.home())
        selected = QFileDialog.getExistingDirectory(self, "Choose a folder to inspect", start)
        if not selected:
            return
        self._scan_path = selected
        self.scan_path_label.setText(selected)
        self.scan_title.setText("Scanning folder…")
        self.scan_status.setText("Reading file sizes in the background. Large folders may take a while.")
        self.scan_table.setRowCount(0)
        self._run_worker(system.scan_directory, (selected,), self._scan_finished, self._scan_failed)

    def _scan_finished(self, result: dict[str, Any]) -> None:
        self.scan_title.setText(f"Folder analysis · {system.format_bytes(result['total'])}")
        self.scan_path_label.setText(result["root"])
        self.scan_table.setSortingEnabled(False)
        self.scan_table.setRowCount(0)
        for entry in result["entries"]:
            row = self.scan_table.rowCount()
            self.scan_table.insertRow(row)
            for col, value in enumerate((entry["name"], entry["kind"], system.format_bytes(entry["size"]), entry["path"])):
                item = QTableWidgetItem(value)
                item.setData(Qt.ItemDataRole.UserRole, entry["path"])
                self.scan_table.setItem(row, col, item)
        self.scan_table.setSortingEnabled(True)
        self.scan_status.setText(f"Counted {result['files_counted']} file(s) · top-level entries are sorted by size · scan is read-only")

    def _scan_failed(self, error: str) -> None:
        self.scan_title.setText("Folder analysis failed")
        self.scan_status.setText(error)

    def refresh_services(self, *_args: Any) -> None:
        if not hasattr(self, "service_table"):
            return
        scope = str(self.service_scope.currentData())
        self.services_status.setText("Loading services…")
        for button in self.service_action_buttons:
            button.setEnabled(False)
        self._run_worker(system.list_services, (scope,), self._services_loaded, self._services_failed)

    def _services_loaded(self, rows: list[dict[str, str]]) -> None:
        self._service_cache = rows
        scope = str(self.service_scope.currentData())
        self.service_table.setSortingEnabled(False)
        self.service_table.setRowCount(0)
        for service in rows:
            row = self.service_table.rowCount()
            self.service_table.insertRow(row)
            values = [service["unit"], service["active"], service["sub"], service["description"]]
            for col, value in enumerate(values):
                item = QTableWidgetItem(value)
                item.setData(Qt.ItemDataRole.UserRole, service["unit"])
                if col == 1:
                    color = GREEN if value == "active" else (AMBER if value == "activating" else MUTED)
                    item.setForeground(QColor(color))
                self.service_table.setItem(row, col, item)
        self.service_table.setSortingEnabled(True)
        for button in self.service_action_buttons:
            button.setEnabled(True)
        scope_label = "user" if scope == "user" else "system"
        self.services_status.setText(f"{len(rows)} loaded {scope_label} service(s) · systemd only · no automatic changes")

    def _services_failed(self, error: str) -> None:
        self._service_cache = []
        self.service_table.setRowCount(0)
        self.services_status.setText(f"Service list unavailable: {error}")
        for button in self.service_action_buttons:
            button.setEnabled(False)

    def run_service_action(self, action: str) -> None:
        selected = self.service_table.selectionModel().selectedRows()
        if not selected:
            QMessageBox.information(self, "Select a service", "Choose a service row first.")
            return
        row = selected[0].row()
        item = self.service_table.item(row, 0)
        if item is None:
            return
        unit = item.text()
        scope = str(self.service_scope.currentData())
        if action == "stop":
            warning = "Stopping a service may disable a desktop feature or interrupt a connection."
        elif action == "restart":
            warning = "Restarting a service briefly interrupts that service."
        else:
            warning = "Starting a service will change its current runtime state."
        if scope == "system":
            warning += "\n\nA system authentication dialog will appear. Only continue if you recognize this service."
        answer = QMessageBox.question(
            self,
            f"{action.title()} service?",
            f"{action.title()} {unit}?\n\n{warning}",
            QMessageBox.StandardButton.Cancel | QMessageBox.StandardButton.Yes,
            QMessageBox.StandardButton.Cancel,
        )
        if answer != QMessageBox.StandardButton.Yes:
            return
        self.services_status.setText(f"Requesting {action} for {unit}…")
        self._run_worker(self._service_action_worker, (unit, scope, action), self._service_action_done, self._service_action_failed)

    @staticmethod
    def _service_action_worker(unit: str, scope: str, action: str) -> str:
        return system.service_action(unit, scope, action)

    def _service_action_done(self, result: str) -> None:
        self.statusBar().showMessage(result or "Service action completed.", 5000)
        self.refresh_services()

    def _service_action_failed(self, error: str) -> None:
        self.services_status.setText(f"Service action failed: {error}")
        QMessageBox.warning(self, "Service action failed", error)

    def refresh_startup(self) -> None:
        try:
            self._startup_cache = system.list_startup_apps()
            self.startup_table.setSortingEnabled(False)
            self.startup_table.setRowCount(0)
            for entry in self._startup_cache:
                row = self.startup_table.rowCount()
                self.startup_table.insertRow(row)
                enabled = bool(entry["enabled"])
                values = [str(entry["name"]), "Enabled" if enabled else "Disabled", str(entry["file"])]
                for col, value in enumerate(values):
                    item = QTableWidgetItem(value)
                    item.setData(Qt.ItemDataRole.UserRole, entry["path"])
                    if col == 1:
                        item.setForeground(QColor(GREEN if enabled else AMBER))
                    self.startup_table.setItem(row, col, item)
            self.startup_table.setSortingEnabled(True)
            self.startup_status.setText(f"{len(self._startup_cache)} startup entry/entries · only your user startup folder is managed")
        except Exception as exc:
            self.startup_status.setText(f"Could not read startup entries: {exc}")

    def toggle_selected_startup(self, enabled: bool) -> None:
        selected = self.startup_table.selectionModel().selectedRows()
        if not selected:
            QMessageBox.information(self, "Select an entry", "Choose a startup entry row first.")
            return
        row = selected[0].row()
        path_item = self.startup_table.item(row, 0)
        if path_item is None:
            return
        path = path_item.data(Qt.ItemDataRole.UserRole)
        try:
            note = system.toggle_startup(str(path), enabled)
            self.startup_status.setText(note)
            self.refresh_startup()
        except Exception as exc:
            QMessageBox.warning(self, "Could not change startup entry", str(exc))

    def refresh_cache_info(self) -> None:
        if not hasattr(self, "cache_size_label"):
            return
        self.cache_progress.show()
        self.cache_detail_label.setText("Calculating folder sizes in the background…")
        self._run_worker(system.get_cache_info, (), self._cache_info_loaded, self._cache_info_failed)

    def _cache_info_loaded(self, result: dict[str, Any]) -> None:
        self.cache_progress.hide()
        self.cache_size_label.setText(system.format_bytes(result["size"]))
        self.cache_path_label.setText(result["path"])
        self.cache_detail_label.setText(f"{result['items']} top-level cache entries · size is approximate if some files are inaccessible")

    def _cache_info_failed(self, error: str) -> None:
        self.cache_progress.hide()
        self.cache_size_label.setText("Unavailable")
        self.cache_detail_label.setText(error)

    def clear_cache_confirmed(self) -> None:
        cache_path = system.get_cache_directory()
        answer = QMessageBox.warning(
            self,
            "Clear user cache?",
            f"Forge will remove the contents of this directory only:\n\n{cache_path}\n\nApplications may need to rebuild cache files. This can include per-user caches such as pip; it does not delete your Downloads folder, personal documents, system files or system package archives outside this directory. Close applications that are actively using large caches before proceeding.\n\nContinue?",
            QMessageBox.StandardButton.Cancel | QMessageBox.StandardButton.Yes,
            QMessageBox.StandardButton.Cancel,
        )
        if answer != QMessageBox.StandardButton.Yes:
            return
        self.cache_detail_label.setText("Clearing user cache…")
        self._run_worker(system.clear_user_cache, (), self._cache_cleared, self._cache_info_failed)

    def _cache_cleared(self, result: dict[str, Any]) -> None:
        errors = result.get("errors", [])
        self.cache_detail_label.setText(f"Removed {result['removed']} top-level item(s). " + (f"Some entries could not be removed: {'; '.join(errors[:3])}" if errors else "Cache cleanup completed."))
        self.refresh_cache_info()


def main() -> int:
    app = QApplication(sys.argv)
    app.setApplicationName("Forge")
    app.setOrganizationName("Forge")
    app.setApplicationDisplayName("Forge · System Center")
    app.setStyle("Fusion")
    font = QFont("Inter", 10)
    app.setFont(font)
    window = ForgeWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
