from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from utils.helpers import wait_clickable, wait_visible, wait_presence
from utils.logger import get_logger
from smartolt.onu_actions import reveal_pppoe_username
from selenium.common.exceptions import StaleElementReferenceException
import time

logger = get_logger(__name__)

def go_to_configured_tab(driver, timeout=10):
    locator = (By.XPATH, "//*[@id='navbar-main']//a[contains(normalize-space(.), 'Configured')]")
    if wait_clickable(driver, locator, timeout=timeout):
        driver.find_element(*locator).click()
        logger.info("Clicked on Configured tab")
        
        wait_visible(driver, (By.XPATH, "//table[contains(@class,'table')]",), timeout=10)
        return True
    else:
        logger.error("No se pudo clicar en Configured")
        return False


def search_user(driver, user, timeout=10):
    locator = (By.XPATH, "//*[@id='free_text' or @name='free_text' or contains(@placeholder,'Search')]")

    logger.info(f"Search: {user}")

    def get_input():
        return wait_visible(driver, locator, timeout=timeout)

    for step in ["find", "clear", "send_keys"]:
        try:
            input_el = get_input()

            if step == "clear":
                input_el.clear()

            elif step == "send_keys":
                input_el.clear()  # extra seguridad
                input_el.send_keys(user)
                input_el.send_keys("\n")

        except StaleElementReferenceException:
            logger.warning(f"[WARN] stale en step '{step}' → reintentando…")
            time.sleep(0.2)
            input_el = get_input()
            if step == "clear":
                input_el.clear()
            elif step == "send_keys":
                input_el.clear()
                input_el.send_keys(user)
                input_el.send_keys("\n")

    logger.info(f"Search executed for user: {user}")
    return True


def go_back(driver, locator, timeout=10):
    driver.back()
    # Espera a que el DOM deje de cambiar (clave para SmartOLT)
    WebDriverWait(driver, timeout).until(
        lambda d: d.execute_script("return document.readyState") == "complete"
    )
    wait_visible(driver, locator, timeout=10)
    time.sleep(2)

def open_matching_result(driver, expected_onu, timeout=10):
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
        real_user = reveal_pppoe_username(driver)
        logger.info(f"Username encontrado en detalle: {real_user}")

        if real_user and real_user.lower() == expected_onu.lower():
            logger.info("Coincidencia exacta encontrada ✔")
            return True

        # No coincide → volver atrás
        logger.info("No coincide. Regresando...")

        go_back(driver, (By.XPATH, "//tr[contains(@class, 'valign-center')]"))

    # Se recorrieron todas las filas
    logger.info("No se encontró coincidencia exacta.")
    return False