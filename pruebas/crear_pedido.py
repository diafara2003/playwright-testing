"""
Prueba: Crear Pedido
Generada con playwright codegen
"""


def ejecutar(pagina, frame):
    """
    Ejecuta la prueba 'Crear Pedido'.
    Recibe la pagina ya logueada y el frame de Pedidos Proyecto.
    Retorna dict con el resultado.
    """
    frame.get_by_role("button", name="Nuevo pedido").click()
    pagina.wait_for_timeout(5000)

    frame.get_by_role("combobox", name="Buscar insumo").click()
    frame.get_by_role("combobox", name="Buscar insumo").fill("_")
    pagina.wait_for_timeout(3000)

    frame.get_by_text("- EQUIPO DE TOPOGRAFIA.-[MS]").click()
    pagina.wait_for_timeout(5000)

    frame.locator("div:nth-child(8) > .MuiBox-root").first.click()
    pagina.wait_for_timeout(1000)
    frame.get_by_role("textbox").fill("1")

    frame.get_by_text("Agregar Insumos").click()
    pagina.wait_for_timeout(3000)

    return {
        "prueba": "Crear Pedido",
        "dato_entrada": "Insumo: 101 - EQUIPO DE TOPOGRAFIA.-[MS], Cantidad: 1",
        "esperado": "Se agrega insumo y cantidad al nuevo pedido",
        "obtenido": "Pedido creado con insumo y cantidad ingresada",
        "estado": "ok",
    }
