"""
Prueba: Crearpedidoactividad
Generada con playwright codegen
"""


def ejecutar(pagina, frame):
    """
    Ejecuta la prueba 'Crearpedidoactividad'.
    Recibe la pagina ya logueada y el frame de Pedidos Proyecto.
    Retorna dict con el resultado.
    """
    pagina.get_by_text("ADPRO").click()
    pagina.get_by_role("button", name="Almacén").click()
    pagina.get_by_title("Ruta: ADPRO/Almacén/PEDIDOS").click()
    pagina.get_by_role("button", name="Pedidos proyecto").click()
    frame.get_by_role("button", name="Nuevo pedido").click()
    frame.get_by_role("button", name="Por Actividad").click()
    frame.get_by_role("combobox", name="Buscar actividades").click()
    frame.get_by_text("1.001 LOCALIZACION Y").click()
    frame.locator("div:nth-child(10) > .MuiBox-root").first.click()
    frame.get_by_role("row", name="101 EQUIPO DE TOPOGRAFIA. MS").get_by_role("textbox").fill("1")
    frame.locator(".MuiBox-root > .MuiPaper-root > div > div > div:nth-child(2)").click()
    frame.get_by_role("heading", name="Guardado exitoso").dblclick()
    pagina.close()

    return {
        "prueba": "Crearpedidoactividad",
        "estado": "ok",
    }
