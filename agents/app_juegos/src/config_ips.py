# config_ips.py
import os
import re
import shutil
import subprocess
import sys
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from typing import List, Dict, Tuple, Optional


def es_ip_valida(ip: str) -> bool:
    """Valida formato IPv4 y rango 0-255 por octeto."""
    partes = ip.split('.')
    if len(partes) != 4:
        return False
    try:
        for p in partes:
            if not 0 <= int(p) <= 255:
                return False
    except ValueError:
        return False
    return True


def verificar_conexion_ip(ip: str, timeout: int = 1, count: int = 1) -> bool:
    """
    Hace ping a la IP. Funciona en Linux/macOS y Windows.
    - timeout: tiempo de espera por ping (segundos).
    - count: número de paquetes a enviar.
    Devuelve True si al menos un ping responde.
    """
    if not es_ip_valida(ip):
        return False
    # Comando distinto en Windows
    if sys.platform.startswith("win"):
        cmd = ["ping", "-n", str(count), "-w", str(timeout * 1000), ip]
    else:
        # -c count, -W timeout (segundos) en many unix; algunos sistemas usan -w (total)
        cmd = ["ping", "-c", str(count), "-W", str(timeout), ip]
    try:
        resultado = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return resultado.returncode == 0
    except Exception:
        return False


IP_REGEX = re.compile(
    r'\b(?:25[0-5]|2[0-4]\d|1\d{2}|[1-9]?\d)'
    r'(?:\.(?:25[0-5]|2[0-4]\d|1\d{2}|[1-9]?\d)){3}\b'
)


def modificar_ip_en_config(ruta_config: str, nueva_ip: str, hacer_backup: bool = True) -> bool:
    """
    Reemplaza todas las IPs válidas (IPv4) dentro de ruta_config por nueva_ip.
    Crea una copia .bak si hacer_backup=True.
    Devuelve True si archivo se modificó (al menos un reemplazo), False en caso contrario.
    Lanza excepciones si no puede leer/escribir el archivo.
    """
    if not es_ip_valida(nueva_ip):
        raise ValueError(f"IP inválida: {nueva_ip}")

    with open(ruta_config, 'r', encoding='utf-8') as f:
        contenido = f.read()

    contenido_modificado, n_repl = IP_REGEX.subn(nueva_ip, contenido)

    if n_repl == 0:
        return False  # nada que cambiar

    if hacer_backup:
        backup_path = ruta_config + ".bak"
        shutil.copy2(ruta_config, backup_path)

    with open(ruta_config, 'w', encoding='utf-8') as f:
        f.write(contenido_modificado)

    return True


def modificar_ips_en_configs(ruta_base: str, nueva_ip: str) -> Tuple[List[str], List[Tuple[str, str]]]:
    """
    Recorre ruta_base buscando carpetas 'etc' y dentro el archivo llamado 'config'.
    Para cada config encontrado intenta reemplazar IPs por nueva_ip.
    Devuelve una tupla:
      - lista de archivos modificados
      - lista de errores (ruta, mensaje)
    """
    modificados = []
    errores = []

    for root, dirs, files in os.walk(ruta_base):
        if "etc" in dirs:
            etc_path = os.path.join(root, "etc")
            try:
                for archivo in os.listdir(etc_path):
                    if archivo == "config":
                        config_path = os.path.join(etc_path, archivo)
                        try:
                            changed = modificar_ip_en_config(config_path, nueva_ip, hacer_backup=True)
                            if changed:
                                modificados.append(config_path)
                        except Exception as e:
                            errores.append((config_path, str(e)))
            except Exception as e:
                errores.append((etc_path, str(e)))

    return modificados, errores


def configurar_ips(ruta_base: str, nueva_ip: str) -> Dict[str, object]:
    """
    Función programática para usar desde otro código.
    -- No abre GUI. Solo valida la IP, verifica la conexión y aplica los cambios.
    Devuelve un dict con campos:
      - 'ok': bool (True si todo correcto)
      - 'modified_files': list[str]
      - 'errors': list[tuple(path, msg)]
      - 'message': str (texto explicativo)
    """
    result = {
        "ok": False,
        "modified_files": [],
        "errors": [],
        "message": ""
    }

    if not es_ip_valida(nueva_ip):
        result["message"] = "IP inválida"
        return result

    if not verificar_conexion_ip(nueva_ip):
        result["message"] = "No se puede conectar a la IP especificada (ping falló)."
        return result

    modificados, errores = modificar_ips_en_configs(ruta_base, nueva_ip)
    result["modified_files"] = modificados
    result["errors"] = errores
    result["ok"] = len(errores) == 0
    result["message"] = f"Archivos modificados: {len(modificados)}. Errores: {len(errores)}"
    return result


def lanzar_gui_configuracion(ruta_base: Optional[str] = None) -> Dict[str, object]:
    """
    Lanza una ventana tkinter para pedir la IP y ejecutar la modificación.
    Devuelve un dict similar a configurar_ips(...) con los resultados.
    Nota: esta función no se ejecuta al importar el módulo; debes llamarla tú.
    """
    if ruta_base is None:
        ruta_base = os.getcwd()

    resultado_final: Dict[str, object] = {
        "ok": False,
        "modified_files": [],
        "errors": [],
        "nueva_ip": None,
        "message": ""
    }

    # --- funciones internas para GUI ---
    def on_procesar():
        ip = entry_ip.get().strip()
        resultado_final["nueva_ip"] = ip

        if not es_ip_valida(ip):
            messagebox.showerror("Error", "La IP proporcionada no es válida. Por favor, verifica e inténtalo de nuevo.")
            return

        # comprobar conectividad
        if not verificar_conexion_ip(ip):
            messagebox.showerror(
                "Error",
                "No se puede establecer conexión. Revisa que EBO esté encendido y que la IP sea la correcta. "
                "Recuerda que tanto este ordenador como EBO tienen que estar conectados al mismo wifi"
            )
            return

        modificados, errores = modificar_ips_en_configs(ruta_base, ip)
        resultado_final["modified_files"] = modificados
        resultado_final["errors"] = errores
        resultado_final["ok"] = len(errores) == 0
        resultado_final["message"] = f"Archivos modificados: {len(modificados)}. Errores: {len(errores)}"

        if resultado_final["ok"]:
            messagebox.showinfo("Éxito", "El proceso se completó correctamente. Reiniciando los juegos para que los cambios surtan efecto.")
        else:
            messagebox.showwarning("Terminado con errores", resultado_final["message"])

        gui_root.destroy()

    # --- construir GUI ---
    gui_root = tk.Tk()
    gui_root.title("Configurador de IPs")
    gui_root.geometry("600x400")
    gui_root.configure(bg="#f5f5f5")

    style = ttk.Style()
    style.configure("TLabel", font=("Arial", 12), background="#f5f5f5")
    style.configure("TButton", font=("Arial", 10), padding=5)

    frame = ttk.Frame(gui_root, padding="10")
    frame.pack(expand=True)

    texto = (
        "Introduce la nueva IP que deseas configurar:\n\n"
        "Para obtener la IP:\n"
        "1- Abre un terminal en EBO\n"
        "2- Ejecuta ifconfig (o ip addr)\n"
        "3- Ahi aparecerá la IP a introducir, en wlan0\n"
        "\n"
        "IP:"
    )

    label_instruccion = ttk.Label(frame, text=texto, justify="left")
    label_instruccion.pack(pady=10)
    entry_ip = ttk.Entry(frame, width=30, font=("Arial", 12))
    entry_ip.pack(pady=5)

    boton_procesar = ttk.Button(frame, text="Procesar", command=on_procesar)
    boton_procesar.pack(pady=20)

    gui_root.mainloop()

    return resultado_final


__all__ = [
    "es_ip_valida",
    "verificar_conexion_ip",
    "modificar_ip_en_config",
    "modificar_ips_en_configs",
    "configurar_ips",
    "lanzar_gui_configuracion",
]

