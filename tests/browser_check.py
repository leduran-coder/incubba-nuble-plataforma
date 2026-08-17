"""
Verificación end-to-end con navegador real (Playwright) contra la app
Streamlit ya corriendo en localhost:8501. Revisa que no aparezcan errores
de Streamlit en pantalla al navegar por cada página, y ejercita el flujo
de importar CSV + evaluar una postulación.
"""
import re
import sys
import time

from playwright.sync_api import sync_playwright

BASE = "http://localhost:8501"
SHOTS = "/root/incubba-platform/tests/screenshots"

import os
os.makedirs(SHOTS, exist_ok=True)

ERRORS = []


def check_no_error(page, label):
    time.sleep(0.6)
    content = page.content()
    for marca in ["Traceback (most recent call last)", "StreamlitAPIException",
                  "This app has encountered an error", "NameError", "AttributeError:",
                  "KeyError:", "TypeError:"]:
        if marca in content:
            ERRORS.append(f"[{label}] posible error en pantalla: contiene '{marca}'")


with sync_playwright() as p:
    browser = p.chromium.launch(executable_path="/opt/pw-browsers/chromium", headless=True)
    page = browser.new_page(viewport={"width": 1440, "height": 900})

    page.goto(BASE, wait_until="networkidle", timeout=30000)
    check_no_error(page, "Inicio (sin login)")
    page.screenshot(path=f"{SHOTS}/00_inicio_sin_login.png", full_page=True)

    # --- Login ---
    page.get_by_label("Correo").fill("admin@incubba.cl")
    page.get_by_label("Contraseña", exact=False).fill("incubba2026")
    page.get_by_role("button", name="Ingresar").click()
    page.wait_for_timeout(1500)
    check_no_error(page, "Inicio (post-login)")
    page.screenshot(path=f"{SHOTS}/01_inicio_post_login.png", full_page=True)

    def ir_a_pagina(nombre_visible):
        link = page.get_by_role("link", name=re.compile(nombre_visible))
        link.first.click()
        page.wait_for_timeout(1800)

    for nombre in ["Postulaciones", "Evaluación", "Resultados", "Estadísticas", "Configuración"]:
        try:
            ir_a_pagina(nombre)
            check_no_error(page, nombre)
            page.screenshot(path=f"{SHOTS}/nav_{nombre}.png", full_page=True)
        except Exception as e:
            ERRORS.append(f"[{nombre}] excepción de Playwright al navegar: {e}")

    # --- Importar CSV en Configuración ---
    try:
        ir_a_pagina("Configuración")
        page.get_by_role("tab", name=re.compile("Importar")).click()
        page.wait_for_timeout(500)
        page.locator('input[type="file"]').set_input_files(
            "/root/incubba-platform/sample_data/postulaciones_ejemplo.csv"
        )
        page.wait_for_timeout(2500)
        check_no_error(page, "Configuración - CSV subido")
        page.screenshot(path=f"{SHOTS}/02_config_csv_subido.png", full_page=True)

        boton_importar = page.get_by_role("button", name="Importar postulaciones")
        boton_importar.click()
        page.wait_for_timeout(2500)
        check_no_error(page, "Configuración - import ejecutado")
        page.screenshot(path=f"{SHOTS}/03_config_import_hecho.png", full_page=True)
    except Exception as e:
        ERRORS.append(f"[Importar CSV] excepción: {e}")

    # --- Revisar Postulaciones ya con datos ---
    try:
        ir_a_pagina("Postulaciones")
        check_no_error(page, "Postulaciones con datos")
        page.screenshot(path=f"{SHOTS}/04_postulaciones_con_datos.png", full_page=True)
    except Exception as e:
        ERRORS.append(f"[Postulaciones con datos] excepción: {e}")

    # --- Evaluación: calificar etapa 1 de la primera postulación ---
    try:
        ir_a_pagina("Evaluación")
        page.wait_for_timeout(1000)
        radios_labels = page.get_by_text("Recomendado", exact=True)
        if radios_labels.count() > 0:
            radios_labels.first.click()
        page.wait_for_timeout(500)
        check_no_error(page, "Evaluación - antes de guardar")
        boton_guardar = page.get_by_role("button", name=re.compile("Guardar evaluación"))
        if boton_guardar.count() > 0:
            boton_guardar.first.click()
            page.wait_for_timeout(1500)
        check_no_error(page, "Evaluación - despues de guardar")
        page.screenshot(path=f"{SHOTS}/05_evaluacion_guardada.png", full_page=True)
    except Exception as e:
        ERRORS.append(f"[Evaluación] excepción: {e}")

    # --- Estadísticas y Resultados con datos reales ---
    try:
        ir_a_pagina("Estadísticas")
        check_no_error(page, "Estadísticas con datos")
        page.screenshot(path=f"{SHOTS}/06_estadisticas_con_datos.png", full_page=True)
    except Exception as e:
        ERRORS.append(f"[Estadísticas con datos] excepción: {e}")

    try:
        ir_a_pagina("Resultados")
        check_no_error(page, "Resultados con datos")
        page.screenshot(path=f"{SHOTS}/07_resultados_con_datos.png", full_page=True)
    except Exception as e:
        ERRORS.append(f"[Resultados con datos] excepción: {e}")

    browser.close()

if ERRORS:
    print("❌ SE ENCONTRARON POSIBLES PROBLEMAS:")
    for e in ERRORS:
        print(" -", e)
    sys.exit(1)
else:
    print("✅ Navegación completa sin errores visibles en pantalla.")
