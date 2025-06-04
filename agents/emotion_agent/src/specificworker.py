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

sys.path.append('/opt/robocomp/lib')
console = Console(highlight=False)

from pydsr import *

import time
from time import sleep
from PIL import Image
import io
from deepface import DeepFace
import os
import pandas as pd
import numpy as np

# If RoboComp was compiled with Python bindings you can use InnerModel in Python
# import librobocomp_qmat
# import librobocomp_osgviewer
# import librobocomp_innermodel


class SpecificWorker(GenericWorker):
    def __init__(self, proxy_map, startup_check=False):
        super(SpecificWorker, self).__init__(proxy_map)
        self.Period = 5000

        # YOU MUST SET AN UNIQUE ID FOR THIS AGENT IN YOUR DEPLOYMENT. "_CHANGE_THIS_ID_" for a valid unique integer
        self.agent_id = 23
        self.g = DSRGraph(0, "pythonAgent", self.agent_id)

        self.emocion = "neutral"

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

    def __del__(self):
        """Destructor"""

    def setParams(self, params):
        # try:
        #	self.innermodel = InnerModel(params["InnerModelPath"])
        # except:
        #	traceback.print_exc()
        #	print("Error reading config params")
        return True

    def mimica(self):
        # Capturamos la imagen de la cámara
        y = self.camerasimple_proxy.getImage()
        imagen = Image.frombytes("RGB", (y.width, y.height), bytes(y.image))

        # Convertimos la imagen: intercambiamos el orden de los canales (de RGB a BGR)
        r, g, b = imagen.split()
        imagen = Image.merge("RGB", (b, g, r))

        # Convertimos la imagen PIL a un array de NumPy para evitar guardar la imagen en disco
        import numpy as np
        imagen_np = np.array(imagen)

        error_detected = False
        # Intentamos analizar las emociones directamente desde el array
        try:
            resultados = DeepFace.analyze(img_path=imagen_np, actions=['emotion'])
            if isinstance(resultados, list):
                resultados = resultados[0]
        except Exception as e:
            print("Error en el análisis de emociones:", e)
            # Si ocurre un error (por ejemplo, no se detecta una cara), asignamos directamente resultados neutrales
            resultados = {
                'emotion': {'neutral': 100, 'angry': 0, 'disgust': 0, 'fear': 0, 'happy': 0, 'sad': 0, 'surprise': 0}
            }
            error_detected = True

        # Extraemos las emociones detectadas y las mostramos en un DataFrame
        emociones = resultados['emotion']
        df_emociones = pd.DataFrame(emociones.items(), columns=['Emoción', 'Probabilidad'])
        print("\n\n\n", df_emociones, "\n")

        # Si se produjo un error, se asigna "neutral" directamente; de lo contrario se devuelve la emoción principal detectada.
        if error_detected:
            emocion_principal = "neutral"
        else:
            emocion_principal = max(emociones, key=emociones.get)

        print("Emoción principal:", emocion_principal, "\n\n")

        return emocion_principal

    @QtCore.Slot()
    def compute(self):

        emocion = self.mimica()
        print("EMOCION:", emocion)
        if emocion != self.emocion:
            print("Cambio detectado, actualizando DSR")
            print("-----------------------------------------")
            self.emocion = emocion
            self.actualizar_dsr()





        return True

    def actualizar_dsr(self):
        node = self.g.get_node("Realtime Adapter")
        node.attrs["emotion"] = Attribute(self.emocion, self.agent_id)
        self.g.update_node(node)
        pass

    def startup_check(self):
        print(f"Testing RoboCompCameraSimple.TImage from ifaces.RoboCompCameraSimple")
        test = ifaces.RoboCompCameraSimple.TImage()
        QTimer.singleShot(200, QApplication.instance().quit)




    ######################
    # From the RoboCompCameraSimple you can call this methods:
    # self.camerasimple_proxy.getImage(...)

    ######################
    # From the RoboCompCameraSimple you can use this types:
    # RoboCompCameraSimple.TImage



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
