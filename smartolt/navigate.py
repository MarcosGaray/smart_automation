from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from utils.helpers import wait_clickable, wait_visible
from utils.logger import get_logger
from smartolt.onu_actions import reveal_pppoe_username
from selenium.common.exceptions import StaleElementReferenceException
import time
from exceptions import ElementException
from data import CONFIGURED_URL

logger = get_logger(__name__)

def go_to_configured_tab(driver, timeout=10):
    try:
        locator = (By.XPATH, "//*[@id='navbar-main']//a[contains(normalize-space(.), 'Configured')]")
        if wait_clickable(driver, locator, timeout=timeout):
            driver.find_element(*locator).click()
            logger.info("Clicked on Configured tab")
            wait_visible(driver, (By.XPATH, "//table[contains(@class,'table')]",), timeout=10)
            return True
        else:
            raise ElementException("No se pudo clicar en Configured")
    except ElementException as e:
        raise
    except Exception as e:
        raise ElementException(f"No se pudo clicar en Configured: {e}")

def go_to_configured_by_URL(driver):
    try:
        driver.get(CONFIGURED_URL)
        wait_visible(driver, (By.XPATH, "//table[contains(@class,'table')]",), timeout=10)
    except Exception as e:
        raise ElementException(f"No se pudo acceder a Configured con la URL")
    
def search_user(driver, onu_username, timeout=10):
    locator = (By.XPATH, "//*[@id='free_text' or @name='free_text' or contains(@placeholder,'Search')]")

    logger.info(f"Search: {onu_username}")

    def get_input():
        return wait_visible(driver, locator, timeout=timeout)

    for step in ["find", "clear", "send_keys"]:
        try:
            input_el = get_input()

            if step == "clear":
                input_el.clear()

            elif step == "send_keys":
                input_el.clear()  # extra seguridad
                input_el.send_keys(onu_username)
                input_el.send_keys("\n")

        except StaleElementReferenceException:
            logger.warning(f"[WARN] stale en step '{step}' → reintentando…")
            time.sleep(0.2)
            input_el = get_input()
            if step == "clear":
                input_el.clear()
            elif step == "send_keys":
                input_el.clear()
                input_el.send_keys(onu_username)
                input_el.send_keys("\n")

    logger.info(f"Search executed for user: {onu_username}")
    return True


def go_back(driver, locator=(By.XPATH, "//tr[contains(@class, 'valign-center')]"), timeout=10):
    driver.back()
    # Espera a que el DOM deje de cambiar (clave para SmartOLT)
    WebDriverWait(driver, timeout).until(
        lambda d: d.execute_script("return document.readyState") == "complete"
    )
    wait_visible(driver, locator, timeout=10)
    time.sleep(2)

def open_matching_result(driver, expected_onu, timeout=2):
    row_locator = (By.XPATH, "//tr[contains(@class, 'valign-center')]")

    try:
        wait_visible(driver, row_locator, timeout)
    except Exception:
        raise ElementException(f"No hay resultados de la busqueda: {expected_onu}. Posible ONU eliminada o en Bridge Mode")

    index = 0

    while True:
        rows = driver.find_elements(*row_locator)

        if index >= len(rows):
            break

        logger.info(f"Analizando fila #{index + 1} ...")

        try:
            row = rows[index]

            view_btn = row.find_element(
                By.XPATH,
                ".//a[contains(.,'View') or contains(.,'view')] | "
                ".//button[contains(.,'View') or contains(.,'view')]"
            )

            view_btn.click()

        except StaleElementReferenceException:
            logger.warning("Fila stale, reintentando...")
            continue
        except Exception:
            logger.error(f"No se pudo abrir View en fila #{index + 1}")
            index += 1
            continue

        real_user = reveal_pppoe_username(driver)
        logger.info(f"Username encontrado en detalle: {real_user}")

        if real_user and real_user.lower() == expected_onu.lower():
            logger.info("Coincidencia exacta encontrada ✔")
            return True

        logger.info("No coincide. Regresando...")
        logger.info("-----------------------------------------------------")
        go_back(driver)

        index += 1

    logger.info("Se recorrieron todas las filas. No se encontró coincidencia exacta.")
    return False