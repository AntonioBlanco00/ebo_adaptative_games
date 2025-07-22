#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Recolecta resultados JSON de los juegos (Pasapalabra y Simón), los pasa a CSV,
hace copia de seguridad y procesa los .txt de conversaciones de ebo_gpt.

La ruta base se toma automáticamente a partir de la ubicación de este script,
por lo que no hace falta tocar nada al moverlo de máquina.
"""

import json
import csv
import os
import shutil
import re
from pathlib import Path
from datetime import datetime

print("-----------------------------------------------------")

# ---------- 1. Configuración de rutas -----------------

PROJECT_ROOT = Path(__file__).resolve().parent            # ~/Antonio/ebo_adaptative_games
AGENTS_DIR   = PROJECT_ROOT / "agents"                    # ~/Antonio/ebo_adaptative_games/agents

RESULT_FOLDER_BASE = PROJECT_ROOT / "resultados"          # ~/Antonio/ebo_adaptative_games/resultados
BACKUP_FOLDER_BASE = PROJECT_ROOT / "copia_seguridad_datos"

# Carpetas donde suelen caer las conversaciones de ebo_gpt
GPT_CONVERSATIONS_DIRS = list(AGENTS_DIR.rglob("ebo_gpt/conversaciones"))

# ---------- 2. Recolectar JSON de resultados de juegos ----------

# Definimos los patrones de búsqueda y cómo clasificar la salida
GAME_PATTERNS = {
    "pasapalabra": "resultados_pasapalabra.json",
    "simonSay"   : "resultados_juego.json",
}

# Lista para llevar el control de los JSON que encontremos
found_json_files = []

def json_to_csv(json_path: Path, game_key: str):
    """
    Convierte un JSONL de resultados en un CSV (modo append si ya existe).
    """
    # Cargar datos línea a línea
    rows = []
    with json_path.open("r", encoding="utf-8") as f:
        for line in f:
            try:
                entry = json.loads(line.strip())
                # Convertir tiempos (min, seg) a "Tiempo total (seg)"
                if {"Tiempo transcurrido (min)", "Tiempo transcurrido (seg)"} <= entry.keys():
                    entry["Tiempo total (seg)"] = (
                        entry["Tiempo transcurrido (min)"] * 60
                        + entry["Tiempo transcurrido (seg)"]
                    )
                    entry.pop("Tiempo transcurrido (min)", None)
                    entry.pop("Tiempo transcurrido (seg)", None)
                rows.append(entry)
            except json.JSONDecodeError:
                print(f"[WARN] Línea malformada en {json_path}: {line!r}")

    if not rows:
        return  # nada que hacer

    # Preparar carpetas
    result_dir = RESULT_FOLDER_BASE / game_key
    result_dir.mkdir(parents=True, exist_ok=True)
    csv_path = result_dir / f"resultados_{game_key}.csv"

    # Escribir / añadir
    new_file = not csv_path.exists()
    with csv_path.open("a" if csv_path.exists() else "w", newline="", encoding="utf-8") as fcsv:
        writer = csv.DictWriter(fcsv, fieldnames=list(rows[0].keys()))
        if new_file:
            writer.writeheader()
        writer.writerows(rows)

    print(f"    ➜ CSV actualizado: {csv_path.relative_to(PROJECT_ROOT)}")

# --- búsqueda recursiva dentro de agents/ ---
print("⏳ Buscando JSON de resultados…")
for game_key, filename in GAME_PATTERNS.items():
    for json_path in AGENTS_DIR.rglob(filename):
        print(f"  • Encontrado {json_path.relative_to(PROJECT_ROOT)}")
        json_to_csv(json_path, game_key)
        found_json_files.append(json_path)

# ---------- 3. Mover JSON a copia de seguridad ----------

def make_unique(dest_dir: Path, base_name: str, suffix: str = ".json") -> Path:
    """
    Genera un nombre único evitando sobrescribir (foo.json → foo_1.json, foo_2.json…)
    """
    counter = 1
    candidate = dest_dir / f"{base_name}{suffix}"
    while candidate.exists():
        candidate = dest_dir / f"{base_name}_{counter}{suffix}"
        counter += 1
    return candidate

print("💾 Moviendo JSON procesados a copia de seguridad…")
for json_path in found_json_files:
    subdir = json_path.parent.name               # p.ej. pasapalabra, simonSay
    backup_dir = BACKUP_FOLDER_BASE / subdir
    backup_dir.mkdir(parents=True, exist_ok=True)

    dest = make_unique(backup_dir, json_path.stem)
    shutil.move(str(json_path), dest)
    print(f"  • {json_path.name} → {dest.relative_to(PROJECT_ROOT)}")

# ---------- 4. Procesar .txt de conversaciones (ebo_gpt) ----------

def rename_and_modify_txt(file_path: Path, out_dir: Path, backup_dir: Path):
    text = file_path.read_text(encoding="utf-8")

    # Extraer goal y nombre del jugador (storytelling) o nombre de usuario (conversacional)
    m = re.search(r'"goal"\s*:\s*"(.*?)".*?"nombre del jugador"\s*:\s*"(.*?)"', text, re.DOTALL)
    if m:
        goal, player = m.group(1).strip(), m.group(2).strip()
        base = f"storytelling_{player}_{goal}"
    else:
        m = re.search(r'Nombre:\s*([^\.\n]+)', text)
        if m:
            base = f"conversacion_{m.group(1).strip()}"
        else:
            print(f"[WARN] No se encontró nombre en {file_path.name}. Se omite.")
            return

    # Eliminar el primer mensaje del usuario
    text = re.sub(r'User:.*?Assistant:', 'Assistant:', text, 1, flags=re.DOTALL)

    out_dir.mkdir(parents=True, exist_ok=True)
    new_path = out_dir / f"{base}.txt"
    counter = 1
    while new_path.exists():
        new_path = out_dir / f"{base}_{counter}.txt"
        counter += 1
    new_path.write_text(text, encoding="utf-8")

    # Mover original a backup
    backup_dir.mkdir(parents=True, exist_ok=True)
    shutil.move(file_path, backup_dir / file_path.name)

    print(f"    ➜ {file_path.name} → {new_path.relative_to(PROJECT_ROOT)} (backup realizado)")

print("📝 Procesando conversaciones de GPT…")
TXT_OUT_DIR    = RESULT_FOLDER_BASE / "conversaciones"
TXT_BACKUP_DIR = BACKUP_FOLDER_BASE / "conversaciones"

for conv_dir in GPT_CONVERSATIONS_DIRS:
    print(f"  • Escaneando {conv_dir.relative_to(PROJECT_ROOT)}")
    for txt_file in conv_dir.glob("*.txt"):
        rename_and_modify_txt(txt_file, TXT_OUT_DIR, TXT_BACKUP_DIR)

print("\n✅  Proceso completado.")

