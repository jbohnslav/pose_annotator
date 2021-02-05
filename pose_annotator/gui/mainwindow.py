# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'mainwindow.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *

from pose_annotator.gui.custom_widgets import *


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(1397, 896)
        self.actionOpen_image = QAction(MainWindow)
        self.actionOpen_image.setObjectName(u"actionOpen_image")
        self.actionOpen_image_directory = QAction(MainWindow)
        self.actionOpen_image_directory.setObjectName(u"actionOpen_image_directory")
        self.actionOpen_video = QAction(MainWindow)
        self.actionOpen_video.setObjectName(u"actionOpen_video")
        self.actionSave = QAction(MainWindow)
        self.actionSave.setObjectName(u"actionSave")
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.centralwidget.sizePolicy().hasHeightForWidth())
        self.centralwidget.setSizePolicy(sizePolicy)
        self.horizontalLayout_2 = QHBoxLayout(self.centralwidget)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(10, 10, 10, 10)
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.toolbox = QGroupBox(self.centralwidget)
        self.toolbox.setObjectName(u"toolbox")
        self.gridLayout_2 = QGridLayout(self.toolbox)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.toolButton = QToolButton(self.toolbox)
        self.toolButton.setObjectName(u"toolButton")
        self.toolButton.setMaximumSize(QSize(30, 30))

        self.gridLayout_2.addWidget(self.toolButton, 0, 0, 1, 1)

        self.toolButton_2 = QToolButton(self.toolbox)
        self.toolButton_2.setObjectName(u"toolButton_2")
        self.toolButton_2.setMaximumSize(QSize(30, 30))

        self.gridLayout_2.addWidget(self.toolButton_2, 0, 1, 1, 1)

        self.toolButton_3 = QToolButton(self.toolbox)
        self.toolButton_3.setObjectName(u"toolButton_3")

        self.gridLayout_2.addWidget(self.toolButton_3, 1, 0, 1, 1)

        self.toolButton_4 = QToolButton(self.toolbox)
        self.toolButton_4.setObjectName(u"toolButton_4")

        self.gridLayout_2.addWidget(self.toolButton_4, 1, 1, 1, 1)


        self.verticalLayout.addWidget(self.toolbox)

        self.keypoints_box = QGroupBox(self.centralwidget)
        self.keypoints_box.setObjectName(u"keypoints_box")
        self.verticalLayout_2 = QVBoxLayout(self.keypoints_box)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")

        self.verticalLayout.addWidget(self.keypoints_box)

        self.verticalLayout.setStretch(0, 1)
        self.verticalLayout.setStretch(1, 4)

        self.horizontalLayout.addLayout(self.verticalLayout)

        self.widget = VideoPlayer(self.centralwidget)
        self.widget.setObjectName(u"widget")
        sizePolicy.setHeightForWidth(self.widget.sizePolicy().hasHeightForWidth())
        self.widget.setSizePolicy(sizePolicy)

        self.horizontalLayout.addWidget(self.widget)

        self.horizontalLayout.setStretch(1, 5)

        self.horizontalLayout_2.addLayout(self.horizontalLayout)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 1397, 22))
        self.menuFile = QMenu(self.menubar)
        self.menuFile.setObjectName(u"menuFile")
        self.menuOpen_image_or_video = QMenu(self.menubar)
        self.menuOpen_image_or_video.setObjectName(u"menuOpen_image_or_video")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuOpen_image_or_video.menuAction())
        self.menuFile.addAction(self.actionSave)
        self.menuOpen_image_or_video.addAction(self.actionOpen_image)
        self.menuOpen_image_or_video.addAction(self.actionOpen_image_directory)
        self.menuOpen_image_or_video.addAction(self.actionOpen_video)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.actionOpen_image.setText(QCoreApplication.translate("MainWindow", u"Open image", None))
        self.actionOpen_image_directory.setText(QCoreApplication.translate("MainWindow", u"Open image directory", None))
        self.actionOpen_video.setText(QCoreApplication.translate("MainWindow", u"Open video", None))
        self.actionSave.setText(QCoreApplication.translate("MainWindow", u"Save", None))
        self.toolbox.setTitle(QCoreApplication.translate("MainWindow", u"Tools", None))
        self.toolButton.setText(QCoreApplication.translate("MainWindow", u"...", None))
        self.toolButton_2.setText(QCoreApplication.translate("MainWindow", u"...", None))
        self.toolButton_3.setText(QCoreApplication.translate("MainWindow", u"...", None))
        self.toolButton_4.setText(QCoreApplication.translate("MainWindow", u"...", None))
        self.keypoints_box.setTitle(QCoreApplication.translate("MainWindow", u"Keypoints", None))
        self.menuFile.setTitle(QCoreApplication.translate("MainWindow", u"File", None))
        self.menuOpen_image_or_video.setTitle(QCoreApplication.translate("MainWindow", u"Open image or video", None))
    # retranslateUi

