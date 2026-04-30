"""
Prueba: Crearpedidoinsumo
Generada con playwright codegen
"""
import re


def ejecutar(pagina, frame, on_paso=None):
    """
    Ejecuta la prueba 'Crearpedidoinsumo'.
    Recibe la pagina ya logueada y el frame de Pedidos Proyecto.
    on_paso: callback opcional para reportar progreso con screenshot.
    Retorna dict con el resultado.
    """
    # Navegacion al modulo
    pagina.get_by_title("Administración de proyectos").click()
    pagina.wait_for_timeout(2000)
    if on_paso: on_paso("ADPRO")
    pagina.get_by_title("Ruta: ADPRO/Almacén").click()
    pagina.wait_for_timeout(2000)
    if on_paso: on_paso("Almacen")
    pagina.get_by_role("button", name="PEDIDOS").click()
    pagina.wait_for_timeout(2000)
    pagina.get_by_role("button", name="Pedidos proyecto").click()
    pagina.wait_for_load_state("networkidle")
    pagina.wait_for_timeout(8000)
    if on_paso: on_paso("Pedidos proyecto")

    # Acciones de la prueba
    frame = pagina.locator("#pagina1").content_frame
    frame.get_by_role("button", name="Nuevo pedido").click(force=True)
    pagina.wait_for_timeout(3000)
    if on_paso: on_paso("Nuevo pedido")
    frame.get_by_role("combobox", name="Buscar insumo").click(force=True)
    pagina.wait_for_timeout(3000)
    if on_paso: on_paso("Buscar insumo")
    frame.get_by_role("combobox", name="Buscar insumo").fill("_")
    pagina.wait_for_timeout(1000)
    frame.get_by_text("1008 - TOPE PUERTA CON").click(force=True)
    pagina.wait_for_timeout(3000)
    if on_paso: on_paso("1008 - TOPE PUERTA CON")

    return {
        "prueba": "Crearpedidoinsumo",
        "estado": "ok",
    }
