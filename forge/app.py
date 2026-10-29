from __future__ import annotations

import csv
import json
import platform
import sys
import time
from pathlib import Path
from typing import Any

from PySide6.QtCore import QByteArray, Qt, QTimer, QSize, QRectF
from PySide6.QtGui import QColor, QFont, QIcon, QKeySequence, QPainter, QPixmap, QPainterPath, QPen, QShortcut
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QFrame, QLabel, QPushButton,
    QToolButton, QLineEdit, QComboBox, QStackedWidget, QVBoxLayout,
    QHBoxLayout, QGridLayout, QTableWidget, QTableWidgetItem, QHeaderView,
    QMessageBox, QFileDialog, QProgressBar, QSizePolicy, QAbstractItemView,
    QSplitter, QScrollArea, QPlainTextEdit, QSpinBox, QSlider,
    QDialog, QListWidget, QListWidgetItem,
)

from . import __version__, advanced, system

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


THEME_PALETTES = {
    "graphite": {"BG": "#111218", "SIDEBAR": "#15161d", "PANEL": "#1a1b24", "PANEL_HOVER": "#22232e", "BORDER": "#2b2c38", "TEXT": "#f2f1f8", "MUTED": "#a09fb2", "SOFT": "#6f7083", "PURPLE_DARK": "#28243e", "GREEN": "#83d6b0", "AMBER": "#e9c27a", "RED": "#f08a9a"},
    "midnight": {"BG": "#0b111c", "SIDEBAR": "#101827", "PANEL": "#141f30", "PANEL_HOVER": "#1b2b42", "BORDER": "#293a50", "TEXT": "#eef4ff", "MUTED": "#a0b0c5", "SOFT": "#71839c", "PURPLE_DARK": "#1b3048", "GREEN": "#75dcc0", "AMBER": "#f2c875", "RED": "#ff8d9e"},
    "emerald": {"BG": "#101713", "SIDEBAR": "#141e19", "PANEL": "#1a2720", "PANEL_HOVER": "#24342b", "BORDER": "#304438", "TEXT": "#edf7ef", "MUTED": "#a5b9aa", "SOFT": "#758b7b", "PURPLE_DARK": "#203c31", "GREEN": "#83d6b0", "AMBER": "#e9c27a", "RED": "#f08a9a"},
    "light": {"BG": "#f0f1f7", "SIDEBAR": "#e5e7f0", "PANEL": "#ffffff", "PANEL_HOVER": "#e5e4f1", "BORDER": "#d4d6e3", "TEXT": "#272635", "MUTED": "#68697d", "SOFT": "#86879a", "PURPLE_DARK": "#e7e2ff", "GREEN": "#247c5a", "AMBER": "#9a6812", "RED": "#b73351"},
}
ACCENT_OPTIONS = {
    "Лавандовый": "#a99bff", "Голубой": "#82b7ff", "Мятный": "#83d6b0",
    "Розовый": "#f0b7cf", "Янтарный": "#f0c674", "Коралловый": "#ff879d",
    "Бирюзовый": "#65d4d0",
}
LIQUID_GLASS_QSS = r"""
/* Liquid Glass for Forge. Qt alpha values range from 0 to 255. */
#sidebar {
    background-color: rgba(20, 21, 32, 218);
    border-right: 1px solid rgba(190, 179, 255, 58);
}
#topbar {
    background-color: rgba(17, 18, 28, 218);
    border-bottom: 1px solid rgba(190, 179, 255, 55);
}
#panel, #metricCard, #systemChip {
    background-color: rgba(29, 30, 45, 184);
    border: 1px solid rgba(196, 184, 255, 66);
    border-radius: 16px;
}
#hero {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 rgba(91, 76, 145, 192),
        stop:0.52 rgba(34, 32, 52, 205),
        stop:1 rgba(20, 22, 34, 218));
    border: 1px solid rgba(202, 190, 255, 100);
    border-radius: 18px;
}
#navButton {
    background-color: rgba(255, 255, 255, 0);
    border: 1px solid rgba(190, 179, 255, 0);
    border-radius: 10px;
}
#navButton:hover {
    background-color: rgba(255, 255, 255, 18);
    border-color: rgba(190, 179, 255, 58);
}
#navButton:checked {
    background-color: rgba(144, 124, 220, 78);
    border: 1px solid rgba(190, 179, 255, 178);
}
#secondaryButton, #quickButton {
    background-color: rgba(255, 255, 255, 15);
    border: 1px solid rgba(205, 197, 255, 64);
    border-radius: 10px;
}
#secondaryButton:hover, #quickButton:hover {
    background-color: rgba(169, 155, 255, 38);
    border-color: rgba(205, 197, 255, 135);
}
#primaryButton {
    border-radius: 10px;
    border: 1px solid rgba(230, 223, 255, 180);
}
QLineEdit, QComboBox, QSpinBox, QPlainTextEdit, QTableWidget, QListWidget {
    background-color: rgba(18, 19, 30, 220);
    border: 1px solid rgba(190, 179, 255, 70);
    border-radius: 9px;
    selection-background-color: rgba(133, 112, 215, 180);
    selection-color: #ffffff;
}
QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QPlainTextEdit:focus {
    border: 1px solid rgba(190, 179, 255, 220);
    background-color: rgba(25, 25, 41, 232);
}
QComboBox::drop-down {
    subcontrol-origin: padding;
    subcontrol-position: top right;
    width: 26px;
    border-left: 1px solid rgba(190, 179, 255, 55);
    background-color: rgba(255, 255, 255, 8);
    border-top-right-radius: 8px;
    border-bottom-right-radius: 8px;
}
QComboBox::drop-down:hover {
    background-color: rgba(169, 155, 255, 32);
}
QComboBox QAbstractItemView {
    background-color: rgb(27, 28, 42);
    color: #f2f1f8;
    border: 1px solid rgba(190, 179, 255, 135);
    border-radius: 8px;
    padding: 5px;
    selection-background-color: rgba(133, 112, 215, 185);
    outline: 0;
}
QSpinBox::up-button, QSpinBox::down-button {
    subcontrol-origin: border;
    width: 20px;
    border: 0;
    background-color: rgba(255, 255, 255, 8);
}
QSpinBox::up-button {
    subcontrol-position: top right;
    margin: 2px 2px 0 0;
    border-top-right-radius: 6px;
}
QSpinBox::down-button {
    subcontrol-position: bottom right;
    margin: 0 2px 2px 0;
    border-bottom-right-radius: 6px;
}
QSpinBox::up-button:hover, QSpinBox::down-button:hover {
    background-color: rgba(169, 155, 255, 46);
}
QHeaderView::section {
    background-color: rgba(255, 255, 255, 14);
    color: #c4c1d6;
    border: 0;
    border-bottom: 1px solid rgba(190, 179, 255, 66);
}
QScrollBar:vertical, QScrollBar:horizontal {
    background-color: rgba(255, 255, 255, 10);
    border: 0;
    border-radius: 5px;
}
QScrollBar:vertical { width: 9px; margin: 2px; }
QScrollBar:horizontal { height: 9px; margin: 2px; }
QScrollBar::handle:vertical, QScrollBar::handle:horizontal {
    background-color: rgba(190, 179, 255, 105);
    border-radius: 4px;
    min-width: 24px;
    min-height: 24px;
}
QScrollBar::handle:vertical:hover, QScrollBar::handle:horizontal:hover {
    background-color: rgba(190, 179, 255, 165);
}
QScrollBar::add-line, QScrollBar::sub-line {
    width: 0;
    height: 0;
    border: 0;
}
QToolTip {
    color: #f2f1f8;
    background-color: rgb(32, 31, 48);
    border: 1px solid rgba(190, 179, 255, 150);
    border-radius: 6px;
    padding: 5px 8px;
}
"""

FONT_SIZE = 13
SIDEBAR_WIDTH = 238


def apply_palette(settings: dict[str, Any]) -> None:
    global BG, SIDEBAR, PANEL, PANEL_HOVER, BORDER, TEXT, MUTED, SOFT
    global PURPLE, PURPLE_DARK, GREEN, AMBER, RED, FONT_SIZE, SIDEBAR_WIDTH
    palette = THEME_PALETTES.get(str(settings.get("theme", "graphite")), THEME_PALETTES["graphite"])
    BG = palette["BG"]
    SIDEBAR = palette["SIDEBAR"]
    PANEL = palette["PANEL"]
    PANEL_HOVER = palette["PANEL_HOVER"]
    BORDER = palette["BORDER"]
    TEXT = palette["TEXT"]
    MUTED = palette["MUTED"]
    SOFT = palette["SOFT"]
    GREEN = palette["GREEN"]
    AMBER = palette["AMBER"]
    RED = palette["RED"]
    PURPLE = str(settings.get("accent", "#a99bff"))
    PURPLE_DARK = palette["PURPLE_DARK"]
    FONT_SIZE = max(10, min(17, int(settings.get("font_size", 13))))
    SIDEBAR_WIDTH = max(190, min(310, int(settings.get("sidebar_width", 238))))

# Tabler-style outline icons, rendered locally. No network or icon-font dependency.
ICON_PATHS = {
    "network": '<path d="M5 6h4v4h-4z" /><path d="M15 14h4v4h-4z" /><path d="M7 10v4h10" /><path d="M17 14V9h-2" /><path d="M14 6h.01" />',
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
        self.icon_name = icon_name
        self.color = color
        self.mark = QLabel()
        self.mark.setPixmap(icon(icon_name, color, 19).pixmap(19, 19))
        top.addWidget(self.mark)
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

    def set_color(self, color: str) -> None:
        self.color = color
        self.mark.setPixmap(icon(self.icon_name, color, 19).pixmap(19, 19))
        self.bar.setStyleSheet(f"QProgressBar{{background:{BORDER};border:0;border-radius:2px}} QProgressBar::chunk{{background:{color};border-radius:2px}}")

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




class WallpaperHost(QWidget):
    """Paint a local wallpaper behind the transparent content surface."""
    def __init__(self) -> None:
        super().__init__()
        self._wallpaper = QPixmap()
        self._wallpaper_strength = 18
        self.setObjectName("root")
        self.setAutoFillBackground(False)

    def set_wallpaper(self, path: str, strength: int) -> None:
        candidate = Path(path).expanduser() if path else Path()
        self._wallpaper = QPixmap(str(candidate)) if path and candidate.is_file() else QPixmap()
        self._wallpaper_strength = max(0, min(70, int(strength)))
        self.update()

    def paintEvent(self, event: Any) -> None:
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor(BG))
        if not self._wallpaper.isNull() and self._wallpaper_strength > 0 and self.width() > 0 and self.height() > 0:
            scaled = self._wallpaper.scaled(self.size(), Qt.AspectRatioMode.KeepAspectRatioByExpanding, Qt.TransformationMode.SmoothTransformation)
            painter.setOpacity(self._wallpaper_strength / 100.0)
            painter.drawPixmap((self.width() - scaled.width()) // 2, (self.height() - scaled.height()) // 2, scaled)
        painter.end()


class HistoryChart(QFrame):
    def __init__(self, title: str, color: str, points: int = 120) -> None:
        super().__init__()
        self.title = title
        self.color = color
        self.points = max(30, min(360, int(points)))
        self.values: list[float | None] = []
        self.setMinimumHeight(174)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setObjectName("historyChart")

    def add_value(self, value: float | None) -> None:
        self.values.append(None if value is None else max(0.0, min(100.0, float(value))))
        self.values = self.values[-self.points:]
        self.update()

    def paintEvent(self, event: Any) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = QRectF(self.rect()).adjusted(0.5, 0.5, -0.5, -0.5)
        glass_enabled = "/* Liquid Glass for Forge." in str(
            getattr(self.window(), "preferences", {}).get("custom_qss", "")
        )
        chart_fill = QColor(PANEL)
        chart_border = QColor(BORDER)
        radius = 16 if glass_enabled else 11
        if glass_enabled:
            chart_fill.setAlpha(184)
            chart_border.setAlpha(115)
        painter.setPen(QPen(chart_border, 1))
        painter.setBrush(chart_fill)
        painter.drawRoundedRect(rect, radius, radius)
        painter.setPen(QColor(TEXT))
        painter.setFont(QFont("Inter", 10, QFont.Weight.DemiBold))
        painter.drawText(QRectF(16, 12, self.width() - 32, 20), Qt.AlignmentFlag.AlignLeft, self.title)
        latest = self.values[-1] if self.values else None
        current = f"{latest:.0f}%" if latest is not None else "—"
        painter.setPen(QColor(self.color))
        painter.setFont(QFont("Inter", 11, QFont.Weight.Bold))
        painter.drawText(QRectF(16, 12, self.width() - 32, 20), Qt.AlignmentFlag.AlignRight, current)
        left, right, top, bottom = 16.0, self.width() - 16.0, 42.0, self.height() - 18.0
        painter.setPen(QPen(QColor(BORDER), 1, Qt.PenStyle.DotLine))
        for fraction in (0.0, 0.5, 1.0):
            y = bottom - (bottom - top) * fraction
            painter.drawLine(int(left), int(y), int(right), int(y))
        if len(self.values) > 1:
            path = QPainterPath()
            previous_valid = False
            for index, value in enumerate(self.values):
                if value is None:
                    previous_valid = False
                    continue
                x = left + (right - left) * index / (len(self.values) - 1)
                y = bottom - (bottom - top) * value / 100.0
                if not previous_valid:
                    path.moveTo(x, y)
                else:
                    path.lineTo(x, y)
                previous_valid = True
            painter.setPen(QPen(QColor(self.color), 2.2, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin))
            painter.drawPath(path)
        painter.end()


class CommandPalette(QDialog):
    """Searchable command list opened with Ctrl+K."""

    def __init__(self, commands: list[tuple[str, str]], parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.commands = commands
        self.selected_command = ""
        self.setWindowTitle("Команды Forge")
        self.setModal(True)
        self.setMinimumWidth(560)
        self.setMinimumHeight(360)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(10)
        title = QLabel("Быстрые команды")
        title.setObjectName("panelTitle")
        layout.addWidget(title)
        self.search = QLineEdit()
        self.search.setPlaceholderText("Введи название раздела или действия…")
        self.search.setClearButtonEnabled(True)
        layout.addWidget(self.search)
        self.command_list = QListWidget()
        self.command_list.setMinimumHeight(250)
        self.command_list.setSpacing(3)
        layout.addWidget(self.command_list)
        hint = QLabel("Enter · выполнить    Esc · закрыть")
        hint.setObjectName("mutedSmall")
        layout.addWidget(hint)
        self.search.textChanged.connect(self.filter_commands)
        self.search.returnPressed.connect(self.activate_current)
        self.command_list.itemActivated.connect(self.activate_item)
        self.filter_commands("")
        self.search.setFocus()

    def filter_commands(self, query: str) -> None:
        needle = query.casefold().strip()
        self.command_list.clear()
        for label, command in self.commands:
            if needle and needle not in label.casefold():
                continue
            item = QListWidgetItem(label)
            item.setData(Qt.ItemDataRole.UserRole, command)
            self.command_list.addItem(item)
        if self.command_list.count():
            self.command_list.setCurrentRow(0)

    def activate_current(self) -> None:
        item = self.command_list.currentItem()
        if item is not None:
            self.selected_command = str(item.data(Qt.ItemDataRole.UserRole) or "")
            self.accept()

    def activate_item(self, item: QListWidgetItem) -> None:
        self.selected_command = str(item.data(Qt.ItemDataRole.UserRole) or "")
        self.accept()


class ForgeWindow(QMainWindow):
    NAV = [
        ("Обзор", "overview", "Обзор"),
        ("Процессы", "process", "Процессы"),
        ("Накопители", "disk", "Накопители"),
        ("Оборудование", "cpu", "Оборудование"),
        ("Мониторинг", "cpu", "Мониторинг"),
        ("История", "refresh", "История"),
        ("Сеть", "network", "Сеть"),
        ("Службы", "services", "Службы"),
        ("Автозапуск", "startup", "Автозапуск"),
        ("Очистка", "cleanup", "Очистка"),
        ("Диагностика", "info", "Диагностика"),
        ("Внешний вид", "settings", "Внешний вид"),
    ]

    def __init__(self, preferences: dict[str, Any] | None = None) -> None:
        super().__init__()
        self.preferences = dict(preferences or advanced.load_preferences())
        apply_palette(self.preferences)
        self.setWindowTitle("Forge · Центр системы")
        self.setMinimumSize(1040, 700)
        self.resize(1360, 860)
        self.setWindowIcon(QIcon(str(APP_ROOT / "assets" / "forge.svg")))
        self.process_rows: list[dict[str, Any]] = []
        self._network_previous: dict[str, Any] | None = None
        self._last_alert_signature = ""
        self.service_rows: list[dict[str, Any]] = []
        self.startup_rows: list[dict[str, Any]] = []
        self._last_history_record = 0.0
        self._history_record_interval = 15.0
        self._build_ui()
        self._apply_theme()
        self.refresh_dashboard()
        self.refresh_processes()
        self.timer = QTimer(self)
        self.timer.setInterval(int(self.preferences.get("refresh_ms", 2500)))
        self.timer.timeout.connect(self.refresh_dashboard)
        self.timer.start()
        self.statusBar().showMessage("Данные остаются на этом компьютере", 5000)

    def _build_ui(self) -> None:
        shell = WallpaperHost()
        self.wallpaper_host = shell
        shell.set_wallpaper(str(self.preferences.get("wallpaper", "")), int(self.preferences.get("wallpaper_strength", 18)))
        shell_layout = QHBoxLayout(shell)
        shell_layout.setContentsMargins(0, 0, 0, 0)
        shell_layout.setSpacing(0)

        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(SIDEBAR_WIDTH)
        self.sidebar = sidebar
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
        self.command_button = self._button("Команды · Ctrl+K", icon_name="search")
        self.command_button.clicked.connect(self.show_command_palette)
        top.addWidget(self.command_button)
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
        self.command_shortcut = QShortcut(QKeySequence("Ctrl+K"), self)
        self.command_shortcut.activated.connect(self.show_command_palette)

        self._page_overview()
        self._page_processes()
        self._page_disks()
        self._page_services()
        self._page_startup()
        self._page_cleanup()
        self._page_hardware()
        self._page_monitoring()
        self._page_history()
        self._page_network()
        self._page_diagnostics()
        self._page_appearance()
        self.navigate("Обзор")

    def _scroll_page(self) -> tuple[QWidget, QVBoxLayout]:
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        inner = QWidget()
        # Allow cards to shrink to the viewport instead of forcing horizontal scrolling.
        inner.setMinimumWidth(0)
        inner.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Preferred)
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
        elif page == "Оборудование":
            self.refresh_hardware()
        elif page == "История":
            self.refresh_history()
        elif page == "Мониторинг":
            self.refresh_sensors()
        elif page == "Сеть":
            self.refresh_network(reset=True)
        elif page == "Диагностика":
            self.refresh_diagnostics()
        elif page == "Внешний вид":
            self._sync_appearance_controls()

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
            if hasattr(self, "cpu_history"):
                self.cpu_history.add_value(data["cpu"])
                self.ram_history.add_value(data["memory_percent"])
            history_now = time.monotonic()
            if history_now - self._last_history_record >= self._history_record_interval:
                gpu_percent = None
                try:
                    gpu_data = advanced.get_sensor_snapshot().get("gpu")
                    if gpu_data:
                        gpu_percent = gpu_data.get("utilization")
                except Exception:
                    pass
                advanced.record_performance_sample({
                    "cpu": data["cpu"],
                    "memory": data["memory_percent"],
                    "disk": data["disk_percent"],
                    "gpu": gpu_percent,
                })
                self._last_history_record = history_now
                if self.stack.currentWidget() == self.pages.get("История"):
                    self.refresh_history()
            if self.stack.currentWidget() == self.pages.get("Сеть"):
                self.refresh_network()
            if self.stack.currentWidget() == self.pages.get("Мониторинг"):
                self.refresh_sensors()
            if self.stack.currentWidget() == self.pages.get("Диагностика"):
                self.refresh_diagnostics()
            warnings: list[str] = []
            if data["cpu"] >= 90:
                warnings.append(f"высокая загрузка CPU ({data['cpu']:.0f}%)")
            if data["memory_percent"] >= 90:
                warnings.append(f"мало свободной памяти ({data['memory_percent']:.0f}% занято)")
            if data["disk_percent"] >= 95:
                warnings.append(f"мало места на системном диске ({data['disk_percent']:.0f}% занято)")
            alert_signature = "|".join(warnings)
            if warnings:
                self.top_status.setText("●  ЕСТЬ ПРЕДУПРЕЖДЕНИЯ")
                self.top_status.setStyleSheet(f"color: {RED}; background: {PANEL}; border: 1px solid {RED}; padding: 7px 10px; border-radius: 7px; font-size: 10px; font-weight: 700;")
                if alert_signature != self._last_alert_signature:
                    advanced.log_event("Системное предупреждение: " + "; ".join(warnings), "WARNING")
            else:
                self.top_status.setText("●  СИСТЕМА ДОСТУПНА")
                self.top_status.setStyleSheet("")
            self._last_alert_signature = alert_signature
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
            advanced.log_event(f"Отправлен сигнал завершения: {name} (PID {pid})")
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
            advanced.log_event(f"Действие службы {unit}: {action} ({scope})")
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
            advanced.log_event(f"Очистка пользовательского кэша: обработано элементов {result['removed']}")
            text = f"Обработано элементов: {result['removed']}."
            if result["errors"]:
                text += "\n\nНе удалось удалить:\n" + "\n".join(result["errors"][:8])
            QMessageBox.information(self, "Результат очистки", text)
            self.refresh_cache_info()
        except Exception as exc:
            QMessageBox.warning(self, "Очистка не выполнена", str(exc))


    def _page_monitoring(self) -> None:
        page, layout = self._scroll_page()
        refresh = self._button("Обновить датчики", icon_name="refresh")
        refresh.clicked.connect(self.refresh_sensors)
        layout.addWidget(Heading("Мониторинг", "История нагрузки и данные датчиков, которые реально доступны системе.", refresh))
        charts = QGridLayout()
        charts.setSpacing(12)
        self.cpu_history = HistoryChart("Загрузка процессора", PURPLE, int(self.preferences.get("history_points", 120)))
        self.ram_history = HistoryChart("Использование памяти", GREEN, int(self.preferences.get("history_points", 120)))
        self.gpu_history = HistoryChart("Загрузка NVIDIA GPU", "#82b7ff", int(self.preferences.get("history_points", 120)))
        charts.addWidget(self.cpu_history, 0, 0)
        charts.addWidget(self.ram_history, 0, 1)
        charts.addWidget(self.gpu_history, 1, 0)
        layout.addLayout(charts)
        sensors, sensor_layout = self._card("Температуры и вентиляторы", "Набор датчиков зависит от оборудования, драйверов и прав доступа.")
        self.sensor_table = self._table(["ДАТЧИК", "ИСТОЧНИК", "ТЕМПЕРАТУРА"])
        self.sensor_table.setColumnWidth(0, 230)
        self.sensor_table.setColumnWidth(1, 210)
        sensor_layout.addWidget(self.sensor_table)
        self.gpu_metrics = QLabel("Данные GPU: проверка при открытии раздела.")
        self.gpu_metrics.setObjectName("muted")
        self.gpu_metrics.setWordWrap(True)
        sensor_layout.addWidget(self.gpu_metrics)
        self.fan_metrics = QLabel("Данные вентиляторов: проверка при открытии раздела.")
        self.fan_metrics.setObjectName("mutedSmall")
        self.fan_metrics.setWordWrap(True)
        sensor_layout.addWidget(self.fan_metrics)
        layout.addWidget(sensors)
        layout.addStretch(1)
        self.pages["Мониторинг"] = page
        self.stack.addWidget(page)

    def _page_hardware(self) -> None:
        page, layout = self._scroll_page()
        refresh = self._button("Обновить сведения", icon_name="refresh")
        refresh.clicked.connect(self.refresh_hardware)
        layout.addWidget(Heading("Оборудование", "Процессор, память, графика, питание и датчики, которые действительно доступны операционной системе.", refresh))

        cards = QGridLayout()
        cards.setSpacing(12)
        self.hardware_cpu_card = MetricCard("ЗАГРУЗКА CPU", "cpu", PURPLE)
        self.hardware_memory_card = MetricCard("ОПЕРАТИВНАЯ ПАМЯТЬ", "memory", GREEN)
        self.hardware_swap_card = MetricCard("ФАЙЛ ПОДКАЧКИ / SWAP", "disk", AMBER)
        cards.addWidget(self.hardware_cpu_card, 0, 0)
        cards.addWidget(self.hardware_memory_card, 0, 1)
        cards.addWidget(self.hardware_swap_card, 0, 2)
        layout.addLayout(cards)

        details, details_layout = self._card("Сведения об устройстве", "Показания зависят от драйверов, прошивки и возможностей ОС. Недоступные данные отмечаются явно.")
        self.hardware_table = self._table(["КОМПОНЕНТ", "СВЕДЕНИЯ"])
        self.hardware_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.hardware_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.hardware_table.setMinimumHeight(300)
        details_layout.addWidget(self.hardware_table)
        layout.addWidget(details)

        sensor_frame, sensor_layout = self._card("Датчики и состояние", "Forge не запрашивает повышенные права для чтения датчиков.")
        self.hardware_sensor_summary = QLabel("Данные появятся после обновления.")
        self.hardware_sensor_summary.setObjectName("muted")
        self.hardware_sensor_summary.setWordWrap(True)
        sensor_layout.addWidget(self.hardware_sensor_summary)
        layout.addWidget(sensor_frame)
        layout.addStretch(1)
        self.pages["Оборудование"] = page
        self.stack.addWidget(page)
        self.refresh_hardware()

    def refresh_hardware(self) -> None:
        if not hasattr(self, "hardware_table"):
            return
        try:
            data = advanced.get_hardware_snapshot()
            cpu_load = float(data.get("cpu_percent", 0.0))
            memory_percent = float(data.get("memory_percent", 0.0))
            swap_percent = float(data.get("swap_percent", 0.0))
            self.hardware_cpu_card.update_value(f"{cpu_load:.0f}%", f"{data['cpu_name']} · {data['logical_cores']} логических потоков", cpu_load)
            self.hardware_memory_card.update_value(fmt_bytes(data["memory_used"]), f"{memory_percent:.0f}% занято из {fmt_bytes(data['memory_total'])}", memory_percent)
            self.hardware_swap_card.update_value(fmt_bytes(data["swap_used"]), f"{swap_percent:.0f}% занято из {fmt_bytes(data['swap_total'])}", swap_percent)

            frequency = data.get("frequency_mhz")
            frequency_text = f"{frequency / 1000:.2f} ГГц" if frequency else "Не предоставляется"
            gpu = data.get("gpu")
            if gpu:
                gpu_parts = [str(gpu.get("name") or "GPU")]
                if gpu.get("utilization") is not None:
                    gpu_parts.append(f"загрузка {float(gpu['utilization']):.0f}%")
                if gpu.get("temperature") is not None:
                    gpu_parts.append(f"{float(gpu['temperature']):.0f} °C")
                if gpu.get("memory_used_mb") is not None and gpu.get("memory_total_mb"):
                    gpu_parts.append(f"VRAM {float(gpu['memory_used_mb']):.0f}/{float(gpu['memory_total_mb']):.0f} MiB")
                gpu_text = " · ".join(gpu_parts)
            else:
                gpu_text = "Название или датчики GPU недоступны"
            battery = data.get("battery")
            battery_text = (f"{battery.get('percent', 0):.0f}% · " + ("зарядка" if battery.get("plugged") else "от батареи")) if battery else "Нет батарейного датчика"
            active = data.get("active_interfaces", [])
            network_text = ", ".join(str(item.get("name", "")) for item in active[:8]) or "Активные интерфейсы не обнаружены"
            temperatures = data.get("temperatures", [])
            temperature_text = " · ".join(
                f"{item['sensor']}: {float(item['celsius']):.1f} °C"
                for item in sorted(temperatures, key=lambda item: float(item.get("celsius", -999)), reverse=True)[:8]
            ) or "Температурные датчики не предоставлены"

            rows = [
                ("Процессор", data["cpu_name"]),
                ("Физические ядра / потоки", f"{data['physical_cores']} / {data['logical_cores']}"),
                ("Текущая частота CPU", frequency_text),
                ("Операционная система", data["os"]),
                ("Архитектура", data["architecture"]),
                ("Время работы", data["uptime"]),
                ("Графика", gpu_text),
                ("Батарея", battery_text),
                ("Активные сетевые интерфейсы", network_text),
                ("Подключённые диски", str(data.get("disk_count", 0))),
            ]
            self.hardware_table.setSortingEnabled(False)
            self.hardware_table.setRowCount(len(rows))
            for index, (name, value) in enumerate(rows):
                self.hardware_table.setItem(index, 0, QTableWidgetItem(name))
                self.hardware_table.setItem(index, 1, QTableWidgetItem(value))
            self.hardware_table.setSortingEnabled(True)
            fans = data.get("fans", [])
            fan_text = " · ".join(f"{item['sensor']}: {item['rpm']} RPM" for item in fans[:8]) or "Датчики вентиляторов не предоставлены"
            self.hardware_sensor_summary.setText(f"Температуры: {temperature_text}\nВентиляторы: {fan_text}")
        except Exception as exc:
            self.statusBar().showMessage(f"Не удалось получить сведения об оборудовании: {exc}", 6000)

    def _page_history(self) -> None:
        page, layout = self._scroll_page()
        layout.addWidget(Heading("История производительности", "Локальная история CPU, памяти, диска и доступной NVIDIA GPU. Запись выполняется примерно раз в 15 секунд; данные не отправляются в сеть."))
        actions = QHBoxLayout()
        refresh = self._button("Обновить историю", icon_name="refresh")
        refresh.clicked.connect(self.refresh_history)
        export = self._button("Экспорт CSV…", "primary", "folder")
        export.clicked.connect(self.export_performance_history)
        clear = self._button("Очистить историю…", "danger", "cleanup")
        clear.clicked.connect(self.clear_performance_history)
        actions.addWidget(refresh)
        actions.addWidget(export)
        actions.addWidget(clear)
        actions.addStretch(1)
        layout.addLayout(actions)
        self.history_summary = QLabel("История пока не собрана.")
        self.history_summary.setObjectName("muted")
        self.history_summary.setWordWrap(True)
        layout.addWidget(self.history_summary)

        charts = QGridLayout()
        charts.setSpacing(12)
        points = int(self.preferences.get("history_points", 120))
        self.history_cpu_chart = HistoryChart("CPU", PURPLE, points)
        self.history_memory_chart = HistoryChart("Оперативная память", GREEN, points)
        self.history_disk_chart = HistoryChart("Занятое место на системном диске", AMBER, points)
        self.history_gpu_chart = HistoryChart("NVIDIA GPU · если доступно", "#82b7ff", points)
        charts.addWidget(self.history_cpu_chart, 0, 0)
        charts.addWidget(self.history_memory_chart, 0, 1)
        charts.addWidget(self.history_disk_chart, 1, 0)
        charts.addWidget(self.history_gpu_chart, 1, 1)
        layout.addLayout(charts)
        layout.addStretch(1)
        self.pages["История"] = page
        self.stack.addWidget(page)
        self.refresh_history()

    def refresh_history(self) -> None:
        if not hasattr(self, "history_cpu_chart"):
            return
        limit = int(self.preferences.get("history_points", 120))
        samples = advanced.read_performance_history(limit=limit)
        for chart, field in (
            (self.history_cpu_chart, "cpu"),
            (self.history_memory_chart, "memory"),
            (self.history_disk_chart, "disk"),
            (self.history_gpu_chart, "gpu"),
        ):
            chart.points = limit
            chart.values = [sample.get(field) for sample in samples]
            chart.update()
        if not samples:
            self.history_summary.setText("История пока пуста. Forge начнёт записывать первую точку автоматически; данные останутся в профиле пользователя.")
            return
        oldest = samples[0]["time"].replace("T", " ")
        newest = samples[-1]["time"].replace("T", " ")
        self.history_summary.setText(
            f"Точек на графиках: {len(samples)} · период: {oldest} — {newest} · "
            "интервал записи около 15 секунд. GPU может отсутствовать, если драйвер не предоставляет данные."
        )

    def export_performance_history(self) -> None:
        path, _ = QFileDialog.getSaveFileName(self, "Экспорт истории Forge", "forge-performance.csv", "CSV (*.csv)")
        if not path:
            return
        samples = advanced.read_performance_history(limit=50000)
        try:
            with Path(path).open("w", encoding="utf-8-sig", newline="") as stream:
                writer = csv.DictWriter(stream, fieldnames=["time", "cpu", "memory", "disk", "gpu"])
                writer.writeheader()
                writer.writerows(samples)
            advanced.log_event(f"Экспортирована история производительности: {len(samples)} точек")
            QMessageBox.information(self, "Экспорт завершён", f"Сохранено записей: {len(samples)}.")
        except OSError as exc:
            QMessageBox.warning(self, "Не удалось экспортировать историю", str(exc))

    def clear_performance_history(self) -> None:
        answer = QMessageBox.question(self, "Очистить историю?", "Удалить локальную историю производительности Forge? Это действие нельзя отменить.")
        if answer != QMessageBox.StandardButton.Yes:
            return
        try:
            advanced.clear_performance_history()
            self.refresh_history()
            advanced.log_event("Очищена история производительности")
            self.statusBar().showMessage("Локальная история производительности очищена", 5000)
        except OSError as exc:
            QMessageBox.warning(self, "Не удалось очистить историю", str(exc))

    def show_command_palette(self) -> None:
        commands = [
            ("Открыть обзор системы", "page:Обзор"),
            ("Открыть управление процессами", "page:Процессы"),
            ("Открыть накопители", "page:Накопители"),
            ("Открыть центр оборудования", "page:Оборудование"),
            ("Открыть мониторинг датчиков", "page:Мониторинг"),
            ("Открыть историю производительности", "page:История"),
            ("Открыть сетевой центр", "page:Сеть"),
            ("Открыть службы", "page:Службы"),
            ("Открыть автозапуск", "page:Автозапуск"),
            ("Открыть очистку кэша", "page:Очистка"),
            ("Открыть диагностику", "page:Диагностика"),
            ("Открыть внешний вид и настройки", "page:Внешний вид"),
            ("Обновить системные показатели", "action:refresh"),
            ("Обновить сведения об оборудовании", "action:hardware"),
            ("Обновить датчики", "action:sensors"),
            ("Обновить диагностику", "action:diagnostics"),
            ("Обновить журнал событий", "action:events"),
            ("Экспортировать историю в CSV", "action:export_history"),
        ]
        dialog = CommandPalette(commands, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self._execute_command(dialog.selected_command)

    def _execute_command(self, command: str) -> None:
        if command.startswith("page:"):
            self.navigate(command.partition(":")[2])
            return
        actions = {
            "action:refresh": self.refresh_dashboard,
            "action:hardware": self.refresh_hardware,
            "action:sensors": self.refresh_sensors,
            "action:diagnostics": self.refresh_diagnostics,
            "action:events": self.refresh_event_log,
            "action:export_history": self.export_performance_history,
        }
        action = actions.get(command)
        if action is not None:
            action()

    def refresh_sensors(self) -> None:
        if not hasattr(self, "sensor_table"):
            return
        try:
            data = advanced.get_sensor_snapshot()
            rows = data["temperatures"]
            self.sensor_table.setSortingEnabled(False)
            self.sensor_table.setRowCount(len(rows))
            for i, row in enumerate(rows):
                value = f"{row['celsius']:.1f} °C"
                critical = row.get("critical")
                if critical is not None and row["celsius"] >= float(critical):
                    value += "  ·  критично"
                for j, text in enumerate((row["sensor"], row["source"], value)):
                    item = QTableWidgetItem(text)
                    if j == 2 and "критично" in text:
                        item.setForeground(QColor(RED))
                    elif j == 2:
                        item.setForeground(QColor(AMBER if row["celsius"] >= 80 else GREEN))
                    self.sensor_table.setItem(i, j, item)
            self.sensor_table.setSortingEnabled(True)
            if not rows:
                self.sensor_table.setRowCount(1)
                self.sensor_table.setItem(0, 0, QTableWidgetItem("Датчики не обнаружены"))
                self.sensor_table.setItem(0, 1, QTableWidgetItem("ОС или оборудование не предоставили показания"))
                self.sensor_table.setItem(0, 2, QTableWidgetItem("—"))
            gpu = data.get("gpu")
            if hasattr(self, "gpu_history"):
                self.gpu_history.add_value(gpu.get("utilization") if gpu else None)
            if gpu:
                parts = [gpu.get("name", "NVIDIA GPU")]
                if gpu.get("temperature") is not None:
                    parts.append(f"температура {gpu['temperature']:.0f} °C")
                if gpu.get("utilization") is not None:
                    parts.append(f"загрузка {gpu['utilization']:.0f}%")
                if gpu.get("memory_used_mb") is not None and gpu.get("memory_total_mb"):
                    parts.append(f"видеопамять {gpu['memory_used_mb']:.0f} / {gpu['memory_total_mb']:.0f} MiB")
                if gpu.get("power_w") is not None:
                    parts.append(f"{gpu['power_w']:.1f} W")
                self.gpu_metrics.setText("GPU · " + "  •  ".join(parts))
            else:
                self.gpu_metrics.setText("GPU · дополнительные показатели доступны через nvidia-smi, если утилита и драйвер установлены.")
            fans = data.get("fans", [])
            self.fan_metrics.setText("Вентиляторы · " + ("  •  ".join(f"{x['sensor']}: {x['rpm']} RPM" for x in fans) if fans else "датчики оборотов не предоставлены системой"))
            if data.get("gpu") and data["gpu"].get("utilization") is not None:
                self.cpu_history.update()
        except Exception as exc:
            self.statusBar().showMessage(f"Мониторинг датчиков: {exc}", 6000)

    def _page_network(self) -> None:
        page, layout = self._scroll_page()
        refresh = self._button("Обновить", icon_name="refresh")
        refresh.clicked.connect(lambda: self.refresh_network(reset=True))
        layout.addWidget(Heading("Сеть", "Скорость передачи, суммарный трафик и доступные интерфейсы.", refresh))
        cards = QGridLayout()
        cards.setSpacing(12)
        download, download_layout = self._card("↓  Получено")
        self.download_value = QLabel("0 B/s")
        self.download_value.setObjectName("bigNumber")
        download_layout.addWidget(self.download_value)
        self.download_total = QLabel("Всего: —")
        self.download_total.setObjectName("muted")
        download_layout.addWidget(self.download_total)
        upload, upload_layout = self._card("↑  Отправлено")
        self.upload_value = QLabel("0 B/s")
        self.upload_value.setObjectName("bigNumber")
        upload_layout.addWidget(self.upload_value)
        self.upload_total = QLabel("Всего: —")
        self.upload_total.setObjectName("muted")
        upload_layout.addWidget(self.upload_total)
        cards.addWidget(download, 0, 0)
        cards.addWidget(upload, 0, 1)
        layout.addLayout(cards)
        interfaces, interface_layout = self._card("Сетевые интерфейсы", "Локальные адреса показываются только в этом окне и не добавляются в диагностический отчёт.")
        self.network_table = self._table(["ИНТЕРФЕЙС", "СОСТОЯНИЕ", "СКОРОСТЬ", "MTU", "IPv4"])
        self.network_table.setColumnWidth(0, 220)
        self.network_table.setColumnWidth(1, 120)
        self.network_table.setColumnWidth(2, 120)
        self.network_table.setColumnWidth(3, 90)
        interface_layout.addWidget(self.network_table)
        self.network_note = QLabel("Скорость измеряется по системным счётчикам трафика. Трафик по отдельным приложениям пока не разделяется.")
        self.network_note.setObjectName("mutedSmall")
        self.network_note.setWordWrap(True)
        interface_layout.addWidget(self.network_note)
        layout.addWidget(interfaces)
        layout.addStretch(1)
        self.pages["Сеть"] = page
        self.stack.addWidget(page)
        self.refresh_network(reset=True)

    def refresh_network(self, reset: bool = False) -> None:
        if not hasattr(self, "network_table"):
            return
        try:
            current = advanced.get_network_snapshot()
            previous = self._network_previous
            elapsed = max(0.1, current["time"] - previous["time"]) if previous and not reset else 0.1
            down_rate = max(0, current["bytes_recv"] - previous["bytes_recv"]) / elapsed if previous and not reset else 0
            up_rate = max(0, current["bytes_sent"] - previous["bytes_sent"]) / elapsed if previous and not reset else 0
            self._network_previous = current
            self.download_value.setText(f"{fmt_bytes(down_rate)}/s")
            self.upload_value.setText(f"{fmt_bytes(up_rate)}/s")
            self.download_total.setText(f"Всего получено: {fmt_bytes(current['bytes_recv'])}")
            self.upload_total.setText(f"Всего отправлено: {fmt_bytes(current['bytes_sent'])}")
            rows = current["interfaces"]
            self.network_table.setSortingEnabled(False)
            self.network_table.setRowCount(len(rows))
            for i, row in enumerate(rows):
                speed = f"{row['speed_mbps']} Мбит/с" if row["speed_mbps"] > 0 else "—"
                values = [row["name"], "Подключён" if row["is_up"] else "Не активен", speed, str(row["mtu"] or "—"), row["ipv4"] or "—"]
                for j, value in enumerate(values):
                    item = QTableWidgetItem(value)
                    if j == 1:
                        item.setForeground(QColor(GREEN if row["is_up"] else MUTED))
                    self.network_table.setItem(i, j, item)
            self.network_table.setSortingEnabled(True)
        except Exception as exc:
            self.network_note.setText(f"Не удалось получить сетевые счётчики: {exc}")

    def _page_diagnostics(self) -> None:
        page, layout = self._scroll_page()
        controls = QHBoxLayout()
        refresh = self._button("Проверить сейчас", icon_name="refresh")
        refresh.clicked.connect(self.refresh_diagnostics)
        export = self._button("Экспортировать отчёт…", "primary", "folder")
        export.clicked.connect(self.export_diagnostic_report)
        controls.addWidget(refresh)
        controls.addWidget(export)
        controls.addStretch(1)
        layout.addWidget(Heading("Диагностика", "Быстрые проверки и локальный журнал действий Forge. Отчёт не отправляется автоматически."))
        layout.addLayout(controls)
        checks, checks_layout = self._card("Проверки состояния")
        self.diag_status = QLabel("Нажми «Проверить сейчас», чтобы собрать сводку.")
        self.diag_status.setObjectName("muted")
        self.diag_status.setWordWrap(True)
        checks_layout.addWidget(self.diag_status)
        layout.addWidget(checks)
        events, events_layout = self._card("Журнал Forge", "Записываются отдельные действия внутри приложения. Это не замена журналу событий Windows или systemd.")
        self.event_view = QPlainTextEdit()
        self.event_view.setReadOnly(True)
        self.event_view.setObjectName("customQssEditor")
        self.event_view.setMinimumHeight(230)
        events_layout.addWidget(self.event_view)
        refresh_events = self._button("Обновить журнал")
        refresh_events.clicked.connect(self.refresh_event_log)
        events_layout.addWidget(refresh_events)
        layout.addWidget(events)
        layout.addStretch(1)
        self.pages["Диагностика"] = page
        self.stack.addWidget(page)
        self.refresh_diagnostics()

    def refresh_diagnostics(self) -> None:
        if not hasattr(self, "diag_status"):
            return
        try:
            data = system.get_system_snapshot()
            checks: list[tuple[str, str]] = []
            checks.append(("ВНИМАНИЕ" if data["cpu"] >= 90 else "OK", f"Процессор: {data['cpu']:.0f}% сейчас"))
            checks.append(("ВНИМАНИЕ" if data["memory_percent"] >= 90 else "OK", f"Память: {data['memory_percent']:.0f}% занято"))
            checks.append(("ВНИМАНИЕ" if data["disk_percent"] >= 95 else "OK", f"Системный диск: {data['disk_percent']:.0f}% занято"))
            sensors = advanced.get_sensor_snapshot()
            if sensors["temperatures"]:
                hottest = max(sensors["temperatures"], key=lambda item: item["celsius"])
                checks.append(("ВНИМАНИЕ" if hottest["celsius"] >= 90 else "OK", f"Самый горячий доступный датчик: {hottest['sensor']} · {hottest['celsius']:.1f} °C"))
            else:
                checks.append(("ИНФО", "Температурные датчики не предоставлены системой"))
            checks.append(("ИНФО", "Сводка показывает текущие значения, а не долгосрочный диагноз"))
            self.diag_status.setText("\n".join(f"{'!' if level == 'ВНИМАНИЕ' else '✓' if level == 'OK' else 'i'}  {message}" for level, message in checks))
            self.diag_status.setStyleSheet(f"color: {RED if any(x[0] == 'ВНИМАНИЕ' for x in checks) else TEXT};")
            self.refresh_event_log()
        except Exception as exc:
            self.diag_status.setText(f"Не удалось завершить проверку: {exc}")

    def refresh_event_log(self) -> None:
        if not hasattr(self, "event_view"):
            return
        events = advanced.read_events(200)
        if not events:
            self.event_view.setPlainText("Пока нет записей. Действия приложения появятся здесь.")
            return
        self.event_view.setPlainText("\n".join(f"[{event['time']}] {event['level']}: {event['message']}" for event in events))

    def export_diagnostic_report(self) -> None:
        path, _ = QFileDialog.getSaveFileName(self, "Сохранить диагностический отчёт", "forge-diagnostic.json", "JSON (*.json)")
        if not path:
            return
        try:
            report = advanced.create_diagnostic_report()
            Path(path).write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
            advanced.log_event("Создан диагностический отчёт (локальный экспорт)")
            QMessageBox.information(self, "Отчёт сохранён", "Файл сохранён локально. Перед отправкой проверь содержимое: в нём есть названия активных процессов и сведения об оборудовании.")
            self.refresh_event_log()
        except Exception as exc:
            QMessageBox.warning(self, "Не удалось создать отчёт", str(exc))

    def _page_appearance(self) -> None:
        page, layout = self._scroll_page()
        layout.addWidget(Heading("Внешний вид", "Персонализируй тему, фон, плотность интерфейса и собственные правила QSS."))
        appearance, appearance_layout = self._card("Основные настройки", "Настройки хранятся локально в профиле пользователя.")
        self.theme_combo = QComboBox()
        for label, value in (("Graphite · графитовый", "graphite"), ("Midnight · полуночный", "midnight"), ("Emerald · изумрудный", "emerald"), ("Light · светлый", "light")):
            self.theme_combo.addItem(label, value)
        self.theme_combo.setFixedWidth(220)
        self.accent_combo = QComboBox()
        for label, value in ACCENT_OPTIONS.items():
            self.accent_combo.addItem(label, value)
        self.accent_combo.setFixedWidth(220)
        self.font_spin = QSpinBox()
        self.font_spin.setRange(10, 17)
        self.font_spin.setSuffix(" px")
        self.sidebar_spin = QSpinBox()
        self.sidebar_spin.setRange(190, 310)
        self.sidebar_spin.setSuffix(" px")
        self.refresh_spin = QSpinBox()
        self.refresh_spin.setRange(1000, 10000)
        self.refresh_spin.setSingleStep(500)
        self.refresh_spin.setSuffix(" мс")
        self.history_spin = QSpinBox()
        self.history_spin.setRange(30, 360)
        self.history_spin.setSuffix(" точек")
        for control in (self.font_spin, self.sidebar_spin, self.refresh_spin, self.history_spin):
            control.setFixedWidth(150)
        self.wallpaper_path = QLineEdit()
        self.wallpaper_path.setReadOnly(True)
        self.wallpaper_path.setMinimumWidth(100)
        self.wallpaper_path.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.wallpaper_path.setPlaceholderText("Выбери локальное изображение…")
        self.wallpaper_strength = QSlider(Qt.Orientation.Horizontal)
        self.wallpaper_strength.setRange(0, 70)
        self.wallpaper_strength.setTickInterval(10)
        self.wallpaper_strength.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.wallpaper_strength_label = QLabel("18%")
        self.wallpaper_strength.valueChanged.connect(lambda value: self.wallpaper_strength_label.setText(f"{value}%"))
        self.wallpaper_choose = self._button("Выбрать обои…", icon_name="folder")
        self.wallpaper_choose.setMinimumWidth(150)
        self.wallpaper_choose.clicked.connect(self.choose_wallpaper)
        self.wallpaper_clear = self._button("Убрать обои")
        self.wallpaper_clear.setMinimumWidth(112)
        self.wallpaper_clear.clicked.connect(lambda: self.wallpaper_path.clear())
        for label, control in (("Тема", self.theme_combo), ("Акцентный цвет", self.accent_combo), ("Размер текста", self.font_spin), ("Ширина бокового меню", self.sidebar_spin), ("Частота обновления", self.refresh_spin), ("Длина истории графиков", self.history_spin)):
            row = QHBoxLayout()
            row.setContentsMargins(0, 2, 0, 2)
            row.setSpacing(14)
            name = QLabel(label)
            name.setObjectName("muted")
            name.setMinimumWidth(175)
            row.addWidget(name, 1)
            row.addWidget(control, 0, Qt.AlignmentFlag.AlignRight)
            appearance_layout.addLayout(row)
        wallpaper_row = QHBoxLayout()
        wallpaper_row.setSpacing(8)
        wallpaper_row.addWidget(self.wallpaper_path, 1)
        wallpaper_row.addWidget(self.wallpaper_choose)
        wallpaper_row.addWidget(self.wallpaper_clear)
        appearance_layout.addLayout(wallpaper_row)
        strength_row = QHBoxLayout()
        strength_name = QLabel("Интенсивность обоев")
        strength_name.setObjectName("muted")
        strength_row.addWidget(strength_name)
        strength_row.addWidget(self.wallpaper_strength, 1)
        strength_row.addWidget(self.wallpaper_strength_label)
        appearance_layout.addLayout(strength_row)
        layout.addWidget(appearance)

        profile, profile_layout = self._card("Профили оформления", "Экспортируй настройки в JSON или перенеси их на другой компьютер. Пути к обоям должны существовать на целевом устройстве.")
        profile_buttons = QHBoxLayout()
        export_profile = self._button("Экспортировать профиль…")
        export_profile.clicked.connect(self.export_preferences)
        import_profile = self._button("Импортировать профиль…")
        import_profile.clicked.connect(self.import_preferences)
        profile_buttons.addWidget(export_profile)
        profile_buttons.addWidget(import_profile)
        profile_buttons.addStretch(1)
        profile_layout.addLayout(profile_buttons)
        layout.addWidget(profile)

        css, css_layout = self._card("Пользовательский стиль (QSS)", "Это Qt Style Sheets, а не браузерный CSS: backdrop-filter не поддерживается. Для эффекта Liquid Glass выбери локальные обои и выставь интенсивность примерно 35–55%.")
        self.custom_qss = QPlainTextEdit()
        self.custom_qss.setObjectName("customQssEditor")
        self.custom_qss.setMinimumHeight(230)
        self.custom_qss.setPlaceholderText("/* Пример: скруглить карточки */\n#panel { border-radius: 18px; }\n#navButton:checked { border: 1px solid #a99bff; }\nQPushButton { padding: 9px 14px; }")
        css_layout.addWidget(self.custom_qss)
        css_buttons = QHBoxLayout()
        liquid_css = self._button("Применить Liquid Glass")
        liquid_css.clicked.connect(self.apply_liquid_glass_preset)
        reset_css = self._button("Очистить пользовательские стили")
        reset_css.clicked.connect(lambda: self.custom_qss.clear())
        apply_css = self._button("Сохранить и применить", "primary", "check")
        apply_css.clicked.connect(self.apply_customization)
        css_buttons.addWidget(liquid_css)
        css_buttons.addWidget(reset_css)
        css_buttons.addWidget(apply_css)
        css_buttons.addStretch(1)
        css_layout.addLayout(css_buttons)
        layout.addWidget(css)
        layout.addStretch(1)
        self.pages["Внешний вид"] = page
        self.stack.addWidget(page)
        self._sync_appearance_controls()

    def _sync_appearance_controls(self) -> None:
        if not hasattr(self, "theme_combo"):
            return
        settings = self.preferences
        theme_index = self.theme_combo.findData(settings.get("theme", "graphite"))
        self.theme_combo.setCurrentIndex(max(0, theme_index))
        accent_index = self.accent_combo.findData(settings.get("accent", "#a99bff"))
        self.accent_combo.setCurrentIndex(max(0, accent_index))
        self.font_spin.setValue(int(settings.get("font_size", 13)))
        self.sidebar_spin.setValue(int(settings.get("sidebar_width", 238)))
        self.refresh_spin.setValue(int(settings.get("refresh_ms", 2500)))
        self.history_spin.setValue(int(settings.get("history_points", 120)))
        self.wallpaper_path.setText(str(settings.get("wallpaper", "")))
        self.wallpaper_strength.setValue(int(settings.get("wallpaper_strength", 18)))
        self.custom_qss.setPlainText(str(settings.get("custom_qss", "")))

    def choose_wallpaper(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, "Выбери обои", str(Path.home()), "Изображения (*.png *.jpg *.jpeg *.webp *.bmp *.gif);;Все файлы (*)")
        if path:
            pixmap = QPixmap(path)
            if pixmap.isNull():
                QMessageBox.warning(self, "Не удалось открыть изображение", "Выбери поддерживаемое изображение PNG, JPEG, WebP, BMP или GIF.")
                return
            self.wallpaper_path.setText(path)

    def apply_liquid_glass_preset(self) -> None:
        """Load and apply the bundled translucent Qt stylesheet."""
        self.custom_qss.setPlainText(LIQUID_GLASS_QSS)
        self.apply_customization()

    def export_preferences(self) -> None:
        path, _ = QFileDialog.getSaveFileName(self, "Экспортировать профиль Forge", "forge-profile.json", "JSON (*.json)")
        if not path:
            return
        try:
            Path(path).write_text(json.dumps(self.preferences, ensure_ascii=False, indent=2), encoding="utf-8")
            advanced.log_event("Экспортирован профиль оформления")
            self.statusBar().showMessage("Профиль оформления экспортирован", 5000)
        except OSError as exc:
            QMessageBox.warning(self, "Ошибка экспорта", str(exc))

    def import_preferences(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, "Импортировать профиль Forge", str(Path.home()), "JSON (*.json)")
        if not path:
            return
        try:
            payload = json.loads(Path(path).read_text(encoding="utf-8"))
            if not isinstance(payload, dict):
                raise ValueError("Файл профиля должен содержать JSON-объект.")
            allowed = advanced.default_preferences()
            if any(key not in allowed for key in payload):
                raise ValueError("Профиль содержит неизвестные параметры. Импорт отменён.")
            merged = advanced.default_preferences()
            merged.update(payload)
            advanced.save_preferences(merged)
            self.preferences = advanced.load_preferences()
            self._sync_appearance_controls()
            self.apply_customization()
            advanced.log_event("Импортирован профиль оформления")
        except (OSError, ValueError, TypeError) as exc:
            QMessageBox.warning(self, "Не удалось импортировать профиль", str(exc))

    def apply_customization(self) -> None:
        settings = dict(self.preferences)
        settings.update({
            "theme": str(self.theme_combo.currentData() or "graphite"),
            "accent": str(self.accent_combo.currentData() or "#a99bff"),
            "font_size": self.font_spin.value(),
            "sidebar_width": self.sidebar_spin.value(),
            "refresh_ms": self.refresh_spin.value(),
            "history_points": self.history_spin.value(),
            "wallpaper": self.wallpaper_path.text().strip(),
            "wallpaper_strength": self.wallpaper_strength.value(),
            "custom_qss": self.custom_qss.toPlainText()[:30000],
        })
        if settings["wallpaper"] and not Path(settings["wallpaper"]).expanduser().is_file():
            QMessageBox.warning(self, "Обои не найдены", "Файл не существует. Выбери его заново или очисти поле.")
            return
        advanced.save_preferences(settings)
        self.preferences = advanced.load_preferences()
        apply_palette(self.preferences)
        self.sidebar.setFixedWidth(SIDEBAR_WIDTH)
        self.wallpaper_host.set_wallpaper(str(self.preferences.get("wallpaper", "")), int(self.preferences.get("wallpaper_strength", 18)))
        app = QApplication.instance()
        if app is not None:
            font = QFont("Inter", FONT_SIZE)
            if not font.exactMatch():
                font = QFont("Noto Sans", FONT_SIZE)
            app.setFont(font)
        if app is not None:
            self.setFont(app.font())
        self._apply_theme()
        for _title, icon_name, key in self.NAV:
            button = self.nav_buttons.get(key)
            if button is not None:
                button.setIcon(icon(icon_name, PURPLE if button.isChecked() else MUTED))
        self.cpu_card.set_color(PURPLE)
        self.ram_card.set_color(GREEN)
        self.disk_card.set_color(AMBER)
        self.proc_card.set_color("#82b7ff")
        self.cpu_history.color = PURPLE
        self.ram_history.color = GREEN
        self.gpu_history.color = "#82b7ff"
        self.history_cpu_chart.color = PURPLE
        self.history_memory_chart.color = GREEN
        self.history_disk_chart.color = AMBER
        self.history_gpu_chart.color = "#82b7ff"
        for chart in (self.cpu_history, self.ram_history, self.gpu_history, self.history_cpu_chart, self.history_memory_chart, self.history_disk_chart, self.history_gpu_chart):
            chart.points = int(self.preferences.get("history_points", 120))
            chart.values = chart.values[-chart.points:]
            chart.update()
        self.top_status.setStyleSheet("")
        self.timer.setInterval(int(self.preferences.get("refresh_ms", 2500)))
        self.statusBar().showMessage("Настройки оформления сохранены и применены", 5000)
        advanced.log_event("Применены настройки оформления")

    def _apply_theme(self) -> None:
        base_style = f"""
            QWidget {{ background: transparent; color: {TEXT}; font-family: 'Inter', 'Noto Sans', 'Segoe UI', sans-serif; font-size: {FONT_SIZE}px; }}
            QMainWindow {{ background: {BG}; }}
            #sidebar {{ background: {SIDEBAR}; border-right: 1px solid {BORDER}; }}
            #logoMark {{ background: transparent; }}
            #brandName {{ font-size: 17px; font-weight: 800; letter-spacing: 2px; color: {TEXT}; }}
            #brandSub, #sectionLabel {{ color: {SOFT}; font-size: 9px; font-weight: 700; letter-spacing: 1.2px; }}
            #sectionLabel {{ padding-left: 9px; padding-bottom: 5px; }}
            #navButton {{ text-align: left; padding: 0 12px; border: 1px solid transparent; border-radius: 9px; color: {MUTED}; background: transparent; font-weight: 500; }}
            #navButton:hover {{ color: {TEXT}; background: {PANEL_HOVER}; }}
            #navButton:checked {{ color: {TEXT}; background: {PURPLE_DARK}; border: 1px solid {PURPLE}; font-weight: 700; }}
            #systemChip {{ background: #1b1c25; border: 1px solid {BORDER}; border-radius: 10px; }}
            #greenDot {{ color: {GREEN}; font-size: 9px; }}
            #systemChip QLabel {{ font-size: 9px; font-weight: 700; color: {MUTED}; }}
            #topbar {{ background: {BG}; border-bottom: 1px solid {BORDER}; }}
            #breadcrumb {{ color: {TEXT}; font-size: 13px; font-weight: 650; }}
            #statusTag {{ color: {GREEN}; background: #1c2b27; border: 1px solid #2c4940; padding: 7px 10px; border-radius: 7px; font-size: 10px; font-weight: 700; }}
            #pageTitle {{ font-size: 25px; font-weight: 750; color: {TEXT}; }}
            #pageSubtitle {{ font-size: 12px; color: {MUTED}; }}
            #hero {{ background: qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 {PURPLE_DARK},stop:0.55 {PANEL},stop:1 {SIDEBAR}); border: 1px solid {BORDER}; border-radius: 14px; }}
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
            QLineEdit, QComboBox, QSpinBox {{ background: {PANEL}; color: {TEXT}; border: 1px solid {BORDER}; border-radius: 8px; selection-background-color: {PURPLE_DARK}; min-height: 18px; }}
            QLineEdit {{ padding: 8px 10px; }}
            QComboBox {{ padding: 0 28px 0 10px; }}
            QSpinBox {{ padding: 0 22px 0 10px; }}
            QLineEdit:focus, QComboBox:focus, QSpinBox:focus {{ border-color: #8173bd; }}
            QComboBox::drop-down {{ subcontrol-origin: padding; subcontrol-position: top right; width: 25px; border-left: 1px solid {BORDER}; background: transparent; border-top-right-radius: 7px; border-bottom-right-radius: 7px; }}
            QComboBox::drop-down:hover {{ background: {PANEL_HOVER}; }}
            QComboBox QAbstractItemView {{ background: {PANEL}; color: {TEXT}; border: 1px solid {BORDER}; selection-background-color: {PURPLE_DARK}; outline: 0; padding: 4px; }}
            QSpinBox::up-button, QSpinBox::down-button {{ subcontrol-origin: border; width: 19px; border: 0; background: transparent; }}
            QSpinBox::up-button {{ subcontrol-position: top right; margin: 2px 2px 0 0; border-top-right-radius: 6px; }}
            QSpinBox::down-button {{ subcontrol-position: bottom right; margin: 0 2px 2px 0; border-bottom-right-radius: 6px; }}
            QSpinBox::up-button:hover, QSpinBox::down-button:hover {{ background: {PANEL_HOVER}; }}
            #dataTable {{ background: {PANEL}; alternate-background-color: #1d1e28; border: 1px solid {BORDER}; border-radius: 9px; selection-background-color: #393252; selection-color: {TEXT}; outline: 0; }}
            #dataTable::item {{ padding: 7px 8px; border-bottom: 1px solid #242530; }}
            #dataTable::item:selected {{ background: #393252; }}
            QHeaderView::section {{ background: #20212b; color: {SOFT}; border: 0; border-bottom: 1px solid {BORDER}; padding: 10px 9px; font-size: 9px; font-weight: 800; }}
            QScrollArea {{ border: 0; background: transparent; }}
            QScrollBar:vertical, QScrollBar:horizontal {{ background: rgba(255, 255, 255, 8); border: 0; border-radius: 4px; }}
            QScrollBar:vertical {{ width: 9px; margin: 2px; }}
            QScrollBar:horizontal {{ height: 9px; margin: 2px; }}
            QScrollBar::handle:vertical, QScrollBar::handle:horizontal {{ background: #454558; border-radius: 4px; min-height: 24px; min-width: 24px; }}
            QScrollBar::handle:vertical:hover, QScrollBar::handle:horizontal:hover {{ background: #655d8d; }}
            QScrollBar::add-line, QScrollBar::sub-line {{ width: 0; height: 0; border: 0; }}
            QStatusBar {{ background: {SIDEBAR}; color: {MUTED}; border-top: 1px solid {BORDER}; font-size: 10px; }}
            QMessageBox, QDialog {{ background: {PANEL}; }}
            QListWidget {{ background: {PANEL}; color: {TEXT}; border: 1px solid {BORDER}; border-radius: 9px; outline: 0; }}
            QListWidget::item {{ padding: 9px 10px; border-radius: 6px; }}
            QListWidget::item:selected {{ background: {PURPLE_DARK}; color: {TEXT}; border: 1px solid {PURPLE}; }}
            QSpinBox, QPlainTextEdit {{ background: {PANEL}; color: {TEXT}; border: 1px solid {BORDER}; border-radius: 8px; padding: 8px; selection-background-color: {PURPLE_DARK}; }}
            #customQssEditor {{ font-family: 'JetBrains Mono', 'Consolas', monospace; font-size: 12px; }}
            QSlider::groove:horizontal {{ height: 5px; background: {BORDER}; border-radius: 2px; }}
            QSlider::handle:horizontal {{ width: 15px; margin: -5px 0; background: {PURPLE}; border-radius: 7px; }}
            #historyChart {{ background: transparent; }}
        """
        self.setStyleSheet(base_style + "\n" + self.preferences.get("custom_qss", ""))


def main() -> int:
    app = QApplication(sys.argv)
    app.setApplicationName("Forge")
    app.setOrganizationName("W0rd3r566")
    app.setStyle("Fusion")
    preferences = advanced.load_preferences()
    apply_palette(preferences)
    font = QFont("Inter", FONT_SIZE)
    if not font.exactMatch():
        font = QFont("Noto Sans", FONT_SIZE)
    app.setFont(font)
    advanced.log_event(f"Forge {__version__} запущен")
    window = ForgeWindow(preferences)
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
