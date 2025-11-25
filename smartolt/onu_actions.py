from selenium.webdriver.common.by import By
from utils.helpers import wait_visible, wait_clickable, find_in
from utils.logger import get_logger

logger = get_logger(__name__)

def reveal_pppoe_username(driver, timeout=8):
    """
    En la vista de ONU, clickea el control que revela el PPPoE username y devuelve el texto.
    Este selector debe adaptarse al HTML real del SmartOLT. Se dan varias opciones.
    """
    # supuestos: hay un botón o link que muestra el PPPoE username; y un span con id 'pppoeUsername' o similar.
    possible_buttons = [
        (By.XPATH, "//button[contains(., 'Show PPPoE') or contains(., 'Reveal')]"),
        (By.XPATH, "//a[contains(., 'Show PPPoE') or contains(., 'Reveal')]"),
        (By.XPATH, "//button[contains(., 'PPP') or contains(., 'pppoe')]"),
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
        (By.XPATH, "//*[contains(@id,'pppoe') and (contains(., '@') or string-length(normalize-space(.))>1)]"),
        (By.XPATH, "//span[contains(.,'@') or contains(.,'pppoe') or contains(@class,'pppoe')]")
    ]
    for sp in possible_spans:
        try:
            el = wait_visible(driver, sp, timeout=4)
            text = el.text.strip()
            if text:
                return text
        except Exception:
            continue

    logger.warning("No se pudo obtener PPPoE username con los selectores configurados.")
    return None

# TODO: agregar migrate_vlan(driver), reboot_onu(driver), etc. cuando tengamos los selectores exactos.
