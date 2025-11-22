from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import time

def go_to_configured_tab(driver):
    """Hace clic en el botón 'Configured'."""
    configured_btn = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, '//*[@id="navbar-main"]/ul[1]/li[2]/a'))
    )
    configured_btn.click()
    time.sleep(1)


def search_user(driver, user):
    """Busca un usuario en el search bar."""
    search_input = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, '//*[@id="free_text"]'))
    )
    search_input.clear()
    search_input.send_keys(user)
    time.sleep(1)
    search_input.send_keys("\n")


def open_first_result(driver):
    """Abre el primer resultado si existe al menos un <tr class='valign-center'>.
    Devuelve True si abre uno, False si no hay resultados.
    """

    try:
        # 1. Buscar filas válidas
        rows = WebDriverWait(driver, 5).until(
            EC.presence_of_all_elements_located(
                (By.XPATH, "//tr[contains(@class, 'valign-center')]")
            )
        )

    except:
        print("⚠️ No hay resultados para este usuario.")
        return False

    if len(rows) == 0:
        print("⚠️ No se encontró ningún resultado.")
        return False

    # 2. Seleccionar la PRIMER fila válida
    first_row = rows[0]

    try:
        # 3. Dentro de esa fila, ubicar el botón 'View'
        view_btn = first_row.find_element(By.XPATH, ".//a[contains(., 'View')]")
        view_btn.click()
        time.sleep(1)
        print("✔️ Primer resultado abierto.")
        return True

    except Exception as e:
        print("❌ Error al intentar abrir el primer resultado:", e)
        return False
