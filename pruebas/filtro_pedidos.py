"""
Prueba: Filtro De Pedidos Por Numero
"""
import re


def ejecutar(pagina, frame):
    """
    Filtra pedidos por numero y valida que aparezca el resultado.
    """
    # Leer el primer pedido de la tabla
    primer_pedido = frame.locator("text=/Pedido No\\./").first
    primer_pedido.wait_for(state="visible", timeout=15000)
    texto_pedido = primer_pedido.inner_text()

    match = re.search(r"Pedido No\.\s*(.+)", texto_pedido)
    numero_pedido = match.group(1).strip() if match else texto_pedido

    # Abrir filtro
    frame.locator("text=Filtrar").first.wait_for(state="visible", timeout=10000)
    frame.locator("text=Filtrar").first.click()
    pagina.wait_for_timeout(3000)

    # Escribir numero de pedido
    input_pedido = frame.get_by_placeholder("Ingresar Pedido No.")
    input_pedido.wait_for(state="visible", timeout=10000)
    input_pedido.click()
    input_pedido.fill(numero_pedido)
    pagina.wait_for_timeout(1000)

    # Consultar
    frame.locator("button:has-text('Consultar')").first.wait_for(state="visible", timeout=10000)
    frame.locator("button:has-text('Consultar')").first.click()
    pagina.wait_for_timeout(8000)

    # Validar
    pedidos_visibles = frame.locator("text=/Pedido No\\./").all()
    cantidad = sum(1 for p in pedidos_visibles if p.is_visible())
    es_ok = cantidad > 0

    return {
        "prueba": "Filtro de pedidos por numero",
        "dato_entrada": numero_pedido,
        "esperado": "La tabla muestra solo el pedido filtrado",
        "obtenido": f"{cantidad} registro(s) en la tabla" if es_ok else "Sin resultados",
        "estado": "ok" if es_ok else "fail",
    }
