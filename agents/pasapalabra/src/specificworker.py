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
import csv
from collections import defaultdict


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
        self.pistas = []
        self.dificultades = []
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
        self.NUM_LEDS = 54
        self.racha_aciertos = 0
        self.umbral_tiempo_pista = 15
        self.pistas_usadas = 0

        self.ROSCOS_POSIBLES = [
            "Animales",
            "Antonimos",
            "Comida",
            "Extremadura",
            "Partes_de_la_casa",
        ]

        ########## DEFINICIÓN DEL DATAFRAME QUE ALMACENA LOS DATOS ##########
        self.df = pd.DataFrame(
            columns=["Nombre", "Nivel actual", "Rosco", "Aciertos", "Fallos", "Pasadas", "Nota partida", "Fecha",
                     "Hora", "Tiempo transcurrido (min)", "Tiempo transcurrido (seg)",
                     "Tiempo de respuesta medio (seg)"])
        self.resp = ""
        self.running = False
        self.boton = False
        self.check = ""
        self.letra_actual = ""
        self.pregunta_actual = ""
        self.pista_actual = ""
        self.dificultad_actual = ""
        self.start_question_time = 0
        self.end_question_time = 0
        self.response_time = 0
        self.responses_times = []
        self.media = 0
        self.nota = ""
        self.nota_partida = 0
        self.rc = ""

        self.archivo_csv = "../../users_info.csv"

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

        self.update_ui_signal.connect(self.on_update_ui)

        # print("INICIANDO TEST DE INICIO JUEGO")
        # self.Pasapalabra_StartGame()

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
    # Para llamar a la función:
    # cupos = {"Fácil": 3, "Media": 4, "Difícil": 2}
    # self.archivo("roscos/animales.json", cupos)

    def archivo(self, ruta_json: str,
                cupos: dict[str, int] | None = None,
                seed: int | None = None) -> None:

        if seed is not None:
            random.seed(seed)

        # 1. Leer el fichero
        with open(ruta_json, encoding="utf-8") as fh:
            todas = json.load(fh)["preguntas"]

        # 2. Filtrar por cupos
        if cupos:
            bolsas = defaultdict(list)
            for q in todas:
                bolsas[q["dificultad"]].append(q)

            seleccion = []
            for nivel, n_pedidas in cupos.items():
                disp = bolsas.get(nivel, [])
                if not disp:
                    console.print(f"[yellow]⚠ No hay preguntas “{nivel}”.")
                    continue
                n = min(n_pedidas, len(disp))
                if n < n_pedidas:
                    console.print(f"[yellow]⚠ Solo hay {n} preguntas “{nivel}”, no {n_pedidas}.")
                seleccion.extend(random.sample(disp, n))
        else:
            seleccion = todas[:]  # copia completa

        # 2.bis ▸ Ordenar alfabéticamente por la letra
        seleccion.sort(key=lambda q: q["letra"].lower())

        # 3. Resetear contenedores
        self.letras.clear();
        self.preguntas.clear();
        self.respuestas.clear()
        self.pistas.clear();
        self.dificultades.clear()

        # 4. Volcar las preguntas seleccionadas y ordenadas
        for q in seleccion:
            self.letras.append(q["letra"])
            self.preguntas.append(q["definicion"])
            self.respuestas.append(q["respuesta"])
            self.pistas.append(q.get("pista", ""))
            self.dificultades.append(q.get("dificultad", ""))

        # TESTEAR QUE FUNCIONA
        print(f"Letras: {self.letras}")
        print(f"Preguntas: {self.preguntas}")
        print(f"Respuestas: {self.respuestas}")
        print(f"Pistas: {self.pistas}")
        print(f"Dificultades: {self.dificultades}")

    ########## REALIZA EL AJSUTE DE DIFICULTAD SEGUN EL NIVEL DEL USUARIO, GENERA EL CUPOS QUE MANDAR A SELF.ARCHIVO ##########
    def cupos_por_nivel(self, nivel: int) -> dict[str, int]:
        # (fácil, media, difícil) para cada nivel 1-21
        tabla = [
            (5, 0, 0),  # 1  Getting Started
            (5, 1, 0),  # 2  First Steps
            (5, 2, 0),  # 3  Gentle Learning
            (5, 3, 0),  # 4  First Challenge
            (5, 4, 0),  # 5  Gradual Progression
            (5, 5, 0),  # 6  Base Level
            (5, 3, 1),  # 7  Basic Competence
            (5, 4, 1),  # 8  Moderate Progress
            (5, 3, 2),  # 9  Strengthening
            (5, 4, 2),  # 10 Consolidation
            (5, 3, 3),  # 11 Initial Breakthrough
            (5, 4, 3),  # 12 Proficiency
            (4, 5, 3),  # 13 Expertise
            (4, 3, 4),  # 14 Mastery
            (3, 5, 3),  # 15 Excellence
            (4, 4, 4),  # 16 Supreme
            (5, 3, 5),  # 17 Higher Challenge
            (4, 5, 4),  # 18 Mythical Level
            (5, 5, 4),  # 19 Epic
            (5, 4, 5),  # 20 Legendary
            (5, 5, 5)  # 21 Legend
        ]

        if not 1 <= nivel <= 21:
            raise ValueError("El nivel debe estar entre 1 y 21 inclusive.")

        faciles, medias, dificiles = tabla[nivel - 1]
        return {"Fácil": faciles, "Media": medias, "Difícil": dificiles}

    ########## PROCESO DEL JUEGO ##########
    def juego(self):
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
                    respuesta_correcta = self.respuestas[indice]
                    self.pregunta_actual = self.preguntas[indice]
                    self.letra_actual = f"Comienza con la letra:{letra}" if self.respuestas[indice].startswith(
                        letra) else f"Contiene la letra:{letra}"
                    self.pista_actual = self.pistas[indice]

                    if self.racha_aciertos == 0 and self.fallos >= (2 + self.pistas_usadas):
                        self.speech_proxy.say(f"{self.letra_actual}, {self.pregunta_actual}. Aquí va una pista: {self.pista_actual}", False)
                        self.pistas_usadas += 1
                    else:
                        self.speech_proxy.say(f"{self.letra_actual}, {self.pregunta_actual}", False)

                    self.terminaHablar()

                    self.start_question_time = time.time()
                    mostrar_pista_tiempo = False

                    self.ui.respuesta.clear()
                    self.ui.respuesta.insertPlainText(respuesta_correcta)
                    self.ui.show()

                    while self.resp == "":
                        QApplication.processEvents()
                        tiempo_actual = time.time() - self.start_question_time
                        # print(f"Tiempo: {tiempo_actual}")

                        # Pista automática por tiempo excesivo
                        if not mostrar_pista_tiempo and tiempo_actual >= self.umbral_tiempo_pista:
                            self.speech_proxy.say(f"Te doy una pista: {self.pista_actual}", False)
                            mostrar_pista_tiempo = True

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
                        self.racha_aciertos = 0
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
                        self.racha_aciertos += 1
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
                        self.racha_aciertos = 0

                    self.ajustar_nota_actual(self.resp, self.dificultades[indice])
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

                    self.resp = ""
                    indice = self.letras.index(letra)
                    respuesta_correcta = self.respuestas[indice]
                    self.pregunta_actual = self.preguntas[indice]
                    self.letra_actual = f"Comienza con la letra:{letra}" if self.respuestas[indice].startswith(
                        letra) else f"Contiene la letra:{letra}"
                    self.pista_actual = self.pistas[indice]

                    self.speech_proxy.say(self.letra_actual, False)
                    self.speech_proxy.say(self.pregunta_actual, False)

                    # Control dinámico para decir pistas por fallos acumulados (en pasadas)
                    if self.racha_aciertos == 0 and self.fallos >= (2 + self.pistas_usadas):
                        self.speech_proxy.say(f"{self.letra_actual}, {self.pregunta_actual}. Aquí va una pista: {self.pista_actual}", False)
                        self.pistas_usadas += 1
                    else:
                        self.speech_proxy.say(f"{self.letra_actual}, {self.pregunta_actual}", False)

                    self.terminaHablar()

                    self.start_question_time = time.time()
                    mostrar_pista_tiempo = False

                    self.ui.respuesta.clear()
                    self.ui.respuesta.insertPlainText(respuesta_correcta)
                    self.ui.show()

                    while self.resp == "":
                        QApplication.processEvents()
                        tiempo_actual = time.time() - self.start_question_time
                        # print(f"Tiempo: {tiempo_actual}")

                        # Pista automática por tiempo excesivo
                        if not mostrar_pista_tiempo and tiempo_actual >= self.umbral_tiempo_pista:
                            self.speech_proxy.say(f"Te doy una pista: {self.pista_actual}", False)
                            mostrar_pista_tiempo = True

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
                        self.racha_aciertos = 0

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
                        self.racha_aciertos += 1

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
                        self.racha_aciertos = 0

                    self.ajustar_nota_actual(self.resp, self.dificultades[indice])
                    self.end_question_time = time.time()
                    self.cerrar_ui(1)
                    self.response_time = self.end_question_time - self.start_question_time
                    self.responses_times.append(self.response_time)

        self.end_time = time.time()
        self.elapsed_time = self.end_time - self.start_time  # Tiempo en segundos
        self.media = sum(self.responses_times) / len(self.responses_times)
        self.running = False
        R = self.calc_nota_final()
        # Resultados finales
        self.speech_proxy.say("Fin del juego. ¡Lo has hecho genial!:", False)
        self.agregar_resultados(self.nombre, self.rosco, self.aciertos, self.fallos, self.pasadas, self.fecha,
                                self.hora, (self.elapsed_time//60), (self.elapsed_time%60), self.media, R)
        self.guardar_resultados()
        self.send_to_csv_manager(self.ajuste_nivel(R))
        # REINICIAR TODAS LAS VARIABLES
        self.reiniciar_variables()
        self.gestorsg_proxy.LanzarApp()

    def ajustar_nota_actual(self, acierto, dificultad):
        if acierto == "si" and dificultad == "Fácil":
            self.nota_partida = self.nota_partida + 5
        if acierto == "si" and dificultad == "Media":
            self.nota_partida = self.nota_partida + 10
        if acierto == "si" and dificultad == "Difícil":
            self.nota_partida = self.nota_partida + 15
        if acierto == "no" and dificultad == "Media":
            self.nota_partida = self.nota_partida - 2
        if acierto == "no" and dificultad == "Difícil":
            self.nota_partida = self.nota_partida - 5
        else:
            pass

    def calc_nota_final(self): # calcular esto y pasarlo por ajsute_nivel
        n_facil = self.dificultades.count("Fácil")
        n_media = self.dificultades.count("Media")
        n_dificil = self.dificultades.count("Difícil")
        nota_max = n_facil * 5 + n_media * 10 + n_dificil * 15
        R = self.nota_partida / nota_max
        print("Nota obtenida en la partida: ", R)
        return R

    def ajuste_nivel(self, R: float) -> int:
        if R == 1.0:
            return +3
        elif 0.85 <= R < 1.0:
            return +2
        elif 0.625 <= R < 0.85:
            return +1
        elif 0.40 <= R < 0.625:
            return 0  # mantener nivel
        elif 0.15 <= R < 0.40:
            return -1
        elif 0.0 < R < 0.15:
            return -2
        else:  # R == 0
            return -3

    def send_to_csv_manager(self, R):
        node = self.g.get_node("CSV Manager")
        nota_final = float(self.nota) + R

        node.attrs["nombre"].value = self.nombre
        node.attrs["pp_nota"].value = str(nota_final)
        node.attrs["pp_rc"].value = self.rc
        node.attrs["actualizar_info"].value = True

        self.vaciar_pp_node()
        self.g.update_node(node)

    def vaciar_pp_node(self):
        node = self.g.get_node("Pasapalabra")

        node.attrs["nombre"].value = ""
        node.attrs["racha"].value = ""
        node.attrs["rosco"].value = ""
        node.attrs["segunda_vuelta"].value = False

        self.g.update_node(node)

    def reiniciar_variables(self):
        self.datos = []
        self.letras = []
        self.preguntas = []
        self.respuestas = []
        self.pistas = []
        self.dificultades = []
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
        self.pista_actual = ""
        self.dificultad_actual = ""
        self.start_question_time = 0
        self.end_question_time = 0
        self.response_time = 0
        self.responses_times = []
        self.media = 0
        self.nota = ""
        self.nota_partida = 0
        self.rc = ""
        self.racha_aciertos = 0
        self.umbral_tiempo_pista = 15
        self.pistas_usadas = 0

        self.df = pd.DataFrame(
            columns=["Nombre", "Nivel actual", "Rosco", "Aciertos", "Fallos", "Pasadas", "Nota partida", "Fecha",
                     "Hora", "Tiempo transcurrido (min)", "Tiempo transcurrido (seg)",
                     "Tiempo de respuesta medio (seg)"])

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
                           tiempo_transcurrido_min, tiempo_transcurrido_seg, tiempo_respuesta_medio, R):

        nota_partida = R*10
        # Crea un diccionario con los datos nuevos
        nuevo_resultado = {
            "Nombre": nombre,
            "Nivel actual": self.nota,
            "Rosco": dificultad,
            "Aciertos": aciertos,
            "Fallos": fallos,
            "Pasadas": pasadas,
            "Nota partida": nota_partida,
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
        ui.label_2.setPixmap(QPixmap("../../igs/logos/logo_euro.png"))
        ui.label_2.setScaledContents(True)  # Asegúrate de que la imagen se ajuste al QLabel

        ui.label_3.setPixmap(QPixmap("../../igs/logos/robolab.png"))
        ui.label_3.setScaledContents(True)  # Ajusta la imagen a los límites del QLabel

        # Conectar botones a funciones
        ui.correcta.clicked.connect(self.correcta_clicked)
        ui.incorrecta.clicked.connect(self.incorrecta_clicked)
        ui.pasapalabra.clicked.connect(self.pasapalabra_clicked)
        ui.repetir.clicked.connect(self.repetir_clicked)

        ui.ayuda.hide()
        ui.ayuda_button.clicked.connect(self.ayuda_clicked)

        ui.back_button.clicked.connect(self.back_clicked)
        
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
        ui.confirmar_button_2.clicked.connect(self.therapist_exist)

        ui.ayuda.hide()
        ui.ayuda_button.clicked.connect(self.ayuda_clicked2)

        ui.back_button_2.clicked.connect(self.back_clicked2)

        self.cargarUsuarios(ui, self.archivo_csv)

        # Cerrar con la x
        if not hasattr(self, 'ui_numbers'):
            self.ui_numbers = {}
            
        self.ui_numbers[ui] = 2  
        ui.installEventFilter(self) 
        return ui

    def ayuda_clicked2(self):
        print("BOTON AYUDA PULSADO")
        if self.ui2.ayuda.isVisible():  # Verifica si está visible
            self.ui2.ayuda.hide()  # Si está visible, ocultarlo
        else:
            self.ui2.ayuda.show()

    def back_clicked2(self):
        print("Volviendo al menu principal")
        self.cerrar_ui(2)
        self.gestorsg_proxy.LanzarApp()

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

    def therapist(self): # primera partida
        cupos = self.cupos_por_nivel(round(10))
        # Obtiene los valores ingresados en los campos
        self.nombre = self.ui2.usuario.toPlainText()
        self.rosco = self.ui2.comboBox.currentText()
        self.nota = "6"

        # Validaciones simples
        if not self.nombre:
            print("Por favor ingresa un nombre de usuario.")
            return
        if self.rosco == "Rosco automático":
            self.rosco = self._rosco_aleatorio_no_repetido()

        if not self.rosco:
            print("Por favor selecciona un rosco.")
            return

        self.archivo(f"roscos/{self.rosco}.json", cupos)
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

    def _rosco_aleatorio_no_repetido(self):
        """Devuelve un rosco que aún no esté en self.rc y lo marca como completado."""
        # 1) normalizamos lo ya completado
        if isinstance(self.rc, str):
            completados = {r.strip().lower() for r in self.rc.split(",") if r.strip()}
        else:  # lista / set
            completados = {os.path.splitext(r)[0].strip().lower() for r in self.rc}

        # 2) calculamos disponibles
        disponibles = [
            r for r in self.ROSCOS_POSIBLES
            if os.path.splitext(r)[0].lower() not in completados
        ]
        if not disponibles:  # todos hechos → se permiten repetidos
            disponibles = self.ROSCOS_POSIBLES

        # 3) seleccionamos
        rosco_elegido = random.choice(disponibles)

        # 4) ACTUALIZAMOS self.rc  (solo el nombre sin extensión, en minúsculas)
        sin_extension = os.path.splitext(rosco_elegido)[0].lower()

        if isinstance(self.rc, str):
            # si estaba vacía, no añadimos coma inicial
            self.rc = ", ".join(filter(None, [self.rc.strip(), sin_extension]))
        else:  # lista / set
            self.rc.append(sin_extension) if isinstance(self.rc, list) else self.rc.add(sin_extension)

        return rosco_elegido

    ######## LOGICA USUARIO EXISTENTE, CARGA DE DATOS E INICIO DE JUEGO ##################
    def therapist_exist(self):
        self.select_user()
        self.leerDatos()
        if self.nota != "":
            cupos = self.cupos_por_nivel(round(float(self.nota)))
        else:
            self.nota = "6"
            cupos = self.cupos_por_nivel(round(float(self.nota)))

        self.rosco = self.ui2.comboBox.currentText()
        print(self.rosco)

        if self.rosco == "Rosco automático":
            self.rosco = self._rosco_aleatorio_no_repetido()

        self.archivo(f"roscos/{self.rosco}.json", cupos)
        print("Valores confirmados. Juego listo para comenzar.")
        self.boton = True
        self.running = True
        self.sounds["click"].play()
        self.cerrar_ui(2)
        self.ui2.usuario.clear()
        self.introduccion()

    def select_user(self):
        print("Usuario seleccionado")
        nombre = self.ui2.comboBox_user.currentText()

        if not nombre or nombre == "Seleccionar usuario...":
            print("Por favor selecciona un usuario.")
            return

        self.nombre_jugador = nombre.split(" - ")[0].strip()
        node = self.g.get_node("CSV Manager")
        node.attrs["nombre"].value = self.nombre_jugador
        self.g.update_node(node)

    def leerDatos(self):
        self.actualizar_datos()
        time.sleep(0.5)
        node = self.g.get_node("CSV Manager")

        self.nombre = node.attrs["nombre"].value
        self.nota = node.attrs["pp_nota"].value
        self.rc = node.attrs["pp_rc"].value

    #########################################################################################

    def configure_combobox(self, ui, folder_path):
        # Acceder al QComboBox por su nombre de objeto
        combobox = ui.findChild(QtWidgets.QComboBox, "comboBox")
        if combobox:
            combobox.addItem("Rosco automático")
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

    def actualizar_datos(self):
        # Manda la señal para que settings adapter haga la adaptación inicial del juego.
        node = self.g.get_node("Settings Adapter")
        node.attrs["set_info"].value = True
        self.g.update_node(node)

    @QtCore.Slot()
    def compute(self):
        # TESTEO FUNCIONES
        # input("Pulsa Enter para probar una generación con 2 preguntas de cada dificultad")
        # cupos = {"Fácil": 1, "Media": 1, "Difícil": 1}
        # self.archivo("roscos/Animales.json", cupos)

        # cupos = self.cupos_por_nivel(10)  # {'Fácil': 5, 'Media': 4, 'Difícil': 3}
        # self.archivo("roscos/Animales.json", cupos)

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
        print("INICIANDO PASAPALABRA")
        self.ui2 = self.therapist_ui()
        self.update_ui_signal.emit()

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
