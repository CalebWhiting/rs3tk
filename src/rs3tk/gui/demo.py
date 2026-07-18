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
/* ── RuneScape Adventurer's Log theme ────────────────────── */
/* Colors extracted from runescape.com:
   - Main background: #071b25
   - Gold accent: #e1bb34
   - Hover gold: #fff2c5
   - Text light: #d7dbe1
   - Secondary text: #a9acad
   - Content bg: #2E3F49
   - Header bg: #355563
   - Blue link: #b2dbee
   - Selection: #8eb0c0
   - Orange accent: #ff8614
*/

QMainWindow, QWidget {
    background-color: #071b25;
    color: #d7dbe1;
    font-family: "Sofia Sans", "Segoe UI", "Noto Sans", sans-serif;
    font-size: 13px;
}

/* ── Top bar ─────────────────────────────────────────────── */

#topBar {
    background-color: #0d1f2d;
    border-bottom: 2px solid #355563;
}

#title {
    font-size: 16px;
    font-weight: bold;
    color: #e1bb34;
}

#subtitle {
    font-size: 11px;
    color: #a9acad;
}

#logo {
    background: transparent;
}

#dashboardButton, #settingsButton, #addAccountButton {
    background: transparent;
    color: #a9acad;
    border: none;
    padding: 6px 12px;
    font-size: 12px;
}

#dashboardButton:checked, #settingsButton:checked {
    color: #fff2c5;
    border-bottom: 2px solid #e1bb34;
}

#minimizeButton, #maximizeButton, #closeButton {
    background: transparent;
    color: #a9acad;
    border: none;
    font-size: 16px;
    min-width: 28px;
    max-width: 28px;
}

#closeButton:hover {
    background-color: #e1bb34;
    color: #071b25;
}

/* ── Left sidebar — accounts ─────────────────────────────── */

#accountsPanel {
    background-color: #0d1f2d;
    border-right: 1px solid #355563;
}

#accountsHeader {
    background-color: #1a3040;
    border-bottom: 1px solid #355563;
}

#accountsTree {
    background-color: transparent;
    border: none;
    color: #d7dbe1;
    outline: none;
}

#accountsTree::item {
    padding: 8px 12px;
    border-bottom: 1px solid #1a3040;
}

#accountsTree::item:selected {
    background-color: #2E3F49;
    color: #fff2c5;
}

#accountsTree::item:hover {
    background-color: #1a3040;
}

#addJagexAccountButton {
    background-color: #1a3040;
    color: #a9acad;
    border: 1px dashed #355563;
    border-radius: 4px;
    margin: 8px;
}

#addJagexAccountButton:hover {
    background-color: #2E3F49;
    color: #fff2c5;
}

/* ── Center — dashboard ──────────────────────────────────── */

#dashboard {
    background-color: #071b25;
}

#characterHeader {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #1a3040, stop:1 #0d1f2d);
    border-radius: 8px;
    margin: 8px 12px;
}

#characterName {
    font-size: 18px;
    font-weight: bold;
    color: #e1bb34;
}

#characterInfo {
    font-size: 12px;
    color: #a9acad;
}

#avatar {
    background-color: #1a3040;
    color: #a9acad;
    border-radius: 28px;
    border: 2px solid #e1bb34;
    font-size: 14px;
}

#statusArea {
    background-color: rgba(141, 176, 192, 0.1);
    border: 1px solid rgba(141, 176, 192, 0.3);
    border-radius: 6px;
    padding: 6px;
}

#statusLabel {
    color: #8eb0c0;
    font-size: 11px;
    font-weight: bold;
}

#onlineCount {
    color: #a9acad;
    font-size: 11px;
}

#navigationTabs {
    background: transparent;
    color: #a9acad;
}

#metricsCard, #questsCard, #activityCard, #skillsCard {
    background-color: #0d1f2d;
    border: 1px solid #355563;
    border-radius: 8px;
    margin: 4px 12px;
    min-height: 160px;
}

/* ── Right sidebar — clients ─────────────────────────────── */

#clientPanel {
    background-color: #0d1f2d;
    border-left: 1px solid #355563;
}

#clientTitle {
    font-size: 14px;
    font-weight: bold;
    color: #e1bb34;
}

#clientList {
    background-color: transparent;
    border: none;
    color: #d7dbe1;
    outline: none;
}

#clientList::item {
    padding: 10px 12px;
    border-bottom: 1px solid #1a3040;
}

#clientList::item:selected {
    background-color: #2E3F49;
    color: #fff2c5;
}

#clientList::item:hover {
    background-color: #1a3040;
}

#playButton {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #e1bb34, stop:1 #c8a42a);
    color: #071b25;
    font-size: 15px;
    font-weight: bold;
    border: none;
    border-radius: 6px;
}

#playButton:hover {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #fff2c5, stop:1 #e1bb34);
}

#playButton:pressed {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #c8a42a, stop:1 #a88a20);
}

#lastPlayed {
    color: #536066;
    font-size: 11px;
}

/* ── Bottom bar ──────────────────────────────────────────── */

#bottomBar {
    background-color: #0d1f2d;
    border-top: 2px solid #355563;
}

#launcherVersion, #updateStatus {
    color: #536066;
    font-size: 11px;
}

#discordButton, #newsButton, #supportButton {
    background: transparent;
    color: #536066;
    border: none;
    font-size: 11px;
}

#discordButton:hover, #newsButton:hover, #supportButton:hover {
    color: #e1bb34;
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
                row.setStyleSheet("color: #e1bb34; font-size: 11px; padding: 4px 0;")
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
