"""
Prueba: Test Datagrid
Generada con playwright codegen
"""
import re


def ejecutar(pagina, frame, on_paso=None):
    """
    Ejecuta la prueba 'Test Datagrid'.
    Recibe la pagina ya logueada en SINCO (despues de seleccionar empresa).
    La prueba incluye la navegacion al modulo correspondiente.
    on_paso: callback opcional para reportar progreso con screenshot.
    Retorna dict con el resultado.
    """
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
    pagina.get_by_role("button", name="Pedidos proyecto", exact=True).click()
    pagina.wait_for_load_state('networkidle')
    pagina.wait_for_timeout(500)
    if on_paso: on_paso("Pedidos proyecto")
    frame = pagina.locator("#pagina1").content_frame
    frame.get_by_role("button", name="Nuevo pedido").click(force=True)
    pagina.wait_for_timeout(3000)
    if on_paso: on_paso("Nuevo pedido")
    frame.get_by_role("combobox", name="Buscar insumo").click(force=True)
    pagina.wait_for_timeout(3000)
    if on_paso: on_paso("Buscar insumo")
    frame.get_by_role("combobox", name="Buscar insumo").fill("101")
    pagina.wait_for_timeout(1000)
    frame.get_by_text("101 - SA - Cuadrilla 1oficial").click(force=True)
    pagina.wait_for_timeout(3000)
    if on_paso: on_paso("101 - SA - Cuadrilla 1oficial")
    frame.get_by_role("row").last.get_by_role("gridcell").last.click(force=True)
    pagina.wait_for_timeout(3000)
    if on_paso: on_paso("Accion")
    frame.locator(".MuiDataGrid-cell--editing input, .MuiBox-root input:visible").last.fill("1")
    pagina.wait_for_timeout(1000)
    frame.get_by_text("Ingrese cantidad para guardar101 - SA - Cuadrilla 1oficial 2 ayudantes-[M]Cant").click(force=True)
    pagina.wait_for_timeout(3000)
    if on_paso: on_paso("Ingrese cantidad para guardar101 - SA - Cuadrilla 1oficial 2 ayudantes-[M]Cant")
    frame.get_by_role("heading", name="Guardado exitoso").click(force=True)
    pagina.wait_for_timeout(3000)
    if on_paso: on_paso("Guardado exitoso")

    return {
        "prueba": "Test Datagrid",
        "estado": "ok",
    }
