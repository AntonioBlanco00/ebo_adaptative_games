#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
#    Copyright (C) 2024 by YOUR NAME HERE
#
#    This file is part of RoboComp
#
#    RoboComp is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    RoboComp is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with RoboComp.  If not, see <http://www.gnu.org/licenses/>.
#

from PySide6.QtCore import QTimer, Qt, QEvent
from PySide6.QtWidgets import QApplication, QDialog, QVBoxLayout, QLabel, QLineEdit, QComboBox, QPushButton
from rich.console import Console
from genericworker import *
import interfaces as ifaces
import traceback
import time
import math

sys.path.append('/opt/robocomp/lib')
console = Console(highlight=False)


# If RoboComp was compiled with Python bindings you can use InnerModel in Python
# import librobocomp_qmat
# import librobocomp_osgviewer
# import librobocomp_innermodel

class JuegoSelector(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Seleccionar Juego y Mensaje")
        self.setFixedSize(600, 325)  # Fija el tamaño de la ventana

        # Layout principal
        layout = QVBoxLayout()

        # Etiqueta para el juego
        self.juego_label = QLabel("Selecciona un juego:")
        layout.addWidget(self.juego_label)

        # ComboBox para seleccionar el juego
        self.juego_combo = QComboBox()
        self.juego_combo.addItem("Conversation_Game")
        self.juego_combo.addItem("Conversation_Test")
        self.juego_combo.addItem("De_charla_con_EBO")
        self.juego_combo.addItem("Colegios")
        layout.addWidget(self.juego_combo)

        # Etiqueta para el mensaje
        self.mensaje_label = QLabel("Introduce un mensaje inicial:")
        layout.addWidget(self.mensaje_label)

        # Campo de texto para el mensaje
        self.mensaje_input = QLineEdit()
        layout.addWidget(self.mensaje_input)

        # Botones de Aceptar y Atrás
        self.aceptar_button = QPushButton("Aceptar")
        self.aceptar_button.clicked.connect(self.aceptar)
        layout.addWidget(self.aceptar_button)

        self.atras_button = QPushButton("Atrás")
        self.atras_button.clicked.connect(self.reject)  # Cierra el widget
        layout.addWidget(self.atras_button)

        # Establecer el layout del widget
        self.setLayout(layout)

    def aceptar(self):
        # Al hacer clic en Aceptar, almacenamos los valores seleccionados
        self.juego_seleccionado = self.juego_combo.currentText()
        self.mensaje_inicial = self.mensaje_input.text()
        self.accept()  # Cierra el widget


class SpecificWorker(GenericWorker):
    def __init__(self, proxy_map, startup_check=False):
        super(SpecificWorker, self).__init__(proxy_map)
        self.Period = 2000
        self.NUM_LEDS = 52
        if startup_check:
            self.startup_check()
        else:
            self.timer.timeout.connect(self.compute)
            self.timer.start(self.Period)
        self.ui.texto_gpt.setVisible(False)

        #Botón para hablar
        self.ui.pushButton.clicked.connect(self.enviar_tts)

        # Agregar evento de teclado para detectar Enter
        self.ui.plainTextEdit.installEventFilter(self)

        # Botón para el modo chatGPT
        self.ui.GPT_mode.clicked.connect(self.activar_gpt)

        #Botones de emociones
        self.ui.feliz.clicked.connect(lambda: self.emotion_clicked("Feliz"))
        self.ui.asco.clicked.connect(lambda: self.emotion_clicked("Asco"))
        self.ui.sorpresa.clicked.connect(lambda: self.emotion_clicked("Sorpresa"))
        self.ui.triste.clicked.connect(lambda: self.emotion_clicked("Triste"))
        self.ui.enfado.clicked.connect(lambda: self.emotion_clicked("Enfado"))
        self.ui.miedo.clicked.connect(lambda: self.emotion_clicked("Miedo"))

        #Botones de movimiento
        self.ui.adelante.clicked.connect(lambda: self.move_clicked("Adelante"))
        self.ui.izquierda.clicked.connect(lambda: self.move_clicked("Izquierda"))
        self.ui.derecha.clicked.connect(lambda: self.move_clicked("Derecha"))
        self.ui.atras.clicked.connect(lambda: self.move_clicked("Atras"))
        self.ui.quieto.clicked.connect(lambda: self.move_clicked("Quieto"))

        # Apagar LEDs
        self.ui.leds_off.clicked.connect(self.apagar_leds)

        print('APP INICIADA')


    def __del__(self):
        """Destructor"""

    def setParams(self, params):
        # try:
        #	self.innermodel = InnerModel(params["InnerModelPath"])
        # except:
        #	traceback.print_exc()
        #	print("Error reading config params")
        return True


    @QtCore.Slot()
    def compute(self):
        # print('SpecificWorker.compute...')


        return True

    def set_all_LEDS_colors(self, red=0, green=0, blue=0, white=0):
        pixel_array = {i: ifaces.RoboCompLEDArray.Pixel(red=red, green=green, blue=blue, white=white) for i in
                       range(self.NUM_LEDS)}
        self.ledarray_proxy.setLEDArray(pixel_array)

    def apagar_leds(self):
        self.set_all_LEDS_colors(red=0, green=0, blue=0, white=0)

    def activar_gpt(self):
        print("ACTIVAR CHATGPT PULSADO")

        # Crear y mostrar el widget para seleccionar juego y mensaje
        self.juego_selector = JuegoSelector()

        # Mostrar el widget como un diálogo modal
        if self.juego_selector.exec() == QDialog.Accepted:
            # Al aceptar, obtenemos los valores seleccionados
            self.juego_seleccionado = self.juego_selector.juego_seleccionado
            self.mensaje_inicial = self.juego_selector.mensaje_inicial

            # Actualizamos la interfaz principal con los nuevos valores
            self.actualizar_interfaz()

            # Aquí, podrías almacenar la variable juego_seleccionado para usarla en otros lugares
            print(f"Juego seleccionado: {self.juego_seleccionado}")
            print(f"Mensaje inicial: {self.mensaje_inicial}")

            print(f"\nIniciando el juego: {self.juego_seleccionado} para el usuario: {self.mensaje_inicial}...\n")
            self.gpt_proxy.setGameInfo(self.juego_seleccionado, self.mensaje_inicial)
            self.gpt_proxy.startChat()

    def actualizar_interfaz(self):
        # Cambiar el texto del botón GPT_mode
        self.ui.GPT_mode.setText("Salir modo GPT")
        self.ui.textEdit.clear()  # Borrar el contenido del QTextEdit sin perder formato
        self.ui.textEdit.insertPlainText("Escribe aquí lo que decir a EBO")

        # Hacer visible el cuadro de texto `texto_gpt`
        self.ui.texto_gpt.setVisible(True)

        # Cambiar la función de pushButton
        self.ui.pushButton.clicked.disconnect()  # Desconectar la acción anterior
        self.ui.pushButton.clicked.connect(self.enviar_gpt)  # Conectar a la nueva función

        # Cambiar la función de modoGPT
        self.ui.GPT_mode.clicked.disconnect()
        self.ui.GPT_mode.clicked.connect(self.desactivar_gpt)

        # Cambiar el texto de plainTextEdit (o cualquier otro cambio que desees)
        self.ui.plainTextEdit.clear()

    def regenerar_interfaz(self):
        self.ui.GPT_mode.setText("Entrar modo GPT")
        self.ui.textEdit.clear()
        self.ui.textEdit.setPlainText("Escribe aquí lo que quieres que diga EBO")

        self.ui.texto_gpt.setVisible(False)

        # Cambiar la función de pushButton
        self.ui.pushButton.clicked.disconnect()  # Desconectar la acción anterior
        self.ui.pushButton.clicked.connect(self.enviar_tts)  # Conectar a la nueva función

        # Cambiar la función de modoGPT
        self.ui.GPT_mode.clicked.disconnect()
        self.ui.GPT_mode.clicked.connect(self.activar_gpt)

        # Cambiar el texto de plainTextEdit (o cualquier otro cambio que desees)
        self.ui.plainTextEdit.clear()


    def enviar_gpt(self):
        mensaje = self.ui.plainTextEdit.toPlainText()
        self.ui.plainTextEdit.clear()
        self.gpt_proxy.continueChat(mensaje)


    def desactivar_gpt(self):
        self.gpt_proxy.continueChat("salir")
        self.regenerar_interfaz()
        pass

    def eventFilter(self, source, event):
        """Detectar si se presionó Enter en el plainTextEdit"""
        if source is self.ui.plainTextEdit and event.type() == QEvent.KeyPress:
            if event.key() == Qt.Key_Enter or event.key() == Qt.Key_Return:
                if self.ui.texto_gpt.isVisible():  # Puedes usar otra condición para verificar el modo GPT
                    self.enviar_gpt()
                else:
                    self.enviar_tts()
                return True  # Evita que el evento de tecla se propague más
        return super().eventFilter(source, event)

    def enviar_tts(self):
        self.emotionalmotor_proxy.expressJoy()
        texto = self.ui.plainTextEdit.toPlainText()
        print("Texto enviado:", texto)
        self.ui.plainTextEdit.clear()
        try:
            self.speech_proxy.say(texto, False)
        except Exception as e:
            traceback.print_exc()
            console.print(f"[bold red]Error[/bold red] al enviar TTS: {e}")

    def emotion_clicked(self, emo):
        try:
            if emo == "Feliz":
                self.ebomoods_proxy.expressJoy()
            elif emo == "Asco":
                self.ebomoods_proxy.expressDisgust()
            elif emo == "Sorpresa":
                self.ebomoods_proxy.expressSurprise()
            elif emo == "Triste":
                self.ebomoods_proxy.expressSadness()
            elif emo == "Enfado":
                self.ebomoods_proxy.expressAnger()
            elif emo == "Miedo":
                self.ebomoods_proxy.expressFear()

        except Exception as e:
            traceback.print_exc()
            console.print(f"[bold red]Error[/bold red] al cambiar emoción: {e}")

    def turn(self, duration: float, angular_speed: float):
        self.differentialrobot_proxy.setSpeedBase(0, angular_speed)
        time.sleep(duration)
        self.differentialrobot_proxy.stopBase()

    def move_clicked(self, mov):
        try:
            if mov == "Adelante":
                self.differentialrobot_proxy.setSpeedBase(0, 50)
            elif mov == "Izquierda":
                self.differentialrobot_proxy.setSpeedBase(-50, 0)
                # self.turn(2.05 / 4, -(math.pi / 9))
            elif mov == "Derecha":
                self.differentialrobot_proxy.setSpeedBase(50, 0)
                # self.turn(2.05 / 4, math.pi / 9)
            elif mov == "Atras":
                self.differentialrobot_proxy.setSpeedBase(0, -50)
            else:
                self.differentialrobot_proxy.setSpeedBase(0, 0)
        except Exception as e:
            traceback.print_exc()
            console.print(f"[bold red]Error[/bold red] al mover el robot: {e}")

    def startup_check(self):
        print(f"Testing RoboCompDifferentialRobot.TMechParams from ifaces.RoboCompDifferentialRobot")
        test = ifaces.RoboCompDifferentialRobot.TMechParams()
        print(f"Testing RoboCompLEDArray.Pixel from ifaces.RoboCompLEDArray")
        test = ifaces.RoboCompLEDArray.Pixel()
        QTimer.singleShot(200, QApplication.instance().quit)




    ######################
    # From the RoboCompDifferentialRobot you can call this methods:
    # self.differentialrobot_proxy.correctOdometer(...)
    # self.differentialrobot_proxy.getBasePose(...)
    # self.differentialrobot_proxy.getBaseState(...)
    # self.differentialrobot_proxy.resetOdometer(...)
    # self.differentialrobot_proxy.setOdometer(...)
    # self.differentialrobot_proxy.setOdometerPose(...)
    # self.differentialrobot_proxy.setSpeedBase(...)
    # self.differentialrobot_proxy.stopBase(...)

    ######################
    # From the RoboCompDifferentialRobot you can use this types:
    # RoboCompDifferentialRobot.TMechParams

    ######################
    # From the RoboCompEboMoods you can call this methods:
    # self.ebomoods_proxy.expressAnger(...)
    # self.ebomoods_proxy.expressDisgust(...)
    # self.ebomoods_proxy.expressFear(...)
    # self.ebomoods_proxy.expressJoy(...)
    # self.ebomoods_proxy.expressSadness(...)
    # self.ebomoods_proxy.expressSurprise(...)

    ######################
    # From the RoboCompEmotionalMotor you can call this methods:
    # self.emotionalmotor_proxy.expressAnger(...)
    # self.emotionalmotor_proxy.expressDisgust(...)
    # self.emotionalmotor_proxy.expressFear(...)
    # self.emotionalmotor_proxy.expressJoy(...)
    # self.emotionalmotor_proxy.expressSadness(...)
    # self.emotionalmotor_proxy.expressSurprise(...)
    # self.emotionalmotor_proxy.isanybodythere(...)
    # self.emotionalmotor_proxy.listening(...)
    # self.emotionalmotor_proxy.pupposition(...)
    # self.emotionalmotor_proxy.talking(...)

    ######################
    # From the RoboCompGPT you can call this methods:
    # self.gpt_proxy.continueChat(...)
    # self.gpt_proxy.setGameInfo(...)
    # self.gpt_proxy.startChat(...)

    ######################
    # From the RoboCompLEDArray you can call this methods:
    # self.ledarray_proxy.getLEDArray(...)
    # self.ledarray_proxy.setLEDArray(...)

    ######################
    # From the RoboCompLEDArray you can use this types:
    # RoboCompLEDArray.Pixel

    ######################
    # From the RoboCompSpeech you can call this methods:
    # self.speech_proxy.isBusy(...)
    # self.speech_proxy.say(...)
    # self.speech_proxy.setPitch(...)
    # self.speech_proxy.setTempo(...)


