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
QMainWindow, QWidget {
    background-color: #1b1b2f;
    color: #e2e8f0;
    font-family: "Segoe UI", "Noto Sans", sans-serif;
    font-size: 13px;
}

/* ── Top bar ─────────────────────────────────────────────── */

#topBar {
    background-color: #16213e;
    border-bottom: 1px solid #2a2a4a;
}

#title {
    font-size: 16px;
    font-weight: bold;
    color: #ffffff;
}

#subtitle {
    font-size: 11px;
    color: #94a3b8;
}

#logo {
    background-color: #e94560;
    color: #ffffff;
    font-size: 18px;
    font-weight: bold;
    border-radius: 6px;
}

#dashboardButton, #settingsButton, #addAccountButton {
    background: transparent;
    color: #94a3b8;
    border: none;
    padding: 6px 12px;
    font-size: 12px;
}

#dashboardButton:checked, #settingsButton:checked {
    color: #ffffff;
    border-bottom: 2px solid #e94560;
}

#minimizeButton, #maximizeButton, #closeButton {
    background: transparent;
    color: #94a3b8;
    border: none;
    font-size: 16px;
    min-width: 28px;
    max-width: 28px;
}

#closeButton:hover {
    background-color: #e94560;
    color: #ffffff;
}

/* ── Left sidebar — accounts ─────────────────────────────── */

#accountsPanel {
    background-color: #16213e;
    border-right: 1px solid #2a2a4a;
}

#accountsHeader {
    background-color: #1a1a36;
    border-bottom: 1px solid #2a2a4a;
}

#accountsTree {
    background-color: transparent;
    border: none;
    color: #e2e8f0;
    outline: none;
}

#accountsTree::item {
    padding: 8px 12px;
    border-bottom: 1px solid #1e1e3a;
}

#accountsTree::item:selected {
    background-color: #1f4068;
    color: #ffffff;
}

#accountsTree::item:hover {
    background-color: #1a2744;
}

#addJagexAccountButton {
    background-color: #1f4068;
    color: #94a3b8;
    border: 1px dashed #3a3a5c;
    border-radius: 4px;
    margin: 8px;
}

#addJagexAccountButton:hover {
    background-color: #254a78;
    color: #ffffff;
}

/* ── Center — dashboard ──────────────────────────────────── */

#dashboard {
    background-color: #1b1b2f;
}

#characterHeader {
    background-color: #1f4068;
    border-radius: 8px;
    margin: 8px 12px;
}

#characterName {
    font-size: 18px;
    font-weight: bold;
    color: #ffffff;
}

#characterInfo {
    font-size: 12px;
    color: #94a3b8;
}

#avatar {
    background-color: #2a2a4a;
    color: #94a3b8;
    border-radius: 28px;
    font-size: 14px;
}

#statusArea {
    background-color: rgba(74, 222, 128, 0.1);
    border: 1px solid rgba(74, 222, 128, 0.3);
    border-radius: 6px;
    padding: 6px;
}

#statusLabel {
    color: #4ade80;
    font-size: 11px;
    font-weight: bold;
}

#onlineCount {
    color: #94a3b8;
    font-size: 11px;
}

#navigationTabs {
    background: transparent;
    color: #94a3b8;
}

#metricsCard, #questsCard, #activityCard, #skillsCard {
    background-color: #16213e;
    border: 1px solid #2a2a4a;
    border-radius: 8px;
    margin: 4px 12px;
    min-height: 160px;
}

/* ── Right sidebar — clients ─────────────────────────────── */

#clientPanel {
    background-color: #16213e;
    border-left: 1px solid #2a2a4a;
}

#clientTitle {
    font-size: 14px;
    font-weight: bold;
    color: #ffffff;
}

#clientList {
    background-color: transparent;
    border: none;
    color: #e2e8f0;
    outline: none;
}

#clientList::item {
    padding: 10px 12px;
    border-bottom: 1px solid #1e1e3a;
}

#clientList::item:selected {
    background-color: #1f4068;
    color: #ffffff;
}

#clientList::item:hover {
    background-color: #1a2744;
}

#playButton {
    background-color: #e94560;
    color: #ffffff;
    font-size: 15px;
    font-weight: bold;
    border: none;
    border-radius: 6px;
}

#playButton:hover {
    background-color: #d63050;
}

#playButton:pressed {
    background-color: #c02040;
}

#lastPlayed {
    color: #64748b;
    font-size: 11px;
}

/* ── Bottom bar ──────────────────────────────────────────── */

#bottomBar {
    background-color: #16213e;
    border-top: 1px solid #2a2a4a;
}

#launcherVersion, #updateStatus {
    color: #64748b;
    font-size: 11px;
}

#discordButton, #newsButton, #supportButton {
    background: transparent;
    color: #64748b;
    border: none;
    font-size: 11px;
}

#discordButton:hover, #newsButton:hover, #supportButton:hover {
    color: #94a3b8;
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
                row.setStyleSheet("color: #e2e8f0; font-size: 11px; padding: 4px 0;")
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
