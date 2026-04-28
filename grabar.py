import os
import sys
import subprocess
from playwright.sync_api import sync_playwright

USUARIO = "office"
PASSWORD = "Office123"
EMPRESA = "SincoPlus Pruebas Módulos"

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
    contexto = navegador.new_context()
    pagina = contexto.new_page()

    print("Abriendo SINCO...")
    pagina.goto("https://www4.sincoerp.com/SincoPlusPruebasModulos2022/V3/Marco/Seleccion_iv.aspx")
    pagina.wait_for_load_state("networkidle")

    print("Ingresando credenciales...")
    pagina.locator("input:visible").nth(0).click()
    pagina.keyboard.type(USUARIO)
    pagina.locator("input:visible").nth(1).click()
    pagina.keyboard.type(PASSWORD)

    print("Iniciando sesion...")
    pagina.locator("button:visible").nth(0).click()
    pagina.wait_for_load_state("networkidle")
    pagina.wait_for_timeout(5000)

    print(f"Seleccionando empresa: {EMPRESA}...")
    pagina.locator("#ddlEmpresa").select_option(label=EMPRESA)
    pagina.wait_for_timeout(3000)

    print("Haciendo click en Ingresar...")
    boton = pagina.locator("button:has-text('Ingresar'), input[value='Ingresar'], a:has-text('Ingresar'), :text('Ingresar')").first
    boton.wait_for(state="visible", timeout=10000)
    boton.click()
    pagina.wait_for_load_state("networkidle")
    pagina.wait_for_timeout(5000)

    print("Navegando a Pedidos Proyecto...")
    pagina.get_by_title("Administración de proyectos").click()
    pagina.wait_for_timeout(2000)
    pagina.get_by_title("Ruta: ADPRO/Almacén").click()
    pagina.wait_for_timeout(2000)
    pagina.get_by_role("button", name="PEDIDOS").click()
    pagina.wait_for_timeout(2000)
    pagina.get_by_role("button", name="Pedidos proyecto").click()
    pagina.wait_for_load_state("networkidle")
    pagina.wait_for_timeout(8000)

    url_actual = pagina.url
    contexto.storage_state(path="sesion.json")
    navegador.close()

print("\nSesion guardada. Abriendo grabador...")
print("=" * 50)
print("INSTRUCCIONES:")
print("1. Se abre un navegador con el grabador de Playwright")
print("2. Navega a Pedidos Proyecto si no estas ahi")
print("3. Realiza las acciones de tu prueba")
print("4. Cuando termines, CIERRA el navegador")
print(f"5. El archivo se guardara en: {archivo_salida}")
print("=" * 50)

# === PASO 2: Lanzar codegen y guardar a archivo temporal ===
archivo_temp = "grabacion_temp.py"
subprocess.run(
    [sys.executable, "-m", "playwright", "codegen",
     "--load-storage=sesion.json", "--target", "python",
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

# === PASO 3: Extraer solo las acciones del frame ===
lineas_acciones = []
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
    # Reemplazar page.locator("#pagina1").content_frame por frame
    linea_limpia = linea.replace('page.locator("#pagina1").content_frame', 'frame')
    # Reemplazar page. por pagina. para acciones fuera del frame
    linea_limpia = linea_limpia.replace('page.', 'pagina.')
    if linea_limpia.strip():
        lineas_acciones.append(linea_limpia)

acciones = "\n".join(lineas_acciones)

# === PASO 4: Generar archivo de prueba ===
nombre_bonito = nombre_prueba.replace("_", " ").title()

contenido = f'''"""
Prueba: {nombre_bonito}
Generada con playwright codegen
"""


def ejecutar(pagina, frame):
    """
    Ejecuta la prueba '{nombre_bonito}'.
    Recibe la pagina ya logueada y el frame de Pedidos Proyecto.
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
print(f"Ya puedes ejecutarla desde el dashboard en http://localhost:5050")
