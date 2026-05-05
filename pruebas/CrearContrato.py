"""
Prueba: Crearcontrato
Generada con playwright codegen
"""
import re


def ejecutar(pagina, frame, on_paso=None):
    """
    Ejecuta la prueba 'Crearcontrato'.
    Recibe la pagina ya logueada en SINCO (despues de seleccionar empresa).
    La prueba incluye la navegacion al modulo correspondiente.
    on_paso: callback opcional para reportar progreso con screenshot.
    Retorna dict con el resultado.
    """
    pagina.get_by_title("Administración de proyectos").click()
    pagina.wait_for_load_state('networkidle')
    pagina.wait_for_timeout(500)
    if on_paso: on_paso("Administración de proyectos")
    pagina.get_by_role("button", name="Contratos").click()
    pagina.wait_for_load_state('networkidle')
    pagina.wait_for_timeout(500)
    if on_paso: on_paso("Contratos")
    pagina.get_by_role("button", name="CONTRATOS", exact=True).click()
    pagina.wait_for_load_state('networkidle')
    pagina.wait_for_timeout(500)
    if on_paso: on_paso("CONTRATOS")
    pagina.get_by_role("button", name="Contratos generales").click()
    pagina.wait_for_load_state('networkidle')
    pagina.wait_for_timeout(500)
    if on_paso: on_paso("Contratos generales")
    frame = pagina.locator("#pagina1").content_frame
    frame.get_by_role("button", name="Consultar").click()
    pagina.wait_for_timeout(3000)
    if on_paso: on_paso("Consultar")
    frame.get_by_text("4", exact=True).click()
    pagina.wait_for_timeout(3000)
    if on_paso: on_paso("4")

    return {
        "prueba": "Crearcontrato",
        "estado": "ok",
    }
