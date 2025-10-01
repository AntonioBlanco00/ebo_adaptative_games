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

sys.path.append('/opt/robocomp/lib')
console = Console(highlight=False)

from pydsr import *
from openai import OpenAI
from dotenv import find_dotenv, load_dotenv
import time
import logging
from datetime import datetime
import os
import sys
import threading
import re

# If RoboComp was compiled with Python bindings you can use InnerModel in Python
# import librobocomp_qmat
# import librobocomp_osgviewer
# import librobocomp_innermodel


class SpecificWorker(GenericWorker):
    def __init__(self, proxy_map, startup_check=False):
        super(SpecificWorker, self).__init__(proxy_map)
        self.Period = 2000

        # YOU MUST SET AN UNIQUE ID FOR THIS AGENT IN YOUR DEPLOYMENT. "_CHANGE_THIS_ID_" for a valid unique integer
        self.agent_id = 451
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

        load_dotenv()

        self.client = OpenAI()
        self.history = []  # memoria de turnos (user/assistant)
        self.model_fast = os.getenv("OPENAI_FAST_MODEL", "gpt-4o-mini")  # Fase A
        self.model_full = os.getenv("OPENAI_FULL_MODEL", "gpt-4o-mini")  # Fase B
        self.phase_a_params = {"temperature": 0.2, "max_tokens": 24}
        self.phase_b_params = {"temperature": 0.6, "max_tokens": 800}

        self.conversacion_en_curso = False
        self.asisstantName  = ""
        self.userInfo = ""
        self.NUM_LEDS = 54
        self.effect_event = threading.Event()
        self.effect_thread = None  # Variable para almacenar el hilo del efecto

        self._turn_t0 = None
        self._first_speak_ts = None
        self._tts_started = False

    def __del__(self):
        """Destructor"""

    def setParams(self, params):
        # try:

        return True

    def _speak(self, text: str):
        if text and text.strip():
            # Parar el spinner SOLO la primera vez que vamos a hablar en el turno
            try:
                if not self._tts_started and self.effect_thread is not None and self.effect_thread.is_alive():
                    self.stop_rotating_effect()
                    self._tts_started = True
            except Exception:
                pass

            # TTPA: registra la primera vez que hablamos
            if self._first_speak_ts is None and self._turn_t0 is not None:
                self._first_speak_ts = time.perf_counter()
                ttpa = self._first_speak_ts - self._turn_t0
                print(f"[TTPA] Tiempo hasta primer audio: {ttpa:.3f} s")

            # Ahora habla
            self.speech_proxy.say(text.strip(), False)

    def _emit_sentences_progressively(self, buffer: str) -> str:
        parts = re.split(r'(?<=[\.\?\!])\s+', buffer)
        for sent in parts[:-1]:
            if sent.strip():
                self._speak(sent.strip())
        return parts[-1] if parts else ""

    def llm_stream_reply_single_message(self, user_text: str) -> str:
        """
        UNA sola llamada con streaming.
        - Arranca con frase breve (≤12 palabras) y sigue sin repetirla.
        - Emite oraciones completas en cuanto cierran.
        - Al final, extrae la emoción una ÚNICA VEZ del remanente final,
          no la pronuncia, la guarda en self._last_emotion y devuelve el texto limpio.
        """
        # Limpia estado de emoción al iniciar turno
        self._last_emotion = ""

        runtime_system = (
            "Empieza con una frase breve (≤12 palabras) que confirme o resuma la intención, "
            "y continúa de inmediato con los detalles SIN repetir esa primera frase. "
            "Finaliza SIEMPRE con una sola palabra en minúsculas elegida de {asco, contento, triste, enfado, miedo, sorpresa}. "
            "No añadas signos de puntuación tras la emoción ni más palabras."
        )

        inputs = [
            *self.history,
            {"role": "system", "content": runtime_system},
            {"role": "user", "content": user_text},
        ]

        # Acumulamos lo hablado (sin emoción) y el remanente
        spoken_parts: list[str] = []
        remnant = ""
        first_chunk_spoken = False
        words_threshold = 12
        t_first_token = None

        try:
            with self.client.responses.stream(
                    model=self.model_full,
                    input=inputs,
                    temperature=self.phase_b_params.get("temperature", 0.6),
                    max_output_tokens=self.phase_b_params.get("max_tokens", 800),
            ) as stream:
                for event in stream:
                    if event.type == "response.output_text.delta":
                        if t_first_token is None and self._turn_t0 is not None:
                            t_first_token = time.perf_counter()
                            print(f"[LLM] Tiempo hasta primer token: {t_first_token - self._turn_t0:.3f} s")

                        delta = getattr(event, "delta", None)
                        if not isinstance(delta, str):
                            delta = getattr(getattr(event, "output_text", None), "delta", "")
                        if not delta:
                            continue

                        remnant += delta

                        # Disparo de arranque: primera oración cerrada o ≥ N palabras
                        if not first_chunk_spoken:
                            parts = re.split(r'(?<=[\.\?\!])\s+', remnant)
                            if len(parts) > 1 and parts[0].strip():
                                first = parts[0].strip()
                                self._speak(first)
                                spoken_parts.append(first)
                                first_chunk_spoken = True
                                remnant = " ".join(parts[1:])
                                continue
                            if len(remnant.strip().split()) >= words_threshold:
                                early = remnant.strip()
                                self._speak(early)
                                spoken_parts.append(early)
                                first_chunk_spoken = True
                                remnant = ""
                                continue

                        # Después del arranque: emitir oraciones completas
                        if first_chunk_spoken:
                            parts = re.split(r'(?<=[\.\?\!])\s+', remnant)
                            for sent in parts[:-1]:
                                s = sent.strip()
                                if s:
                                    self._speak(s)
                                    spoken_parts.append(s)
                            remnant = parts[-1] if parts else ""

                    elif event.type == "response.error":
                        print("LLM stream error:", getattr(event, "error", "unknown"))
                    elif event.type == "response.completed":
                        break

            # === ÚNICO sitio donde extraemos la emoción ===
            # No pronunciamos el remanente sin limpiar; primero quitamos la emoción.
            tail_clean, emo = self._strip_trailing_emotion(remnant)
            self._last_emotion = emo  # emoción disponible para quien la necesite

            if tail_clean.strip():
                self._speak(tail_clean.strip())
                spoken_parts.append(tail_clean.strip())

        except Exception as e:
            print("Stream error:", e)

        # Texto final limpio (sin emoción) = lo ya hablado + cola limpia
        assistant_text = " ".join(spoken_parts).strip()

        # Guarda al historial (sin emoción)
        self.history.append({"role": "user", "content": user_text})
        self.history.append({"role": "assistant", "content": assistant_text})

        return assistant_text

    def set_all_LEDS_colors(self, red=0, green=0, blue=0, white=0):
        pixel_array = {i: ifaces.RoboCompLEDArray.Pixel(red=red, green=green, blue=blue, white=white) for i in
                       range(self.NUM_LEDS)}
        self.ledarray_proxy.setLEDArray(pixel_array)

    def rotating_turquoise_leds(self, delay=0.01, group_size=13):
        """
        Hace que los LEDs se enciendan en turquesa en grupos, simulando un movimiento circular.
        :param delay: Tiempo en segundos entre cada cambio de grupo.
        :param group_size: Tamaño del grupo de LEDs que se encienden juntos.
        """
        print("--------------------------------------")
        try:
            while not self.effect_event.is_set():  # El hilo sigue mientras el evento no está activado
                for i in range(self.NUM_LEDS):
                    if self.effect_event.is_set():  # Si el evento se activa, salimos del bucle
                        break
                    # Crear un array de píxeles donde un grupo de LEDs esté encendido
                    pixel_array = {
                        j: ifaces.RoboCompLEDArray.Pixel(
                            red=64 if i <= j < i + group_size else 0,
                            green=224 if i <= j < i + group_size else 0,
                            blue=208 if i <= j < i + group_size else 0,
                            white=0
                        )
                        for j in range(self.NUM_LEDS)
                    }
                    self.ledarray_proxy.setLEDArray(pixel_array)
                    time.sleep(delay)  # Esperar un poco antes de pasar al siguiente grupo
        except Exception as e:
            print(f"Error en la ejecución del efecto: {e}")
        finally:
            # Apagar los LEDs después de detener el efecto
            self.set_all_LEDS_colors(0, 0, 0, 0)

    def start_rotating_effect(self, delay=0.01, group_size=13):
        """
        Inicia el efecto de LEDs rotatorios en un hilo separado.
        """
        if self.effect_thread is None or not self.effect_thread.is_alive():  # Solo iniciar si no hay un hilo en ejecución
            self.effect_event.clear()  # Restablecer el evento para continuar el efecto
            self.effect_thread = threading.Thread(target=self.rotating_turquoise_leds, args=(delay, group_size), daemon=True)
            self.effect_thread.start()

    def stop_rotating_effect(self):
        """
        Detiene el efecto de LEDs.
        """
        if self.effect_thread is not None:
            self.effect_event.set()  # Activar el evento para detener el efecto
            self.effect_thread.join()  # Esperar a que el hilo termine correctamente
            print("Efecto detenido")

    @QtCore.Slot()
    def compute(self):
        # print("MIAU")
        return True

    def startup_check(self):
        QTimer.singleShot(200, QApplication.instance().quit)

    def _assistant_name(self) -> str:
        name = getattr(self, "asisstantName", "") or getattr(self, "assistantName", "")
        return (name or "EBO").strip()

    def _ebo_repo_root(self):
        env = os.getenv("EBO_ROOT")
        if env and os.path.isdir(env):
            print(f"[PATH] EBO_ROOT={env}")
            return os.path.abspath(env)

        here = os.path.abspath(__file__)
        cur = os.path.dirname(here)
        for _ in range(14):
            if os.path.isdir(os.path.join(cur, "agents", "ebo_gpt", "profiles")):
                print(f"[PATH] Repo root autodetectado: {cur}")
                return cur
            if os.path.basename(cur).lower() == "ebo_adaptive_games":
                print(f"[PATH] Repo root por nombre de carpeta: {cur}")
                return cur
            parent = os.path.dirname(cur)
            if parent == cur:
                break
            cur = parent

        fallback = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        print(f"[PATH][WARN] No se detectó repo root. Fallback: {fallback}")
        return fallback

    def _resolve_prompt_path(self, name: str, index_rel: str = 'src/assistants.txt') -> str | None:
        keys = {name, name.replace(" ", "_"), name.replace("_", " ")}
        repo_root = self._ebo_repo_root()
        agents_root = os.path.join(repo_root, "agents", "ebo_gpt")
        profiles_root = os.path.join(agents_root, "profiles")

        # Candidatos de índice (probamos varios sitios razonables)
        index_candidates = [
            os.path.join(agents_root, "src", "assistants.txt"),  # esperado
            os.path.join(os.path.dirname(__file__), "src", "assistants.txt"),
            os.path.join(os.path.dirname(__file__), "assistants.txt"),
            os.path.join(profiles_root, "assistants.txt"),  # por si acaso
        ]

        tried = []
        for idx in index_candidates:
            tried.append(idx)
            if not os.path.exists(idx):
                continue

            print(f"[LLM] Leyendo índice: {idx}")
            try:
                with open(idx, 'r', encoding='utf-8') as f:
                    for raw in f:
                        line = raw.strip()
                        if not line or ';' not in line or line.startswith('#'):
                            continue
                        stored_name, stored_value = line.split(';', 1)
                        if stored_name not in keys:
                            continue

                        p = stored_value.strip()

                        # 1) Ruta absoluta
                        if os.path.isabs(p) and os.path.exists(p):
                            print(f"[LLM] Prompt ABS encontrado (directo): {p}")
                            return p

                        # 2) Prefijo 'profiles/' bajo agents_root
                        if p.startswith(("profiles/", "profiles\\")):
                            cand = os.path.join(agents_root, p)
                            if os.path.exists(cand):
                                print(f"[LLM] Prompt encontrado (profiles/ bajo agents): {cand}")
                                return cand

                        # 3) Relativa al directorio del índice
                        cand2 = os.path.join(os.path.dirname(idx), p)
                        if os.path.exists(cand2):
                            print(f"[LLM] Prompt encontrado (relativo al índice): {cand2}")
                            return cand2

                        # 4) Solo nombre de archivo -> buscar en profiles_root
                        cand3 = os.path.join(profiles_root, os.path.basename(p))
                        if os.path.exists(cand3):
                            print(f"[LLM] Prompt encontrado (en profiles_root): {cand3}")
                            return cand3

                        print(f"[LLM][WARN] Entrada coincide '{stored_name}' pero no existe ruta: {p}")
            except Exception as e:
                print(f"[LLM][ERR] No se pudo leer {idx}: {e}")

        print(f"[LLM][ERR] No se encontró prompt para '{name}'. Índices probados:")
        for p in tried:
            print(f"  - {p}  {'OK' if os.path.exists(p) else 'NO'}")
        print(f"[LLM][HINT] Confirma que existe: {os.path.join(agents_root, 'src', 'assistants.txt')}")
        print(f"[LLM][HINT] Y que las líneas son tipo: Nombre;profiles/Nombre.prompt.txt")
        return None

    def _load_system_prompt_and_params(self, name: str):
        """
        Lee el archivo .prompt.txt:
          - Cabecera opcional con líneas '# clave: valor'
          - Prompt (lo demás)
        Devuelve (system_prompt:str, cfg:dict) donde cfg puede tener:
          fast_model, full_model, temp_a, temp_b, max_tokens_a, max_tokens_b
        """
        cfg = {}
        path = self._resolve_prompt_path(name)
        print(f"[LLM] Prompt cargado: {path}")
        if path and os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                lines = f.read().splitlines()
            body = []
            for line in lines:
                m = re.match(r'\s*#\s*(fast_model|full_model|temp_a|temp_b|max_tokens_a|max_tokens_b)\s*:\s*(.+)\s*$',
                             line)
                if m:
                    k, v = m.groups()
                    v = v.strip()
                    if k in ("temp_a", "temp_b"):
                        try:
                            v = float(v)
                        except:
                            pass
                    elif k in ("max_tokens_a", "max_tokens_b"):
                        try:
                            v = int(v)
                        except:
                            pass
                    cfg[k] = v
                else:
                    body.append(line)
            system_prompt = ("\n".join(body)).strip()
        else:
            # Si no hay archivo, usa un prompt mínimo
            system_prompt = f"Eres {name}, un asistente útil. Responde claro y con pasos concretos."
        return system_prompt, cfg

    def guardar_chat_history(self, folder="conversaciones", filename_prefix="chat"):
        """
        Guarda el contenido de self.history en un archivo local legible.
        """
        try:
            os.makedirs(folder, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{filename_prefix}_{timestamp}.txt"
            filepath = os.path.join(folder, filename)

            def fmt(msg):
                role = msg.get("role", "?").capitalize()
                content = msg.get("content", "")
                return f"{role}: {content}"

            with open(filepath, "w", encoding="utf-8") as f:
                f.write("--- Conversación completa ---\n")
                for m in self.history:
                    f.write(fmt(m) + "\n")
                f.write("--- Fin de la conversación ---\n")

            print(f"Conversación guardada en: {filepath}")
        except Exception as e:
            print(f"Error al guardar el chat: {e}")

    def _strip_trailing_emotion(self, text: str):
        pattern = r"(asco|contento|triste|enfado|miedo|sorpresa)[\.\!\?]?\s*$"
        m = re.search(pattern, text.strip(), re.IGNORECASE)
        if not m:
            return text.strip(), ""
        emo = m.group(1).lower()
        clean = re.sub(pattern, "", text.strip(), flags=re.IGNORECASE).rstrip()
        return clean, emo

    def split_last_word(self, text):
        text = text.strip().rstrip('.')
        words = text.split()
        if words:
            last_word = words[-1]  # La última palabra
            remaining_text = ' '.join(words[:-1])  # El texto sin la última palabra
            return remaining_text, last_word
        else:
            return "", ""  # Si el texto está vacío, retorna dos strings vacíos

    def set_emotion(self, emotion):
        print("Activando emoción")
        emo = emotion.lower()
        if emo == "asco":
            self.ebomoods_proxy.expressDisgust()
        elif emo == "contento":
            self.ebomoods_proxy.expressJoy()
        elif emo == "triste":
            self.ebomoods_proxy.expressSadness()
        elif emo == "enfado":
            self.ebomoods_proxy.expressAnger()
        elif emo == "miedo":
            self.ebomoods_proxy.expressFear()
        elif emo == "sorpresa":
            self.ebomoods_proxy.expressSurprise()
        else:
            pass


    # =============== Methods for Component Implements ==================
    # ===================================================================

    #
    # IMPLEMENTATION of continueChat method from GPT interface
    #
    def GPT_continueChat(self, message):
        if message.strip().lower() == "03827857295769204":
            print("Almacenando chat...")
            self.guardar_chat_history(filename_prefix=f"chat_{self._assistant_name()}")
            self.exit_program()
            return

        # Señales y cronómetro
        self.set_all_LEDS_colors(0, 0, 0, 0)
        self._turn_t0 = time.perf_counter()
        self._first_speak_ts = None
        self._tts_started = False
        self.start_rotating_effect()

        t0 = time.perf_counter()
        try:
            response_text = self.llm_stream_reply_single_message(message)
            dt = time.perf_counter() - t0
            print(f"[GPT] Latencia total (stream): {dt:.3f} s")

            # NO re-extraer. Usar lo que dejó el stream.
            emo = getattr(self, "_last_emotion", "") or ""
            print(f"Assistant Response: {response_text}")
            print(f"Emotion: {emo or 'N/A'}")
            if emo:
                self.set_emotion(emo)
        finally:
            self.stop_rotating_effect()

    #
    # IMPLEMENTATION of setGameInfo method from GPT interface
    #
    def GPT_setGameInfo(self, asisstantName, userInfo):
        self.asisstantName = asisstantName
        self.userInfo = userInfo
        pass


    #
    # IMPLEMENTATION of startChat method from GPT interface
    #
    def GPT_startChat(self):
        name = self._assistant_name()
        system_prompt, cfg = self._load_system_prompt_and_params(name)

        # Aplica config si existe
        self.model_full = cfg.get("full_model", self.model_full)
        self.phase_b_params["temperature"] = cfg.get("temp_b", self.phase_b_params["temperature"])
        self.phase_b_params["max_tokens"] = cfg.get("max_tokens_b", self.phase_b_params["max_tokens"])

        # Historial con system prompt del asistente
        self.history = [{"role": "system", "content": system_prompt}]

        initial_prompt = (self.userInfo or "").strip() or "Saluda al usuario y preséntate brevemente."

        # Señales y cronómetro
        self.set_all_LEDS_colors(0, 0, 0, 0)
        self._turn_t0 = time.perf_counter()
        self._first_speak_ts = None
        self._tts_started = False
        self.start_rotating_effect()

        try:
            response_text = self.llm_stream_reply_single_message(initial_prompt)
            emo = getattr(self, "_last_emotion", "") or ""
            print(f"Assistant Response: {response_text}")
            print(f"Emotion: {emo or 'N/A'}")
            if emo:
                self.set_emotion(emo)
        finally:
            self.stop_rotating_effect()

    def actualizar_dsr(self, aficiones, familiares):
        node = self.g.get_node("CSV Manager")
        node.attrs["familiares"].value = familiares
        node.attrs["aficiones"].value = aficiones
        self.g.update_node(node)
        print("DSR Actualizado con los valores de aficiones y familiares")

    def actualizar_dsr2(self, juego):
        node = self.g.get_node("CSV Manager")
        actual = node.attrs["st_jc"].value
        node.attrs["st_jc"].value = f"{actual}, {juego}"
        self.g.update_node(node)
        print("DSR Actualizado con los juegos completados")

    def exit_mode(self):
        node = self.g.get_node("Storytelling")
        game = node.attrs["actual_game"].value

        if game == "Conversation":
            # Pide al LLM que extraiga Aficiones y Familiares a partir del historial
            prompt_usuario = (
                "La conversación ha terminado. A partir del historial, actualiza los datos. Si tenía aficiones previas o familiares pero no se habló de ellos incluyelos nuevamente. "
                "iniciales del usuario proporcionados según la conversación. Devuélvelo EXACTAMENTE "
                "en este formato (una línea por campo):\n"
                "Aficiones: ...\n"
                "Familiares: ..."
            )

            # Monta entrada con system prompt + historial + la instrucción final
            inputs = [
                *self.history,
                {"role": "user", "content": prompt_usuario},
            ]

            r = self.client.responses.create(
                model=self.model_full,
                input=inputs,
                temperature=0.0,
                max_output_tokens=200,
            )
            response = r.output_text.strip()

            # Extrae campos con regex (como ya hacías)
            aficiones_match = re.search(r"Aficiones:\s*(.*)", response)
            familiares_match = re.search(r"Familiares:\s*(.*)", response)
            aficiones = aficiones_match.group(1).strip() if aficiones_match else ""
            familiares = familiares_match.group(1).strip() if familiares_match else ""

            self.actualizar_dsr(aficiones, familiares)
        else:
            self.actualizar_dsr2(game)

        node.attrs["actual_game"].value = ""
        self.g.update_node(node)

    def exit_program(self):
        self.exit_mode()
        time.sleep(0.5)
        print("-------------------- El programa ha terminado --------------------")
        self.conversacion_en_curso = False
        self.actualizar_csv()

    def actualizar_csv(self):
        node = self.g.get_node("CSV Manager")
        node.attrs["actualizar_info"].value = True
        self.g.update_node(node)

    # ===================================================================
    # ===================================================================


    ######################
    # From the RoboCompEboMoods you can call this methods:
    # self.ebomoods_proxy.expressAnger(...)
    # self.ebomoods_proxy.expressDisgust(...)
    # self.ebomoods_proxy.expressFear(...)
    # self.ebomoods_proxy.expressJoy(...)
    # self.ebomoods_proxy.expressSadness(...)
    # self.ebomoods_proxy.expressSurprise(...)

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
    # self.speech_proxy.setPitch(...)
    # self.speech_proxy.setTempo(...)



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
