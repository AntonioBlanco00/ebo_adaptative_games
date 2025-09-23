# ebo_adaptative_games

## Configuración del DSR

Para configurar el **DSR** correctamente, sigue estos pasos:

### 1. Copiar los archivos de configuración
Debes mover los siguientes archivos a las carpetas correspondientes dentro del componente **dsr_graph**:

- **`ebo_adaptative_scene.json`** → `dsr-graph/components/idserver/`
- **`config_ebo_adaptative`** → `dsr-graph/components/idserver/etc/`

### 2. Lanzar el DSR
Una vez copiados los archivos, ejecuta el siguiente comando desde la carpeta `dsr-graph/components/idserver/`:

```sh
bin/idserver etc/config_ebo_adaptative
```

---

## Lanzador por doble clic (Desktop shortcut)

Esto crea un acceso directo **EBO_adaptative** en tu Escritorio y en el menú de aplicaciones, para ejecutar `auto_launch.sh` con doble clic.

### Requisitos

Debes tener instalados:
- **yakuake**
- **xdotool**
- **gnome-terminal**
- (opcional) `gio` para marcar el acceso como “confiable”

Instálalos si faltan (Debian/Ubuntu):
```sh
sudo apt-get install -y yakuake xdotool gnome-terminal libglib2.0-bin
```

### Instalación del lanzador

Desde la carpeta del repo `ebo_adaptative_games`:

```sh
cd ebo_adaptative_games
chmod +x install_launcher.sh auto_launch.sh
./install_launcher.sh
```

Al finalizar, tendrás:

- Escritorio: `~/Escritorio/EBO_adaptative.desktop` (y/o `~/Desktop/EBO_adaptative.desktop`)
- Menú de apps: `~/.local/share/applications/EBO_adaptative.desktop`

> Si en tu Escritorio aparece como archivo y no como app, haz **clic derecho → “Permitir ejecutar”**.  
> El instalador ya intenta marcarlo como confiable con `gio`, pero algunas distros piden confirmación manual.

### Desinstalación del lanzador

Borra los accesos:
```sh
rm -f ~/Escritorio/EBO_adaptative.desktop       ~/Desktop/EBO_adaptative.desktop       ~/.local/share/applications/EBO_adaptative.desktop
```
