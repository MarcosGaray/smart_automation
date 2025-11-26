from selenium.webdriver.common.by import By
from utils.helpers import wait_visible, wait_clickable, find_in,wait_presence, wait_clickable, safe_click
from utils.logger import get_logger
from sheets.sheets_writer import log_success, log_fail, save_unprocessed
import pdb

logger = get_logger(__name__)

def reveal_pppoe_username(driver, timeout=8):
    """
    En la vista de ONU, clickea el control que revela el PPPoE username y devuelve el texto.
    Este selector debe adaptarse al HTML real del SmartOLT. Se dan varias opciones.
    """
    # supuestos: hay un botón o link que muestra el PPPoE username; y un span con id 'pppoeUsername' o similar.
    possible_buttons = [
        (By.XPATH, "//a[contains(@class,'show_pppoe_username')]")
    ]

    clicked = False
    for sel in possible_buttons:
        try:
            if wait_clickable(driver, sel, timeout=2):
                driver.find_element(*sel).click()
                clicked = True
                break
        except Exception:
            continue

    # buscar el span que contiene el username
    possible_spans = [
        (By.XPATH, "//span[contains(@class, 'pppoe_username') and not(contains(@class, 'hidden'))]")
    ]
    #pdb.set_trace()
    for span in possible_spans:
        try:
            username_field = wait_presence(driver, span, timeout=4)
            text = username_field.get_attribute("innerText").strip()
            if text:
                return text
        except Exception:
            continue

    logger.warning("No se pudo obtener PPPoE username con los selectores configurados.")
    return None

def get_onu_status(driver, timeout=8):
    element_status = wait_visible(driver, (By.XPATH, "//dd[@id='onu_status_wrapper']"), timeout=timeout)
    return element_status.get_attribute("innerText").strip()

def migrate_vlan(driver, onu, timeout=8):
    onu_status = get_onu_status(driver, timeout=timeout)    
    expected_status = 'Online'
    
    configure_locator = (By.XPATH, "//a[@href='#updateSpeedProfiles']")
    
    try:
        safe_click(driver, configure_locator)
        input("Continuar...")
    except Exception:
        log_fail(onu, "No se pudo acceder a la sección de configuración.")
        logger.error("No se pudo acceder a la sección de configuración.")
        return False
    
    return True

# TODO: agregar migrate_vlan(driver), reboot_onu(driver), etc. cuando tengamos los selectores exactos.
