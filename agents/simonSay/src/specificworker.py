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
from tensorflow.python.ops.gen_experimental_dataset_ops import experimental_latency_stats_dataset_eager_fallback

from genericworker import *
import interfaces as ifaces
from time import sleep
from pynput import keyboard
import random
from PySide6 import QtUiTools
from PySide6.QtWidgets import QPushButton, QVBoxLayout, QWidget
from PySide6.QtCore import Qt
import pygame
import time
import pandas as pd
from datetime import datetime
import csv
import math
import json
import csv
from pathlib import Path

CSV_PATH = Path(__file__).resolve().parent / "../../users_info.csv"


sys.path.append('/opt/robocomp/lib')
console = Console(highlight=False)

from pydsr import *

# If RoboComp was compiled with Python bindings you can use InnerModel in Python
# import librobocomp_qmat
# import librobocomp_osgviewer
# import librobocomp_innermodel


class SpecificWorker(GenericWorker):
    update_ui_signal = Signal()
    def __init__(self, proxy_map, startup_check=False):
        super(SpecificWorker, self).__init__(proxy_map)
        self.Period = 2000

        # YOU MUST SET AN UNIQUE ID FOR THIS AGENT IN YOUR DEPLOYMENT. "_CHANGE_THIS_ID_" for a valid unique integer
        self.agent_id = 901
        self.g = DSRGraph(0, "pythonAgent", self.agent_id)

        try:
            signals.connect(self.g, signals.UPDATE_NODE_ATTR, self.update_node_att)
            # signals.connect(self.g, signals.UPDATE_NODE, self.update_node)
            # signals.connect(self.g, signals.DELETE_NODE, self.delete_node)
            # signals.connect(self.g, signals.UPDATE_EDGE, self.update_edge)
            # signals.connect(self.g, signals.UPDATE_EDGE_ATTR, self.update_edge_att)
            # signals.connect(self.g, signals.DELETE_EDGE, self.delete_edge)
            # console.print("signals connected")
        except RuntimeError as e:
            print(e)

        if startup_check:
            self.startup_check()
        else:
            self.timer.timeout.connect(self.compute)
            self.timer.start(self.Period)

        pygame.init()

        ########## INTRODUCCIÓN DE SONIDOS  ##########
        self.sounds = {
            "rojo": pygame.mixer.Sound('src/rojo.wav'),
            "verde": pygame.mixer.Sound('src/verde.wav'),
            "azul": pygame.mixer.Sound('src/azul.wav'),
            "amarillo": pygame.mixer.Sound('src/amarillo.wav'),
            "win": pygame.mixer.Sound('src/win.wav'),
            "click": pygame.mixer.Sound('src/click.wav'),
            "game_over": pygame.mixer.Sound('src/game_over.wav'),
        }

        self.NUM_LEDS = 54
        self.nombre = ""
        self.dificultad = ""
        self.intentos = 0
        self.running = False
        self.respuesta = []
        self.rondas = ""

        self.ayuda = False
        self.archivo_csv = "../../users_info.csv"

        self.ui = self.load_ui()
        self.ui2 = self.therapist_ui()
        self.ui3 = self.load_check()
        self.ui4 = self.comenzar_checked()

        self.boton = False
        self.reiniciar = False
        self.gameOver = False
        self.start_time = None
        self.end_time = None
        self.elapsed_time = None

        self.rondas_complet = 0
        self.fecha = 0
        self.hora = 0
        self.fallos = 0

        self.v1 = 2
        self.v2 = 1

        self.start_question_time = None
        self.end_question_time = 0
        self.response_time = 0
        self.responses_times = []
        self.media = 0
        self.puntuacion = 1000

        # Atributos para el seguimiento en tiempo real:
        self.racha = 0           # Racha actual de aciertos.
        self.fallo_detectado = False  # Bandera para indicar si hubo fallo reciente.

        ########## DEFINICIÓN DEL DATAFRAME DONDE SE ALMACENAN LOS DATOS ##########
        self.df = pd.DataFrame(columns=[
            "Nombre", "Intentos", "Rondas", "Dificultad", "Fecha", "Hora",
            "Rondas completadas", "Fallos", "Tiempo transcurrido (min)", "Tiempo transcurrido (seg)", "Tiempo medio respuesta (seg):", "Puntuación"
        ])

        ########## CARGAR BATERÍA DE RESPUESTAS ##########
        with open("src/bateria_respuestas.json", "r", encoding="utf-8") as file:
            baterias = json.load(file)

        self.bateria_responder = baterias["responder"]
        self.bateria_aciertos = baterias["aciertos"]
        self.bateria_fallos = baterias["fallos"]
        self.bateria_rondas = baterias["rondas"]
        self.baterias_racha = baterias["racha"]
        self.bateria_fin_juego = baterias["fin_juego"]

        self.bateria_rondas_actual = self.bateria_rondas

        # Diccionario con los valores de v_off y v_on para cada nivel de dificultad.
        self.v_values = {
            "Muy fácil": {"v_off": 1, "v_on": 4},
            "Fácil": {"v_off": 1, "v_on": 3},
            "Intermedio bajo": {"v_off": 1, "v_on": 2},
            "Intermedio": {"v_off": 0.5, "v_on": 1},
            "Intermedio alto": {"v_off": 0.25, "v_on": 0.5},
            "Difícil": {"v_off": 0.15, "v_on": 0.25},
            "Extremo": {"v_off": 0.05, "v_on": 0.1}
        }

        # Lista ordenada de niveles para facilitar la subida o bajada de dificultad.
        self.niveles = [
            "Muy fácil",
            "Fácil",
            "Intermedio bajo",
            "Intermedio",
            "Intermedio alto",
            "Difícil",
            "Extremo"
        ]

        self.update_ui_signal.connect(self.on_update_ui)

    ########## FUNCIÓN PARA AGREGAR LOS DATOS RECOGIDOS AL DATAFRAME ##########
    def agregar_resultados(self, nombre, intentos, rondas, dificultad, fecha, hora, rondas_completadas, fallos, tiempo_transcurrido_min, tiempo_transcurrido_seg, tiempo_medio_respuesta, puntuacion):
        # Crea un diccionario con los datos nuevos
        nuevo_resultado = {
            "Nombre": nombre,
            "Intentos": intentos,
            "Rondas": rondas,
            "Dificultad": dificultad,
            "Fecha": fecha,
            "Hora": hora,
            "Rondas completadas": rondas_completadas,
            "Fallos": fallos,
            "Tiempo transcurrido (min)": tiempo_transcurrido_min,
            "Tiempo transcurrido (seg)": tiempo_transcurrido_seg,  # Corregido aquí
            "Tiempo medio respuesta (seg):": tiempo_medio_respuesta,  # Corregido aquí
            "Puntuación": puntuacion
        }

        # Convierte el diccionario en un DataFrame de una fila
        nuevo_df = pd.DataFrame([nuevo_resultado])

        # Agrega la nueva fila al DataFrame existente
        self.df = pd.concat([self.df, nuevo_df], ignore_index=True)


    def __del__(self):
        """Destructor"""

    def setParams(self, params):
        # try:
        #	self.innermodel = InnerModel(params["InnerModelPath"])
        # except:
        #	traceback.print_exc()
        #	print("Error reading config params")
        return True

    ########## FUNCIÓN PARA ALEATORIZAR RESPUESTAS ##########

    def elegir_respuesta(self, bateria, **kwargs):
        if "ronda" in kwargs:
            # Si el kwargs contiene 'ronda', formatea las respuestas de las rondas
            bateria = [respuesta.format(ronda=kwargs["ronda"]) if "ronda" in respuesta else respuesta for respuesta in
                       bateria]
        return random.choice(bateria)

    ########## FUNCIONES PARA EL PROCESO DEL JUEGO  ##########
    def procesoJuego(self):
        if self.dificultad == "facil":
            self.v1 = 3
            self.v2 = 1.5
        elif self.dificultad == "medio":
            self.v1 = 1
            self.v2 = 0.5
        elif self.dificultad == "dificil":
            self.v1 = 0.5
            self.v2 = 0.25
        else:
            pass

        self.color_aleatorio = []
        i = 0
        sleep(0.5)
        rondas = self.rondas

        while i < int(rondas) and self.running:
            self.speech_proxy.say(self.elegir_respuesta(self.bateria_rondas_actual, ronda= i+1), False)
            print(f"Ronda número {i + 1}")
            self.rondas_complet = i+1
            self.RT_adjust()
            self.terminaHablar()
            self.random_color()
            print(self.color_aleatorio)
            for color in self.color_aleatorio:
                self.encender_LEDS(color)
                sleep(self.v1)
                self.encender_LEDS("negro")
                sleep(self.v2)

            self.start_question_time = None
            self.get_respuesta()
            print("Tu respuesta ha sido:", self.respuesta)
            if not self.running:
                break
            i += 1

        if i == rondas:
            self.finJuego()

    def finJuego(self):
        self.end_time = time.time()
        self.elapsed_time = self.end_time - self.start_time  # Tiempo en segundos
        # Convertir el tiempo a minutos y segundos
        minutes = int(self.elapsed_time // 60)
        seconds = int(self.elapsed_time % 60)
        self.speech_proxy.say(self.elegir_respuesta(self.bateria_fin_juego), False)
        print(f"Juego terminado. Tiempo transcurrido: {minutes} minutos y {seconds} segundos.")
        self.terminaHablar()
        pygame.mixer.stop()
        self.sounds["win"].play()
        self.set_all_LEDS_colors(0, 255, 0, 0)
        self.emotionalmotor_proxy.expressSurprise()
        sleep(0.5)
        self.encender_LEDS("negro")
        sleep(0.5)
        self.boton = False
        self.media = sum(self.responses_times) / len(self.responses_times)
        self.calc_new_score("gana")
        self.agregar_resultados(self.nombre, self.intentos, self.rondas, self.dificultad, self.fecha, self.hora, self.rondas_complet, self.fallos, minutes, seconds, self.media, self.puntuacion)
        time.sleep(0.5)
        self.send_to_csv_manager()
        self.guardar_resultados()
        self.gestorsg_proxy.LanzarApp()
        return

    ########## FUNCIÓN QUE GENERA LA SECUENCIA DE COLORES  ##########
    def random_color(self):
        color = random.choice(["rojo", "azul", "verde", "amarillo"])
        # Comprobar si el último color es el mismo que el nuevo
        while self.color_aleatorio and self.color_aleatorio[-1] == color:
            color = random.choice(["rojo", "azul", "verde", "amarillo"])
        self.color_aleatorio.append(color)

    ########## FUNCIÓN PARA ENCENDER LAS LUCES LEDS ##########
    def encender_LEDS(self,color):
        if color == "rojo" and self.gameOver:
            self.sounds["game_over"].play()
        elif color in self.sounds:
            pygame.mixer.stop()
            self.sounds[color].play()
        if color== "negro":
            self.set_all_LEDS_colors(0, 0, 0, 0)
        elif color == "rojo":
            self.set_all_LEDS_colors(255, 0, 0, 0)
        elif color== "verde":
            self.set_all_LEDS_colors(0, 255, 0, 0)
        elif color == "azul":
            self.set_all_LEDS_colors(0, 0, 255, 0)
        elif color == "amarillo":
            self.set_all_LEDS_colors(255, 255, 0, 0)
        else:
            print("Error, apagando LEDS")
            self.set_all_LEDS_colors(0, 0, 0, 0)

    def set_all_LEDS_colors(self, red=0, green=0, blue=0, white=0):
        pixel_array = {i: ifaces.RoboCompLEDArray.Pixel(red=red, green=green, blue=blue, white=white) for i in
                       range(self.NUM_LEDS)}
        self.ledarray_proxy.setLEDArray(pixel_array)

    ########## INTRODUCCIÓN AL JUEGO  ##########
    def introduccion (self):

        QApplication.processEvents()

        # Introducción al juego
        self.emotionalmotor_proxy.expressJoy()
        self.speech_proxy.say(f"Hola {self.nombre}, vamos a jugar a Simón Dice.", False)
        print (f"Hola {self.nombre}, vamos a jugar a Simón Dice.")

        self.speech_proxy.say("Simón Dice es un juego de memoria en el que debes repetir la secuencia de colores que se ilumina. ", False)
        print("Simón Dice es un juego de memoria en el que debes repetir la secuencia de colores que se ilumina. ")
        self.speech_proxy.say ("¿Quieres que te explique el juego?", False)
        print("¿Quieres que te explique el juego?")
        self.terminaHablar()

        self.check = ""
        self.centrar_ventana(self.ui3)
        self.ui3.show()
        QApplication.processEvents()
        self.ui3.exec_()

        # Explicación del Juego
        if self.check == "si":
            self.speech_proxy.say("A medida que avances, la secuencia se volverá más larga, poniendo a prueba tu memoria y concentración. "
                                  "Cómo jugar: Se mostrará un color en mis luces, por ejemplo rojo. ", False)
            print ("A medida que avances, la secuencia se volverá más larga, poniendo a prueba tu memoria y concentración. "
                                  "Cómo jugar: Se mostrará un color en mis luces, por ejemplo rojo. ")
            self.terminaHablar()
            self.set_all_LEDS_colors(255, 0, 0, 0)
            sleep(1)
            self.set_all_LEDS_colors(0,0,0,0)
            self.speech_proxy.say("Deberás introducir ese mismo color. "
                                  "Al acertar, añadiré otro color a la secuencia, por ejemplo rojo + azul). ", False)
            print("Deberás introducir ese mismo color. "
                                  "Al acertar, añadiré otro color a la secuencia, por ejemplo rojo + azul). ")
            self.terminaHablar()
            self.set_all_LEDS_colors(255, 0, 0, 0)
            sleep(1)
            self.set_all_LEDS_colors(0, 0, 0, 0)
            sleep(1)
            self.set_all_LEDS_colors(0, 0, 255, 0)
            sleep(1)
            self.set_all_LEDS_colors(0, 0, 0, 0)
            self.speech_proxy.say("Ahora debes repetir ambos en el orden correcto. "
                                  "Con cada turno, la secuencia crece y debes recordar cada color en el orden correcto.", False)
            print("Ahora debes repetir ambos en el orden correcto. "
                                  "Con cada turno, la secuencia crece y debes recordar cada color en el orden correcto.")

        # Prueba de juego
        self.speech_proxy.say("¿Quieres hacer una prueba?", False)
        print("¿Quieres hacer una prueba?")
        self.terminaHablar()

        self.check = ""
        self.centrar_ventana(self.ui3)
        self.ui3.show()
        self.ui3.exec_()

        if self.check == "si":
            self.prueba()
        if self.check == "no":
            if int(self.intentos) == 1:
                self.speech_proxy.say("Vamos a ver cuánto tiempo eres capaz de seguir la secuencia sin equivocarte", False)
                print("Vamos a ver cuánto tiempo eres capaz de seguir la secuencia sin equivocarte")
            elif int(self.intentos) > 1:
                self.speech_proxy.say(f"""Tienes un número limitado de intentos. Si te equivocas en algún color {self.intentos}
                                        veces antes de completar la secuencia, el juego terminará.""", False)
                print(f"""Tienes un número limitado de intentos. Si te equivocas en algún color {self.intentos}
                                        veces antes de completar la secuencia, el juego terminará.""")
            self.speech_proxy.say("¡Comencemos con el juego!", False)
            print("¡Comencemos con el juego!")

        self.terminaHablar()

        self.centrar_ventana(self.ui4)
        self.ui4.show()
        self.ui4.exec_()
        self.start_time =time.time()
        self.fecha = datetime.now().strftime("%d-%m-%Y")
        self.hora = datetime.now().strftime("%H:%M:%S")

    ########## FUNCIÓN PARA OBTENER LA RESPUESTA  ##########
    def get_respuesta(self):
        self.respuesta = []
        self.intent = 0
        
        if self.start_question_time is None:
            self.start_question_time = time.time()

        print("Introduce la secuencia de colores uno a uno")

        # Inicio de la ronda, aparecen los 4 botones.
        while len(self.respuesta) < len(self.color_aleatorio) and self.running is True:
            # Mostrar la interfaz gráfica con botones
            self.centrar_ventana(self.ui)
            self.ui.show()
            QApplication.processEvents()

            self.emotionalmotor_proxy.expressJoy()
            # Verifica si la respuesta es correcta hasta el momento, cada pulsado de botón.
            for idx in range(len(self.respuesta)):
                if self.respuesta[idx] != self.color_aleatorio[idx]:
                    self.intent += 1
                    self.restantes = int(self.intentos) - int(self.intent)
                    if self.restantes > 1:
                        self.speech_proxy.say(
                            f"Respuesta incorrecta. {self.elegir_respuesta(self.bateria_fallos)} .Te quedan {self.restantes} intentos.", False)
                    elif self.restantes == 1:
                        self.speech_proxy.say(
                            f"Respuesta incorrecta. {self.elegir_respuesta(self.bateria_fallos)}.Este es tu último intento.", False)
                    else:
                        self.speech_proxy.say(
                            f"Respuesta incorrecta, no te quedan más intentos.", False)

                    self.cerrar_ui(1)
                    self.terminaHablar()
                    self.fallos = self.fallos + 1
                    if self.restantes <= 0:
                        self.end_time = time.time()
                        self.elapsed_time = self.end_time - self.start_time  # Tiempo en segundos
                        self.media = sum(self.responses_times) / len(self.responses_times)
                        # Convertir el tiempo a minutos y segundos
                        minutes = int(self.elapsed_time // 60)
                        seconds = int(self.elapsed_time % 60)
                        rondas = int(self.rondas_complet) - 1
                        print("Game Over")
                        self.speech_proxy.say(self.elegir_respuesta(self.bateria_fin_juego), False)
                        print(f"Juego terminado. Tiempo transcurrido: {minutes} minutos y {seconds} segundos.")
                        self.terminaHablar()
                        self.fantasia_color()
                        self.running = False
                        self.boton = False
                        self.calc_new_score("pierde")
                        self.agregar_resultados(self.nombre, self.intentos, self.rondas, self.dificultad, self.fecha, self.hora,
                                                rondas, self.fallos, minutes, seconds ,self.media, self.puntuacion)
                        time.sleep(0.5)
                        self.send_to_csv_manager()
                        self.guardar_resultados()
                        self.gestorsg_proxy.LanzarApp()
                        return

                    self.fallo_detectado = True
                    print("Fallo: racha reiniciada a 0.")
                    self.RT_adjust()
                    print("Mostrando la secuencia nuevamente...")
                    self.speech_proxy.say("Atención, repito la secuencia.", False)
                    self.respuesta = []  # Reinicia la respuesta
                    self.terminaHablar()
                    print(self.color_aleatorio)
                    for color in self.color_aleatorio:
                        self.encender_LEDS(color)
                        sleep(self.v1)
                        self.encender_LEDS("negro")
                        sleep(self.v2)
                    break
        
        if self.running is True:
            self.cerrar_ui(1) # Cierra la ventana cuando el juego termine
            self.racha += 1
            self.fallo_detectado = False
            print(f"Acierto: racha incrementada a {self.racha}")
            self.speech_proxy.say(self.elegir_respuesta(self.bateria_aciertos), False)
            self.terminaHablar()
            print("Tu respuesta ha sido:", self.respuesta)


    def fantasia_color(self):
        i = 0
        self.emotionalmotor_proxy.expressJoy()
        self.gameOver = True
        while i < 3:
            self.encender_LEDS("rojo")
            sleep(0.5)
            self.encender_LEDS("negro")
            sleep(0.5)
            i += 1
        self.gameOver = False

    def prueba (self):
        self.speech_proxy.say("¡Genial! Comencemos con la prueba. Vamos a hacer 2 rondas",False)

        print("¡Genial! Comencemos con la prueba. Vamos a hacer 2 rondas")

        self.terminaHablar()

        self.color_aleatorio = []
        self.running = True
        i = 0
        while i <= 1 and self.running:
            self.speech_proxy.say(f"Ronda número {i + 1}", False)
            print(f"Ronda número {i + 1}")
            self.terminaHablar()
            self.random_color()
            print(self.color_aleatorio)

            for color in self.color_aleatorio:
                self.encender_LEDS(color)
                sleep(1)
                self.encender_LEDS("negro")
                sleep(0.5)

            self.get_respuesta()
            print("Tu respuesta ha sido:", self.respuesta)
            i += 1

        if i == 2:
            self.running = False
            self.speech_proxy.say ("¡Lo has hecho muy bien!",False)
            print("¡Lo has hecho muy bien!")

    def terminaHablar(self):
        sleep(2.5)
        while self.speech_proxy.isBusy():
            pass

                        ########## INTERFACES GRÁFICAS ##########
    ####################################################################################################################################

    def load_ui (self):
        #Carga la interfaz desde el archivo .ui
        loader = QtUiTools.QUiLoader()
        file = QtCore.QFile("../../igs/simon_botones.ui")
        file.open(QtCore.QFile.ReadOnly)
        ui = loader.load(file)
        file.close()

        # Conectar botones a funciones
        ui.rojo.clicked.connect(self.rojo_clicked)
        ui.azul.clicked.connect(self.azul_clicked)
        ui.verde.clicked.connect(self.verde_clicked)
        ui.amarillo.clicked.connect(self.amarillo_clicked)
        
        # Cerrar con la x
        if not hasattr(self, 'ui_numbers'):
            self.ui_numbers = {}
            
        self.ui_numbers[ui] = 1  
        ui.installEventFilter(self) 

        return ui

    def rojo_clicked(self):
        self.respuesta.append("rojo")
        self.sounds["rojo"].play()
        self.register_time_until_pressed()
        print("Respuesta: Rojo")

    def azul_clicked(self):
        self.respuesta.append("azul")
        self.sounds["azul"].play()
        self.register_time_until_pressed()
        print("Respuesta: Azul")

    def verde_clicked(self):
        self.respuesta.append("verde")
        self.sounds["verde"].play()
        self.register_time_until_pressed()
        print("Respuesta: Verde")

    def amarillo_clicked(self):
        self.respuesta.append("amarillo")
        self.sounds["amarillo"].play()
        self.register_time_until_pressed()
        print("Respuesta: Amarillo")
    
    def register_time_until_pressed(self):
        if self.end_question_time is None:
            self.end_question_time = time.time()
        
        self.response_time = self.end_question_time - self.start_question_time
        if self.response_time < 0.00001:
            print("Error, valor no almacenado")
        else:
            self.responses_times.append(self.response_time)

        self.start_question_time = None
        self.end_question_time = None

        if self.start_question_time is None:
            self.start_question_time = time.time()
        
        print("------------------------------")
        print(f"Tiempo de respuesta: {self.response_time}")
        print("------------------------------")

    ####################################################################################################################################

    def therapist_ui (self):
        #Cargar interfaz
        loader = QtUiTools.QUiLoader()
        file = QtCore.QFile("../../igs/simon_menu.ui")
        file.open(QtCore.QFile.ReadOnly)
        ui = loader.load(file)
        file.close()
        ui.confirmar_button.clicked.connect(self.therapist)
        ui.confirmar_button_2.clicked.connect(self.automatic)

        self.cargarUsuarios(ui, self.archivo_csv)
        # Cerrar con la x
        if not hasattr(self, 'ui_numbers'):
            self.ui_numbers = {}
            
        self.ui_numbers[ui] = 2  
        ui.installEventFilter(self) 
        return ui

    def cargarUsuarios(self, ui, archivo_csv):
        opciones = ["Seleccionar usuario..."]
        try:
            with open(archivo_csv, newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile, delimiter=';')
                for row in reader:
                    nombre = row['nombre'].strip()
                    residencia = row['residencia'].strip() if row['residencia'].strip() else "Desconocida"
                    opciones.append(f"{nombre} - {residencia}")
        except Exception as e:
            print(f"Error al leer el CSV: {e}")
        ui.comboBox_user.addItems(opciones)


    def therapist(self):
        # Obtiene los valores ingresados en los campos
        self.nombre = self.ui2.usuario.toPlainText()
        self.primer_partida()


    def primer_partida(self):
        self.intentos = 2
        self.rondas = 4
        self.dificultad = "Fácil"
        self.first_time()
        # Validaciones simples
        if not self.nombre:
            print("Por favor ingresa un nombre de usuario.")
            return

        # Muestra los valores en consola
        self.set_all_LEDS_colors(0, 0, 0, 0)
        print(f"Usuario: {self.nombre}")
        print(f"Intentos: {self.intentos}")
        print(f"Rondas: {self.rondas}")
        print(f"Dificultad: {self.dificultad}")
        print("Valores confirmados. Juego listo para comenzar.")
        self.boton = True
        self.fallos = 0 # Reinicia contador al empezar juego
        self.sounds["click"].play()
        self.cerrar_ui(2)
        self.ui2.usuario.clear()
        self.introduccion()
        self.procesoJuego()


    def automatic(self):
        if self.first_game():
            self.select_user()
            self.primer_partida()              # ← cámbiala por la tuya
            return

        self.dificultad = "auto"
        self.leerDatos()
        self.intentos = 2

        # Muestra los valores en consola
        self.set_all_LEDS_colors(0, 0, 0, 0)
        print(f"Usuario: {self.nombre}")
        print(f"Intentos: {self.intentos}")
        print(f"Rondas: {self.rondas}")
        print(f"Dificultad: {self.dificultad}")
        print("Valores confirmados. Juego listo para comenzar.")
        self.boton = True
        self.fallos = 0  # Reinicia contador al empezar juego
        self.sounds["click"].play()
        self.cerrar_ui(2)
        self.ui2.usuario.clear()

        self.emotionalmotor_proxy.expressJoy()
        self.speech_proxy.say(f"Hola {self.nombre}, vamos a jugar a Simón Dice. Recuerda repetir las luces en el orden en el que aparezcan. Jugaremos {self.rondas} rondas, con 2 intentos por ronda.¡Comencemos con el juego!", False)
        self.terminaHablar()

        self.centrar_ventana(self.ui4)
        self.ui4.show()
        self.ui4.exec_()
        self.start_time =time.time()
        self.fecha = datetime.now().strftime("%d-%m-%Y")
        self.hora = datetime.now().strftime("%H:%M:%S")

        self.procesoJuego()

    def first_game(self) -> bool:
        """
        Devuelve True si el usuario no tiene todavía un número de partidas
        registrado en users_info.csv (columna 'num_partidas' vacía o None).
        En cualquier otro caso devuelve False.
        """
        try:
            with CSV_PATH.open(newline="", encoding="utf-8") as f:
                lector = csv.DictReader(f)
                for fila in lector:
                    if fila.get("nombre") == self.nombre:
                        num = fila.get("num_partidas")
                        return (num is None) or (str(num).strip() == "")
        except FileNotFoundError:
            # Si el CSV no existe consideramos que es el primer juego
            print(f"Advertencia: no se encontró el archivo {CSV_PATH}")
            return True

        # Si el usuario no está en el CSV, lo tratamos como primer juego
        return True

    ####################################################################################################################################
    
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
        
    ####################################################################################################################################

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

    ####################################################################################################################################
    
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
                    self.set_all_LEDS_colors(0, 0, 0, 0)
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

    def guardar_resultados(self):
        archivo = "resultados_juego.json"
        # Inicializar un DataFrame vacío para los datos existentes
        datos_existentes = pd.DataFrame()
        # Intentar leer el archivo existente si existe
        if os.path.exists(archivo):
            try:
                datos_existentes = pd.read_json(archivo, orient='records', lines=True)
            except ValueError:
                print("El archivo JSON existente tiene un formato inválido o está vacío. Sobrescribiendo el archivo.")

        # Verificar que el DataFrame actual no esté vacío
        if self.df.empty:
            print("El DataFrame de nuevos resultados está vacío. No se guardará nada.")
            return

        # Concatenar los datos existentes con los nuevos (si existen)
        if not datos_existentes.empty:
            self.df = pd.concat([datos_existentes, self.df], ignore_index=True)

        # Eliminar duplicados basados en todas las columnas
        self.df = self.df.drop_duplicates()
        # Guardar el DataFrame combinado en formato JSON
        self.df.to_json(archivo, orient='records', lines=True)
        print(f"Resultados guardados correctamente en {archivo}")
        # Leer y mostrar el archivo actualizado para verificar
        df_resultados = pd.read_json(archivo, orient='records', lines=True)
        print(df_resultados)
        # Reiniciar la variable self.df para la próxima partida
        self.reiniciar_variables()
        print("Variable self.df reiniciada para la próxima partida.")

    def reiniciar_variables(self):
        self.nombre = ""
        self.dificultad = ""
        self.intentos = 0
        self.running = False
        self.respuesta = []
        self.rondas = ""
        
        self.boton = False
        self.reiniciar = False
        self.gameOver = False
        self.start_time = None
        self.end_time = None
        self.elapsed_time = None

        self.rondas_complet = 0
        self.fecha = 0
        self.hora = 0
        self.fallos = 0

        self.v1 = 2
        self.v2 = 1

        self.start_question_time = None
        self.end_question_time = 0
        self.response_time = 0
        self.responses_times = []
        self.media = 0
        self.puntuacion = 1000

        # Atributos para el seguimiento en tiempo real:
        self.racha = 0           # Racha actual de aciertos.
        self.fallo_detectado = False  # Bandera para indicar si hubo fallo reciente.

        self.df = pd.DataFrame(columns=[
            "Nombre", "Intentos", "Rondas", "Dificultad", "Fecha", "Hora",
            "Rondas completadas", "Fallos", "Tiempo transcurrido (min)", "Tiempo transcurrido (seg)", "Tiempo medio respuesta (seg):", "Puntuación"
        ])

    def calc_new_score(self, resultado):
        # Variables para los cálculos:
        K_min = 40
        K_max = 400
        alpha = 0.3466

        w = 1.5
        if resultado == "pierde":
            rondas_completadas = self.rondas_complet - 1
        else:
            rondas_completadas = int(self.rondas)

        rondas_totales = int(self.rondas)
        fallos_totales = int(self.fallos)

        D_min = 31/20
        D_max = 31.5

        node = self.g.get_node("Simon Say")
        actual_score = node.attrs["nota"].value
        num_partida = node.attrs["num_partidas"].value

        if num_partida == "" or num_partida is None:
            partida_actual = 1
        else:
            partida_actual = int(float(num_partida)) + 1

        print("Partida actual: ", partida_actual)

        # Cálculo del porcentaje de rondas completadas (umbral basado en rondas, sin fallos)
        print(f"Rondas completadas: {rondas_completadas}. Rondas totales: {rondas_totales}")

        ratio = rondas_completadas / rondas_totales if rondas_totales != 0 else 0.0
        print(f"Porcentaje de rondas completadas: {ratio}")

        # 1) Score real (S)
        origS = (rondas_completadas / rondas_totales) - (0.1 * (fallos_totales / (rondas_totales * 2))) if rondas_totales != 0 else 0.0
        # print(f"Score real S: {S}")

        if ratio >= 0.75:
            S = origS
        else:
            S = origS - 0.75
        print(f"Score ajustado S: {S}")

        # 2) Ajustamos tiempos para evitar dividir por cero
        t_on= self.v1 if self.v1 > 0 else 1e-9
        t_off = self.v2  if self.v2  > 0 else 1e-9

        # 3) Dificultad bruta (D)
        D = (1.0 / t_on + 1.0 / t_off) + w * (rondas_totales / 15.0)

        # 4) Normalización de la dificultad (E)
        E = ((D - D_min) / (D_max - D_min)) if (D_max != D_min) else 0.0
        E = 0.0 if E < 0.0 else (1.0 if E > 1.0 else E)  # Limitamos a [0,1]
        print(f"Dificultad normalizada E: {E}")

        # 5) Factor K para la partida (K_partida)
        K_game= K_min + (K_max - K_min) * math.exp(-alpha * (partida_actual - 1))
        print(f"Valor de K Game: {K_game}")


        # 6) Nueva puntuación
        if actual_score == "":
            actual_score = 1000

        new_score = round(float(actual_score) + K_game * (S - E))
        print("Nuevo ELO: ", new_score)

        # ---- CORRECCIÓN POSTERIOR ----
        diff = new_score - float(actual_score)
        # 1) Si superó 75% de rondas => mínimo +40
        if ratio >= 0.75:
            if diff < 41:
                print(f"Incremento de {diff} < 41 => se fuerza a +41")
                new_score = float(actual_score) + 41
        # 2) Si NO superó el 75% => mínimo de -40
        else:
            if diff > -41:
                print(f"Diferencia de {diff} > -41 => se fuerza a -41")
                new_score = float(actual_score) - 41

        # Redondeo final
        new_score = round(new_score)
        print("Nuevo ELO final: ", new_score)

        self.puntuacion = new_score

        self.media = round(self.media, 2)

        print("Actualizando valores en el nodo de SimonSay")
        node.attrs["nombre"].value = self.nombre
        node.attrs["aciertos"].value = str(rondas_completadas)
        node.attrs["dificultad"].value = self.dificultad
        node.attrs["rondas"].value = str(rondas_totales)
        node.attrs["fallos"].value = str(fallos_totales)
        node.attrs["t_medio"].value = str(self.media)
        node.attrs["nota"].value = str(new_score)
        node.attrs["num_partidas"].value = str(partida_actual)

        self.g.update_node(node)

    def first_time(self):
        node = self.g.get_node("Simon Say")
        node.attrs["num_partidas"].value = "0"
        self.g.update_node(node)

    def send_to_csv_manager(self):
        node = self.g.get_node("CSV Manager")
        node2 = self.g.get_node("Simon Say")

        node.attrs["nombre"].value = node2.attrs["nombre"].value
        node.attrs["ss_au"].value = node2.attrs["aciertos"].value
        node.attrs["ss_du"].value = node2.attrs["dificultad"].value
        node.attrs["ss_ru"].value = node2.attrs["rondas"].value
        node.attrs["ss_fu"].value = node2.attrs["fallos"].value
        node.attrs["ss_tu"].value = node2.attrs["t_medio"].value
        node.attrs["ss_nota"].value = node2.attrs["nota"].value
        node.attrs["num_partidas"].value = node2.attrs["num_partidas"].value
        node.attrs["actualizar_info"].value = True

        self.vaciar_ss_node()
        self.g.update_node(node)

    def vaciar_ss_node(self):
        node = self.g.get_node("Simon Say")

        node.attrs["nombre"].value = ""
        node.attrs["aciertos"].value = ""
        node.attrs["dificultad"].value = ""
        node.attrs["rondas"].value = ""
        node.attrs["fallos"].value = ""
        node.attrs["t_medio"].value = ""
        node.attrs["nota"].value = ""
        node.attrs["num_partidas"].value = ""

        self.g.update_node(node)

    @QtCore.Slot()
    def compute(self):

        return True



    def startup_check(self):
        print(f"Testing RoboCompCameraSimple.TImage from ifaces.RoboCompCameraSimple")
        test = ifaces.RoboCompCameraSimple.TImage()
        print(f"Testing RoboCompLEDArray.Pixel from ifaces.RoboCompLEDArray")
        test = ifaces.RoboCompLEDArray.Pixel()
        QTimer.singleShot(200, QApplication.instance().quit)

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

    def vaciar_csv_manager(self):
        node = self.g.get_node("CSV Manager")
        atributos_ignore = ["ID", "name", "pos_x", "pos_y", "pp_sv", "actualizar_info"]

        node.attrs["actualizar_info"].value = False
        node.attrs["pp_sv"].value = False

        for atributo in node.attrs:
            if atributo in atributos_ignore:
                pass
            else:
                node.attrs[atributo].value = ""
        self.g.update_node(node)

    def select_user(self):
        print("Usuario seleccionado")
        nombre = self.ui2.comboBox_user.currentText()

        if not nombre or nombre == "Seleccionar usuario...":
            print("Por favor selecciona un usuario.")
            return

        self.nombre = nombre.split(" - ")[0].strip()
        node = self.g.get_node("CSV Manager")
        node.attrs["nombre"].value = self.nombre
        self.g.update_node(node)

    def leerDatos(self):
        self.actualizar_datos()
        time.sleep(0.5)
        node = self.g.get_node("Simon Say")

        self.nombre = node.attrs["nombre"].value
        self.dificultad = node.attrs["dificultad"].value
        self.rondas = int(node.attrs["rondas"].value)
        self.v1 = float(node.attrs["v_on"].value)
        self.v2 = float(node.attrs["v_off"].value)

        pass

    def actualizar_datos(self):
        # Manda la señal para que settings adapter haga la adaptación inicial del juego.
        node = self.g.get_node("Settings Adapter")
        node.attrs["set_info"].value = True
        self.g.update_node(node)

    def RT_adjust(self):
        """
        Función que se llama en tiempo real para:
         - Revisar la racha y detectar fallos.
         - Ajustar los valores de v_off y v_on en consecuencia,
           sin modificar la dificultad base.
         - Mostrar los cambios efectuados.
        """
        print("--------------------------------------------------------")
        print("Ajustando en tiempo real")
        print("--------------------------------------------------------")

        # Si se detectó fallo, reiniciamos la racha y reseteamos la bandera.
        if self.fallo_detectado:
            print("Se detectó fallo reciente. Reiniciando racha a 0.")

        else:
            print(f"Racha actual: {self.racha}")

        print(f"Dificultad base: '{self.dificultad}'")
        self.ajustar_valores_v()
        print(f"Valores asignados: v_off = {self.v2}, v_on = {self.v1}")
        print("--------------------------------------------------------\n")

    def ajustar_valores_v(self):
        """
        Ajusta self.v_off y self.v_on según la racha y fallo detectado:
         - Si hay fallo, se usan los valores del nivel inferior respecto a la dificultad base.
         - Si la racha es >= 4, se usan los valores del nivel superior respecto a la dificultad base.
         - En rachas de 1 a 3 se mantienen los valores del nivel base.
        La dificultad base (self.dificultad_asignada) permanece inalterada.
        """
        # Nivel base que se definió en la inicialización (no se modifica).
        nivel_base = self.dificultad
        nivel_temporal = nivel_base  # Por defecto se mantienen los valores de la dificultad base.

        if self.fallo_detectado is True and self.racha < 3:
            print("Fallo detectado: ajustando valores a nivel inferior.")
            self.fallo_detectado = False
            self.racha = 0
            indice_base = self.niveles.index(nivel_base)
            if indice_base > 0:
                nivel_temporal = self.niveles[indice_base - 1]
                print(f"Se utilizarán los valores del nivel inferior: '{nivel_temporal}'")
            else:
                print(f"Ya se encuentra en el nivel mínimo ('{nivel_base}'); se mantienen los valores base.")
        elif self.racha >= 3 and self.fallo_detectado is False:
            print(f"Racha alta ({self.racha}) detectada: ajustando valores a nivel superior.")
            indice_base = self.niveles.index(nivel_base)
            self.bateria_rondas_actual = self.baterias_racha
            if indice_base < len(self.niveles) - 1:
                nivel_temporal = self.niveles[indice_base + 1]
                print(f"Se utilizarán los valores del nivel superior: '{nivel_temporal}'")
            else:
                print(f"Ya se encuentra en el nivel máximo ('{nivel_base}'); se mantienen los valores base.")
        elif self.fallo_detectado is True and self.racha >= 3:
            self.racha = 0
            self.bateria_rondas_actual = self.bateria_rondas
        else:
            print(f"Racha de {self.racha}: se mantienen los valores del nivel base ('{nivel_base}').")

        # Actualización de los valores de v_off y v_on usando el nivel temporal.
        self.v2 = self.v_values[nivel_temporal]["v_off"]
        self.v1 = self.v_values[nivel_temporal]["v_on"]
        print(f"Valores actualizados: v_off = {self.v2}, v_on = {self.v1}")


    # =============== Methods for Component Implements ==================
    # ===================================================================

    #
    # IMPLEMENTATION of StartGame method from JuegoSimonSay interface
    #
    def JuegoSimonSay_StartGame(self):
        self.set_all_LEDS_colors(255,0,0,0)
        self.update_ui_signal.emit()
        # pass

    @Slot()
    def on_update_ui(self):
        # Este código se ejecutará en el hilo principal
        if not self.ui:
            print("Error: la interfaz de usuario no se ha cargado correctamente.")
            return

        self.ui2 = self.therapist_ui()
        self.centrar_ventana(self.ui2)
        self.ui2.raise_()
        self.ui2.show()
        QApplication.processEvents()
    # ===================================================================
    # ===================================================================


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
