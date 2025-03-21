# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'mainUI.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *


class Ui_guiDlg(object):
    def setupUi(self, guiDlg):
        if not guiDlg.objectName():
            guiDlg.setObjectName(u"guiDlg")
        guiDlg.resize(0, 0)
        palette = QPalette()
        brush = QBrush(QColor(239, 239, 239, 255))
        brush.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Active, QPalette.Button, brush)
        brush1 = QBrush(QColor(255, 255, 255, 255))
        brush1.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Active, QPalette.Base, brush1)
        brush2 = QBrush(QColor(0, 0, 0, 255))
        brush2.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Active, QPalette.Window, brush2)
        palette.setBrush(QPalette.Inactive, QPalette.Button, brush)
        palette.setBrush(QPalette.Inactive, QPalette.Base, brush1)
        palette.setBrush(QPalette.Inactive, QPalette.Window, brush2)
        palette.setBrush(QPalette.Disabled, QPalette.Button, brush)
        palette.setBrush(QPalette.Disabled, QPalette.Base, brush2)
        palette.setBrush(QPalette.Disabled, QPalette.Window, brush2)
        guiDlg.setPalette(palette)
        self.rojo = QPushButton(guiDlg)
        self.rojo.setObjectName(u"rojo")
        self.rojo.setGeometry(QRect(50, 40, 331, 271))
        palette1 = QPalette()
        brush3 = QBrush(QColor(237, 51, 59, 255))
        brush3.setStyle(Qt.SolidPattern)
        palette1.setBrush(QPalette.Active, QPalette.Button, brush3)
        palette1.setBrush(QPalette.Inactive, QPalette.Button, brush3)
        palette1.setBrush(QPalette.Disabled, QPalette.Button, brush3)
        self.rojo.setPalette(palette1)
        self.azul = QPushButton(guiDlg)
        self.azul.setObjectName(u"azul")
        self.azul.setGeometry(QRect(440, 40, 331, 271))
        palette2 = QPalette()
        brush4 = QBrush(QColor(98, 160, 234, 255))
        brush4.setStyle(Qt.SolidPattern)
        palette2.setBrush(QPalette.Active, QPalette.Button, brush4)
        palette2.setBrush(QPalette.Inactive, QPalette.Button, brush4)
        palette2.setBrush(QPalette.Disabled, QPalette.Button, brush4)
        self.azul.setPalette(palette2)
        self.verde = QPushButton(guiDlg)
        self.verde.setObjectName(u"verde")
        self.verde.setGeometry(QRect(440, 370, 331, 271))
        palette3 = QPalette()
        brush5 = QBrush(QColor(87, 227, 137, 255))
        brush5.setStyle(Qt.SolidPattern)
        palette3.setBrush(QPalette.Active, QPalette.Button, brush5)
        palette3.setBrush(QPalette.Inactive, QPalette.Button, brush5)
        palette3.setBrush(QPalette.Disabled, QPalette.Button, brush5)
        self.verde.setPalette(palette3)
        self.amarillo = QPushButton(guiDlg)
        self.amarillo.setObjectName(u"amarillo")
        self.amarillo.setGeometry(QRect(50, 370, 331, 271))
        palette4 = QPalette()
        brush6 = QBrush(QColor(248, 228, 92, 255))
        brush6.setStyle(Qt.SolidPattern)
        palette4.setBrush(QPalette.Active, QPalette.Button, brush6)
        palette4.setBrush(QPalette.Inactive, QPalette.Button, brush6)
        palette4.setBrush(QPalette.Disabled, QPalette.Button, brush6)
        self.amarillo.setPalette(palette4)

        self.retranslateUi(guiDlg)

        QMetaObject.connectSlotsByName(guiDlg)
    # setupUi

    def retranslateUi(self, guiDlg):
        guiDlg.setWindowTitle(QCoreApplication.translate("guiDlg", u"simonSay", None))
        self.rojo.setText(QCoreApplication.translate("guiDlg", u"ROJO", None))
        self.azul.setText(QCoreApplication.translate("guiDlg", u"AZUL", None))
        self.verde.setText(QCoreApplication.translate("guiDlg", u"VERDE", None))
        self.amarillo.setText(QCoreApplication.translate("guiDlg", u"AMARILLO", None))
    # retranslateUi

