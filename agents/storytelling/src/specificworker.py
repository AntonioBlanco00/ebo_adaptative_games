#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
#    Copyright (C) 2025 by YOUR NAME HERE
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
from PySide6 import QtUiTools
from rich.console import Console
from genericworker import *
import interfaces as ifaces
import time
import os
import json
import csv
import random
import threading

from PySide6.QtCore import Signal, Slot

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
        self.agent_id = 452
        self.g = DSRGraph(0, "pythonAgent", self.agent_id)

        try:
            signals.connect(self.g, signals.UPDATE_NODE_ATTR, self.update_node_att)
            # signals.connect(self.g, signals.UPDATE_NODE, self.update_node)
            # signals.connect(self.g, signals.DELETE_NODE, self.delete_node)
            # signals.connect(self.g, signals.UPDATE_EDGE, self.update_edge)
            # signals.connect(self.g, signals.UPDATE_EDGE_ATTR, self.update_edge_att)
            # signals.connect(self.g, signals.DELETE_EDGE, self.delete_edge)
            console.print("signals connected")
        except RuntimeError as e:
            print(e)

        if startup_check:
            self.startup_check()
        else:
            self.timer.timeout.connect(self.compute)
            self.timer.start(self.Period)

        print("COMPONENTE STORYTELLING INICIADO")
        self.archivo_csv = "../../users_info.csv"

        # CARGA DE IGS
        self.ui = self.game_selector_ui()
        self.ui2 = self.conversational_ui()
        self.ui3 = self.storytelling_ui()
        self.ui4 = self.respuesta_ui()

        self.reiniciar_variables()

        # Variables para lógica autónoma
        self.autonomo = False
        self._autonomo_thread = None
        self._asr_lock = threading.Lock()

        self.update_ui_signal.connect(self.on_update_ui)

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

        return True

    def reiniciar_variables(self):
        self.nombre_jugador = ""
        self.aficiones = ""
        self.edad = ""
        self.familiares = ""

        self.personalidad = ""
        self.st_jc = ""

    # METHOD PARA CARGAR UIS
    def load_ui(self, ui_path, ui_number, logo_paths=None, botones=None, ayuda_button=None, back_button=None,
                combo_options=None):
        """
        Method genérico para cargar una UI desde archivo .ui.

        :param ui_path: Ruta al archivo .ui
        :param ui_number: Número identificador de la UI (1,2,3,4)
        :param logo_paths: Diccionario de QLabel -> ruta de imagen
        :param botones: Diccionario de botón -> función a conectar
        :param ayuda_button: Nombre del botón de ayuda para mostrar/ocultar panel ayuda
        :param back_button: Nombre del botón de back para volver al menú principal
        :param combo_options: Diccionario de QComboBox -> lista de opciones a cargar
        :return: Objeto UI cargado
        """
        loader = QtUiTools.QUiLoader()
        file = QFile(ui_path)
        file.open(QFile.ReadOnly)
        ui = loader.load(file)
        file.close()

        # Configurar logos
        if logo_paths:
            for label_name, path in logo_paths.items():
                label = getattr(ui, label_name, None)
                if label:
                    label.setPixmap(QPixmap(path))
                    label.setScaledContents(True)

        # Conectar botones
        if botones:
            for btn_name, func in botones.items():
                btn = getattr(ui, btn_name, None)
                if btn:
                    btn.clicked.connect(func)

        # Botón de ayuda
        if ayuda_button and hasattr(ui, ayuda_button):
            getattr(ui, ayuda_button).clicked.connect(lambda: self.toggle_ayuda(ui))
            if hasattr(ui, "ayuda"):
                ui.ayuda.hide()

        # Botón de back
        if back_button and hasattr(ui, back_button):
            getattr(ui, back_button).clicked.connect(lambda: self.back_clicked_ui(ui_number))

        # Cargar opciones en ComboBox si se pasan
        if combo_options:
            for combo_name, opciones in combo_options.items():
                combo = getattr(ui, combo_name, None)
                if combo:
                    combo.addItems(opciones)

        # Registrar UI para eventFilter
        if not hasattr(self, 'ui_numbers'):
            self.ui_numbers = {}
        self.ui_numbers[ui] = ui_number
        ui.installEventFilter(self)

        return ui

    # CARGA DE UIs

    def game_selector_ui(self):
        return self.load_ui(
            "../../igs/seleccion_menu.ui",
            ui_number=1,
            logo_paths={
                "label": "../../igs/logos/logo_euro.png",
                "label_2": "../../igs/logos/robolab.png"
            },
            botones={
                "conversation_game": self.conversation_clicked,
                "storytelling_game": self.story_clicked
            },
            ayuda_button="ayuda_button",
            back_button="back_button"
        )

    def conversational_ui(self):
        ui = self.load_ui(
            "../../igs/conversacional_menu.ui",
            ui_number=2,
            logo_paths={
                "label": "../../igs/logos/logo_euro.png",
                "label_2": "../../igs/logos/robolab.png"
            },
            botones={
                "startGame": lambda: self.start_game(tipo="conv", manual=True),
                "startGame_user": lambda: self.start_game(tipo="conv", manual=False)
            },
            ayuda_button="ayuda_button",
            back_button="back_button"
        )

        # Agregar opciones de personalidad
        opciones = ["Seleccionar Personalidad...", "EBO_simpatico", "EBO_neutro", "EBO_pasional"]
        ui.comboBox.addItems(opciones)

        # Cargar usuarios desde CSV
        self.cargarUsuarios(ui, self.archivo_csv)

        return ui

    def storytelling_ui(self):
        ui = self.load_ui(
            "../../igs/storytelling_menu.ui",
            ui_number=3,
            logo_paths={
                "label": "../../igs/logos/logo_euro.png",
                "label_2": "../../igs/logos/robolab.png"
            },
            botones={
                "startGame": lambda: self.start_game(tipo="story", manual=True),
                "startGame_user": lambda: self.start_game(tipo="story", manual=False)
            },
            ayuda_button="ayuda_button",
            back_button="back_button_2"
        )

        # Configurar ComboBox con juegos
        self.configure_combobox(ui, "../juegos_story")

        # Cargar usuarios desde CSV
        self.cargarUsuarios(ui, self.archivo_csv)

        return ui

    def respuesta_ui(self):
        ui = self.load_ui(
            "../../igs/respuesta_gpt.ui",
            ui_number=4,
            logo_paths={
                "label": "../../igs/logos/logo_euro.png",
                "label_2": "../../igs/logos/robolab.png"
            },
            botones={
                "enviar": self.enviar_clicked,
                "salir": self.salir_clicked,
                "checkAutonomo": self.toggle_autonomo_clicked
            },
            ayuda_button="ayuda_button"
        )

        # Registrar eventFilter para QTextEdit (respuestas)
        ui.respuesta.installEventFilter(self)

        checkbox = getattr(ui, "checkAutonomo", None)
        if checkbox:
            # Aseguramos que empieza apagado y sin modo autónomo
            checkbox.setChecked(False)
            self.autonomo = False

        return ui

    ################ FUNCIONES RELACIONADAS CON LA INTERFAZ GRÁFICA ################

    def centrar_ventana(self, ventana):
        pantalla = QApplication.primaryScreen().availableGeometry()
        tamano_ventana = ventana.size()

        x = (pantalla.width() - tamano_ventana.width()) // 2
        y = (pantalla.height() - tamano_ventana.height()) // 2

        ventana.move(x, y)

    ### FUNCIONES QUE IMPLEMENTAN LAS UI

    def back_clicked_ui(self, ui_number):
        """
        Función genérica para el botón de back.
        Cierra la UI correspondiente y lanza el menú principal.
        """
        if ui_number == 4:
            if self.autonomo:
                self.detener_autonomo()
            self.gpt_proxy.continueChat("03827857295769204")

        self.cerrar_ui(ui_number)  # Cierra la ventana correspondiente
        self.gestorsg_proxy.LanzarApp()  # Vuelve al menú principal

    def select_user_generic(self, ui, st=False):
        """Selecciona un usuario del comboBox y actualiza el CSV Manager."""
        nombre = ui.comboBox_user.currentText()

        if not nombre or "Seleccionar usuario" in nombre:
            print("Por favor selecciona un usuario.")
            return False

        self.nombre_jugador = nombre.split(" - ")[0].strip()
        node = self.g.get_node("CSV Manager")
        node.attrs["nombre"].value = self.nombre_jugador
        self.g.update_node(node)
        return True

    def toggle_ayuda(self, ui):
        if hasattr(ui, "ayuda") and ui.ayuda.isVisible():
            ui.ayuda.hide()
        elif hasattr(ui, "ayuda"):
            ui.ayuda.show()

    def leer_datos_generic(self, st=False):
        """Actualiza variables desde CSV Manager. st indica si es StoryTelling."""
        self.actualizar_datos()
        time.sleep(0.5)
        node = self.g.get_node("CSV Manager")

        self.nombre_jugador = node.attrs["nombre"].value
        self.aficiones = node.attrs["aficiones"].value
        self.edad = node.attrs["edad"].value
        self.familiares = node.attrs["familiares"].value

        if st:
            self.st_jc = node.attrs["st_jc"].value

        self.user_info = (f"Los datos del usuario con el que vas a hablar son los siguientes. "
                          f"Nombre: {self.nombre_jugador}. "
                          f"Edad: {self.edad}. "
                          f"Aficiones: {self.aficiones}. "
                          f"Familiares: {self.familiares}.")

        print("-------------------------------------------------------------------")
        print(self.user_info)
        print("-------------------------------------------------------------------")

    def start_game(self, tipo="story", manual=True):
        """
        Inicia un juego.
        tipo: "story" o "conv"
        manual: True si los datos se ingresan manualmente, False si se seleccionan del CSV
        """
        ui = self.ui3 if tipo == "story" else self.ui2

        if manual:
            self.nombre_jugador = ui.nombreE.toPlainText()
            self.aficiones = ui.aficionE.toPlainText()
            self.edad = ui.edadE.toPlainText()
            self.familiares = ui.famiE.toPlainText()
        else:
            self.select_user_generic(ui, st=(tipo == "story"))
            self.leer_datos_generic(st=(tipo == "story"))

        self.update_dsr()  # Actualiza CSV Manager

        if tipo == "story":
            juego = ui.comboBox.currentText() if manual else self.select_random_game()
            if not juego or "Seleccionar juego" in juego:
                print("Por favor selecciona un juego.")
                return
            self.archivo_path = os.path.join("../juegos_story", f"{juego}.json")
            self.user_info = self.archivo_json_a_string(self.archivo_path)
            self.story_selected_dsr(juego)
        else:
            if manual:
                self.user_info = f"Conversación con {self.nombre_jugador}"

            self.story_selected_dsr("Conversation")

        self.cerrar_ui(3 if tipo == "story" else 2)

        assistant_name = "StoryTelling" if tipo == "story" else self._get_selected_personality()
        print(f"[START] assistantName={assistant_name} | tipo={tipo}")
        self.gpt_proxy.setGameInfo(assistant_name, self.user_info)
        self.lanzar_ui4()
        self.ui4.text_info.setText("EBO comenzará a hablar en breve")
        self.gpt_proxy.startChat()
        self.ui4.text_info.setText("Introduzca respuesta")

    def _get_selected_personality(self) -> str:
        """Devuelve la personalidad elegida en la UI conversacional.
        Fallback seguro a 'EBO_simpatico' si no hay selección."""
        if not hasattr(self, "ui2") or not hasattr(self.ui2, "comboBox"):
            print("[UI] comboBox de personalidad NO encontrado; usando 'EBO_simpatico'")
            return "EBO_simpatico"

        val = self.ui2.comboBox.currentText().strip()
        if not val or "Seleccionar Personalidad" in val:
            print("[UI] Personalidad no seleccionada; usando 'EBO_simpatico'")
            return "EBO_simpatico"

        return val  # p. ej. 'EBO_simpatico', 'EBO_neutro', 'EBO_pasional'

    def conversation_clicked(self):
        print("Conversación Seleccionada")
        self.cerrar_ui(1)
        self.lanzar_ui2()

    def story_clicked(self):
        print("Story Telling Seleccionado")
        self.cerrar_ui(1)
        self.lanzar_ui3()

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

    def setDatos(self):
        self.nombre_jugador = self.ui2.nombreE.toPlainText()
        self.aficiones = self.ui2.aficionE.toPlainText()
        self.edad = self.ui2.edadE.toPlainText()
        self.familiares = self.ui2.famiE.toPlainText()

        self.user_info = (f"Los datos del usuario con el que vas a hablar son los siguientes. "
                          f"Nombre: {self.nombre_jugador}. "
                          f"Edad: {self.edad}. "
                          f"Aficiones: {self.aficiones}. "
                          f"Familiares: {self.familiares}. "
                          f"Presentate, saludale e inicia la conversación adaptandote a sus aficiones. Más adelante puedes preguntarle por sus aficiones"
                          )
        print("-------------------------------------------------------------------")
        print(self.user_info)
        print("-------------------------------------------------------------------")


    def actualizar_datos(self):
        node = self.g.get_node("Settings Adapter")
        node.attrs["set_info"].value = True
        self.g.update_node(node)

    def configure_combobox(self, ui, folder_path):
        # Acceder al QComboBox por su nombre de objeto
        combobox = ui.findChild(QtWidgets.QComboBox, "comboBox")
        if combobox:
            combobox.addItem("Seleccionar juego...")
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

    def archivo_json_a_string(self, ruta_archivo):
        with open(ruta_archivo, 'r') as archivo:
            json_data = json.load(archivo)  # Carga el contenido del archivo JSON

        # Actualizar valores en el JSON
        json_data["nombre del jugador"] = self.nombre_jugador
        json_data["aficiones"] = self.aficiones
        json_data["edad"] = self.edad
        json_data["familiares"] = self.familiares

        return json.dumps(json_data)


    def update_dsr(self):
        node = self.g.get_node("CSV Manager")
        node.attrs["nombre"].value = self.nombre_jugador
        node.attrs["aficiones"].value = self.aficiones
        node.attrs["edad"].value = self.edad
        node.attrs["familiares"].value = self.familiares
        self.g.update_node(node)

    def setDatos_clicked(self):
        self.nombre_jugador = self.ui3.nombreE.toPlainText()
        self.aficiones = self.ui3.aficionE.toPlainText()
        self.edad = self.ui3.edadE.toPlainText()
        self.familiares = self.ui3.famiE.toPlainText()

        self.ui3.startGame.setEnabled(True)

    #### ################ ############################################### ################


    def select_random_game(self):
        jc = [j.strip().lower() for j in self.st_jc.split(",")]
        print(f"JUEGOS COMPLETADOS: {jc}")
        carpeta_juegos = "../juegos_story"

        juegos_en_carpeta = [
            os.path.splitext(f)[0].strip().lower()
            for f in os.listdir(carpeta_juegos)
            if os.path.isfile(os.path.join(carpeta_juegos, f))
        ]
        juegos_disponibles = [j for j in juegos_en_carpeta if j not in jc]

        print(f"JUEGOS DISPONIBLES {juegos_disponibles}")

        juego_seleccionado = random.choice(juegos_disponibles) if juegos_disponibles else None

        print("Juego seleccionado:", juego_seleccionado)

        return juego_seleccionado


    def enviar_clicked(self):
        if self.autonomo:
            print("El envío manual está bloqueado: Modo Autónomo activo.")
            return

        mensaje = self.ui4.respuesta.toPlainText()

        if not mensaje:
            return
        
        self.ui4.respuesta.clear()  # Limpiar el QTextEdit
        self.ui4.respuesta.clearFocus()  # Forzar que pierda el foco
        self.ui4.respuesta.setFocus()  # Volver a darle foco después
    
        self.ui4.text_info.setText("Mensaje ENVIADO, EBO está pensando...")
        QApplication.processEvents()

        self.gpt_proxy.continueChat(mensaje)
        self.ui4.text_info.setText("Introduzca respuesta")
            
    def salir_clicked(self):
        respuesta = QMessageBox.question(
        self.ui4, "Confirmar salida", "¿Estás seguro de que quieres salir?",
        QMessageBox.Yes | QMessageBox.No, QMessageBox.No
    )

        if respuesta == QMessageBox.Yes:
            if self.autonomo:
                self.detener_autonomo()
            self.reiniciar_variables()
            self.ui4.text_info.setText("Saliendo del programa...")
            QApplication.processEvents()
            self.cerrar_ui(4)
            self.gestorsg_proxy.LanzarApp()
            self.gpt_proxy.continueChat("03827857295769204")
        else:
            pass

    # ==========================================================
    # ==== INICIO: FUNCIONES DEL MODO AUTÓNOMO ====
    # ==========================================================

    def iniciar_autonomo(self):
        """ Inicia el proceso del modo autónomo. """
        if self.autonomo:
            print("iniciar_autonomo: Ya está activo o iniciándose. No hacer nada.")
            return

        self.autonomo = True
        print("iniciar_autonomo: Flag 'autonomo' puesto a True.")

        waiter_thread = threading.Thread(
            target=self.esperar_y_lanzar_autonomo,
            daemon=True
        )
        waiter_thread.start()
        print("iniciar_autonomo: Hilo observador lanzado.")

    def esperar_y_lanzar_autonomo(self):
        print("Hilo observador: Esperando a que EBO termine de hablar...")

        try:
            while self.speech_proxy.isBusy():
                if not self.autonomo:
                    print("Hilo observador: Arranque cancelado por el usuario (mientras esperaba).")
                    return

                time.sleep(0.1)

        except Exception as e:
            print(f"Hilo observador: Error comprobando isBusy(): {e}. Abortando.")
            self.autonomo = False
            return

        if not self.autonomo:
            print("Hilo observador: Arranque cancelado justo al terminar de hablar.")
            return

        print("Hilo observador: Habla terminada. Lanzando hilo autónomo principal...")
        self._autonomo_thread = threading.Thread(
            target=self.run_autonomous_loop,
            daemon=True
        )
        self._autonomo_thread.start()
        print("Modo Autónomo INICIADO.")

    def detener_autonomo(self):
        """Pone a False la variable de control, llama a stopListening y espera a que el hilo termine (join)."""
        if self.autonomo:
            self.autonomo = False
            print("Señal de DETENCIÓN enviada al modo autónomo.")

            # PASO 1: Notificar al componente ASR que debe detener su escucha bloqueante
            try:
                self.eboasr_proxy.stopListening()
                print("Llamada a eboasr_proxy.stopListening() enviada.")
            except Exception as e:
                print(f"Error al llamar a stopListening: {e}")

            # PASO 2: Esperar a que el hilo termine (Join)
            if self._autonomo_thread and self._autonomo_thread.is_alive():
                print("Esperando a que el hilo autónomo finalice...")
                # Usar un timeout (e.g., 3.0 segundos) para no bloquear indefinidamente.
                self._autonomo_thread.join(timeout=3.0)

                if self._autonomo_thread and self._autonomo_thread.is_alive():
                    # Esto indica que el hilo no terminó a tiempo, pero el proceso principal continúa.
                    print("Advertencia: El hilo autónomo no se detuvo a tiempo.")
                else:
                    print("Hilo autónomo DETENIDO correctamente.")

            self._autonomo_thread = None  # Limpiar la referencia

    def run_autonomous_loop(self):
        while self.autonomo:
            with self._asr_lock:
                text = self.eboasr_proxy.listenandtranscript()
                print("EBO HA ESCUCHADO: ", text)

            if not self.autonomo:
                break

            if not text:
                time.sleep(0.1)
                continue

            self._asr_lock.acquire()
            try:
                self.gpt_proxy.continueChat(text)

                ok = self.wait_for_speech_cycle_forgiving(
                    wait_for_start_timeout=5,
                    wait_for_end_timeout=120.0,
                    poll_interval=0.05,
                    post_silence_grace=0.5,
                    fallback_wait_after_no_start=0.8
                )
                if not ok:
                    time.sleep(1.0)
            finally:
                self._asr_lock.release()

            time.sleep(0.1)

        print("Hilo del modo autónomo DETENIDO.")

    def wait_for_speech_cycle_forgiving(self,
                                        wait_for_start_timeout: float = 1.5,
                                        wait_for_end_timeout: float = 30.0,
                                        poll_interval: float = 0.05,
                                        post_silence_grace: float = 0.25,
                                        fallback_wait_after_no_start: float = 0.8) -> bool:

        start_deadline = time.time() + wait_for_start_timeout
        saw_start = False

        # 1) Esperar inicio hasta timeout
        while time.time() < start_deadline:
            try:
                if self.speech_proxy.isBusy():
                    saw_start = True
                    break
            except Exception:
                pass
            time.sleep(poll_interval)

        if not saw_start:
            # No empezó a hablar: fallback corto y salir (modo forgiving)
            time.sleep(fallback_wait_after_no_start)
            return True

        # 2) Si empezó a hablar, esperar a que termine
        end_deadline = time.time() + wait_for_end_timeout
        while time.time() < end_deadline:
            try:
                if not self.speech_proxy.isBusy():
                    # pequeña confirmación post-silence
                    time.sleep(post_silence_grace)
                    if not self.speech_proxy.isBusy():
                        return True

            except Exception:
                pass
            time.sleep(poll_interval)

        # timeout esperando a que termine de hablar
        return False

    @Slot()
    def toggle_autonomo_clicked(self, checked):
        enviar_btn = getattr(self.ui4, "enviar", None)

        if checked:
            # Modo Autónomo Activado (ON)
            self.iniciar_autonomo()

            if enviar_btn:
                enviar_btn.setEnabled(False)

            self.ui4.text_info.setText("Modo Autónomo ACTIVADO. EBO está a la escucha...")

        else:
            # Modo Autónomo Desactivado (OFF)
            self.detener_autonomo()
            if enviar_btn:
                enviar_btn.setEnabled(True)
            self.ui4.text_info.setText("Introduzca respuesta")

    # ==========================================================
    # ==== FIN: FUNCIONES DEL MODO AUTÓNOMO ====
    # ==========================================================
        

    ################ ############################################### ################

    def eventFilter(self, obj, event):
        ui_number = self.ui_numbers.get(obj, None)

        if ui_number is not None and event.type() == QtCore.QEvent.Close:
            target_ui = self.ui if ui_number == 1 else getattr(self, f'ui{ui_number}', None)

            if obj == target_ui:
                respuesta = QMessageBox.question(
                    target_ui, "Cerrar", "¿Estás seguro de que quieres salir del juego?",
                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No
                )
                if respuesta == QMessageBox.Yes:
                    print(f"Ventana {ui_number} cerrada por el usuario.")

                    if ui_number == 4:
                        if self.autonomo:
                            self.detener_autonomo()
                        self.gpt_proxy.continueChat("03827857295769204")

                    self.reiniciar_variables()
                    self.vaciar_csv_manager()
                    self.gestorsg_proxy.LanzarApp()
                    return False
                else:
                    print(f"Cierre de la ventana {ui_number} cancelado.")
                    event.ignore()
                    return True

        if hasattr(self, 'ui4') and obj == self.ui4.respuesta and event.type() == QtCore.QEvent.KeyPress:
            if event.key() in (Qt.Key_Return, Qt.Key_Enter):
                self.enviar_clicked()
                return True

        return super().eventFilter(obj, event)

    
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

    def vaciar_csv_manager(self):
        print("VACIAR CSV MANAGER LLAMADO")
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

    def game_selected_dsr(self, game):
        node = self.g.get_node("Actual Game")
        node.attrs["actual_game"].value = game
        self.g.update_node(node)

    def story_selected_dsr(self, game):
        node = self.g.get_node("Storytelling")
        node.attrs["actual_game"].value = game
        self.g.update_node(node)

    def lanzar_ui2(self):
        self.ui2 = self.conversational_ui()
        self.game_selected_dsr("Conversation")
        self.centrar_ventana(self.ui2)
        self.ui2.show()
        QApplication.processEvents()

    def lanzar_ui3(self):
        self.ui3 = self.storytelling_ui()
        self.game_selected_dsr("Storytelling")
        self.centrar_ventana(self.ui3)
        self.ui3.show()
        QApplication.processEvents()

    def lanzar_ui4(self):
        self.centrar_ventana(self.ui4)
        self.ui4.show()
        QApplication.processEvents()

    def startup_check(self):
        QTimer.singleShot(200, QApplication.instance().quit)



    # =============== Methods for Component Implements ==================
    # ===================================================================

    #
    # IMPLEMENTATION of StartGame method from StoryTelling interface
    #
    def StoryTelling_StartGame(self):
        self.update_ui_signal.emit()

        # print("Juego terminado o ventana cerrada")

    @Slot()
    def on_update_ui(self):
        # Este código se ejecutará en el hilo principal
        if not self.ui:
            print("Error: la interfaz de usuario no se ha cargado correctamente.")
            return

        self.centrar_ventana(self.ui)
        self.ui.raise_()
        self.ui.show()
        QApplication.processEvents()
    # ===================================================================
    # ===================================================================


    ######################
    # From the RoboCompEboASR you can call this methods:
    # self.eboasr_proxy.listenandtranscript(...)
    # self.eboasr_proxy.stopListening(...)

    ######################
    # From the RoboCompGPT you can call this methods:
    # self.gpt_proxy.continueChat(...)
    # self.gpt_proxy.setGameInfo(...)
    # self.gpt_proxy.startChat(...)

    ######################
    # From the RoboCompGestorSG you can call this methods:
    # self.gestorsg_proxy.LanzarApp(...)

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
