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
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QApplication
from PySide6 import QtUiTools
from rich.console import Console
from genericworker import *
from time import sleep
import interfaces as ifaces
import subprocess

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
        self.agent_id = 450
        self.g = DSRGraph(0, "pythonAgent", self.agent_id)

        try:
            signals.connect(self.g, signals.UPDATE_NODE_ATTR, self.update_node_att)
            signals.connect(self.g, signals.UPDATE_NODE, self.update_node)
            signals.connect(self.g, signals.DELETE_NODE, self.delete_node)
            signals.connect(self.g, signals.UPDATE_EDGE, self.update_edge)
            signals.connect(self.g, signals.UPDATE_EDGE_ATTR, self.update_edge_att)
            signals.connect(self.g, signals.DELETE_EDGE, self.delete_edge)
            console.print("signals connected")
        except RuntimeError as e:
            print(e)

        if startup_check:
            self.startup_check()
        else:
            self.timer.timeout.connect(self.compute)
            self.timer.start(self.Period)

        self.ui = self.v_principal()

        self.juego_seleccionado = False

        self.ultimo_estado = None

        self.GestorSG_LanzarApp()


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
        # Verificamos el estado actual y lo comparamos con el último impreso
        if self.juego_seleccionado is False and self.ui.isVisible() is False:
            # self.GestorSG_LanzarApp()
            estado_actual = "Relanzando APP"
        elif self.juego_seleccionado is True and self.ui.isVisible() is False:
            estado_actual = "Juego en Curso"
        else:
            estado_actual = "Juego en selección"

        # Si el estado actual es diferente al último impreso, imprimimos
        if estado_actual != self.ultimo_estado:
            if self.ultimo_estado is not None:  # No imprimir línea si es el primer estado
                print("------------------------------")
            print(estado_actual)
            self.ultimo_estado = estado_actual  # Actualizamos el último estado

        return True

    def startup_check(self):
        QTimer.singleShot(200, QApplication.instance().quit)

    ######## INTERFAZ GRÁFICA ################

    def v_principal (self):
        #Cargar interfaz
        loader = QtUiTools.QUiLoader()
        file = QtCore.QFile("../../igs/app_juegos.ui")
        file.open(QtCore.QFile.ReadOnly)
        ui = loader.load(file)
        file.close()
	
	    # Asignar las imágenes a los QLabel después de cargar la UI
        ui.label.setPixmap(QPixmap("../../igs/logos/logo_euro.png"))
        ui.label.setScaledContents(True)  # Asegúrate de que la imagen se ajuste al QLabel

        ui.label_2.setPixmap(QPixmap("../../igs/logos/robolab.png"))
        ui.label_2.setScaledContents(True)  # Ajusta la imagen a los límites del QLabel


        ui.story_button.clicked.connect(self.story_clicked)
        ui.simon_button.clicked.connect(self.simon_clicked)
        ui.pasapalabra_button.clicked.connect(self.pasapalabra_clicked)
        
        # Asegurar que el diccionario de UIs existe
        if not hasattr(self, 'ui_numbers'):
            self.ui_numbers = {}
            
        self.ui_numbers[ui] = 1  
        ui.installEventFilter(self) 

        return ui


    def story_clicked(self):
        self.ui.removeEventFilter(self) # Desactivamos y activamos el eventfilter antes y despues de cerrar la ventana para que no se raye
        self.ui.close()
        self.ui.installEventFilter(self)
        
        self.juego_seleccionado = True
        self.storytelling_proxy.StartGame()



    def simon_clicked(self):
        self.ui.removeEventFilter(self)
        self.ui.close()
        self.ui.installEventFilter(self)
        
        self.juego_seleccionado = True
        self.juegosimonsay_proxy.StartGame()



    def pasapalabra_clicked(self):
        self.ui.removeEventFilter(self)
        self.ui.close()
        self.ui.installEventFilter(self)
        
        self.juego_seleccionado = True
        self.pasapalabra_proxy.StartGame()

    
    ####################################################################################################################################
    
    def eventFilter(self, obj, event):
        """ Captura eventos de la UI """
        
        # Obtener el número de UI asociado al objeto
        ui_number = self.ui_numbers.get(obj, None)

        if ui_number is not None and event.type() == QtCore.QEvent.Close:
            target_ui = self.ui if ui_number == 1 else getattr(self, f'ui{ui_number}', None)
            
            if obj == target_ui:
                respuesta = QMessageBox.question(
                    target_ui, "Cerrar", f"¿Estás seguro de que quieres cerrar los juegos?",
                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No
                )
                if respuesta == QMessageBox.Yes:
                    print(f"Ventana {ui_number} cerrada por el usuario.")
                    subprocess.run(["python3", "../reiniciar.py"])
                    return False  # Permitir el cierre
                else:
                    print(f"Cierre de la ventana {ui_number} cancelado.")
                    event.ignore()  # Bloquear el cierre
                    return True  # **DETENER la propagación del evento para que no se cierre**

        return False  # Propaga otros eventos normalmente


    ####################################################################################################################################

    # =============== Methods for Component Implements ==================
    # ===================================================================

    #
    # IMPLEMENTATION of LanzarApp method from GestorSG interface
    #
    def GestorSG_LanzarApp(self):
        self.juego_seleccionado = False
        self.centrar_ventana(self.ui)
        self.ui.show()
        QApplication.processEvents()
        pass



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
    # ===================================================================
    # ===================================================================


    ######################
    # From the RoboCompJuegoSimonSay you can call this methods:
    # self.juegosimonsay_proxy.StartGame(...)

    ######################
    # From the RoboCompPasapalabra you can call this methods:
    # self.pasapalabra_proxy.StartGame(...)

    ######################
    # From the RoboCompStoryTelling you can call this methods:
    # self.storytelling_proxy.StartGame(...)



    # =============== DSR SLOTS  ================
    # =============================================

    def update_node_att(self, id: int, attribute_names: [str]):
        console.print(f"UPDATE NODE ATT: {id} {attribute_names}", style='green')

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
