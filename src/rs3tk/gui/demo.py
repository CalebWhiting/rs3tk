"""Demo launcher — loads compiled UI and applies dark theme styling."""

from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QApplication,
    QFrame,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QTreeWidget,
    QTreeWidgetItem,
)

from rs3tk.gui.launcher_ui import Ui_RuneLauncher

_ASSETS = Path(__file__).parent / "assets"

_DARK_THEME = """
/* ── RuneScape-inspired theme ──────────────────────────────── */
/* Colors extracted from runescape.com:
   - Logo gradient: #ffecc2 → #b6977b
   - Text gold: #f7da96, #f2d593
   - Orange accent: #ff8614
   - Backgrounds: #141414, #1a1a1a
   - White: #ffffff
   - Gray: #a6a6a6
   - Blue: #0099ff
*/

QMainWindow, QWidget {
    background-color: #0e0e14;
    color: #e0e0e0;
    font-family: "Sofia Sans", "Segoe UI", "Noto Sans", sans-serif;
    font-size: 13px;
}

/* ── Top bar ─────────────────────────────────────────────── */

#topBar {
    background-color: #141414;
    border-bottom: 2px solid #2a2218;
}

#title {
    font-size: 16px;
    font-weight: bold;
    color: #f7da96;
}

#subtitle {
    font-size: 11px;
    color: #a6a6a6;
}

#logo {
    background: transparent;
}

#dashboardButton, #settingsButton, #addAccountButton {
    background: transparent;
    color: #a6a6a6;
    border: none;
    padding: 6px 12px;
    font-size: 12px;
}

#dashboardButton:checked, #settingsButton:checked {
    color: #f7da96;
    border-bottom: 2px solid #f7da96;
}

#minimizeButton, #maximizeButton, #closeButton {
    background: transparent;
    color: #a6a6a6;
    border: none;
    font-size: 16px;
    min-width: 28px;
    max-width: 28px;
}

#closeButton:hover {
    background-color: #ff8614;
    color: #ffffff;
}

/* ── Left sidebar — accounts ─────────────────────────────── */

#accountsPanel {
    background-color: #141414;
    border-right: 1px solid #2a2218;
}

#accountsHeader {
    background-color: #1a1a1a;
    border-bottom: 1px solid #2a2218;
}

#accountsTree {
    background-color: transparent;
    border: none;
    color: #e0e0e0;
    outline: none;
}

#accountsTree::item {
    padding: 8px 12px;
    border-bottom: 1px solid #1e1e1e;
}

#accountsTree::item:selected {
    background-color: #2a2218;
    color: #f7da96;
}

#accountsTree::item:hover {
    background-color: #1e1e1e;
}

#addJagexAccountButton {
    background-color: #1a1a1a;
    color: #a6a6a6;
    border: 1px dashed #3a3a3a;
    border-radius: 4px;
    margin: 8px;
}

#addJagexAccountButton:hover {
    background-color: #2a2218;
    color: #f7da96;
}

/* ── Center — dashboard ──────────────────────────────────── */

#dashboard {
    background-color: #0e0e14;
}

#characterHeader {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #2a2218, stop:1 #1a1a1a);
    border-radius: 8px;
    margin: 8px 12px;
}

#characterName {
    font-size: 18px;
    font-weight: bold;
    color: #f7da96;
}

#characterInfo {
    font-size: 12px;
    color: #a6a6a6;
}

#avatar {
    background-color: #1a1a1a;
    color: #a6a6a6;
    border-radius: 28px;
    border: 2px solid #b6977b;
    font-size: 14px;
}

#statusArea {
    background-color: rgba(255, 134, 20, 0.1);
    border: 1px solid rgba(255, 134, 20, 0.3);
    border-radius: 6px;
    padding: 6px;
}

#statusLabel {
    color: #ff8614;
    font-size: 11px;
    font-weight: bold;
}

#onlineCount {
    color: #a6a6a6;
    font-size: 11px;
}

#navigationTabs {
    background: transparent;
    color: #a6a6a6;
}

#metricsCard, #questsCard, #activityCard, #skillsCard {
    background-color: #141414;
    border: 1px solid #2a2218;
    border-radius: 8px;
    margin: 4px 12px;
    min-height: 160px;
}

/* ── Right sidebar — clients ─────────────────────────────── */

#clientPanel {
    background-color: #141414;
    border-left: 1px solid #2a2218;
}

#clientTitle {
    font-size: 14px;
    font-weight: bold;
    color: #f7da96;
}

#clientList {
    background-color: transparent;
    border: none;
    color: #e0e0e0;
    outline: none;
}

#clientList::item {
    padding: 10px 12px;
    border-bottom: 1px solid #1e1e1e;
}

#clientList::item:selected {
    background-color: #2a2218;
    color: #f7da96;
}

#clientList::item:hover {
    background-color: #1e1e1e;
}

#playButton {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #ff8614, stop:1 #ff6a00);
    color: #ffffff;
    font-size: 15px;
    font-weight: bold;
    border: none;
    border-radius: 6px;
}

#playButton:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #ffa040, stop:1 #ff8020);
}

#playButton:pressed {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #e07010, stop:1 #c05000);
}

#lastPlayed {
    color: #666666;
    font-size: 11px;
}

/* ── Bottom bar ──────────────────────────────────────────── */

#bottomBar {
    background-color: #141414;
    border-top: 2px solid #2a2218;
}

#launcherVersion, #updateStatus {
    color: #666666;
    font-size: 11px;
}

#discordButton, #newsButton, #supportButton {
    background: transparent;
    color: #666666;
    border: none;
    font-size: 11px;
}

#discordButton:hover, #newsButton:hover, #supportButton:hover {
    color: #f7da96;
}
"""


def _populate_demo_data(window: QMainWindow) -> None:
    # ── Logo ──────────────────────────────────────────────────────────────
    logo = window.findChild(QLabel, "logo")
    if logo:
        pixmap = QPixmap(str(_ASSETS / "runescape_logo.png"))
        scaled = pixmap.scaled(32, 32, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        logo.setPixmap(scaled)
        logo.setFixedSize(32, 32)

    # ── Avatar ────────────────────────────────────────────────────────────
    avatar = window.findChild(QLabel, "avatar")
    if avatar:
        # Placeholder — would fetch from RuneMetrics API in production
        avatar_pixmap = QPixmap(str(_ASSETS / "runescape_logo.png"))
        scaled = avatar_pixmap.scaled(
            56, 56, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation
        )
        avatar.setPixmap(scaled)
        avatar.setFixedSize(56, 56)

    # ── Accounts tree ─────────────────────────────────────────────────────
    tree = window.findChild(QTreeWidget, "accountsTree")
    if tree:
        tree.setHeaderHidden(True)

        account_item = QTreeWidgetItem(tree, ["johndoe"])
        account_item.setExpanded(True)
        QTreeWidgetItem(account_item, ["Cow31337Killer"])
        QTreeWidgetItem(account_item, ["IronMan2026"])

        account_item2 = QTreeWidgetItem(tree, ["janedoe"])
        QTreeWidgetItem(account_item2, ["Skiller99"])

    # ── Client list ───────────────────────────────────────────────────────
    qlist = window.findChild(QListWidget, "clientList")
    if qlist:
        for name, installed in [("RS3 NXT", True), ("OSRS Official", False), ("RuneLite", True), ("HDOS", False)]:
            item = QListWidgetItem(f"{'●' if installed else '○'}  {name}")
            item.setData(Qt.ItemDataRole.UserRole, name.lower().replace(" ", "_"))
            qlist.addItem(item)

    # ── Activity card with news thumbnails ────────────────────────────────
    activity_card = window.findChild(QFrame, "activityCard")
    if activity_card:
        layout = activity_card.layout()
        if layout:
            news_items = [
                "Player-Owned House Update - Day 2",
                "Everything about Player Owned Housing!",
                "Player Owned Housing Rework Out Now!",
                "The Road Ahead...",
                "Dive into Sunlight Sands!",
            ]
            for title in news_items:
                row = QLabel(f"  {title}")
                row.setStyleSheet("color: #f7da96; font-size: 11px; padding: 4px 0;")
                layout.addWidget(row)


def main() -> None:
    app = QApplication(sys.argv)
    app.setStyleSheet(_DARK_THEME)

    window = QMainWindow()
    ui = Ui_RuneLauncher()
    ui.setupUi(window)  # type: ignore[no-untyped-call]

    _populate_demo_data(window)

    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
