"""
Prueba: Contratos
Generada con playwright codegen
"""
import re


def ejecutar(pagina, frame, on_paso=None):
    """
    Ejecuta la prueba 'Contratos'.
    Recibe la pagina ya logueada en SINCO (despues de seleccionar empresa).
    La prueba incluye la navegacion al modulo correspondiente.
    on_paso: callback opcional para reportar progreso con screenshot.
    Retorna dict con el resultado.
    """
    pagina.get_by_text("ADPRO").click()
    pagina.wait_for_load_state('networkidle')
    pagina.wait_for_timeout(500)
    if on_paso: on_paso("ADPRO")
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
    frame.get_by_role("button", name="").click(force=True)
    pagina.wait_for_timeout(3000)
    if on_paso: on_paso("")
    frame.get_by_role("textbox", name="Buscar contratista").click(force=True)
    pagina.wait_for_timeout(3000)
    if on_paso: on_paso("Buscar contratista")
    frame.get_by_role("textbox", name="Buscar contratista").fill("_")
    pagina.wait_for_timeout(1000)
    frame.get_by_text("ACERO SUAREZ INGRID PAOLA").click(force=True)
    pagina.wait_for_timeout(3000)
    if on_paso: on_paso("ACERO SUAREZ INGRID PAOLA")
    frame.get_by_role("button", name="Aceptar").click(force=True)
    pagina.wait_for_timeout(3000)
    if on_paso: on_paso("Aceptar")

    return {
        "prueba": "Contratos",
        "estado": "ok",
    }
