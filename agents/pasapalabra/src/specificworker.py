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

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication
from rich.console import Console
from genericworker import *
import interfaces as ifaces
import json
from time import sleep
import pandas as pd
import time
from datetime import datetime
from PySide6 import QtUiTools
from PySide6.QtWidgets import QPushButton, QVBoxLayout, QWidget
from PySide6.QtCore import Qt
import pygame
from pynput import keyboard
import threading
import random


sys.path.append('/opt/robocomp/lib')
console = Console(highlight=False)

from pydsr import *


# If RoboComp was compiled with Python bindings you can use InnerModel in Python
# import librobocomp_qmat
# import librobocomp_osgviewer
# import librobocomp_innermodel

class SpecificWorker(GenericWorker):
    def __init__(self, proxy_map, startup_check=False):
        super(SpecificWorker, self).__init__(proxy_map)
        self.Period = 2000

        # YOU MUST SET AN UNIQUE ID FOR THIS AGENT IN YOUR DEPLOYMENT. "_CHANGE_THIS_ID_" for a valid unique integer
        self.agent_id = 444
        self.g = DSRGraph(0, "pythonAgent", self.agent_id)

        try:
            signals.connect(self.g, signals.UPDATE_NODE_ATTR, self.update_node_att)
        #     signals.connect(self.g, signals.UPDATE_NODE, self.update_node)
        #     signals.connect(self.g, signals.DELETE_NODE, self.delete_node)
        #     signals.connect(self.g, signals.UPDATE_EDGE, self.update_edge)
        #     signals.connect(self.g, signals.UPDATE_EDGE_ATTR, self.update_edge_att)
        #     signals.connect(self.g, signals.DELETE_EDGE, self.delete_edge)
        #     console.print("signals connected")
        except RuntimeError as e:
            print(e)

        if startup_check:
            self.startup_check()
        else:
            self.timer.timeout.connect(self.compute)
            self.timer.start(self.Period)

        pygame.init()

        ########## INTRODUCCIÓN DE SONIDOS ##########
        self.sounds = {
            "click": pygame.mixer.Sound('src/click.wav'),
        }

        self.datos = []
        self.letras = []
        self.preguntas = []
        self.respuestas = []
        self.aciertos = 0
        self.fallos = 0
        self.pasadas = 0
        self.letras_pasadas = []
        self.nombre = ""
        self.fecha = 0
        self.hora = 0
        self.start_time = None
        self.end_time = None
        self.elapsed_time = None
        self.rosco = ""
        self.bd = ""

        ########## DEFINICIÓN DEL DATAFRAME QUE ALMACENA LOS DATOS ##########
        self.df = pd.DataFrame(columns=["Nombre", "Rosco", "Aciertos", "Fallos", "Pasadas", "Fecha", "Hora", "Tiempo transcurrido (min)",
                                        "Tiempo transcurrido (seg)", "Tiempo de respuesta medio (seg)"])
        self.resp = ""
        self.running = False
        self.boton = False
        self.check = ""
        self.letra_actual = ""
        self.pregunta_actual = ""
        self.start_question_time = 0
        self.end_question_time = 0
        self.response_time = 0
        self.responses_times = []
        self.media = 0

        QApplication.processEvents()

        self.ui = self.load_ui()
        self.ui2 = self.therapist_ui()
        self.ui3 = self.load_check()
        self.ui4 = self.comenzar_checked()

        ########## BATERÍA DE RESPUESTAS Y FUNCIÓN PARA ALEATORIZAR ##########
        self.bateria_aciertos = [
            "¡Increíble, acertaste!",
            "¡Qué bien, has acertado!",
            "¡Excelente trabajo, lo lograste!",
            "¡Estupendo, muy bien hecho!",
            "¡Fantástico, respuesta correcta!",
            "¡Bien hecho, estás en racha!",
            "¡Lo hiciste perfecto, sigue así!",
            "¡Genial, has acertado, sigue adelante!"
        ]

        self.bateria_fallos = [
            "Incorrecto. No te preocupes, todos fallamos alguna vez.",
            "Fallo. ¡Ánimo, la próxima vez seguro que aciertas!",
            "Error. ¡No pasa nada, lo seguirás haciendo mejor!",
            "Incorrecto. Un pequeño tropiezo, sigue adelante, ¡lo lograrás!",
            "Mal, pero ¡No te rindas, sigue intentándolo!",
            "Fallo. ¡Sigue adelante, cada intento te acerca más!",
            "Fallaste pero ¡El error no te define, lo harás mejor la próxima!",
            "Incorrecto. ¡Ánimo, que pronto lo conseguirás!"
        ]

        self.bateria_pasapalabra = [
            "¡Pasapalabra, sigue adelante, que te va a ir genial!",
            "¡Pasapalabra! Vamos a la siguiente, ¡tú puedes!",
            "¡No te preocupes, pasamos a la siguiente palabra!",
            "¡Pasapalabra! La siguiente será tuya.",
            "¡Siguiente palabra, que va a ser más fácil!",
            "¡Pasapalabra, a por la siguiente con todo!",
            "¡Vamos, pasemos a la siguiente, lo lograrás!",
            "¡Pasapalabra, ahora es el turno de la siguiente!"
        ]

    def elegir_respuesta(self, bateria):
        return random.choice(bateria)

    def __del__(self):
        """Destructor"""

    def setParams(self, params):
        # try:
        # 	self.innermodel = InnerModel(params["InnerModelPath"])
        # except:
        #	traceback.print_exc()
        #	print("Error reading config params")
        return True

    ########## FUNCIÓN PARA ENCENDER LAS LUCES LEDS ##########
    def set_all_LEDS_colors(self, red=0, green=0, blue=0, white=0):
        pixel_array = {i: ifaces.RoboCompLEDArray.Pixel(red=red, green=green, blue=blue, white=white) for i in
                       range(self.NUM_LEDS)}
        self.ledarray_proxy.setLEDArray(pixel_array)

    ########## OBTIENE LOS ROSCOS ##########
    def archivo(self, archivo_json):
        """Cargar los datos desde el archivo JSON"""
        # Donde json es una string con el nombre del json, ruta a futuro.
        self.bd = archivo_json
        with open(self.bd, 'r', encoding='utf-8') as json_file:
            self.datos = json.load(json_file)["preguntas"] # Acceder a la clave 'preguntas'

        # Iterar sobre las preguntas y almacenar las letras, preguntas y respuestas
        for pregunta in self.datos:
            self.letras.append(pregunta['letra'])  # Guardar las letras
            self.preguntas.append(pregunta['definicion'])  # Guardar las definiciones
            self.respuestas.append(pregunta['respuesta'])  # Guardar las respuestas

    ########## PROCESO DEL JUEGO ##########
    def juego(self):
        json_elegido = "roscos/" + self.rosco  + ".json"
        self.archivo(json_elegido)
        print("Comienzo de juego")
        self.start_time = time.time()
        letras_restantes = self.letras.copy()

        while letras_restantes or self.letras_pasadas:
            # Proceso principal de letras restantes
            if letras_restantes:
                for letra in letras_restantes[:]:  # Iteramos sobre una copia de la lista
                    if not self.running:
                        break

                    self.resp = ""
                    indice = self.letras.index(letra)
                    if self.respuestas[indice].startswith(letra):
                        self.letra_actual = f"Comienza con la letra:{letra}"
                        self.speech_proxy.say(f"Comienza con la letra:{letra}", False)
                        print(f'Con la letra: {letra}')
                    else:
                        self.letra_actual = f"Contiene la letra:{letra}"
                        self.speech_proxy.say(f"Contiene la letra:{letra}", False)
                        print(f'Contiene la letra: {letra}')

                    self.speech_proxy.say(f"{self.preguntas[indice]}", False)
                    print(self.preguntas[indice])
                    respuesta_correcta = self.respuestas[indice]
                    self.pregunta_actual = self.preguntas[indice]
                    self.terminaHablar()
                    self.start_question_time = time.time()
                    self.ui.respuesta.clear()
                    self.ui.respuesta.insertPlainText(respuesta_correcta)
                    self.ui.show()
                    while self.resp == "":
                        QApplication.processEvents()

                    if self.resp == "pasapalabra":
                        self.speech_proxy.say(self.elegir_respuesta(self.bateria_pasapalabra), False)
                        print("Has pasado esta letra.")
                        self.set_all_LEDS_colors(255,255,0)
                        self.emotionalmotor_proxy.expressSurprise()
                        sleep(2)
                        self.set_all_LEDS_colors(0, 0, 0)
                        sleep (1)
                        self.letras_pasadas.append(letra)
                        self.pasadas += 1
                        self.emotionalmotor_proxy.expressJoy()
                        letras_restantes.remove(letra)
                    elif self.resp == "si":
                        self.speech_proxy.say(self.elegir_respuesta(self.bateria_aciertos), False)
                        print("¡Respuesta correcta!")
                        self.set_all_LEDS_colors(0,255,0)
                        self.emotionalmotor_proxy.expressJoy()
                        sleep(1)
                        self.set_all_LEDS_colors(0, 0, 0)
                        sleep (1)
                        self.aciertos += 1
                        self.emotionalmotor_proxy.expressJoy()
                        letras_restantes.remove(letra)  # Eliminar la letra de letras_restantes si es correcta
                    else:
                        self.speech_proxy.say(f"{self.elegir_respuesta(self.bateria_fallos)} La respuesta correcta era {respuesta_correcta}", False)
                        print(f"Respuesta incorrecta! La respuesta es {respuesta_correcta}")
                        self.set_all_LEDS_colors(255,0,0)
                        self.emotionalmotor_proxy.expressSadness()
                        sleep(2)
                        self.set_all_LEDS_colors(0,0,0)
                        sleep (1)
                        self.fallos += 1
                        self.emotionalmotor_proxy.expressJoy()
                        letras_restantes.remove(letra)  # Eliminar la letra de letras_restantes si es correcta

                    self.end_question_time = time.time()
                    self.cerrar_ui(1)
                    self.response_time = self.end_question_time - self.start_question_time
                    self.responses_times.append(self.response_time)

            # Proceso de letras pasadas
            elif self.letras_pasadas:
                self.speech_proxy.say("Vamos a dar otra vuelta con las letras que pasaste.", False)
                print("Ahora vamos a repasar las letras que pasaste.")
                for letra in self.letras_pasadas[:]:  # Iteramos sobre una copia de la lista
                    if not self.running:
                        break

                    self.resp=""
                    indice = self.letras.index(letra)
                    if self.respuestas[indice].startswith(letra):
                        self.speech_proxy.say(f"Comienza con la letra:{letra}", False)
                        print(f'Con la letra: {letra}')
                    else:
                        self.speech_proxy.say(f"Contiene la letra:{letra}", False)
                        print(f'Contiene la letra: {letra}')

                    pregunta = self.preguntas[indice]
                    respuesta_correcta = self.respuestas[indice]
                    self.speech_proxy.say(f"{pregunta}", False)
                    print(f'Pregunta: {pregunta}')
                    self.terminaHablar()
                    self.ui.respuesta.clear()
                    self.ui.respuesta.insertPlainText(respuesta_correcta)
                    self.ui.show()
                    self.start_question_time = time.time()
                    while self.resp == "":
                        QApplication.processEvents()

                    if self.resp == "pasapalabra":
                        self.speech_proxy.say(f"Has pasado esta letra nuevamente", False)
                        print("Has pasado esta letra nuevamente.")
                        self.set_all_LEDS_colors(255, 255, 0)
                        self.emotionalmotor_proxy.expressSurprise()
                        sleep(2)
                        self.set_all_LEDS_colors(0, 0, 0)
                        sleep(1)
                        self.letras_pasadas.remove(letra)
                        self.emotionalmotor_proxy.expressJoy()
                    elif self.resp == "si":
                        self.speech_proxy.say(self.elegir_respuesta(self.bateria_aciertos), False)
                        print("¡Respuesta correcta!")
                        self.set_all_LEDS_colors(0, 255, 0)
                        self.emotionalmotor_proxy.expressJoy()
                        sleep(1)
                        self.set_all_LEDS_colors(0, 0, 0)
                        sleep(1)
                        self.aciertos += 1
                        self.pasadas -= 1
                        self.emotionalmotor_proxy.expressJoy()
                        self.letras_pasadas.remove(letra)  # Eliminar la letra de letras_pasadas si es incorrecta
                    else:
                        self.speech_proxy.say(f"{self.elegir_respuesta(self.bateria_fallos)} La respuesta correcta era {respuesta_correcta}", False)
                        print(f"Respuesta incorrecta! La respuesta es {respuesta_correcta}")
                        self.set_all_LEDS_colors(255, 0, 0)
                        self.emotionalmotor_proxy.expressSadness()
                        sleep(1)
                        self.set_all_LEDS_colors(0, 0, 0)
                        sleep(1)
                        self.fallos += 1
                        self.pasadas -= 1
                        self.emotionalmotor_proxy.expressJoy()
                        self.letras_pasadas.remove(letra)  # Eliminar la letra de letras_pasadas si es incorrecta

                    self.end_question_time = time.time()
                    self.cerrar_ui(1)
                    self.response_time = self.end_question_time - self.start_question_time
                    self.responses_times.append(self.response_time)

        self.end_time = time.time()
        self.elapsed_time = self.end_time - self.start_time  # Tiempo en segundos
        self.media = sum(self.responses_times) / len(self.responses_times)
        self.running = False
        # Resultados finales
        self.speech_proxy.say("Fin del juego. ¡Lo has hecho genial!:", False)
        self.agregar_resultados(self.nombre, self.rosco, self.aciertos, self.fallos, self.pasadas, self.fecha,
                                self.hora, (self.elapsed_time//60), (self.elapsed_time%60), self.media)
        self.guardar_resultados()
        # REINICIAR TODAS LAS VARIABLES
        self.reiniciar_variables()
        self.gestorsg_proxy.LanzarApp()

    def reiniciar_variables(self):
        self.datos = []
        self.letras = []
        self.preguntas = []
        self.respuestas = []
        self.aciertos = 0
        self.fallos = 0
        self.pasadas = 0
        self.letras_pasadas = []
        self.nombre = ""
        self.fecha = 0
        self.hora = 0
        self.start_time = None
        self.end_time = None
        self.elapsed_time = None
        self.rosco = ""
        self.bd = ""
        self.resp =""
        self.running = False
        self.boton = False
        self.check = ""
        self.letra_actual = ""
        self.pregunta_actual = ""
        self.start_question_time = 0
        self.end_question_time = 0
        self.response_time = 0
        self.responses_times = []
        self.media = 0

        self.df = pd.DataFrame(columns=["Nombre", "Rosco", "Aciertos", "Fallos", "Pasadas", "Fecha", "Hora", "Tiempo transcurrido (min)",
                                        "Tiempo transcurrido (seg)", "Tiempo de respuesta medio (seg)"])
        print("Variable self.df reiniciada para la próxima partida.")

    ########## INTRODUCCIÓN AL JUEGO ##########
    def introduccion (self):
        while self.running:
            if not self.running:
                break

            QApplication.processEvents()

            self.fecha = datetime.now().strftime("%d-%m-%Y")
            self.hora = datetime.now().strftime("%H:%M:%S")
            self.emotionalmotor_proxy.expressJoy()
            self.speech_proxy.say(f"Hola {self.nombre}, vamos a jugar a Pasapalabra.", False)
            print(f"Hola {self.nombre}, vamos a jugar a Pasapalabra.")
            self.speech_proxy.say( "Pasapalabra es un juego donde tienes que responder correctamente a preguntas cuyas respuestas empiezan o "
                                   "contienen cada letra del abecedario ", False)
            print("Pasapalabra es un juego donde tienes que responder correctamente a preguntas cuyas respuestas empiezan o "
                                   "contienen cada letra del abecedario ")
            self.speech_proxy.say("¿Quieres que te explique el juego?", False)
            print("¿Quieres que te explique el juego?")
            self.terminaHablar()
            # Introducir interfaz
            self.check = ""
            self.ui3.show()
            self.ui3.exec_()

            if self.check == "si":
                self.speech_proxy.say(
                    "Cada letra tiene una pregunta asociada. Por ejemplo: Con la A: Accesorio de joyería que se pone en los dedos. "
                    "La respuesta sería Anillos", False)
                print( "Cada letra tiene una pregunta asociada. Por ejemplo: Con la A: Accesorio de joyería que se pone en los dedos. "
                    "La respuesta sería Anillos")
                self.speech_proxy.say("Si no sabes la respuesta, puedes decir pasapalabra para saltar esa pregunta y volver a ella más tarde", False)
                print("Si no sabes la respuesta, puedes decir pasapalabra para saltar esa pregunta y volver a ella más tarde")
                self.speech_proxy.say("El juego termina cuando hayas contestado las preguntas asociadas a todas las letras", False)
                print("El juego termina cuando hayas contestado las preguntas asociadas a todas las letras")
            elif self.check == "no":
                self.speech_proxy.say("Mantén la calma, escucha bien las preguntas, y si dudas, ¡pasapalabra!", False)
                print("Mantén la calma, escucha bien las preguntas, y si dudas, ¡pasapalabra!")
                self.speech_proxy.say("¡Comencemos con el juego!", False)
                print("Comencemos con el juego")

            self.terminaHablar()
            self.ui4.show()
            self.ui4.exec_()
            self.juego()

    def terminaHablar(self):
        sleep(2.5)
        while self.speech_proxy.isBusy():
            pass

    ########## FUNCIÓN QUE AGREGA LOS RESULTADOS AL DATAFRAME ##########
    def agregar_resultados(self, nombre,dificultad, aciertos, fallos, pasadas, fecha, hora,
                           tiempo_transcurrido_min, tiempo_transcurrido_seg, tiempo_respuesta_medio):
        # Crea un diccionario con los datos nuevos
        nuevo_resultado = {
            "Nombre": nombre,
            "Rosco" : dificultad,
            "Aciertos": aciertos,
            "Fallos": fallos,
            "Pasadas": pasadas,
            "Fecha": fecha,
            "Hora": hora,
            "Tiempo transcurrido (min)": tiempo_transcurrido_min,
            "Tiempo transcurrido (seg)": tiempo_transcurrido_seg,
            "Tiempo de respuesta medio (seg)": tiempo_respuesta_medio
        }

        # Convierte el diccionario en un DataFrame de una fila
        nuevo_df = pd.DataFrame([nuevo_resultado])

        # Agrega la nueva fila al DataFrame existente
        self.df = pd.concat([self.df, nuevo_df], ignore_index=True)

    ########## FUNCIÓN QUE GUARDA LOS RESULTADOS DEL JUEGO ##########
    def guardar_resultados(self):
        archivo = "resultados_pasapalabra.json"

        # Inicializar un DataFrame vacío para los resultados existentes
        datos_existentes = pd.DataFrame()

        # Intentar leer el archivo existente si existe
        if os.path.exists(archivo):
            try:
                datos_existentes = pd.read_json(archivo, orient='records', lines=True)
            except ValueError:
                print(
                    "El archivo JSON existente tiene un formato inválido o está vacío. Sobrescribiendo el archivo.")

        # Asegurarse de que los DataFrames no estén vacíos antes de concatenar
        if not self.df.empty:
            if not datos_existentes.empty:
                # Concatenar si ambos DataFrames tienen contenido válido
                self.df = pd.concat([datos_existentes, self.df], ignore_index=True)
            else:
                # Si no hay datos existentes válidos, usar solo los nuevos
                print("No se encontraron datos previos válidos, creando un nuevo archivo.")
        else:
            print("El DataFrame de nuevos resultados está vacío. No se guardará nada.")
            return

        # Guardar el DataFrame combinado en formato JSON
        self.df.to_json(archivo, orient='records', lines=True)
        print(f"Resultados guardados correctamente en {archivo}")
        df_resultados = pd.read_json(archivo, orient='records', lines=True)
        print(df_resultados)

    ##########################################################################################

    def load_ui(self):
        # Carga la interfaz desde el archivo .ui
        loader = QtUiTools.QUiLoader()
        file = QtCore.QFile("../../igs/pasapalabra_respuesta.ui")
        file.open(QtCore.QFile.ReadOnly)
        ui = loader.load(file)
        file.close()

        # Asignar las imágenes a los QLabel después de cargar la UI
        # ui.label_2.setPixmap(QPixmap("../../igs/logos/logo_euro.png"))
        # ui.label_2.setScaledContents(True)  # Asegúrate de que la imagen se ajuste al QLabel

        # ui.label_3.setPixmap(QPixmap("../../igs/logos/robolab.png"))
        # ui.label_3.setScaledContents(True)  # Ajusta la imagen a los límites del QLabel

        # Conectar botones a funciones
        ui.correcta.clicked.connect(self.correcta_clicked)
        ui.incorrecta.clicked.connect(self.incorrecta_clicked)
        ui.pasapalabra.clicked.connect(self.pasapalabra_clicked)
        ui.repetir.clicked.connect(self.repetir_clicked)

        # ui.ayuda.hide()
        # ui.ayuda_button.clicked.connect(self.ayuda_clicked)

        # ui.back_button.clicked.connect(self.back_clicked)
        
        # Cerrar con la x
        if not hasattr(self, 'ui_numbers'):
            self.ui_numbers = {}
            
        self.ui_numbers[ui] = 1  
        ui.installEventFilter(self) 
        return ui

    def correcta_clicked(self):
        self.resp = "si"
        print("Respuesta: Sí")
        # self.ui.exec_()  # Cierra el diálogo cuando el botón es presionado
        self.sounds["click"].play()
        self.cerrar_ui(1)

    def incorrecta_clicked(self):
        self.resp = "no"
        print("Respuesta: No")
        # self.ui.exec_()   # Cierra el diálogo cuando el botón es presionado
        self.sounds["click"].play()
        self.cerrar_ui(1)

    def pasapalabra_clicked(self):
        self.resp = "pasapalabra"
        print("Respuesta: No")
        # self.ui.exec_()   # Cierra el diálogo cuando el botón es presionado
        self.sounds["click"].play()
        self.cerrar_ui(1)

    def repetir_clicked (self):
        print("Respuesta: Repetir")
        if self.speech_proxy.isBusy():
            pass
        else:
            self.speech_proxy.say(f"{self.letra_actual}, {self.pregunta_actual}", False)


    ##########################################################################################

    def therapist_ui (self):
        # self.start_listener_thread()
        self.running = True

        #Cargar interfaz
        loader = QtUiTools.QUiLoader()
        file = QtCore.QFile("../../igs/pasapalabra_menu.ui")
        file.open(QtCore.QFile.ReadOnly)
        ui = loader.load(file)
        file.close()

        # Asignar las imágenes a los QLabel después de cargar la UI
        ui.label.setPixmap(QPixmap("../../igs/logos/logo_euro.png"))
        ui.label.setScaledContents(True)  # Asegúrate de que la imagen se ajuste al QLabel

        ui.label_2.setPixmap(QPixmap("../../igs/logos/robolab.png"))
        ui.label_2.setScaledContents(True)  # Ajusta la imagen a los límites del QLabel

        self.configure_combobox(ui, "roscos")
        ui.confirmar_button.clicked.connect(self.therapist)

        ui.ayuda.hide()
        ui.ayuda_button.clicked.connect(self.ayuda_clicked2)

        ui.back_button.clicked.connect(self.back_clicked2)
        
        # Cerrar con la x
        if not hasattr(self, 'ui_numbers'):
            self.ui_numbers = {}
            
        self.ui_numbers[ui] = 2  
        ui.installEventFilter(self) 
        return ui

    def therapist(self):
        # Obtiene los valores ingresados en los campos
        self.nombre = self.ui2.usuario.toPlainText()
        self.rosco = self.ui2.comboBox.currentText()

        # Validaciones simples
        if not self.nombre:
            print("Por favor ingresa un nombre de usuario.")
            return
        if not self.rosco or self.rosco == "Seleccionar rosco...":
            print("Por favor selecciona un rosco.")
            return

        # Muestra los valores en consola
        print(f"Usuario: {self.nombre}")
        print(f"Rosco: {self.rosco}")

        print("Valores confirmados. Juego listo para comenzar.")
        self.boton = True
        self.running = True
        self.sounds["click"].play()
        self.cerrar_ui(2)
        self.ui2.usuario.clear()
        self.introduccion()

    def configure_combobox(self, ui, folder_path):
        # Acceder al QComboBox por su nombre de objeto
        combobox = ui.findChild(QtWidgets.QComboBox, "comboBox")
        if combobox:
            combobox.addItem("Seleccionar rosco...")
            # Obtener la lista de archivos en la carpeta
            try:
                archivos = [
                    archivo for archivo in os.listdir(folder_path)
                    if os.path.isfile(os.path.join(folder_path, archivo))
                ]
                # Agregar los nombres de los archivos al QComboBox sin la extensión .json
                for archivo in archivos:
                    nombre_sin_extension, ext = os.path.splitext(archivo)
                    # Agregar solo el nombre sin la extensión
                    combobox.addItem(nombre_sin_extension)
            except FileNotFoundError:
                print(f"La carpeta {folder_path} no existe.")
            except Exception as e:
                print(f"Error al listar archivos: {e}")
        else:
            print("No se encontró el QComboBox")

    def ayuda_clicked(self):
        print("BOTON AYUDA PULSADO")
        if self.ui.ayuda.isVisible():  # Verifica si está visible
            self.ui.ayuda.hide()  # Si está visible, ocultarlo
        else:
            self.ui.ayuda.show()

    def ayuda_clicked2(self):
        print("BOTON AYUDA PULSADO")
        if self.ui2.ayuda.isVisible():  # Verifica si está visible
            self.ui2.ayuda.hide()  # Si está visible, ocultarlo
        else:
            self.ui2.ayuda.show()

    def back_clicked(self):
        self.cerrar_ui(1)
        self.gestorsg_proxy.LanzarApp()

    def back_clicked2(self):
        self.cerrar_ui(2)
        self.gestorsg_proxy.LanzarApp()

    ##########################################################################################

    def load_check(self):
        # Carga la interfaz desde el archivo .ui
        loader = QtUiTools.QUiLoader()
        file = QtCore.QFile("../../igs/botonUI.ui")
        file.open(QtCore.QFile.ReadOnly)
        ui = loader.load(file)
        file.close()

        # Conectar botones a funciones
        ui.si.clicked.connect(self.si_clicked)
        ui.no.clicked.connect(self.no_clicked)
        
        # Cerrar con la x
        if not hasattr(self, 'ui_numbers'):
            self.ui_numbers = {}
            
        self.ui_numbers[ui] = 3
        ui.installEventFilter(self) 
        return ui

    def si_clicked(self):
        self.check = "si"
        print("Respuesta: Sí")
        self.ui3.accept()  # Cierra el diálogo cuando el botón es presionado
        self.sounds["click"].play()

    def no_clicked(self):
        self.check = "no"
        print("Respuesta: No")
        self.ui3.accept()  # Cierra el diálogo cuando el botón es presionado
        self.sounds["click"].play()

    ##########################################################################################

    def comenzar_checked(self):
        # Carga la interfaz desde el archivo .ui
        loader = QtUiTools.QUiLoader()
        file = QtCore.QFile("../../igs/comenzarUI.ui")
        file.open(QtCore.QFile.ReadOnly)
        ui = loader.load(file)
        file.close()

        # Conectar botones a funciones
        ui.comenzar.clicked.connect(self.comenzar)
        
        # Cerrar con la x
        if not hasattr(self, 'ui_numbers'):
            self.ui_numbers = {}
            
        self.ui_numbers[ui] = 4  
        ui.installEventFilter(self) 
        return ui

    def comenzar (self):
        self.running = True
        print("¡El juego ha comenzado!")
        self.ui4.accept()  # Cierra el diálogo cuando el botón es presionado
        self.sounds["click"].play()

    ##########################################################################################
    
    def eventFilter(self, obj, event):
        """ Captura eventos de la UI """
        # Obtener el número de UI asociado al objeto
        ui_number = self.ui_numbers.get(obj, None)

        if ui_number is not None and event.type() == QtCore.QEvent.Close:
            target_ui = self.ui if ui_number == 1 else getattr(self, f'ui{ui_number}', None)
            
            if obj == target_ui:
                respuesta = QMessageBox.question(
                    target_ui, "Cerrar", f"¿Estás seguro de que quieres salir del juego?",
                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No
                )
                if respuesta == QMessageBox.Yes:
                    print(f"Ventana {ui_number} cerrada por el usuario.")
                    self.reiniciar_variables()
                    self.gestorsg_proxy.LanzarApp()
                    return False  # Permitir el cierre
                else:
                    print(f"Cierre de la ventana {ui_number} cancelado.")
                    event.ignore()  # Bloquear el cierre
                    return True  # **DETENER la propagación del evento para que no se cierre**
        return False  # Propaga otros eventos normalmente
    
    def cerrar_ui(self, numero):
        ui_nombre = "ui" if numero == 1 else f"ui{numero}"
        ui_obj = getattr(self, ui_nombre, None)
        
        if ui_obj:
            ui_obj.removeEventFilter(self)  # Desactiva el event filter
            ui_obj.close()  # Cierra la ventana
            ui_obj.installEventFilter(self)  # Reactiva el event filter
        else:
            print(f"Error: {ui_nombre} no existe en la instancia.")

    ####################################################################################################################################

    @QtCore.Slot()
    def compute(self):

        return True

    def startup_check(self):
        print(f"Testing RoboCompCameraSimple.TImage from ifaces.RoboCompCameraSimple")
        test = ifaces.RoboCompCameraSimple.TImage()
        print(f"Testing RoboCompLEDArray.Pixel from ifaces.RoboCompLEDArray")
        test = ifaces.RoboCompLEDArray.Pixel()
        QTimer.singleShot(200, QApplication.instance().quit)



    # =============== Methods for Component Implements ==================
    # ===================================================================

    #
    # IMPLEMENTATION of StartGame method from Pasapalabra interface
    #
    def Pasapalabra_StartGame(self):
        self.boton = False
        while not self.boton:
            self.boton = True
            self.centrar_ventana(self.ui2)
            self.ui2.show()
            QApplication.processEvents()
            sleep(1)
        print("Juego terminado o ventana cerrada")

    def centrar_ventana(self, ventana):
        # Obtener la geometría de la pantalla
        pantalla = QApplication.primaryScreen().availableGeometry()

        # Obtener el tamaño de la ventana
        tamano_ventana = ventana.size()

        # Calcular las coordenadas para centrar la ventana
        x = (pantalla.width() - tamano_ventana.width()) // 2
        y = (pantalla.height() - tamano_ventana.height()) // 2

        # Mover la ventana a la posición calculada
        ventana.move(x, y)
    ######################
    # From the RoboCompCameraSimple you can call this methods:
    # self.camerasimple_proxy.getImage(...)

    ######################
    # From the RoboCompCameraSimple you can use this types:
    # RoboCompCameraSimple.TImage

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
    # From the RoboCompGestorSG you can call this methods:
    # self.gestorsg_proxy.LanzarApp(...)

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



    # =============== DSR SLOTS  ================
    # =============================================

    def update_node_att(self, id: int, attribute_names: [str]):
        # console.print(f"UPDATE NODE ATT: {id} {attribute_names}", style='green')
        pass

    def update_node(self, id: int, type: str):
        console.print(f"UPDATE NODE: {id} {type}", style='green')

    def delete_node(self, id: int):
        console.print(f"DELETE NODE:: {id} ", style='green')

    def update_edge(self, fr: int, to: int, type: str):

        console.print(f"UPDATE EDGE: {fr} to {type}", type, style='green')

    def update_edge_att(self, fr: int, to: int, type: str, attribute_names: [str]):
        console.print(f"UPDATE EDGE ATT: {fr} to {type} {attribute_names}", style='green')

    def delete_edge(self, fr: int, to: int, type: str):
        console.print(f"DELETE EDGE: {fr} to {type} {type}", style='green')
