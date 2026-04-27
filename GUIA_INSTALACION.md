# Guía de instalación - Script automático SINCO

Este script abre automáticamente el navegador, entra a la página de SINCO e inicia sesión con las credenciales configuradas.

---

## Paso 1: Instalar Python

Si no tienes Python instalado, descárgalo desde:

👉 https://www.python.org/downloads/

Durante la instalación, **marca la casilla "Add Python to PATH"** (esto es muy importante).

Para verificar que quedó instalado correctamente, abre una **terminal** y escribe:

```
python3 --version
```

Debe aparecer algo como `Python 3.x.x`. Si aparece un error, reinicia el computador e intenta de nuevo.

### ¿Cómo abrir una terminal?

- **Mac**: Buscar "Terminal" en Spotlight (Cmd + Espacio)
- **Windows**: Buscar "cmd" o "PowerShell" en el menú de inicio

---

## Paso 2: Copiar el proyecto

Copia la carpeta **sinco** completa al computador. Dentro debe haber estos archivos:

```
sinco/
├── main.py              ← el script principal
├── requirements.txt     ← lista de dependencias
└── GUIA_INSTALACION.md  ← este documento
```

---

## Paso 3: Abrir la terminal en la carpeta del proyecto

1. Abre una terminal
2. Escribe el siguiente comando para ir a la carpeta del proyecto (ajusta la ruta según donde hayas copiado la carpeta):

**Mac:**
```
cd /Users/TU_USUARIO/Documents/sinco
```

**Windows:**
```
cd C:\Users\TU_USUARIO\Documents\sinco
```

> Reemplaza `TU_USUARIO` por tu nombre de usuario del computador.

---

## Paso 4: Instalar dependencias

Copia y pega este comando en la terminal y presiona **Enter**:

```
pip3 install -r requirements.txt
```

Espera a que termine (puede tardar unos segundos).

---

## Paso 5: Instalar el navegador

Copia y pega este comando en la terminal y presiona **Enter**:

```
python3 -m playwright install chromium
```

Esto descarga el navegador que usará el script. Puede tardar unos minutos dependiendo de tu conexión a internet.

---

## Paso 6: Ejecutar el script

Copia y pega este comando en la terminal y presiona **Enter**:

```
python3 main.py
```

### ¿Qué va a pasar?

1. Se abrirá una ventana del navegador automáticamente
2. El navegador entrará a la página de SINCO
3. Escribirá el usuario y la contraseña solo
4. Tomará una foto de la pantalla (se guarda como `paso2_despues_login.png` en la misma carpeta)
5. Se cerrará el navegador después de 5 segundos

---

## Cambiar usuario y contraseña

Si necesitas usar otras credenciales, abre el archivo `main.py` con cualquier editor de texto (por ejemplo Bloc de Notas o TextEdit) y cambia estas líneas al inicio del archivo:

```
USUARIO = "admin"
PASSWORD = "Admin123"
```

Guarda el archivo y vuelve a ejecutar el paso 6.

---

## Problemas frecuentes

**"command not found" o "no se reconoce el comando"**
→ Python no está instalado o no se agregó al PATH. Vuelve al Paso 1 y asegúrate de marcar "Add Python to PATH" durante la instalación.

**El navegador no se abre**
→ Verifica que ejecutaste el Paso 5 (instalar el navegador).

**Error de conexión o la página no carga**
→ Verifica que tienes acceso a internet y que puedes abrir https://desarrollo.sincoerp.com en un navegador normal.

**En Windows, `pip3` no funciona**
→ Intenta con `pip` en lugar de `pip3`, y `python` en lugar de `python3`.
