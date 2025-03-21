# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'therapistUI.ui'
##
## Created by: Qt User Interface Compiler version 6.8.0
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
from PySide6.QtWidgets import (QApplication, QLineEdit, QPushButton, QSizePolicy,
    QTextBrowser, QWidget)

class Ui_therapist(object):
    def setupUi(self, therapist):
        if not therapist.objectName():
            therapist.setObjectName(u"therapist")
        therapist.resize(0, 0)
        palette = QPalette()
        brush = QBrush(QColor(255, 255, 255, 255))
        brush.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Active, QPalette.Base, brush)
        brush1 = QBrush(QColor(0, 0, 0, 255))
        brush1.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Active, QPalette.Window, brush1)
        palette.setBrush(QPalette.Inactive, QPalette.Base, brush)
        palette.setBrush(QPalette.Inactive, QPalette.Window, brush1)
        palette.setBrush(QPalette.Disabled, QPalette.Base, brush1)
        palette.setBrush(QPalette.Disabled, QPalette.Window, brush1)
        therapist.setPalette(palette)
        self.dificil = QPushButton(therapist)
        self.dificil.setObjectName(u"dificil")
        self.dificil.setGeometry(QRect(230, 190, 91, 41))
        self.n_intentos = QLineEdit(therapist)
        self.n_intentos.setObjectName(u"n_intentos")
        self.n_intentos.setGeometry(QRect(190, 60, 111, 25))
        self.rondas = QTextBrowser(therapist)
        self.rondas.setObjectName(u"rondas")
        self.rondas.setGeometry(QRect(300, 100, 41, 41))
        self.n_usuario = QLineEdit(therapist)
        self.n_usuario.setObjectName(u"n_usuario")
        self.n_usuario.setGeometry(QRect(30, 40, 151, 25))
        self.dificultad = QLineEdit(therapist)
        self.dificultad.setObjectName(u"dificultad")
        self.dificultad.setGeometry(QRect(30, 150, 131, 25))
        self.n_rondas = QLineEdit(therapist)
        self.n_rondas.setObjectName(u"n_rondas")
        self.n_rondas.setGeometry(QRect(190, 110, 101, 25))
        self.medio = QPushButton(therapist)
        self.medio.setObjectName(u"medio")
        self.medio.setGeometry(QRect(130, 190, 91, 41))
        self.usuario = QTextBrowser(therapist)
        self.usuario.setObjectName(u"usuario")
        self.usuario.setGeometry(QRect(30, 70, 151, 61))
        self.intentos = QTextBrowser(therapist)
        self.intentos.setObjectName(u"intentos")
        self.intentos.setGeometry(QRect(310, 50, 41, 41))
        self.facil = QPushButton(therapist)
        self.facil.setObjectName(u"facil")
        self.facil.setGeometry(QRect(30, 190, 91, 41))

        self.retranslateUi(therapist)

        QMetaObject.connectSlotsByName(therapist)
    # setupUi

    def retranslateUi(self, therapist):
        therapist.setWindowTitle(QCoreApplication.translate("therapist", u"Form", None))
        self.dificil.setText(QCoreApplication.translate("therapist", u"Dif\u00edcil", None))
        self.n_intentos.setText(QCoreApplication.translate("therapist", u"N\u00ba de intentos:", None))
        self.n_usuario.setText(QCoreApplication.translate("therapist", u"Nombre del usuario:", None))
        self.dificultad.setText(QCoreApplication.translate("therapist", u"Elige la dificultad", None))
        self.n_rondas.setText(QCoreApplication.translate("therapist", u"N\u00ba de  rondas:", None))
        self.medio.setText(QCoreApplication.translate("therapist", u"Medio", None))
        self.facil.setText(QCoreApplication.translate("therapist", u"F\u00e1cil", None))
    # retranslateUi

