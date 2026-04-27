import re
import json
import queue
import base64
import threading
from datetime import datetime
from flask import Flask, Response, send_file, jsonify, request
from playwright.sync_api import sync_playwright

app = Flask(__name__)

# Cola global para enviar eventos al frontend
eventos = {}

USUARIO = "office"
PASSWORD = "Office123"
EMPRESA = "SincoPlus Pruebas Módulos"
URL_BASE = "https://www4.sincoerp.com/SincoPlusPruebasModulos2022/V3/Marco/Seleccion_iv.aspx"


def enviar_evento(session_id, tipo, data):
    if session_id in eventos:
        eventos[session_id].put(json.dumps({"tipo": tipo, **data}))


def ejecutar_prueba(session_id, usuario, password, empresa, url_base):
    total_pasos = 10
    paso_actual = 0

    def captura(pagina):
        """Toma screenshot y retorna base64."""
        buf = pagina.screenshot()
        return base64.b64encode(buf).decode("utf-8")

    def paso(nombre, descripcion, screenshot_b64=None):
        nonlocal paso_actual
        paso_actual += 1
        porcentaje = round((paso_actual / total_pasos) * 100)
        data = {
            "paso": paso_actual,
            "total": total_pasos,
            "porcentaje": porcentaje,
            "nombre": nombre,
            "descripcion": descripcion,
        }
        if screenshot_b64:
            data["screenshot"] = screenshot_b64
        enviar_evento(session_id, "progreso", data)

    try:
        with sync_playwright() as p:
            navegador = p.chromium.launch(headless=True)
            pagina = navegador.new_page()

            # Paso 1: Abrir SINCO
            pagina.goto(url_base)
            pagina.wait_for_load_state("networkidle")
            paso("Conexion", "Pagina de SINCO cargada", captura(pagina))

            # Paso 2: Credenciales
            pagina.locator("input:visible").nth(0).click()
            pagina.keyboard.type(usuario)
            pagina.locator("input:visible").nth(1).click()
            pagina.keyboard.type(password)
            paso("Credenciales", f"Usuario {usuario} ingresado", captura(pagina))

            # Paso 3: Login
            pagina.locator("button:visible").nth(0).click()
            pagina.wait_for_load_state("networkidle")
            pagina.wait_for_timeout(5000)
            paso("Login", "Sesion iniciada correctamente", captura(pagina))

            # Paso 4: Empresa
            pagina.locator("#ddlEmpresa").select_option(label=empresa)
            pagina.wait_for_timeout(3000)
            paso("Empresa", f"Empresa seleccionada: {empresa}", captura(pagina))

            # Paso 5: Ingresar
            boton = pagina.locator("button:has-text('Ingresar'), input[value='Ingresar'], a:has-text('Ingresar'), :text('Ingresar')").first
            boton.wait_for(state="visible", timeout=10000)
            boton.click()
            pagina.wait_for_load_state("networkidle")
            pagina.wait_for_timeout(5000)
            paso("Ingresar", "Ingreso al sistema completado", captura(pagina))

            # Paso 6: Navegar menu
            pagina.locator("text=ADPRO").first.wait_for(state="visible", timeout=10000)
            pagina.locator("text=ADPRO").first.click()
            pagina.wait_for_timeout(2000)

            pagina.locator("text=Almacén").first.wait_for(state="visible", timeout=10000)
            pagina.locator("text=Almacén").first.click()
            pagina.wait_for_timeout(2000)

            pagina.locator("text=Pedidos").first.wait_for(state="visible", timeout=10000)
            pagina.locator("text=Pedidos").first.click()
            pagina.wait_for_timeout(2000)

            pagina.locator("text=Pedidos proyecto").last.wait_for(state="visible", timeout=10000)
            pagina.locator("text=Pedidos proyecto").last.click()
            pagina.wait_for_load_state("networkidle")
            pagina.wait_for_timeout(8000)
            paso("Navegacion", "Ruta: ADPRO > Almacen > Pedidos > Pedidos proyecto", captura(pagina))

            # Paso 7: Leer pedido
            frame = pagina.frames[1]
            primer_pedido = frame.locator("text=/Pedido No\\./").first
            primer_pedido.wait_for(state="visible", timeout=15000)
            texto_pedido = primer_pedido.inner_text()

            match = re.search(r"Pedido No\.\s*(.+)", texto_pedido)
            numero_pedido = match.group(1).strip() if match else texto_pedido
            paso("Lectura", f"Pedido encontrado: {texto_pedido}", captura(pagina))

            enviar_evento(session_id, "info", {
                "mensaje": f"Pedido encontrado: {texto_pedido}"
            })

            # Paso 8: Abrir filtro
            frame.locator("text=Filtrar").first.wait_for(state="visible", timeout=10000)
            frame.locator("text=Filtrar").first.click()
            pagina.wait_for_timeout(3000)
            paso("Filtro", "Drawer de filtro abierto", captura(pagina))

            # Paso 9: Escribir y consultar
            input_pedido = frame.get_by_placeholder("Ingresar Pedido No.")
            input_pedido.wait_for(state="visible", timeout=10000)
            input_pedido.click()
            input_pedido.fill(numero_pedido)
            pagina.wait_for_timeout(1000)

            frame.locator("button:has-text('Consultar')").first.wait_for(state="visible", timeout=10000)
            frame.locator("button:has-text('Consultar')").first.click()
            pagina.wait_for_timeout(8000)
            paso("Consulta", f"Filtrado por pedido {numero_pedido}", captura(pagina))

            # Paso 10: Validar
            pedidos_visibles = frame.locator("text=/Pedido No\\./").all()
            cantidad = sum(1 for p in pedidos_visibles if p.is_visible())
            paso("Validacion", f"Resultados: {cantidad} registro(s) en la tabla", captura(pagina))

            navegador.close()

        es_ok = cantidad > 0
        fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        enviar_evento(session_id, "resultado", {
            "prueba": "Filtro de pedidos por numero",
            "dato_entrada": numero_pedido,
            "esperado": "La tabla muestra solo el pedido filtrado",
            "obtenido": f"{cantidad} registro(s) en la tabla" if es_ok else "Sin resultados en la tabla",
            "estado": "ok" if es_ok else "fail",
            "fecha": fecha,
            "empresa": empresa,
            "usuario": usuario,
        })

        enviar_evento(session_id, "fin", {"exito": es_ok})

    except Exception as e:
        enviar_evento(session_id, "error", {"mensaje": str(e)})
        enviar_evento(session_id, "fin", {"exito": False})


@app.route("/")
def index():
    return send_file("dashboard.html")


@app.route("/config")
def config():
    return jsonify({
        "usuario": USUARIO,
        "password": PASSWORD,
        "empresa": EMPRESA,
        "url": URL_BASE,
    })


@app.route("/ejecutar", methods=["POST"])
def ejecutar():
    data = request.get_json() or {}
    usuario = data.get("usuario", USUARIO)
    password = data.get("password", PASSWORD)
    empresa = data.get("empresa", EMPRESA)
    url_base = data.get("url", URL_BASE)

    session_id = str(datetime.now().timestamp())
    eventos[session_id] = queue.Queue()
    hilo = threading.Thread(
        target=ejecutar_prueba,
        args=(session_id, usuario, password, empresa, url_base),
        daemon=True,
    )
    hilo.start()
    return jsonify({"session_id": session_id})


@app.route("/stream/<session_id>")
def stream(session_id):
    def generar():
        q = eventos.get(session_id)
        if not q:
            return
        while True:
            try:
                data = q.get(timeout=120)
                yield f"data: {data}\n\n"
                parsed = json.loads(data)
                if parsed["tipo"] == "fin":
                    del eventos[session_id]
                    break
            except queue.Empty:
                yield "data: {\"tipo\": \"ping\"}\n\n"

    return Response(generar(), mimetype="text/event-stream")


if __name__ == "__main__":
    print("Servidor iniciado en http://localhost:5000")
    app.run(debug=False, port=5050)
