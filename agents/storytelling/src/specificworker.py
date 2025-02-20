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

        self.flag_test = True
        print("COMPONENTE STORYTELLING INICIADO")

        self.ui = self.game_selector_ui()
        self.ui2 = self.conversational_ui()
        self.ui3 = self.storytelling_ui()
        self.ui4 = self.respuesta_ui()

        # Actualizar valores en el JSON
        self.nombre_jugador = ""
        self.aficiones = ""
        self.edad = ""
        self.familiares = ""

        self.personalidad = ""

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
        
    ################ FUNCIONES RELACIONADAS CON LA INTERFAZ GRÁFICA ################

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

    #### UI 1 #### ################ ############################################### ################
    def game_selector_ui (self):
        #Carga la interfaz desde el archivo .ui
        loader = QtUiTools.QUiLoader()
        file = QtCore.QFile("../../igs/seleccion_menu.ui")
        file.open(QtCore.QFile.ReadOnly)
        ui = loader.load(file)
        file.close()

        # Conectar botones a funciones
        ui.conversation_game.clicked.connect(self.conversation_clicked)
        ui.storytelling_game.clicked.connect(self.story_clicked)
        
        # Cerrar con la x
        if not hasattr(self, 'ui_numbers'):
            self.ui_numbers = {}
            
        self.ui_numbers[ui] = 1  
        ui.installEventFilter(self) 


        return ui


    def conversation_clicked(self):
        print("Conversación Seleccionada")
        self.cerrar_ui(1)
        self.lanzar_ui2()

    def story_clicked(self):
        print("Story Telling Seleccionado")
        self.cerrar_ui(1)
        self.lanzar_ui3()

    #### UI 2 #### ################ ############################################### ################
    def conversational_ui (self):
        #Carga la interfaz desde el archivo .ui
        loader = QtUiTools.QUiLoader()
        file = QtCore.QFile("../../igs/conversacional_menu.ui")
        file.open(QtCore.QFile.ReadOnly)
        ui = loader.load(file)
        file.close()

        # Conectar botones a funciones
        ui.startGame.clicked.connect(self.startGame_clicked_conv)

        # Añadir opciones al ComboBox
        opciones = ["Seleccionar Personalidad...", "EBO_simpatico", "EBO_neutro", "EBO_pasional"]
        ui.comboBox.addItems(opciones)
        
        # Cerrar con la x
        if not hasattr(self, 'ui_numbers'):
            self.ui_numbers = {}
            
        self.ui_numbers[ui] = 2  
        ui.installEventFilter(self) 

        return ui

    def startGame_clicked_conv(self):
        self.setDatos()
        self.personalidad = self.ui2.comboBox.currentText()
        if not self.personalidad or self.personalidad == "Seleccionar Personalidad...":
            print("Por favor selecciona una personalidad.")
            return

        self.ui2.nombreE.clear()
        self.ui2.aficionE.clear()
        self.ui2.edadE.clear()
        self.ui2.famiE.clear()
        # self.ui2.startGame.setEnabled(False)

        print("Iniciando juego con los datos seleccionados")
        self.cerrar_ui(2)
        # SET GAME INFO
        self.gpt_proxy.setGameInfo(self.personalidad, self.user_info)
        self.lanzar_ui4()
        self.ui4.text_info.setText("EBO comenzará a hablar en breve")
        # START CHAT
        self.gpt_proxy.startChat()
        self.ui4.text_info.setText("Introduzca respuesta")

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



    #### UI 3 #### ################ ############################################### ################
    def storytelling_ui (self):
        #Carga la interfaz desde el archivo .ui
        loader = QtUiTools.QUiLoader()
        file = QtCore.QFile("../../igs/storytelling_menu.ui")
        file.open(QtCore.QFile.ReadOnly)
        ui = loader.load(file)
        file.close()

        # Conectar botones a funciones
        ui.startGame.clicked.connect(self.startGame_clicked)
        self.configure_combobox(ui, "../juegos_story")
        
        # Cerrar con la x
        if not hasattr(self, 'ui_numbers'):
            self.ui_numbers = {}
            
        self.ui_numbers[ui] = 3  
        ui.installEventFilter(self) 

        return ui

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

    def startGame_clicked(self):
        juego = self.ui3.comboBox.currentText()

        if not juego or juego == "Seleccionar juego...":
            print("Por favor selecciona un juego.")
            return

        self.nombre_jugador = self.ui3.nombreE.toPlainText()
        self.aficiones = self.ui3.aficionE.toPlainText()
        self.edad = self.ui3.edadE.toPlainText()
        self.familiares = self.ui3.famiE.toPlainText()
        
        folder_path = "../juegos_story"
        archivo_json = f"{juego}.json"
        self.archivo_path = os.path.join(folder_path, archivo_json)

        self.user_info = self.archivo_json_a_string(self.archivo_path)
        
        print("------------ JSON ENVIADO ---------------------------------")
        print(self.user_info)
        print("------------ JSON ENVIADO ---------------------------------")

        self.ui3.nombreE.clear()
        self.ui3.aficionE.clear()
        self.ui3.edadE.clear()
        self.ui3.famiE.clear()

        print("Iniciando juego con los datos seleccionados")
        self.cerrar_ui(3)
        # SET GAME INFO
        self.gpt_proxy.setGameInfo("StoryTelling", self.user_info)
        self.lanzar_ui4()
        self.ui4.text_info.setText("EBO comenzará a hablar en breve")
        # START CHAT
        self.gpt_proxy.startChat()
        self.ui4.text_info.setText("Introduzca respuesta")

    def setDatos_clicked(self):
        self.nombre_jugador = self.ui3.nombreE.toPlainText()
        self.aficiones = self.ui3.aficionE.toPlainText()
        self.edad = self.ui3.edadE.toPlainText()
        self.familiares = self.ui3.famiE.toPlainText()

        self.ui3.startGame.setEnabled(True)



    #### UI 4 #### ################ ############################################### ################
    def respuesta_ui (self):
        #Carga la interfaz desde el archivo .ui
        loader = QtUiTools.QUiLoader()
        file = QtCore.QFile("../../igs/respuesta_gpt.ui")
        file.open(QtCore.QFile.ReadOnly)
        ui = loader.load(file)
        file.close()

        # Conectar botones a funciones
        ui.enviar.clicked.connect(self.enviar_clicked)
        ui.salir.clicked.connect(self.salir_clicked)
        
        ui.respuesta.installEventFilter(self)
        
        # Cerrar con la x
        if not hasattr(self, 'ui_numbers'):
            self.ui_numbers = {}
            
        self.ui_numbers[ui] = 4  
        ui.installEventFilter(self) 

        return ui
    
    def enviar_clicked(self):
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
            self.reiniciar_variables()
            self.ui4.text_info.setText("Saliendo del programa...")
            QApplication.processEvents()
            self.cerrar_ui(4)
            self.gestorsg_proxy.LanzarApp()
            self.gpt_proxy.continueChat("03827857295769204")
        else:
            pass
        

    ################ ############################################### ################
    
    def eventFilter(self, obj, event):
        """ Captura eventos de la UI """
        
        # Manejar eventos de cierre de ventana
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
                    self.reiniciar_variables()
                    self.gestorsg_proxy.LanzarApp()
                    return False  # Permitir el cierre
                else:
                    print(f"Cierre de la ventana {ui_number} cancelado.")
                    event.ignore()  # Bloquear el cierre
                    return True  # Detener la propagación del evento

        # Manejar eventos de teclas en ui4.respuesta
        if hasattr(self, 'ui4') and obj == self.ui4.respuesta and event.type() == QtCore.QEvent.KeyPress:
            if event.key() in (Qt.Key_Return, Qt.Key_Enter):
                self.enviar_clicked()  # Llamar a la función enviar
                return True  # Indicar que el evento ha sido manejado

        return super().eventFilter(obj, event)  # Propagar otros eventos normalmente

    
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

    def lanzar_ui2(self):
        self.centrar_ventana(self.ui2)
        self.ui2.show()
        QApplication.processEvents()

    def lanzar_ui3(self):
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
    # From the RoboCompGPT you can call this methods:
    # self.gpt_proxy.continueChat(...)
    # self.gpt_proxy.setGameInfo(...)
    # self.gpt_proxy.startChat(...)

    ######################
    # From the RoboCompGestorSG you can call this methods:
    # self.gestorsg_proxy.LanzarApp(...)



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
