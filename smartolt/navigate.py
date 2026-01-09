from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from sheets.sheets_writer import log_fail, log_migration_success
from smartolt.onu_actions import change_speed_profile
from utils.helpers import wait_clickable, wait_visible
from utils.logger import get_logger
from smartolt.onu_functions import reveal_pppoe_username
from selenium.common.exceptions import StaleElementReferenceException
import time
from exceptions import ElementException
from data import CONFIGURED_URL
from utils.locators import ONU_ROW_VIEW_BUTTON_LOCATOR, ROW_LOCATOR, CONFIGURED_BUTTON_LOCATOR, GENERIC_TABLE_LOCATOR_1, SEARCH_USER_TEXTBOX_LOCATOR
logger = get_logger(__name__)

def go_to_configured_tab(driver, timeout=10):
    try:
        locator = CONFIGURED_BUTTON_LOCATOR
        if wait_clickable(driver, locator, timeout=timeout):
            driver.find_element(*locator).click()
            logger.info("Clicked on Configured tab")
            wait_visible(driver, GENERIC_TABLE_LOCATOR_1, timeout=10)
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
        wait_visible(driver,  GENERIC_TABLE_LOCATOR_1, timeout=10)
    except Exception as e:
        raise ElementException(f"No se pudo acceder a Configured con la URL")

def go_to_URL(driver, url, wait_for = None):
    try:
        driver.get(url)
        time.sleep(1)
        if wait_for is not None:
            wait_visible(driver, wait_for, timeout=10)
    except Exception as e:
        raise ElementException(f'No se pudo acceder a la URL "{url}"')
    
def search_user(driver, onu_username, timeout=10):
    locator = SEARCH_USER_TEXTBOX_LOCATOR

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


def go_back(driver, locator=ROW_LOCATOR, timeout=10):
    driver.back()
    # Espera a que el DOM deje de cambiar (clave para SmartOLT)
    WebDriverWait(driver, timeout).until(
        lambda d: d.execute_script("return document.readyState") == "complete"
    )
    wait_visible(driver, locator, timeout=10)
    time.sleep(2)

def open_matching_result(driver, expected_onu, timeout=2):
    row_locator = ROW_LOCATOR

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

            view_btn = row.find_element(*ONU_ROW_VIEW_BUTTON_LOCATOR)

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


def open_matching_results_and_change_speed_profile(driver, go_to_URL_callback):
    row_locator = ROW_LOCATOR

    try:
        wait_visible(driver, row_locator)
    except Exception:
        raise ElementException(f"No hay ONUS en la URL especificada")

    index = 0

    while True:
        rows = driver.find_elements(*row_locator)

        if 0 >= len(rows):
            break

        logger.info(f"Analizando fila #{index + 1} ...")

        try:
            row = rows[0]

            view_btn = row.find_element(
                *ONU_ROW_VIEW_BUTTON_LOCATOR
            )

            view_btn.click()

        except StaleElementReferenceException:
            logger.warning("Fila stale, reintentando...")
            continue
        except Exception:
            logger.error(f"No se pudo abrir View en fila #{index + 1}")
            index += 1
            continue
        
        try:
            try:
                username = reveal_pppoe_username(driver)
                logger.info(f"Username encontrado en detalle: {username}")
            except Exception:
                raise

            change_speed_profile(driver, username)
            log_migration_success(username, driver.current_url)
            logger.info(f"ÉXITO: {username}.")
        except Exception as e:
            short_msg = getattr(e, "msg", str(e)).split("\n")[0].strip()
            log_fail(username,f"{short_msg}")
            logger.error(f"ERROR: {short_msg}")

        go_to_URL_callback()

        index += 1

    logger.info("Se recorrieron todas las filas. Perfiles de velocidad cambiados.")