from selenium.webdriver.common.by import By
from utils.helpers import wait_clickable, wait_visible
from utils.logger import get_logger
import time

logger = get_logger(__name__)

def go_to_configured_tab(driver, timeout=10):
    locator = (By.XPATH, "//*[@id='navbar-main']//a[contains(normalize-space(.), 'Configured')]")
    if wait_clickable(driver, locator, timeout=timeout):
        driver.find_element(*locator).click()
        logger.info("Clicked on Configured tab")
        # esperar que la tabla exista
        wait_visible(driver, (By.XPATH, "//table[contains(@class,'table')]",), timeout=10)
        return True
    else:
        logger.error("No se pudo clicar en Configured")
        return False


def search_user(driver, user, timeout=10):
    locator = (By.XPATH, "//*[@id='free_text' or @name='free_text' or contains(@placeholder,'Search')]")
    input_el = wait_visible(driver, locator, timeout=timeout)
    input_el.clear()
    input_el.send_keys(user)

    # Enviar enter
    input_el.send_keys("\n")
    logger.info(f"Search executed for user: {user}")
    return True


def extract_view_username(driver):
    """
    Desde la página de detalle de la ONU, extrae el username real.
    Ajusta el XPATH según SmartOLT real.
    """
    try:
        user_locator = (By.XPATH, "//td[contains(text(),'Username')]/following-sibling::td")
        cell = wait_visible(driver, user_locator, timeout=5)
        return cell.text.strip()
    except:
        return None

def _get_result_rows(driver):
    """Helper: devuelve la lista actual de filas resultantes (puede ser vacía)."""
    try:
        return driver.find_elements(By.XPATH, "//tr[contains(@class, 'valign-center')]")
    except Exception:
        return []

def open_matching_result(driver, expected_onu, timeout=10):
    """
    Recorre TODAS las filas, abre cada View, lee username, compara.
    Devuelve True si encuentra coincidencia exacta.
    """
    locator = (By.XPATH, "//tr[contains(@class, 'valign-center')]")
    wait_visible(driver, locator, 2)
    
    rows = driver.find_elements(*locator)

    if not rows:
        logger.info("No hay filas para procesar.")
        return False

    for i, row in enumerate(rows, start=1):
        logger.info(f"Analizando fila #{i} ...")

        try:
            view_btn = row.find_element(
                By.XPATH,
                ".//a[contains(.,'View') or contains(.,'view')] | .//button[contains(.,'View') or contains(.,'view')]"
            )
            view_btn.click()
        except Exception as e:
            logger.error(f"No se pudo abrir View en fila #{i}: {e}")
            continue

        # Extraer username real
        real_user = extract_view_username(driver)
        logger.info(f"Username encontrado en detalle: {real_user}")

        if real_user and real_user.lower() == expected_onu.lower():
            logger.info("Coincidencia exacta encontrada ✔")
            return True

        # No coincide → volver atrás
        logger.info("No coincide. Regresando...")
        driver.back()

        # Esperar tabla de nuevo
        wait_visible(driver, (By.XPATH, "//tr[contains(@class, 'valign-center')]"), timeout=10)
        time.sleep(1)

    # Se recorrieron todas las filas
    logger.info("No se encontró coincidencia exacta.")
    return False