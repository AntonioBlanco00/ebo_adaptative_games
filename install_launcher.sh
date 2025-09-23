#!/bin/bash
set -euo pipefail

PROJECT_PATH="$(pwd)"
DESKTOP_TEMPLATE="$PROJECT_PATH/EBO_adaptative.desktop"
SCRIPT_TARGET="$PROJECT_PATH/auto_launch.sh"
ICON_FILE="$PROJECT_PATH/icon.png"

APP_DIR="$HOME/.local/share/applications"
LAUNCHER_NAME="EBO_adaptative.desktop"

DESKTOP_DIRS=()
[ -d "$HOME/Escritorio" ] && DESKTOP_DIRS+=("$HOME/Escritorio")
[ -d "$HOME/Desktop" ]    && DESKTOP_DIRS+=("$HOME/Desktop")
# si no existe ninguno, creamos ~/Escritorio por defecto
if [ ${#DESKTOP_DIRS[@]} -eq 0 ]; then
  DESKTOP_DIRS=("$HOME/Escritorio")
  mkdir -p "$HOME/Escritorio"
fi

# Comprobaciones
[ -f "$DESKTOP_TEMPLATE" ] || { echo "No existe $DESKTOP_TEMPLATE"; exit 1; }
[ -f "$SCRIPT_TARGET" ]    || { echo "No existe $SCRIPT_TARGET"; exit 1; }
[ -f "$ICON_FILE" ]        || { echo "No existe $ICON_FILE"; exit 1; }

ABS_SCRIPT="$(readlink -f "$SCRIPT_TARGET")"
ABS_ICON="$(readlink -f "$ICON_FILE")"

# Genera .desktop final en /tmp
TMP_DESK="$(mktemp)"
sed -e "s|^Exec=.*|Exec=$ABS_SCRIPT|" \
    -e "s|^Icon=.*|Icon=$ABS_ICON|" \
    "$DESKTOP_TEMPLATE" > "$TMP_DESK"

chmod +x "$ABS_SCRIPT" "$TMP_DESK"

# Copia a cada escritorio detectado
for DIR in "${DESKTOP_DIRS[@]}"; do
  mkdir -p "$DIR"
  cp -f "$TMP_DESK" "$DIR/$LAUNCHER_NAME"
  chmod +x "$DIR/$LAUNCHER_NAME"
  # marcar como confiable (evita “marcar como de confianza”)
  if command -v gio >/dev/null 2>&1; then
    gio set "$DIR/$LAUNCHER_NAME" "metadata::trusted" yes || true
  fi
done

# Copia al menú
mkdir -p "$APP_DIR"
cp -f "$TMP_DESK" "$APP_DIR/$LAUNCHER_NAME"
chmod +x "$APP_DIR/$LAUNCHER_NAME"
if command -v update-desktop-database >/dev/null 2>&1; then
  update-desktop-database "$APP_DIR" || true
fi

rm -f "$TMP_DESK"

echo "Lanzador instalado en:"
for DIR in "${DESKTOP_DIRS[@]}"; do
  echo "  - $DIR/$LAUNCHER_NAME"
done
echo "  - $APP_DIR/$LAUNCHER_NAME"

