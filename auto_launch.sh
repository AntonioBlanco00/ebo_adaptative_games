#!/bin/bash

# Abrir Yakuake
yakuake &

# Esperar un momento para que Yakuake se abra completamente
sleep 3

# Definir las rutas y nombres de las pestañas
ruta1="$HOME/robocomp/components/dsr-graph/components/idserver"
nombre1="DSR"
ruta2="agents/app_juegos"
nombre2="APP_Juegos"
ruta3="../csv_manager"
nombre3="CSV_Manager"
ruta4="../ebo_gpt"
nombre4="EBO_GPT"
ruta5="../settings_adapter"
nombre5="Settings_Adapter"
ruta6="../storytelling"
nombre6="Storytelling"
ruta7="../simonSay"
nombre7="SimonSay"


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


