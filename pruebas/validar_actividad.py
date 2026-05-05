"""
Prueba: Validar Actividad
Generada con playwright codegen
"""
import re


def ejecutar(pagina, frame, on_paso=None):
    """
    Ejecuta la prueba 'Validar Actividad'.
    Recibe la pagina ya logueada en SINCO (despues de seleccionar empresa).
    La prueba incluye la navegacion al modulo correspondiente.
    on_paso: callback opcional para reportar progreso con screenshot.
    Retorna dict con el resultado.
    """
    pagina.get_by_title("Administración de proyectos").click()
    pagina.wait_for_load_state('networkidle')
    pagina.wait_for_timeout(500)
    if on_paso: on_paso("ADPRO")
    pagina.get_by_role("button", name="Ejecución").click()
    pagina.wait_for_load_state('networkidle')
    pagina.wait_for_timeout(500)
    if on_paso: on_paso("Ejecución")
    pagina.get_by_role("button", name="Estado de ítems").click()
    pagina.wait_for_load_state('networkidle')
    pagina.wait_for_timeout(500)
    if on_paso: on_paso("Estado de ítems")
    frame = pagina.locator("#pagina1").content_frame
    frame.get_by_label("Estados").select_option("0")
    pagina.wait_for_timeout(500)
    frame.get_by_role("button", name="Consultar").click(force=True)
    pagina.wait_for_timeout(3000)
    if on_paso: on_paso("Consultar")
    frame.get_by_title("Opciones").click(force=True)
    pagina.wait_for_timeout(3000)
    if on_paso: on_paso("Opciones")
    frame.get_by_label("Estados").select_option("2")
    pagina.wait_for_timeout(500)
    frame.get_by_role("button", name="Consultar").click(force=True)
    pagina.wait_for_timeout(3000)
    if on_paso: on_paso("Consultar")
    frame.get_by_title("Opciones").click(force=True)
    pagina.wait_for_timeout(3000)
    if on_paso: on_paso("Opciones")
    frame.get_by_label("Estados").select_option("-1")
    pagina.wait_for_timeout(500)
    frame.get_by_role("button", name="Consultar").click(force=True)
    pagina.wait_for_timeout(3000)
    if on_paso: on_paso("Consultar")
    frame.get_by_role("cell", name="1.001", exact=True).click(force=True)
    pagina.wait_for_timeout(3000)
    if on_paso: on_paso("1.001")
    pagina.get_by_title("Administración de proyectos").locator("#textomodulo").click()
    pagina.wait_for_load_state('networkidle')
    pagina.wait_for_timeout(500)
    if on_paso: on_paso("Administración de proyectos")
    pagina.get_by_role("button", name="Almacén").click()
    pagina.wait_for_load_state('networkidle')
    pagina.wait_for_timeout(500)
    if on_paso: on_paso("Almacén")
    pagina.get_by_role("button", name="PEDIDOS").click()
    pagina.wait_for_load_state('networkidle')
    pagina.wait_for_timeout(500)
    if on_paso: on_paso("PEDIDOS")
    pagina.get_by_role("button", name="Pedidos proyecto").click()
    pagina.wait_for_load_state('networkidle')
    pagina.wait_for_timeout(500)
    if on_paso: on_paso("Pedidos proyecto")
    frame.get_by_role("button", name="Nuevo pedido").click(force=True)
    pagina.wait_for_timeout(3000)
    if on_paso: on_paso("Nuevo pedido")
    frame.get_by_role("button", name="Por Actividad").click(force=True)
    pagina.wait_for_timeout(3000)
    if on_paso: on_paso("Por Actividad")
    frame.get_by_role("combobox", name="Buscar actividades").click(force=True)
    pagina.wait_for_timeout(3000)
    if on_paso: on_paso("Buscar actividades")
    frame.get_by_text("1.001 LOCALIZACION Y").click(force=True)
    pagina.wait_for_timeout(3000)
    if on_paso: on_paso("1.001 LOCALIZACION Y")

    return {
        "prueba": "Validar Actividad",
        "estado": "ok",
    }
