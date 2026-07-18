# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'launcher.ui'
##
## Created by: Qt User Interface Compiler version 6.11.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QFrame, QHBoxLayout, QHeaderView,
    QLabel, QListWidget, QListWidgetItem, QMainWindow,
    QPushButton, QSizePolicy, QSpacerItem, QTabBar,
    QToolButton, QTreeWidget, QTreeWidgetItem, QVBoxLayout,
    QWidget)

class Ui_RuneLauncher(object):
    def setupUi(self, RuneLauncher):
        if not RuneLauncher.objectName():
            RuneLauncher.setObjectName(u"RuneLauncher")
        RuneLauncher.setMinimumSize(QSize(1100, 700))
        self.centralWidget = QWidget(RuneLauncher)
        self.centralWidget.setObjectName(u"centralWidget")
        self.rootLayout = QVBoxLayout(self.centralWidget)
        self.rootLayout.setSpacing(0)
        self.rootLayout.setObjectName(u"rootLayout")
        self.rootLayout.setContentsMargins(0, 0, 0, 0)
        self.topBar = QFrame(self.centralWidget)
        self.topBar.setObjectName(u"topBar")
        self.topBar.setMinimumSize(QSize(0, 48))
        self.topBar.setMaximumSize(QSize(16777215, 48))
        self.hboxLayout = QHBoxLayout(self.topBar)
        self.hboxLayout.setSpacing(8)
        self.hboxLayout.setObjectName(u"hboxLayout")
        self.hboxLayout.setContentsMargins(12, -1, 8, -1)
        self.branding = QWidget(self.topBar)
        self.branding.setObjectName(u"branding")
        self.hboxLayout1 = QHBoxLayout(self.branding)
        self.hboxLayout1.setSpacing(8)
        self.hboxLayout1.setObjectName(u"hboxLayout1")
        self.hboxLayout1.setContentsMargins(0, 0, 0, 0)
        self.logo = QLabel(self.branding)
        self.logo.setObjectName(u"logo")
        self.logo.setMinimumSize(QSize(32, 32))
        self.logo.setMaximumSize(QSize(32, 32))
        self.logo.setAlignment(Qt.AlignCenter)

        self.hboxLayout1.addWidget(self.logo)

        self.vboxLayout = QVBoxLayout()
        self.vboxLayout.setSpacing(0)
        self.vboxLayout.setObjectName(u"vboxLayout")
        self.title = QLabel(self.branding)
        self.title.setObjectName(u"title")

        self.vboxLayout.addWidget(self.title)

        self.subtitle = QLabel(self.branding)
        self.subtitle.setObjectName(u"subtitle")

        self.vboxLayout.addWidget(self.subtitle)


        self.hboxLayout1.addLayout(self.vboxLayout)


        self.hboxLayout.addWidget(self.branding)

        self.dashboardButton = QToolButton(self.topBar)
        self.dashboardButton.setObjectName(u"dashboardButton")
        self.dashboardButton.setCheckable(True)
        self.dashboardButton.setChecked(True)

        self.hboxLayout.addWidget(self.dashboardButton)

        self.settingsButton = QToolButton(self.topBar)
        self.settingsButton.setObjectName(u"settingsButton")
        self.settingsButton.setCheckable(True)

        self.hboxLayout.addWidget(self.settingsButton)

        self.addAccountButton = QToolButton(self.topBar)
        self.addAccountButton.setObjectName(u"addAccountButton")

        self.hboxLayout.addWidget(self.addAccountButton)

        self.topSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.hboxLayout.addItem(self.topSpacer)

        self.minimizeButton = QToolButton(self.topBar)
        self.minimizeButton.setObjectName(u"minimizeButton")

        self.hboxLayout.addWidget(self.minimizeButton)

        self.maximizeButton = QToolButton(self.topBar)
        self.maximizeButton.setObjectName(u"maximizeButton")

        self.hboxLayout.addWidget(self.maximizeButton)

        self.closeButton = QToolButton(self.topBar)
        self.closeButton.setObjectName(u"closeButton")

        self.hboxLayout.addWidget(self.closeButton)


        self.rootLayout.addWidget(self.topBar)

        self.contentLayout = QHBoxLayout()
        self.contentLayout.setSpacing(0)
        self.contentLayout.setObjectName(u"contentLayout")
        self.accountsPanel = QFrame(self.centralWidget)
        self.accountsPanel.setObjectName(u"accountsPanel")
        self.accountsPanel.setMinimumSize(QSize(220, 0))
        self.accountsPanel.setMaximumSize(QSize(220, 16777215))
        self.vboxLayout1 = QVBoxLayout(self.accountsPanel)
        self.vboxLayout1.setSpacing(0)
        self.vboxLayout1.setObjectName(u"vboxLayout1")
        self.vboxLayout1.setContentsMargins(0, 0, 0, 0)
        self.accountsHeader = QFrame(self.accountsPanel)
        self.accountsHeader.setObjectName(u"accountsHeader")
        self.accountsHeader.setMinimumSize(QSize(0, 40))
        self.accountsHeader.setMaximumSize(QSize(16777215, 40))

        self.vboxLayout1.addWidget(self.accountsHeader)

        self.accountsTree = QTreeWidget(self.accountsPanel)
        self.accountsTree.setObjectName(u"accountsTree")
        self.accountsTree.setHeaderHidden(True)
        self.accountsTree.setIndentation(12)
        self.accountsTree.setRootIsDecorated(True)

        self.vboxLayout1.addWidget(self.accountsTree)

        self.addJagexAccountButton = QPushButton(self.accountsPanel)
        self.addJagexAccountButton.setObjectName(u"addJagexAccountButton")
        self.addJagexAccountButton.setMinimumSize(QSize(0, 36))

        self.vboxLayout1.addWidget(self.addJagexAccountButton)


        self.contentLayout.addWidget(self.accountsPanel)

        self.dashboard = QWidget(self.centralWidget)
        self.dashboard.setObjectName(u"dashboard")
        self.vboxLayout2 = QVBoxLayout(self.dashboard)
        self.vboxLayout2.setObjectName(u"vboxLayout2")
        self.vboxLayout2.setContentsMargins(0, 0, 0, 0)
        self.characterHeader = QFrame(self.dashboard)
        self.characterHeader.setObjectName(u"characterHeader")
        self.characterHeader.setMinimumSize(QSize(0, 80))
        self.characterHeader.setMaximumSize(QSize(16777215, 80))
        self.hboxLayout2 = QHBoxLayout(self.characterHeader)
        self.hboxLayout2.setObjectName(u"hboxLayout2")
        self.hboxLayout2.setContentsMargins(16, -1, 16, -1)
        self.avatar = QLabel(self.characterHeader)
        self.avatar.setObjectName(u"avatar")
        self.avatar.setMinimumSize(QSize(56, 56))
        self.avatar.setMaximumSize(QSize(56, 56))
        self.avatar.setAlignment(Qt.AlignCenter)

        self.hboxLayout2.addWidget(self.avatar)

        self.vboxLayout3 = QVBoxLayout()
        self.vboxLayout3.setSpacing(2)
        self.vboxLayout3.setObjectName(u"vboxLayout3")
        self.characterName = QLabel(self.characterHeader)
        self.characterName.setObjectName(u"characterName")

        self.vboxLayout3.addWidget(self.characterName)

        self.characterInfo = QLabel(self.characterHeader)
        self.characterInfo.setObjectName(u"characterInfo")

        self.vboxLayout3.addWidget(self.characterInfo)

        self.navigationTabs = QTabBar(self.characterHeader)
        self.navigationTabs.setObjectName(u"navigationTabs")
        self.navigationTabs.setCurrentIndex(0)

        self.vboxLayout3.addWidget(self.navigationTabs)


        self.hboxLayout2.addLayout(self.vboxLayout3)

        self.headerSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.hboxLayout2.addItem(self.headerSpacer)

        self.statusArea = QFrame(self.characterHeader)
        self.statusArea.setObjectName(u"statusArea")
        self.statusArea.setMinimumSize(QSize(140, 0))
        self.vboxLayout4 = QVBoxLayout(self.statusArea)
        self.vboxLayout4.setSpacing(4)
        self.vboxLayout4.setObjectName(u"vboxLayout4")
        self.statusLabel = QLabel(self.statusArea)
        self.statusLabel.setObjectName(u"statusLabel")

        self.vboxLayout4.addWidget(self.statusLabel)

        self.onlineCount = QLabel(self.statusArea)
        self.onlineCount.setObjectName(u"onlineCount")

        self.vboxLayout4.addWidget(self.onlineCount)


        self.hboxLayout2.addWidget(self.statusArea)


        self.vboxLayout2.addWidget(self.characterHeader)

        self.hboxLayout3 = QHBoxLayout()
        self.hboxLayout3.setObjectName(u"hboxLayout3")
        self.metricsCard = QFrame(self.dashboard)
        self.metricsCard.setObjectName(u"metricsCard")

        self.hboxLayout3.addWidget(self.metricsCard)

        self.questsCard = QFrame(self.dashboard)
        self.questsCard.setObjectName(u"questsCard")

        self.hboxLayout3.addWidget(self.questsCard)


        self.vboxLayout2.addLayout(self.hboxLayout3)

        self.hboxLayout4 = QHBoxLayout()
        self.hboxLayout4.setObjectName(u"hboxLayout4")
        self.activityCard = QFrame(self.dashboard)
        self.activityCard.setObjectName(u"activityCard")

        self.hboxLayout4.addWidget(self.activityCard)

        self.skillsCard = QFrame(self.dashboard)
        self.skillsCard.setObjectName(u"skillsCard")

        self.hboxLayout4.addWidget(self.skillsCard)


        self.vboxLayout2.addLayout(self.hboxLayout4)


        self.contentLayout.addWidget(self.dashboard)

        self.clientPanel = QFrame(self.centralWidget)
        self.clientPanel.setObjectName(u"clientPanel")
        self.clientPanel.setMinimumSize(QSize(200, 0))
        self.clientPanel.setMaximumSize(QSize(200, 16777215))
        self.vboxLayout5 = QVBoxLayout(self.clientPanel)
        self.vboxLayout5.setSpacing(8)
        self.vboxLayout5.setObjectName(u"vboxLayout5")
        self.vboxLayout5.setContentsMargins(8, 12, 8, 8)
        self.clientTitle = QLabel(self.clientPanel)
        self.clientTitle.setObjectName(u"clientTitle")

        self.vboxLayout5.addWidget(self.clientTitle)

        self.clientList = QListWidget(self.clientPanel)
        self.clientList.setObjectName(u"clientList")

        self.vboxLayout5.addWidget(self.clientList)

        self.playButton = QPushButton(self.clientPanel)
        self.playButton.setObjectName(u"playButton")
        self.playButton.setMinimumSize(QSize(0, 40))

        self.vboxLayout5.addWidget(self.playButton)

        self.lastPlayed = QLabel(self.clientPanel)
        self.lastPlayed.setObjectName(u"lastPlayed")

        self.vboxLayout5.addWidget(self.lastPlayed)


        self.contentLayout.addWidget(self.clientPanel)


        self.rootLayout.addLayout(self.contentLayout)

        self.bottomBar = QFrame(self.centralWidget)
        self.bottomBar.setObjectName(u"bottomBar")
        self.bottomBar.setMinimumSize(QSize(0, 32))
        self.bottomBar.setMaximumSize(QSize(16777215, 32))
        self.hboxLayout5 = QHBoxLayout(self.bottomBar)
        self.hboxLayout5.setObjectName(u"hboxLayout5")
        self.hboxLayout5.setContentsMargins(12, -1, 8, -1)
        self.launcherVersion = QLabel(self.bottomBar)
        self.launcherVersion.setObjectName(u"launcherVersion")

        self.hboxLayout5.addWidget(self.launcherVersion)

        self.updateStatus = QLabel(self.bottomBar)
        self.updateStatus.setObjectName(u"updateStatus")

        self.hboxLayout5.addWidget(self.updateStatus)

        self.bottomSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.hboxLayout5.addItem(self.bottomSpacer)

        self.discordButton = QToolButton(self.bottomBar)
        self.discordButton.setObjectName(u"discordButton")

        self.hboxLayout5.addWidget(self.discordButton)

        self.newsButton = QToolButton(self.bottomBar)
        self.newsButton.setObjectName(u"newsButton")

        self.hboxLayout5.addWidget(self.newsButton)

        self.supportButton = QToolButton(self.bottomBar)
        self.supportButton.setObjectName(u"supportButton")

        self.hboxLayout5.addWidget(self.supportButton)


        self.rootLayout.addWidget(self.bottomBar)

        RuneLauncher.setCentralWidget(self.centralWidget)

        self.retranslateUi(RuneLauncher)

        self.clientList.setCurrentRow(-1)


        QMetaObject.connectSlotsByName(RuneLauncher)
    # setupUi

    def retranslateUi(self, RuneLauncher):
        RuneLauncher.setWindowTitle(QCoreApplication.translate("RuneLauncher", u"RS3TK", None))
        self.logo.setText(QCoreApplication.translate("RuneLauncher", u"R", None))
        self.title.setText(QCoreApplication.translate("RuneLauncher", u"RS3TK", None))
        self.subtitle.setText(QCoreApplication.translate("RuneLauncher", u"RuneScape ToolKit", None))
        self.dashboardButton.setText(QCoreApplication.translate("RuneLauncher", u"Dashboard", None))
        self.settingsButton.setText(QCoreApplication.translate("RuneLauncher", u"Settings", None))
        self.addAccountButton.setText(QCoreApplication.translate("RuneLauncher", u"+ Add Account", None))
        self.minimizeButton.setText(QCoreApplication.translate("RuneLauncher", u"-", None))
        self.maximizeButton.setText(QCoreApplication.translate("RuneLauncher", u"\u25a1", None))
        self.closeButton.setText(QCoreApplication.translate("RuneLauncher", u"\u00d7", None))
        ___qtreewidgetitem = self.accountsTree.headerItem()
        ___qtreewidgetitem.setText(0, QCoreApplication.translate("RuneLauncher", u"1", None))
        self.addJagexAccountButton.setText(QCoreApplication.translate("RuneLauncher", u"+ Add Jagex Account", None))
        self.avatar.setText(QCoreApplication.translate("RuneLauncher", u"Avatar", None))
        self.characterName.setText(QCoreApplication.translate("RuneLauncher", u"Cow31337Killer", None))
        self.characterInfo.setText(QCoreApplication.translate("RuneLauncher", u"Combat 151 | Rank 89,609 | Total XP 1.28B", None))
        self.statusLabel.setText(QCoreApplication.translate("RuneLauncher", u"All Systems Operational", None))
        self.onlineCount.setText(QCoreApplication.translate("RuneLauncher", u"151,698 online", None))
        self.clientTitle.setText(QCoreApplication.translate("RuneLauncher", u"Game Clients", None))
        self.playButton.setText(QCoreApplication.translate("RuneLauncher", u"PLAY", None))
        self.lastPlayed.setText(QCoreApplication.translate("RuneLauncher", u"Last played: 2 hours ago", None))
        self.launcherVersion.setText(QCoreApplication.translate("RuneLauncher", u"v0.1.0", None))
        self.updateStatus.setText(QCoreApplication.translate("RuneLauncher", u"Up to date", None))
        self.discordButton.setText(QCoreApplication.translate("RuneLauncher", u"Discord", None))
        self.newsButton.setText(QCoreApplication.translate("RuneLauncher", u"News", None))
        self.supportButton.setText(QCoreApplication.translate("RuneLauncher", u"Support", None))
    # retranslateUi

