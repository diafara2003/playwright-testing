"""
Script de inspeccion del DOM de ADPRO.
Navega a paginas de ADPRO, extrae atributos del DOM dentro del iframe #pagina1,
detecta tecnologia (React/MUI vs HTML puro) y genera reporte.
"""
import os
import re
import json
from datetime import datetime
from playwright.sync_api import sync_playwright

USUARIO = "office"
PASSWORD = "Office123"
EMPRESA = "SincoPlus Pruebas Módulos"
URL_BASE = "https://www4.sincoerp.com/SincoPlusPruebasModulos2022/V3/Marco/Seleccion_iv.aspx"

# Rutas a inspeccionar - agregar mas con el formato: ("title"|"button"|"text", "Nombre visible")
RUTAS_ADPRO = [
    {
        "nombre": "Pedidos Proyecto",
        "ruta": [
            ("title", "Administración de proyectos"),
            ("title", "Ruta: ADPRO/Almacén"),
            ("button", "PEDIDOS"),
            ("button", "Pedidos proyecto"),
        ],
    },
]


def hacer_login(pagina):
    """Login en SINCO y seleccionar empresa."""
    pagina.goto(URL_BASE)
    pagina.wait_for_load_state("networkidle")

    pagina.locator("input:visible").nth(0).click()
    pagina.keyboard.type(USUARIO)
    pagina.locator("input:visible").nth(1).click()
    pagina.keyboard.type(PASSWORD)

    pagina.locator("button:visible").nth(0).click()
    pagina.wait_for_load_state("networkidle")
    pagina.wait_for_timeout(5000)

    pagina.locator("#ddlEmpresa").select_option(label=EMPRESA)
    pagina.wait_for_timeout(3000)

    boton = pagina.locator(
        "button:has-text('Ingresar'), input[value='Ingresar'], "
        "a:has-text('Ingresar'), :text('Ingresar')"
    ).first
    boton.wait_for(state="visible", timeout=10000)
    boton.click()
    pagina.wait_for_load_state("networkidle")
    pagina.wait_for_timeout(5000)
    return pagina.url


def navegar_menu(pagina, ruta):
    """Navega por el menu usando la lista de tuplas (tipo, texto)."""
    for tipo, texto in ruta:
        if tipo == "title":
            pagina.get_by_title(texto).click()
        elif tipo == "button":
            pagina.get_by_role("button", name=texto).click()
        elif tipo == "text":
            pagina.locator(f"text={texto}").first.click()
        pagina.wait_for_timeout(2000)
    pagina.wait_for_load_state("networkidle")
    pagina.wait_for_timeout(5000)


def extraer_dom(frame):
    """Extrae informacion de elementos interactivos del DOM del frame."""
    return frame.evaluate("""() => {
        const selectores = 'input, button, select, textarea, a, [role], [data-testid], [aria-label], [data-field], [data-id], [data-rowindex], [aria-colindex], [aria-rowindex]';
        const elementos = document.querySelectorAll(selectores);
        const resultado = [];
        for (const el of elementos) {
            const clases = [...el.classList];
            resultado.push({
                tag: el.tagName.toLowerCase(),
                id: el.id || null,
                classes: clases,
                role: el.getAttribute('role'),
                ariaLabel: el.getAttribute('aria-label'),
                ariaColindex: el.getAttribute('aria-colindex'),
                ariaRowindex: el.getAttribute('aria-rowindex'),
                name: el.getAttribute('name'),
                title: el.getAttribute('title'),
                placeholder: el.getAttribute('placeholder'),
                dataTestId: el.getAttribute('data-testid'),
                dataField: el.getAttribute('data-field'),
                dataId: el.getAttribute('data-id'),
                dataRowindex: el.getAttribute('data-rowindex'),
                type: el.getAttribute('type'),
                text: (el.textContent || '').trim().substring(0, 80),
                tieneIdReact: /(_r_\d+_|:r[0-9a-f]+:)/.test(el.id || ''),
                tieneCssEmotion: clases.some(c => /^css-[a-z0-9]+$/.test(c)),
                tieneMui: clases.some(c => c.startsWith('Mui')),
            });
        }
        return resultado;
    }""")


def detectar_tecnologia(elementos):
    """Detecta si la pagina usa React/MUI o HTML puro."""
    tiene_mui = any(e["tieneMui"] for e in elementos)
    tiene_css_emotion = any(e["tieneCssEmotion"] for e in elementos)
    tiene_id_react = any(e["tieneIdReact"] for e in elementos)
    tiene_aspnet = any(
        e["id"] and ("ctl00" in e["id"] or "ContentPlaceHolder" in e["id"])
        for e in elementos
    )

    if tiene_mui or tiene_css_emotion or tiene_id_react:
        return "React/MUI"
    elif tiene_aspnet:
        return "HTML puro (ASP.NET)"
    else:
        return "Desconocido"


def analizar_atributos(elementos):
    """Analiza cobertura de atributos estables vs fragiles."""
    total = len(elementos)
    interactivos = [e for e in elementos if e["tag"] in ("input", "button", "select", "textarea", "a") or e["role"]]
    total_interactivos = len(interactivos)

    con_role = sum(1 for e in interactivos if e["role"])
    con_aria_label = sum(1 for e in interactivos if e["ariaLabel"])
    con_name = sum(1 for e in interactivos if e["name"])
    con_title = sum(1 for e in interactivos if e["title"])
    con_placeholder = sum(1 for e in interactivos if e["placeholder"])
    con_data_testid = sum(1 for e in interactivos if e["dataTestId"])
    con_texto = sum(1 for e in interactivos if e["text"])

    con_id_react = sum(1 for e in interactivos if e["tieneIdReact"])
    con_css_emotion = sum(1 for e in interactivos if e["tieneCssEmotion"])
    con_mui = sum(1 for e in interactivos if e["tieneMui"])

    return {
        "total_elementos": total,
        "total_interactivos": total_interactivos,
        "estables": {
            "role": con_role,
            "aria-label": con_aria_label,
            "name": con_name,
            "title": con_title,
            "placeholder": con_placeholder,
            "data-testid": con_data_testid,
            "texto_visible": con_texto,
        },
        "fragiles": {
            "id_react_dinamico": con_id_react,
            "css_emotion": con_css_emotion,
            "clases_mui": con_mui,
        },
    }


def imprimir_reporte(resultado):
    """Imprime reporte en consola."""
    print(f"\n{'=' * 60}")
    print(f"  {resultado['nombre']}")
    print(f"  Tecnologia: {resultado['tecnologia']}")
    print(f"{'=' * 60}")

    a = resultado["analisis"]
    print(f"\n  Elementos totales: {a['total_elementos']}")
    print(f"  Elementos interactivos: {a['total_interactivos']}")

    print(f"\n  ATRIBUTOS ESTABLES (usables como selectores):")
    for attr, count in a["estables"].items():
        barra = "#" * min(count, 40)
        print(f"    {attr:15s}: {count:3d}  {barra}")

    print(f"\n  ATRIBUTOS FRAGILES (cambian entre sesiones):")
    for attr, count in a["fragiles"].items():
        barra = "!" * min(count, 40)
        print(f"    {attr:20s}: {count:3d}  {barra}")

    # Mostrar elementos con IDs React dinamicos
    fragiles = [e for e in resultado["elementos"] if e["tieneIdReact"]]
    if fragiles:
        print(f"\n  ELEMENTOS CON IDs REACT DINAMICOS ({len(fragiles)}):")
        for e in fragiles[:10]:
            alternativas = []
            if e["role"]:
                alternativas.append(f'role="{e["role"]}"')
            if e["ariaLabel"]:
                alternativas.append(f'aria-label="{e["ariaLabel"]}"')
            if e["placeholder"]:
                alternativas.append(f'placeholder="{e["placeholder"]}"')
            if e["name"]:
                alternativas.append(f'name="{e["name"]}"')
            alt_str = " | ".join(alternativas) if alternativas else "SIN ALTERNATIVA ESTABLE"
            print(f"    <{e['tag']}> id=\"{e['id']}\" -> {alt_str}")

    # Mostrar estructura del DataGrid (roles ARIA)
    grid_elements = [e for e in resultado["elementos"] if e["role"] in ("grid", "treegrid", "row", "gridcell", "columnheader", "rowgroup")]
    if grid_elements:
        print(f"\n  ESTRUCTURA DATAGRID ({len(grid_elements)} elementos):")
        roles_count = {}
        for e in grid_elements:
            roles_count[e["role"]] = roles_count.get(e["role"], 0) + 1
        for role, count in sorted(roles_count.items()):
            print(f"    role=\"{role}\": {count}")

        # Mostrar columnas (columnheader)
        headers = [e for e in grid_elements if e["role"] == "columnheader"]
        if headers:
            print(f"\n  COLUMNAS DEL DATAGRID ({len(headers)}):")
            for h in headers:
                field = h.get("dataField", "?")
                col_idx = h.get("ariaColindex", "?")
                texto = h["text"][:40] if h["text"] else ""
                print(f"    col={col_idx} field=\"{field}\" texto=\"{texto}\"")

        # Mostrar ejemplo de celdas (primeras filas)
        celdas = [e for e in grid_elements if e["role"] == "gridcell"]
        if celdas:
            print(f"\n  CELDAS DEL DATAGRID (primeras 10 de {len(celdas)}):")
            for c in celdas[:10]:
                col_idx = c.get("ariaColindex", "?")
                row_idx = c.get("ariaRowindex", "?")
                field = c.get("dataField", "?")
                texto = c["text"][:30] if c["text"] else ""
                print(f"    [{row_idx},{col_idx}] field=\"{field}\" texto=\"{texto}\"")

        # Mostrar filas con data-id
        filas = [e for e in grid_elements if e["role"] == "row" and e.get("dataId")]
        if filas:
            print(f"\n  FILAS CON data-id ({len(filas)}):")
            for f in filas[:5]:
                print(f"    data-id=\"{f['dataId']}\" rowindex={f.get('dataRowindex', '?')}")


def main():
    os.makedirs("reportes", exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    dir_reporte = f"reportes/inspeccion_{timestamp}"
    os.makedirs(dir_reporte, exist_ok=True)
    os.makedirs(f"{dir_reporte}/screenshots", exist_ok=True)

    resultados = []

    with sync_playwright() as p:
        navegador = p.chromium.launch(headless=False)
        contexto = navegador.new_context(ignore_https_errors=True)
        pagina = contexto.new_page()

        print("Haciendo login en SINCO...")
        url_post_login = hacer_login(pagina)
        print(f"Login exitoso. URL: {url_post_login}")

        for ruta_info in RUTAS_ADPRO:
            nombre = ruta_info["nombre"]
            print(f"\nNavegando a: {nombre}...")

            try:
                navegar_menu(pagina, ruta_info["ruta"])

                # Esperar a que el iframe cargue
                pagina.locator("#pagina1").wait_for(state="attached", timeout=10000)
                pagina.wait_for_timeout(3000)

                # Screenshot
                screenshot_path = f"{dir_reporte}/screenshots/{nombre.replace(' ', '_')}.png"
                pagina.screenshot(path=screenshot_path)
                print(f"  Screenshot: {screenshot_path}")

                # Extraer DOM del iframe - necesitamos el Frame real, no FrameLocator
                iframe_element = pagina.locator("#pagina1")
                frame_real = iframe_element.content_frame
                # content_frame retorna FrameLocator; para evaluate necesitamos el Frame
                # Usamos page.frame() para obtener el Frame real
                frames = pagina.frames
                frame_obj = None
                for f in frames:
                    if "pagina1" in (f.name or "") or f != pagina.main_frame:
                        frame_obj = f
                        break
                if not frame_obj:
                    print("  WARN: No se encontro el frame, usando primer frame hijo")
                    frame_obj = frames[1] if len(frames) > 1 else frames[0]
                elementos = extraer_dom(frame_obj)
                tecnologia = detectar_tecnologia(elementos)
                analisis = analizar_atributos(elementos)

                # Inspeccion profunda: buscar TODOS los roles y clases MUI del grid
                estructura_grid = frame_obj.evaluate("""() => {
                    const todos = document.querySelectorAll('*');
                    const roles = {};
                    const muiClasses = {};
                    const dataAttrs = [];
                    for (const el of todos) {
                        const role = el.getAttribute('role');
                        if (role) roles[role] = (roles[role] || 0) + 1;
                        for (const cls of el.classList) {
                            if (cls.startsWith('MuiDataGrid') || cls.startsWith('MuiTable')) {
                                muiClasses[cls] = (muiClasses[cls] || 0) + 1;
                            }
                        }
                        if (el.getAttribute('data-field') || el.getAttribute('data-id') || el.getAttribute('data-rowindex')) {
                            dataAttrs.push({
                                tag: el.tagName.toLowerCase(),
                                role: role,
                                dataField: el.getAttribute('data-field'),
                                dataId: el.getAttribute('data-id'),
                                dataRowindex: el.getAttribute('data-rowindex'),
                                ariaColindex: el.getAttribute('aria-colindex'),
                                ariaRowindex: el.getAttribute('aria-rowindex'),
                                text: (el.textContent || '').trim().substring(0, 50),
                                classes: [...el.classList].filter(c => c.startsWith('Mui')).join(', '),
                            });
                        }
                    }
                    return { roles, muiClasses, dataAttrs: dataAttrs.slice(0, 30) };
                }""")

                print(f"\n  ROLES ARIA EN TODO EL DOM:")
                for role, count in sorted(estructura_grid["roles"].items()):
                    print(f"    role=\"{role}\": {count}")

                if estructura_grid["muiClasses"]:
                    print(f"\n  CLASES MUI DATAGRID/TABLE:")
                    for cls, count in sorted(estructura_grid["muiClasses"].items()):
                        print(f"    {cls}: {count}")

                if estructura_grid["dataAttrs"]:
                    print(f"\n  ELEMENTOS CON data-field/data-id/data-rowindex ({len(estructura_grid['dataAttrs'])}):")
                    for d in estructura_grid["dataAttrs"][:15]:
                        print(f"    <{d['tag']}> role={d['role']} field={d['dataField']} id={d['dataId']} row={d['dataRowindex']} col={d['ariaColindex']} texto=\"{d['text'][:30]}\"")

                # Inspeccion extra: estructura de tabla (tr, td, th)
                tabla_info = frame_obj.evaluate("""() => {
                    const tablas = document.querySelectorAll('table');
                    const info = [];
                    for (const tabla of tablas) {
                        const headers = [...tabla.querySelectorAll('th')].map(th => ({
                            texto: (th.textContent || '').trim().substring(0, 30),
                            classes: [...th.classList].filter(c => c.startsWith('Mui')).join(', '),
                        }));
                        const filas = tabla.querySelectorAll('tbody tr');
                        const primera_fila = filas.length > 0 ? [...filas[0].querySelectorAll('td')].map(td => ({
                            texto: (td.textContent || '').trim().substring(0, 30),
                            classes: [...td.classList].filter(c => c.startsWith('Mui')).join(', '),
                        })) : [];
                        info.push({
                            clases_tabla: [...tabla.classList].join(', '),
                            num_filas: filas.length,
                            headers: headers,
                            primera_fila: primera_fila,
                        });
                    }
                    // Buscar divs que parezcan grids custom
                    const divGrids = document.querySelectorAll('[class*="grid"], [class*="Grid"], [class*="table"], [class*="Table"]');
                    const grids_custom = [...divGrids].slice(0, 5).map(g => ({
                        tag: g.tagName.toLowerCase(),
                        classes: [...g.classList].join(', '),
                        hijos: g.children.length,
                    }));
                    return { tablas: info, grids_custom: grids_custom };
                }""")

                if tabla_info["tablas"]:
                    for i, t in enumerate(tabla_info["tablas"]):
                        print(f"\n  TABLA #{i+1} (clases: {t['clases_tabla']}, {t['num_filas']} filas):")
                        if t["headers"]:
                            print(f"    HEADERS: {' | '.join(h['texto'] for h in t['headers'])}")
                        if t["primera_fila"]:
                            print(f"    FILA 1:  {' | '.join(c['texto'][:20] for c in t['primera_fila'])}")

                if tabla_info["grids_custom"]:
                    print(f"\n  DIVS CON CLASES GRID/TABLE:")
                    for g in tabla_info["grids_custom"]:
                        print(f"    <{g['tag']}> classes=\"{g['classes'][:80]}\" hijos={g['hijos']}")

                resultado = {
                    "nombre": nombre,
                    "tecnologia": tecnologia,
                    "analisis": analisis,
                    "elementos": elementos,
                }
                resultados.append(resultado)
                imprimir_reporte(resultado)

            except Exception as e:
                print(f"  ERROR en {nombre}: {e}")
                resultados.append({"nombre": nombre, "error": str(e)})

            # Volver al menu principal
            pagina.goto(url_post_login)
            pagina.wait_for_load_state("networkidle")
            pagina.wait_for_timeout(3000)

        navegador.close()

    # Guardar reporte JSON (sin elementos completos para no ser enorme)
    reporte_resumen = []
    for r in resultados:
        if "error" in r:
            reporte_resumen.append(r)
        else:
            reporte_resumen.append({
                "nombre": r["nombre"],
                "tecnologia": r["tecnologia"],
                "analisis": r["analisis"],
                "elementos_fragiles": [e for e in r["elementos"] if e["tieneIdReact"] or e["tieneCssEmotion"]],
            })

    reporte_path = f"{dir_reporte}/reporte.json"
    with open(reporte_path, "w", encoding="utf-8") as f:
        json.dump(reporte_resumen, f, indent=2, ensure_ascii=False)

    print(f"\n{'=' * 60}")
    print(f"Reporte guardado en: {reporte_path}")
    print(f"Screenshots en: {dir_reporte}/screenshots/")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
