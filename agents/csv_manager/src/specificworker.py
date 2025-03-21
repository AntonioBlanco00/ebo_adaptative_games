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
from numba.core.typing.builtins import Print
from rich.console import Console
from genericworker import *
import interfaces as ifaces

sys.path.append('/opt/robocomp/lib')
console = Console(highlight=False)

from pydsr import *
import pandas as pd


# If RoboComp was compiled with Python bindings you can use InnerModel in Python
# import librobocomp_qmat
# import librobocomp_osgviewer
# import librobocomp_innermodel


class SpecificWorker(GenericWorker):
    def __init__(self, proxy_map, startup_check=False):
        super(SpecificWorker, self).__init__(proxy_map)
        self.Period = 2000

        # YOU MUST SET AN UNIQUE ID FOR THIS AGENT IN YOUR DEPLOYMENT. "_CHANGE_THIS_ID_" for a valid unique integer
        self.agent_id = 453
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

        self.atributos_a_verificar = ["nombre", "edad", "aficiones", "familiares", "st_jc", "pp_rc", "pp_nota", "ss_ru", "ss_du", "ss_au", "ss_fu", "ss_tu", "ss_nota", "num_partidas"]


    def recoger_info(self):
        node = self.g.get_node("CSV Manager")

        # Diccionario base con claves establecidas pero valores vacíos
        datos_nuevos = {
            'residencia': '',
            'edad': '',
            'aficiones': '',
            'familiares': '',
            'story_completados': '',
            'roscos_completados': '',
            'nota_psp': '',
            'rondas_ult': '',
            'intentos_ult': '',
            'dificultad_ult': '',
            'aciertos_ult': '',
            'fallos_ult': '',
            't_ult': '',
            'nota_sim': '',
            'num_partidas': ''
        }

        # Diccionario de mapeo para renombrar atributos
        renombrar_atributos = {
            "st_jc": "story_completados",
            "pp_rc": "roscos_completados",
            "pp_nota": "nota_psp",
            "ss_ru": "rondas_ult",
            "ss_du": "dificultad_ult",
            "ss_au": "aciertos_ult",
            "ss_fu": "fallos_ult",
            "ss_tu": "t_ult",
            "ss_nota": "nota_sim"
        }

        nombre = None  # Variable para el nombre

        for atributo in node.attrs:
            if atributo in self.atributos_a_verificar and node.attrs[atributo].value:
                valor = node.attrs[atributo].value  # Obtener el valor

                if atributo == "nombre":
                    nombre = valor  # Guardamos el nombre
                else:
                    # Si el atributo tiene un nombre mapeado, lo usamos
                    clave_final = renombrar_atributos.get(atributo, atributo)
                    datos_nuevos[clave_final] = valor  # Guardamos el valor con el nombre correcto


        # Si hay un nombre, actualizar CSV
        if nombre:
            self.actualizar_csv(nombre, datos_nuevos)
            print("DATOS ACTUALIZADOS")

        # Volvemos a poner a False la flag para actualizar la info
        self.vaciar_atributos()

    def vaciar_atributos(self):
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

    def actualizar_csv(self, nombre, datos_nuevos):
        # Leer el archivo CSV en un DataFrame
        df = pd.read_csv(self.archivo_csv, sep=";")

        if nombre in df['nombre'].values:
            for clave, valor in datos_nuevos.items():
                if valor != "":  # Solo actualizar si el valor no es una cadena vacía
                    df.loc[df['nombre'] == nombre, clave] = valor
        else:
            # Eliminar claves con valores vacíos antes de agregar una nueva fila
            datos_nuevos = {k: v for k, v in datos_nuevos.items() if v != ""}
            nueva_fila = {**{'nombre': nombre}, **datos_nuevos}
            nueva_fila_df = pd.DataFrame([nueva_fila])  # Convertir la nueva fila en un DataFrame
            df = pd.concat([df, nueva_fila_df], ignore_index=True)  # Usar concat para agregar la fila

        # Guardar los cambios en el archivo CSV
        df.to_csv(self.archivo_csv, sep=";", index=False)

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
        # computeCODE
        # try:
        #   self.differentialrobot_proxy.setSpeedBase(100, 0)
        # except Ice.Exception as e:
        #   traceback.print_exc()
        #   print(e)

        # The API of python-innermodel is not exactly the same as the C++ version
        # self.innermodel.updateTransformValues('head_rot_tilt_pose', 0, 0, 0, 1.3, 0, 0)
        # z = librobocomp_qmat.QVec(3,0)
        # r = self.innermodel.transform('rgbd', z, 'laser')
        # r.printvector('d')
        # print(r[0], r[1], r[2])

        return True

    def startup_check(self):
        QTimer.singleShot(200, QApplication.instance().quit)






    # =============== DSR SLOTS  ================
    # =============================================

    def update_node_att(self, id: int, attribute_names: [str]):
        # console.print(f"UPDATE NODE ATT: {id} {attribute_names}", style='green')
        node = self.g.get_node("CSV Manager")
        if node.attrs["actualizar_info"].value is 1:
            self.recoger_info()
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
