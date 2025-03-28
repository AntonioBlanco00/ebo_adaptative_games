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
import math

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
        self.nota_sim = 1000
        self.ss_du = None
        self.ss_nota = 1000
        self.num_partidas = None

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
            if pd.notna(resultado['num_partidas'].iloc[0]):
                self.num_partidas = resultado['num_partidas'].iloc[0]

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
            self.update_simonsay()

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

    def update_simonsay(self):
        # Aqui se determinan rondas y nota(tiempos) que se van a usar.
        node = self.g.get_node("Simon Say")
        nota = self.nota_sim
        print("-------------------------")
        print(nota)
        print("--------------------------------")
        # 1) Rondas base según nota:  R_base = R̃(nota)
        if nota < 700:
            R_base = 3
            dificultad_asignada = "Muy fácil"
            v_off_asignada = 1
            v_on_asignada = 4

        elif nota < 900:
            R_base = 4
            dificultad_asignada = "Fácil"
            v_off_asignada = 1
            v_on_asignada = 3

        elif nota < 1100:
            R_base = 5
            dificultad_asignada = "Intermedio bajo"
            v_off_asignada = 1
            v_on_asignada = 2

        elif nota < 1300:
            R_base = 7
            dificultad_asignada = "Intermedio"
            v_off_asignada = 0.5
            v_on_asignada = 1

        elif nota < 1500:
            R_base = 10
            dificultad_asignada = "Intermedio alto"
            v_off_asignada = 0.25
            v_on_asignada = 0.5

        elif nota < 1700:
            R_base = 12
            dificultad_asignada = "Difícil"
            v_off_asignada = 0.15
            v_on_asignada = 0.25

        else:
            R_base = 15
            dificultad_asignada = "Extremo"
            v_off_asignada = 0.05
            v_on_asignada = 0.1

        proporcion = 0.0
        if self.rondas_ult > 0:
            proporcion = self.aciertos_ult / self.rondas_ult

        # --- 3) Ajuste por porcentaje de aciertos ---
        ajuste_aciertos = 0
        if self.aciertos_ult == self.rondas_ult:  # Ha completado TODAS las rondas
            if self.fallos_ult == 0:
                ajuste_aciertos = 2
            else:
                ajuste_aciertos = 1
        else:
            if proporcion >= 0.75:
                ajuste_aciertos = 0
            else:
                ajuste_aciertos = -1

        # --- 4) Ajuste por tiempo medio de respuesta ---
        ajuste_tiempo = 0
        if self.t_ult < 4.0:
            ajuste_tiempo = 1
        elif self.t_ult > 10.0:
            ajuste_tiempo = -1
        # Entre 4 y 10 => no hay ajuste (0)

        # Sumamos todos los ajustes a partir de R_ult
        if self.aciertos_ult < R_base:
            rondas = R_base
        else:
            rondas = self.aciertos_ult

        R_adjusted = rondas + ajuste_aciertos + ajuste_tiempo

        print(f"Ajuste por aciertos: {ajuste_aciertos}, Ajuste por tiempo: {ajuste_tiempo}")
        print(f"R_ult + ajustes = {R_adjusted}")

        # --- 5) hacemos la media aritmética entre R_base y R_adjusted
        R_temp = (R_base + R_adjusted) / 2.0
        print(f"R_temp (media de R_base y R_adjusted): {R_temp}")

        # LOGICA FINAL DE RONDAS:
        #  - Si nota >= 1700 (Extremo): si R_adjusted > R_base => R_final=R_adjusted, si no => R_final=R_base
        #  - En caso contrario, usamos la lógica previa de redondeo

        if nota >= 1700:
            # Nivel extremo
            if self.aciertos_ult > R_base:
                R_final = R_adjusted
                print("Nivel Extremo: R_adjusted > R_base -> tomamos R_adjusted")
            else:
                R_final = R_base + ajuste_aciertos + ajuste_tiempo
                print("Nivel Extremo: R_adjusted <= R_base -> tomamos R_base + ajuste_aciertos + ajuste_tiempo")
        else:
            # Niveles inferiores: lógica de redondeo
            if R_base == self.rondas_ult:
                # Si R_base == R_ult => No redondeamos, usamos R_adjusted directamente
                R_final = R_adjusted
                print(f"R_base == R_ult -> R_final = {R_final}")
            else:
                # Redondeo al alza
                R_final = math.ceil(R_temp)
                print(f"R_base != R_ult -> redondeo al alza: R_final = {R_final}")

        # Forzar un mínimo de 3 rondas
        if R_final < 3:
            R_final = 3

        print(f"R_final tras mínimo de 3: {R_final}")
        print("------------------------------------------")

        node.attrs["nombre"].value = self.nombre
        node.attrs["nota"].value = str(self.nota_sim)
        node.attrs["num_partidas"].value = str(self.num_partidas)
        node.attrs["dificultad"].value = dificultad_asignada
        node.attrs["rondas"].value = str(R_final)
        node.attrs["v_off"].value = str(v_off_asignada)
        node.attrs["v_on"].value = str(v_on_asignada)

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
        self.nota_sim = 1000
        self.ss_du = None
        self.ss_nota = 1000
        self.num_partidas = None

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
