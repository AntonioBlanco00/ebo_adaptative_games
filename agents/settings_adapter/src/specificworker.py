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
from rich.console import Console
from genericworker import *
import interfaces as ifaces
import time

import pandas as pd

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
        self.agent_id = 600
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

        self.archivo_csv = "../../users_info.csv"

        self.nombre = None
        self.edad = None
        self.aficiones = None
        self.familiares = None
        self.story_completados = None
        self.roscos_completados = None
        self.nota_psp = None
        self.rondas_ult = None
        self.intentos_ult = None
        self.dificultad_ult = None
        self.aciertos_ult = None
        self.fallos_ult = None
        self.t_ult = None
        self.nota_sim = None
        self.ss_du = None
        self.ss_nota = None

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

    def startup_check(self):
        QTimer.singleShot(200, QApplication.instance().quit)

    def obtener_datos(self):
        df = pd.read_csv(self.archivo_csv, sep=';')

        node = self.g.get_node("CSV Manager")

        nombre_buscar = node.attrs["nombre"].value

        resultado = df[df['nombre'] == nombre_buscar]

        if not resultado.empty:
            # Asignar los valores de cada columna a atributos de la clase (self), solo si no están vacíos
            if pd.notna(resultado['nombre'].iloc[0]):
                self.nombre = resultado['nombre'].iloc[0]
            if pd.notna(resultado['edad'].iloc[0]):
                self.edad = resultado['edad'].iloc[0]
            if pd.notna(resultado['aficiones'].iloc[0]):
                self.aficiones = resultado['aficiones'].iloc[0]
            if pd.notna(resultado['familiares'].iloc[0]):
                self.familiares = resultado['familiares'].iloc[0]
            if pd.notna(resultado['story_completados'].iloc[0]):
                self.story_completados = resultado['story_completados'].iloc[0]
            if pd.notna(resultado['roscos_completados'].iloc[0]):
                self.roscos_completados = resultado['roscos_completados'].iloc[0]
            if pd.notna(resultado['nota_psp'].iloc[0]):
                self.nota_psp = resultado['nota_psp'].iloc[0]
            if pd.notna(resultado['rondas_ult'].iloc[0]):
                self.rondas_ult = resultado['rondas_ult'].iloc[0]
            if pd.notna(resultado['intentos_ult'].iloc[0]):
                self.intentos_ult = resultado['intentos_ult'].iloc[0]
            if pd.notna(resultado['dificultad_ult'].iloc[0]):
                self.dificultad_ult = resultado['dificultad_ult'].iloc[0]
            if pd.notna(resultado['aciertos_ult'].iloc[0]):
                self.aciertos_ult = resultado['aciertos_ult'].iloc[0]
            if pd.notna(resultado['fallos_ult'].iloc[0]):
                self.fallos_ult = resultado['fallos_ult'].iloc[0]
            if pd.notna(resultado['t_ult'].iloc[0]):
                self.t_ult = resultado['t_ult'].iloc[0]
            if pd.notna(resultado['nota_sim'].iloc[0]):
                self.nota_sim = resultado['nota_sim'].iloc[0]
            if pd.notna(resultado['ss_du'].iloc[0]):
                self.ss_du = resultado['ss_du'].iloc[0]
            if pd.notna(resultado['ss_nota'].iloc[0]):
                self.ss_nota = resultado['ss_nota'].iloc[0]

        else:
            print("No se encontraron datos para los criterios proporcionados.")

        pass

    def change_info(self):
        node_game = self.g.get_node("Actual Game")
        game = node_game.attrs["actual_game"].value
        self.obtener_datos()

        if game == "Storytelling":
            print("Cargando info para Storytelling")
            self.update_storytelling()

        elif game == "Conversation":
            print("Cargando info para Conversation")
            self.update_conversation()

        elif game == "Simon Say":
            print("Cargando info para Simon Say")

        elif game == "Pasapalabra":
            print("Cargando info para Pasapalabra")

    def update_storytelling(self):
        node = self.g.get_node("CSV Manager")
        node.attrs["nombre"].value = self.nombre
        node.attrs["edad"].value = str(self.edad)
        node.attrs["aficiones"].value = self.aficiones
        node.attrs["familiares"].value = self.familiares
        node.attrs["st_jc"].value = self.story_completados
        self.vaciar_variables()
        self.g.update_node(node)

    def update_conversation(self):
        node = self.g.get_node("CSV Manager")
        node.attrs["nombre"].value = self.nombre
        node.attrs["edad"].value = str(self.edad)
        node.attrs["aficiones"].value = self.aficiones
        node.attrs["familiares"].value = self.familiares
        self.vaciar_variables()
        self.g.update_node(node)

    def vaciar_variables(self):
        self.nombre = None
        self.edad = None
        self.aficiones = None
        self.familiares = None
        self.story_completados = None
        self.roscos_completados = None
        self.nota_psp = None
        self.rondas_ult = None
        self.intentos_ult = None
        self.dificultad_ult = None
        self.aciertos_ult = None
        self.fallos_ult = None
        self.t_ult = None
        self.nota_sim = None
        self.ss_du = None
        self.ss_nota = None

    def return_to_false(self):
        node = self.g.get_node("Settings Adapter")
        node.attrs["set_info"].value = False
        self.g.update_node(node)

    # =============== DSR SLOTS  ================
    # =============================================

    def update_node_att(self, id: int, attribute_names: [str]):
        # console.print(f"UPDATE NODE ATT: {id} {attribute_names}", style='green')
        node = self.g.get_node("Settings Adapter")
        if node.attrs["set_info"].value is 1:
            self.return_to_false()
            self.change_info()
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
