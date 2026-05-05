import os
import re
import sys
import subprocess
from playwright.sync_api import sync_playwright

USUARIO = "admin"
PASSWORD = "Admin123"
EMPRESA = "DEMO SAS"

if len(sys.argv) < 2:
    print("Uso: python3 grabar.py <nombre_prueba>")
    print("Ejemplo: python3 grabar.py crear_pedido")
    sys.exit(1)

nombre_prueba = sys.argv[1]
archivo_salida = f"pruebas/{nombre_prueba}.py"

# === PASO 1: Login y guardar sesion ===
print("=" * 50)
print(f"Grabando prueba: {nombre_prueba}")
print("=" * 50)

with sync_playwright() as p:
    navegador = p.chromium.launch(headless=False)
    contexto = navegador.new_context(ignore_https_errors=True)
    pagina = contexto.new_page()

    print("Abriendo SINCO...")
    pagina.goto("https://desarrollo.sincoerp.com/SincoOk/V3/Marco/Login_iv.aspx")
    pagina.wait_for_load_state("networkidle")

    print("Ingresando credenciales...")
    pagina.locator("input:visible").nth(0).click()
    pagina.keyboard.type(USUARIO)
    pagina.locator("input:visible").nth(1).click()
    pagina.keyboard.type(PASSWORD)

    print("Iniciando sesion...")
    pagina.locator("button:visible").nth(0).click()
    try:
        pagina.wait_for_load_state("load", timeout=30000)
    except Exception:
        # Si la pagina original se cerro, buscar la pagina activa del contexto
        paginas = contexto.pages
        if paginas:
            pagina = paginas[-1]
            pagina.wait_for_load_state("load", timeout=15000)
    pagina.wait_for_timeout(5000)

    # Verificar si hay selector de empresa (puede que el login redirija directo)
    tiene_empresa = pagina.locator("#ddlEmpresa").count() > 0
    if tiene_empresa:
        print(f"Seleccionando empresa: {EMPRESA}...")
        pagina.locator("#ddlEmpresa").select_option(label=EMPRESA)
        pagina.wait_for_timeout(3000)

        print("Haciendo click en Ingresar...")
        boton = pagina.locator("button:has-text('Ingresar'), input[value='Ingresar'], a:has-text('Ingresar'), :text('Ingresar')").first
        boton.wait_for(state="visible", timeout=10000)
        boton.click()
        try:
            pagina.wait_for_load_state("networkidle", timeout=15000)
        except Exception:
            pass
        pagina.wait_for_timeout(5000)
    else:
        print("No se encontro selector de empresa, continuando...")

    url_actual = pagina.url
    contexto.storage_state(path="sesion.json")
    navegador.close()

print("\nSesion guardada. Abriendo grabador...")
print("=" * 50)
print("INSTRUCCIONES:")
print("1. Se abre un navegador ya logueado en SINCO")
print("2. Navega al modulo que quieras probar (ej. ADPRO > Contratos)")
print("3. Realiza las acciones de tu prueba")
print("4. Cuando termines, CIERRA el navegador")
print(f"5. El archivo se guardara en: {archivo_salida}")
print("=" * 50)

# === PASO 2: Lanzar codegen y guardar a archivo temporal ===
archivo_temp = "grabacion_temp.py"
subprocess.run(
    [sys.executable, "-m", "playwright", "codegen",
     "--load-storage=sesion.json", "--target", "python",
     "--ignore-https-errors",
     "-o", archivo_temp, url_actual],
)

if not os.path.exists(archivo_temp):
    print("\nNo se genero el archivo de grabacion.")
    sys.exit(1)

with open(archivo_temp, "r", encoding="utf-8") as f:
    codigo_grabado = f.read().strip()

os.remove(archivo_temp)

if not codigo_grabado:
    print("\nNo se capturo codigo. Verifica que realizaste acciones en el navegador.")
    sys.exit(1)

# === PASO 3: Extraer solo las acciones (navegacion + prueba) ===

# Detectar tecnologia del codigo grabado
es_mui = any(p in codigo_grabado for p in ['Mui', 'css-', '_r_', ':r'])
if es_mui:
    print("Tecnologia detectada: React/MUI - aplicando limpieza de selectores")
else:
    print("Tecnologia detectada: HTML puro")


def _reemplazar_id_react(match, linea_contexto):
    """Reemplaza IDs dinamicos de React con selectores estables."""
    # Buscar si la linea tiene .fill() -> es un input/textbox
    if ".fill(" in linea_contexto:
        # Buscar placeholder en el contexto cercano
        ph = re.search(r'placeholder=["\']([^"\']+)["\']', linea_contexto)
        if ph:
            return f'.get_by_placeholder("{ph.group(1)}")'
        return '.get_by_role("textbox")'
    # Buscar si tiene .select_option() -> es un combobox
    if ".select_option(" in linea_contexto:
        return '.get_by_role("combobox")'
    # Buscar si tiene .check() o .uncheck() -> es un checkbox
    if ".check(" in linea_contexto or ".uncheck(" in linea_contexto:
        return '.get_by_role("checkbox")'
    # Default: textbox (la mayoria de inputs MUI con ID React son textbox)
    return '.get_by_role("textbox")'


lineas_acciones = []
num_paso = 0
frame_asignado = False
for linea in codigo_grabado.split("\n"):
    linea_strip = linea.strip()
    # Saltar boilerplate de codegen
    if any(skip in linea_strip for skip in [
        "from playwright", "import re", "def run", "browser =", "context =",
        "page = context", "page.goto", "context.close", "browser.close",
        "with sync_playwright", "run(playwright", "-> None:",
    ]):
        continue
    if not linea_strip or linea_strip == "# ---------------------":
        continue
    # Saltar cierre de pagina (rompe el runner)
    if "page.close()" in linea_strip or "pagina.close()" in linea_strip:
        continue
    # Reemplazar page.locator("#pagina1").content_frame.XXX por asignacion de frame + frame.XXX
    linea_limpia = linea.replace('page.locator("#pagina1").content_frame', 'frame')
    # Reemplazar page. por pagina. para acciones fuera del frame
    linea_limpia = linea_limpia.replace('page.', 'pagina.')
    if linea_limpia.strip():
        es_frame = linea_limpia.lstrip().startswith("frame.")
        # Auto-asignar frame la primera vez que se usa
        if es_frame and not frame_asignado:
            frame_asignado = True
            indent = len(linea_limpia) - len(linea_limpia.lstrip())
            espacio = " " * indent
            lineas_acciones.append(f'{espacio}frame = pagina.locator("#pagina1").content_frame')
        # === REEMPLAZOS GENERALES (ambas tecnologias) ===

        # Navegacion de modulos: get_by_text("ADPRO") es ambiguo (3 matches)
        # Codegen graba el texto del boton pero hay multiples elementos con "ADPRO"
        linea_limpia = linea_limpia.replace(
            'get_by_text("ADPRO").click()',
            'get_by_title("Administración de proyectos").click()',
        )
        linea_limpia = linea_limpia.replace(
            "get_by_text('ADPRO').click()",
            "get_by_title('Administración de proyectos').click()",
        )

        # === REEMPLAZOS DE LOCATORS FRAGILES DE MUI ===
        if es_mui:
            # 1) IDs dinamicos de React: _r_XX_, :rXX:, mui-XX
            #    React/MUI genera IDs que cambian cada render/sesion
            #    Estrategia: buscar placeholder o aria-label en el selector,
            #    si no hay, usar get_by_role con el tipo de elemento correcto

            # 1a) Cualquier .locator() que contenga un ID dinamico de React
            #     Patrones: _r_XX_, :rXX:, mui-XX (en cualquier formato de selector)
            linea_limpia = re.sub(
                r'\.locator\([^)]*(?:_r_\d+_|:r[0-9a-f]+:|mui-\d+)[^)]*\)',
                lambda m: _reemplazar_id_react(m, linea_limpia),
                linea_limpia,
            )

            # 2) Locators posicionales de MUI DataGrid (div:nth-child(N) > .MuiBox-root)
            #    MUI DataGrid usa role="row" y role="gridcell", NO <tr>/<td>
            linea_limpia = re.sub(
                r'\.locator\("div:nth-child\(\d+\) > \.MuiBox-root"\)(\.first)?',
                '.get_by_role("row").last.get_by_role("gridcell").last',
                linea_limpia,
            )

            # 3) Clases CSS-in-JS (.css-XXXXXXX) solas o combinadas
            #    MUI genera clases como .css-1tdeh38 que cambian entre builds
            #    Buscar contexto: si hay .click() es probablemente un boton
            if re.search(r'\.locator\("[^"]*\.css-[a-z0-9]+', linea_limpia):
                if ".click(" in linea_limpia or ".click()" in linea_limpia:
                    reemplazo_css = '.locator("button:visible").last'
                elif ".fill(" in linea_limpia:
                    reemplazo_css = '.get_by_role("textbox")'
                else:
                    reemplazo_css = '.locator("[role]:visible").last'
                linea_limpia = re.sub(
                    r'\.locator\("[^"]*\.css-[a-z0-9]+[^"]*"\)',
                    reemplazo_css,
                    linea_limpia,
                )

        # Para clicks en el frame con MUI: usar force=True para evitar "subtree intercepts pointer events"
        if es_frame and es_mui and ".click()" in linea_limpia:
            linea_limpia = linea_limpia.replace(".click()", ".click(force=True)")

        # Si un .fill() usa get_by_role("textbox") despues de un click en gridcell,
        # el textbox es el input de edicion de la celda (MUI DataGrid)
        if es_mui and es_frame and '.get_by_role("textbox").fill(' in linea_limpia:
            # Verificar si la accion anterior fue un click en gridcell/row
            acciones_previas = [a for a in lineas_acciones if a.strip() and not a.strip().startswith("if on_paso") and not a.strip().startswith("pagina.wait")]
            if acciones_previas:
                ultima = acciones_previas[-1]
                if "gridcell" in ultima or "get_by_role(\"row\")" in ultima or "MuiBox" in ultima:
                    linea_limpia = linea_limpia.replace(
                        '.get_by_role("textbox").fill(',
                        '.locator(".MuiDataGrid-cell--editing input, .MuiBox-root input:visible").last.fill(',
                    )

        lineas_acciones.append(linea_limpia)
        # Inyectar espera y captura despues de clicks
        indent = len(linea_limpia) - len(linea_limpia.lstrip())
        espacio = " " * indent
        if ".click(" in linea_limpia:
            # Extraer descripcion del click
            desc_match = re.search(r'name="([^"]+)"', linea_limpia)
            if not desc_match:
                desc_match = re.search(r'get_by_text\("([^"]+)"', linea_limpia)
            if not desc_match:
                desc_match = re.search(r'get_by_title\("([^"]+)"', linea_limpia)
            desc = desc_match.group(1) if desc_match else "Accion"
            num_paso += 1
            if es_frame:
                lineas_acciones.append(f"{espacio}pagina.wait_for_timeout(3000)")
            else:
                lineas_acciones.append(f"{espacio}pagina.wait_for_load_state('networkidle')")
                lineas_acciones.append(f"{espacio}pagina.wait_for_timeout(500)")
            lineas_acciones.append(f'{espacio}if on_paso: on_paso("{desc}")')
        elif ".fill(" in linea_limpia and es_frame:
            lineas_acciones.append(f"{espacio}pagina.wait_for_timeout(1000)")
        elif ".select_option(" in linea_limpia:
            lineas_acciones.append(f"{espacio}pagina.wait_for_timeout(500)")

acciones = "\n".join(lineas_acciones)

# === PASO 4: Generar archivo de prueba ===
nombre_bonito = nombre_prueba.replace("_", " ").title()

contenido = f'''"""
Prueba: {nombre_bonito}
Generada con playwright codegen
"""
import re


def ejecutar(pagina, frame, on_paso=None):
    """
    Ejecuta la prueba '{nombre_bonito}'.
    Recibe la pagina ya logueada en SINCO (despues de seleccionar empresa).
    La prueba incluye la navegacion al modulo correspondiente.
    on_paso: callback opcional para reportar progreso con screenshot.
    Retorna dict con el resultado.
    """
{acciones}

    return {{
        "prueba": "{nombre_bonito}",
        "estado": "ok",
    }}
'''

with open(archivo_salida, "w", encoding="utf-8") as f:
    f.write(contenido)

print(f"\nPrueba guardada en: {archivo_salida}")
print(f"Pasos de prueba detectados: {num_paso}")
print(f"Ya puedes ejecutarla desde el dashboard en http://localhost:5050")
