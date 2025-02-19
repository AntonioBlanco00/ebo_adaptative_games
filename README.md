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

