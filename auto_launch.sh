#!/bin/bash

# Función para matar yakuake si estaba abierto
function kill_yakuake() {
  pkill -TERM -x yakuake 2>/dev/null || true
  sleep 0.5
  pkill -KILL -x yakuake 2>/dev/null || true
}

# Función para mostrar al terapeuta cuando puede usar la app:
function mostrar_countdown_y_salir() {
  if command -v tput >/dev/null 2>&1; then tput civis; trap 'tput cnorm' EXIT; fi

  for n in 3 2 1; do
    printf "\rLanzamiento completado. Aplicación lista en %s..." "$n"
    sleep 1
  done
  printf "\rYa puedes usar la app.                          \n"
  sleep 2
}

# Función para cambiar el nombre de la pestaña
function cambiar_nombre_pestania() {
    xdotool key ctrl+alt+s
    sleep 0.5
    xdotool type "$1"
    xdotool key Return
    sleep 0.5
}

# Función para abrir una nueva pestaña en Yakuake, ejecutar un comando y cambiar el nombre
function abrir_nueva_pestania() {
    # Crear nueva pestaña
    xdotool key ctrl+shift+t
    sleep 0.5
    # Navegar a la ruta especificada
    xdotool type "cd $1"
    xdotool key Return
    sleep 0.5
    # Cambiar el nombre de la pestaña
    cambiar_nombre_pestania "$2"
    # Ejecutar el comando adicional si se especifica
    if [ -n "$3" ]; then
        xdotool type "$3"
        xdotool key Return
    fi
}

# Mensaje inicial
echo Iniciando juegos, por favor, espera y no toques nada...

# Matar yakuake
kill_yakuake
sleep 1

# Abrir Yakuake desacoplado del terminal que ejecuta este script
trap '' HUP
nohup yakuake >/dev/null 2>&1 & disown

# Esperar un momento para que Yakuake se abra completamente
sleep 3

ruta="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Definir las rutas y nombres de las pestañas
ruta1="$HOME/robocomp/components/dsr-graph/components/idserver"
nombre1="DSR"

ruta2="$ruta/agents/app_juegos"
nombre2="APP_Juegos"

ruta3="$ruta/agents/csv_manager"
nombre3="CSV_Manager"

ruta4="$ruta/agents/ebo_gpt"
nombre4="EBO_GPT"

ruta5="$ruta/agents/settings_adapter"
nombre5="Settings_Adapter"

ruta6="$ruta/agents/storytelling"
nombre6="Storytelling"

ruta7="$ruta/agents/simonSay"
nombre7="SimonSay"

ruta8="$ruta/agents/pasapalabra"
nombre8="Pasapalabra"

ruta9="$ruta/agents/ebo_app"
nombre9="APP Terapeuta"

# Abrir la primera ruta en la pestaña inicial
xdotool type "cd $ruta1"
xdotool key Return
cambiar_nombre_pestania "$nombre1"
# Ejecutar comando opcional en la primera pestaña
xdotool type "bin/idserver etc/config_ebo_adaptative"
xdotool key Return

# Abrir las siguientes rutas en nuevas pestañas, cambiar nombre y ejecutar comandos opcionales
abrir_nueva_pestania "$ruta2" "$nombre2" "src/app_juegos.py etc/config"
abrir_nueva_pestania "$ruta3" "$nombre3" "src/csv_manager.py etc/config"
abrir_nueva_pestania "$ruta4" "$nombre4" "src/ebo_gpt.py etc/config"
abrir_nueva_pestania "$ruta5" "$nombre5" "src/settings_adapter.py etc/config"
abrir_nueva_pestania "$ruta6" "$nombre6" "src/storytelling.py etc/config"
abrir_nueva_pestania "$ruta7" "$nombre7" "src/simonSay.py etc/config"
abrir_nueva_pestania "$ruta8" "$nombre8" "src/pasapalabra.py etc/config"
abrir_nueva_pestania "$ruta9" "$nombre9" "src/ebo_app.py etc/config"

if command -v xdotool >/dev/null 2>&1; then for wid in $(xdotool search --class yakuake 2>/dev/null); do xdotool windowminimize "$wid" 2>/dev/null || xdotool windowunmap "$wid" 2>/dev/null; done; fi
mostrar_countdown_y_salir
exit 0

