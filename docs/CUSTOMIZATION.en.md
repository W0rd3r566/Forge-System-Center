# Forge customization handbook

[Русская версия](CUSTOMIZATION.md) · [Main README](../README.en.md)

Forge uses **Qt Style Sheets (QSS)**. QSS looks like CSS, but targets Qt widgets rather than an HTML page. It can change colors, backgrounds, translucency, borders, corner radii, spacing, fonts, selection, button states, tables, tooltips, sliders and scrollbars.

Open **Appearance → Custom style (QSS)**. Available presets are **Liquid Glass**, **Soft Acrylic**, **Miku Cyan** and **Minimal**. Start with a preset, tweak the rules and select **Save and apply**. QSS can be imported and exported as `.qss` files or plain `.css` text. Custom styles are stored in the user profile, not in the source files.

> This guide covers visual customization. QSS cannot add Python event handlers, new pages, application logic or new system features.

## 1. Built-in appearance controls

| Setting | What it changes |
| --- | --- |
| Theme | Graphite, Midnight, Emerald, Light |
| Accent color | Any user-selected color |
| Font family | A font installed on the system |
| Font size | 10–24 px |
| Sidebar width | 190–360 px |
| Corner radius | Card, button and input radius, 4–28 px |
| Density | Compact, Comfortable, Spacious |
| Wallpaper | Local image blended into the background |
| Transparent window background | Enables the Liquid Glass backdrop layer |
| Frosted tint strength | Backdrop tint alpha, 0–220 |
| Refresh interval | 1000–10000 ms |
| Chart history | 30–360 points |
| Alerts | CPU, memory, disk and temperature thresholds |
| Mini monitor | Visibility, opacity and refresh interval |
| System tray | Optionally minimize Forge to the tray on close |
| Work modes | Balanced, Gaming, Work, Quiet |
| Settings profiles | Import/export JSON |
| QSS | Edit, import, export and load presets |

The image itself is not embedded in a JSON profile. If you move a profile to another computer, the wallpaper path must exist there too.

## 2. Widget object names and selectors

In Qt, `#panel` selects a widget whose `objectName` is `panel`. `QPushButton` selects push buttons. User QSS is appended after the built-in theme, so it can override built-in properties.

### Main areas

| Selector | Target |
| --- | --- |
| `#root` | Root window/background layer |
| `#sidebar` | Sidebar |
| `#topbar` | Top bar |
| `#breadcrumb` | Current section name |
| `#statusTag` | System status indicator |
| `#brandName` | FORGE wordmark |
| `#brandSub` | Wordmark subtitle |
| `#logoMark` | Sidebar logo area |
| `#sectionLabel` | Small section labels |
| `#navButton` | Navigation buttons |
| `#systemChip` | Local-mode card at the bottom of the sidebar |

### Cards and text

| Selector | Target |
| --- | --- |
| `#hero` | Large overview banner |
| `#heroOverline` | Small text above hero heading |
| `#heroTitle` | Hero heading |
| `#heroSubtitle` | Hero description |
| `#panel` | General panel/card |
| `#panelTitle` | Panel heading |
| `#metricCard` | System metric card |
| `#metricValue` | Main CPU/RAM/etc. value |
| `#livePill` | LIVE label |
| `#infoValue` | Value in a details row |
| `#bigNumber` | Large number in network center |
| `#muted` | Secondary text |
| `#mutedSmall` | Small caption |
| `#pathLabel` | Path text |
| `#greenDot` | Local status dot |

### Buttons, tables and charts

| Selector | Target |
| --- | --- |
| `#quickButton` | Quick action on the overview |
| `#primaryButton` | Primary action |
| `#secondaryButton` | Standard button |
| `#dangerButton` | Destructive action, such as terminating a process |
| `#dataTable` | Process, disk, sensor and interface tables |
| `#historyChart` | Custom-painted history charts |
| `#customQssEditor` | QSS editor and text logs |
| `#miniMonitorWindow` | Mini-monitor top-level window |
| `#miniMonitorCard` | Mini-monitor glass card |
| `#miniMonitorTitle` | Mini-monitor title |
| `#miniMonitorReadout` | CPU/RAM/Disk readout |
| `#miniMonitorFooter` | Mini-monitor footer |
| `#miniMonitorClose` | Mini-monitor close button |

Some components are custom-painted with `QPainter`, including graphs and the background. Their drawing logic can limit what QSS can change.

## 3. General Qt selectors

You can also use widget-class selectors:

- `QWidget`, `QMainWindow`, `QFrame`, `QLabel`
- `QPushButton`, `QToolButton`, `QCheckBox`
- `QLineEdit`, `QComboBox`, `QSpinBox`, `QPlainTextEdit`
- `QTableWidget`, `QHeaderView::section`, `QListWidget`
- `QScrollBar:vertical`, `QScrollBar:horizontal`, `QStatusBar`
- `QSlider::groove:horizontal`, `QSlider::handle:horizontal`
- `QProgressBar`, `QToolTip`, `QDialog`, `QMessageBox`

Subcontrols include `QComboBox::drop-down`, `QComboBox QAbstractItemView`, `QSpinBox::up-button`, `QSpinBox::down-button` and `QListWidget::item:selected`.

### States

| Selector | Example |
| --- | --- |
| `:hover` | Pointer is over a button |
| `:focus` | An input has focus |
| `:checked` | Selected navigation button or checkbox |
| `:disabled` | Disabled control |
| `::item:selected` | Selected list item |

## 4. Ready-to-use QSS snippets

### Translucent cards

```css
#panel, #metricCard, #systemChip {
    background-color: rgba(28, 30, 46, 155);
    border: 1px solid rgba(190, 179, 255, 110);
    border-radius: 18px;
}
```

### Brighter active navigation

```css
#navButton:checked {
    color: #ffffff;
    background-color: rgba(169, 155, 255, 70);
    border: 1px solid rgba(205, 195, 255, 220);
    border-radius: 12px;
}
#navButton:hover {
    background-color: rgba(255, 255, 255, 20);
}
```

### Font and buttons

```css
QLabel {
    letter-spacing: 0.2px;
}
QPushButton {
    padding: 9px 14px;
    border-radius: 11px;
}
QPushButton:disabled {
    color: #77788a;
    background-color: rgba(100, 100, 120, 35);
}
```

### Gradient hero

```css
#hero {
    background: qlineargradient(
        x1: 0, y1: 0, x2: 1, y2: 1,
        stop: 0 rgba(105, 88, 170, 210),
        stop: 1 rgba(24, 26, 42, 190)
    );
    border: 1px solid rgba(200, 188, 255, 175);
    border-radius: 22px;
}
```

### Table rows

```css
#dataTable {
    alternate-background-color: rgba(255, 255, 255, 8);
    selection-background-color: rgba(135, 115, 220, 170);
    selection-color: #ffffff;
}
QHeaderView::section {
    padding: 10px;
    color: #bcb8d2;
    background-color: rgba(255, 255, 255, 15);
    border-bottom: 1px solid rgba(190, 179, 255, 90);
}
```

### Scrollbars

```css
QScrollBar:vertical {
    width: 9px;
    background: transparent;
    margin: 2px;
}
QScrollBar::handle:vertical {
    min-height: 24px;
    background: rgba(190, 179, 255, 115);
    border-radius: 4px;
}
QScrollBar::handle:vertical:hover {
    background: rgba(210, 200, 255, 180);
}
QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical {
    height: 0;
}
```

## 5. Colors and translucency

Use HEX colors such as `#a99bff` or RGBA:

```css
background-color: rgba(30, 32, 50, 150);
```

The alpha channel ranges from **0–255**: `0` is fully transparent and `255` is fully opaque. The result depends on the content behind the widget, the window compositor and the desktop environment.

### Configure Liquid Glass

1. Open **Appearance**.
2. Choose a local wallpaper image.
3. Select **Liquid Glass** or **Soft Acrylic** in the QSS presets and click **Load preset**.
4. Enable **Transparent window background**.
5. Tune wallpaper intensity and frosted tint strength. Lower tint reveals more of the backdrop; higher tint creates a darker, more readable surface.
6. Select **Save and apply**.

**Limitations:** QSS does not support web CSS features such as `backdrop-filter`, `box-shadow`, `transition`, `animation`, `display: flex`, `grid`, CSS variables like `var(--name)`, or JavaScript. Forge blends translucent surfaces with a softened backdrop made from the selected wallpaper. This does not guarantee real-time blur of the desktop behind the application; that depends on the window compositor.

## 6. What to avoid overriding

- A global rule like `QWidget { background-color: ...; }` can paint every nested control and hide transparency. Prefer specific selectors such as `#panel`, `#sidebar` and `#topbar`.
- Do not set an opaque background on `#root` or `QMainWindow` when using a transparent window.
- Very low contrast makes metric labels hard to read.
- QSS cannot change action logic, safety checks or which hardware sensors are available.
- The custom QSS limit is **30,000 characters**.

## 7. Where settings live

- Settings and custom QSS are stored locally in `settings.json` under the Forge user configuration directory.
- Logs and performance history are not uploaded automatically.
- JSON profiles include settings and QSS but do not copy wallpaper files.
- Export a profile before major styling experiments. The rollback button in Diagnostics is available only for actions Forge explicitly marks as reversible.
