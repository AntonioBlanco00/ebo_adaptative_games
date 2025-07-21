# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'mainUI.ui'
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
from PySide6.QtWidgets import (QApplication, QFrame, QLabel, QPlainTextEdit,
    QPushButton, QSizePolicy, QTextEdit, QWidget)

class Ui_guiDlg(object):
    def setupUi(self, guiDlg):
        if not guiDlg.objectName():
            guiDlg.setObjectName(u"guiDlg")
        guiDlg.resize(942, 624)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(guiDlg.sizePolicy().hasHeightForWidth())
        guiDlg.setSizePolicy(sizePolicy)
        self.adelante = QPushButton(guiDlg)
        self.adelante.setObjectName(u"adelante")
        self.adelante.setGeometry(QRect(618, 250, 101, 25))
        self.derecha = QPushButton(guiDlg)
        self.derecha.setObjectName(u"derecha")
        self.derecha.setGeometry(QRect(680, 280, 89, 25))
        self.derecha.setLayoutDirection(Qt.LeftToRight)
        self.plainTextEdit = QPlainTextEdit(guiDlg)
        self.plainTextEdit.setObjectName(u"plainTextEdit")
        self.plainTextEdit.setGeometry(QRect(40, 60, 581, 101))
        self.plainTextEdit.setFrameShape(QFrame.StyledPanel)
        self.plainTextEdit.setFrameShadow(QFrame.Sunken)
        self.plainTextEdit.setLineWidth(1)
        self.atras = QPushButton(guiDlg)
        self.atras.setObjectName(u"atras")
        self.atras.setGeometry(QRect(620, 310, 101, 25))
        self.izquierda = QPushButton(guiDlg)
        self.izquierda.setObjectName(u"izquierda")
        self.izquierda.setGeometry(QRect(560, 280, 89, 25))
        self.label = QLabel(guiDlg)
        self.label.setObjectName(u"label")
        self.label.setGeometry(QRect(270, 390, 291, 171))
        self.label.setPixmap(QPixmap(u"../../../../Antonio/Desktop/json_generator/interfaz_g/robolab.png"))
        self.textEdit = QTextEdit(guiDlg)
        self.textEdit.setObjectName(u"textEdit")
        self.textEdit.setGeometry(QRect(40, 20, 381, 31))
        self.textEdit.setAutoFillBackground(True)
        self.textEdit.setStyleSheet(u"background-color: transparent;")
        self.textEdit.setFrameShape(QFrame.NoFrame)
        self.textEdit.setFrameShadow(QFrame.Sunken)
        self.textEdit.setReadOnly(True)
        self.quieto = QPushButton(guiDlg)
        self.quieto.setObjectName(u"quieto")
        self.quieto.setGeometry(QRect(550, 350, 231, 81))
        self.miedo = QPushButton(guiDlg)
        self.miedo.setObjectName(u"miedo")
        self.miedo.setGeometry(QRect(270, 260, 90, 60))
        self.miedo.setStyleSheet(u"")
        icon = QIcon()
        icon.addFile(u"img/miedo.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.miedo.setIcon(icon)
        self.miedo.setIconSize(QSize(88, 58))
        self.sorpresa = QPushButton(guiDlg)
        self.sorpresa.setObjectName(u"sorpresa")
        self.sorpresa.setGeometry(QRect(270, 340, 90, 60))
        self.sorpresa.setStyleSheet(u"")
        icon1 = QIcon()
        icon1.addFile(u"img/sorpresa.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.sorpresa.setIcon(icon1)
        self.sorpresa.setIconSize(QSize(88, 58))
        self.triste = QPushButton(guiDlg)
        self.triste.setObjectName(u"triste")
        self.triste.setGeometry(QRect(160, 340, 90, 60))
        self.triste.setStyleSheet(u"")
        icon2 = QIcon()
        icon2.addFile(u"img/tristeza.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.triste.setIcon(icon2)
        self.triste.setIconSize(QSize(88, 58))
        self.textEdit_2 = QTextEdit(guiDlg)
        self.textEdit_2.setObjectName(u"textEdit_2")
        self.textEdit_2.setGeometry(QRect(50, 210, 381, 31))
        self.textEdit_2.setAutoFillBackground(True)
        self.textEdit_2.setStyleSheet(u"background-color: transparent;")
        self.textEdit_2.setFrameShape(QFrame.NoFrame)
        self.textEdit_2.setFrameShadow(QFrame.Sunken)
        self.textEdit_2.setReadOnly(True)
        self.feliz = QPushButton(guiDlg)
        self.feliz.setObjectName(u"feliz")
        self.feliz.setGeometry(QRect(50, 260, 90, 60))
        self.feliz.setStyleSheet(u"")
        icon3 = QIcon()
        icon3.addFile(u"img/alegria.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.feliz.setIcon(icon3)
        self.feliz.setIconSize(QSize(88, 58))
        self.asco = QPushButton(guiDlg)
        self.asco.setObjectName(u"asco")
        self.asco.setGeometry(QRect(160, 260, 90, 60))
        self.asco.setStyleSheet(u"")
        icon4 = QIcon()
        icon4.addFile(u"img/asco.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.asco.setIcon(icon4)
        self.asco.setIconSize(QSize(88, 58))
        self.enfado = QPushButton(guiDlg)
        self.enfado.setObjectName(u"enfado")
        self.enfado.setGeometry(QRect(50, 340, 90, 60))
        self.enfado.setStyleSheet(u"")
        icon5 = QIcon()
        icon5.addFile(u"img/ira.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.enfado.setIcon(icon5)
        self.enfado.setIconSize(QSize(88, 58))
        self.pushButton = QPushButton(guiDlg)
        self.pushButton.setObjectName(u"pushButton")
        self.pushButton.setGeometry(QRect(660, 90, 89, 41))
        self.textEdit_3 = QTextEdit(guiDlg)
        self.textEdit_3.setObjectName(u"textEdit_3")
        self.textEdit_3.setGeometry(QRect(520, 200, 381, 31))
        self.textEdit_3.setAutoFillBackground(True)
        self.textEdit_3.setStyleSheet(u"background-color: transparent;")
        self.textEdit_3.setFrameShape(QFrame.NoFrame)
        self.textEdit_3.setFrameShadow(QFrame.Sunken)
        self.textEdit_3.setReadOnly(True)
        self.GPT_mode = QPushButton(guiDlg)
        self.GPT_mode.setObjectName(u"GPT_mode")
        self.GPT_mode.setGeometry(QRect(780, 90, 141, 41))
        self.leds_off = QPushButton(guiDlg)
        self.leds_off.setObjectName(u"leds_off")
        self.leds_off.setGeometry(QRect(160, 410, 90, 31))
        self.leds_off.setStyleSheet(u"")
        self.leds_off.setIconSize(QSize(88, 58))
        self.texto_gpt = QTextEdit(guiDlg)
        self.texto_gpt.setObjectName(u"texto_gpt")
        self.texto_gpt.setGeometry(QRect(680, 50, 381, 31))
        self.texto_gpt.setAutoFillBackground(True)
        self.texto_gpt.setStyleSheet(u"background-color: transparent;")
        self.texto_gpt.setInputMethodHints(Qt.ImhMultiLine)
        self.texto_gpt.setFrameShape(QFrame.NoFrame)
        self.texto_gpt.setFrameShadow(QFrame.Sunken)
        self.texto_gpt.setReadOnly(True)
        self.label_2 = QLabel(guiDlg)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setGeometry(QRect(680, 460, 221, 141))
        self.label_2.setPixmap(QPixmap(u"img/robolab.png"))
        self.label_2.setScaledContents(True)
        self.label_3 = QLabel(guiDlg)
        self.label_3.setObjectName(u"label_3")
        self.label_3.setGeometry(QRect(20, 470, 631, 141))
        self.label_3.setPixmap(QPixmap(u"img/euroage.png"))
        self.label_3.setScaledContents(True)

        self.retranslateUi(guiDlg)

        QMetaObject.connectSlotsByName(guiDlg)
    # setupUi

    def retranslateUi(self, guiDlg):
        guiDlg.setWindowTitle(QCoreApplication.translate("guiDlg", u"app_ebo", None))
        self.adelante.setText(QCoreApplication.translate("guiDlg", u"\u21d1", None))
        self.derecha.setText(QCoreApplication.translate("guiDlg", u"\u21d2", None))
        self.atras.setText(QCoreApplication.translate("guiDlg", u"\u21d3", None))
        self.izquierda.setText(QCoreApplication.translate("guiDlg", u"\u21d0", None))
        self.label.setText("")
        self.textEdit.setHtml(QCoreApplication.translate("guiDlg", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:'Ubuntu'; font-size:11pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:14pt;\">Escribe aqu\u00ed lo que quieres que diga EBO:</span></p></body></html>", None))
        self.quieto.setText(QCoreApplication.translate("guiDlg", u"STOP", None))
        self.miedo.setText("")
        self.sorpresa.setText("")
        self.triste.setText("")
        self.textEdit_2.setHtml(QCoreApplication.translate("guiDlg", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:'Ubuntu'; font-size:11pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:14pt;\">Controla el estado de \u00e1nimo de EBO:</span></p></body></html>", None))
        self.feliz.setText("")
        self.asco.setText("")
        self.enfado.setText("")
        self.pushButton.setText(QCoreApplication.translate("guiDlg", u"Enviar", None))
        self.textEdit_3.setHtml(QCoreApplication.translate("guiDlg", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:'Ubuntu'; font-size:11pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:14pt;\">Controla el movimiento de EBO:</span></p></body></html>", None))
        self.GPT_mode.setText(QCoreApplication.translate("guiDlg", u"Entrar Modo GPT", None))
        self.leds_off.setText(QCoreApplication.translate("guiDlg", u"Apagar LEDs", None))
        self.texto_gpt.setHtml(QCoreApplication.translate("guiDlg", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:'Ubuntu'; font-size:11pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:14pt;\">\u00a1MODO GPT ACTIVADO!</span></p></body></html>", None))
        self.label_2.setText("")
        self.label_3.setText("")
    # retranslateUi

