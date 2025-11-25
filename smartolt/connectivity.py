# smartolt/connectivity.py
from utils.helpers import wait_visible
from selenium.webdriver.common.by import By
from utils.logger import get_logger

logger = get_logger(__name__)

def open_tr069_and_check_ppp(driver, timeout=8):
    """
    Abre la sección tr069Stat -> PPP Interface y devuelve 'connected', 'connecting', 'disconnected' o None.
    Implementación depende de HTML real.
    """
    try:
        # click TR-069 tab/button (ejemplo de selector)
        if wait_visible(driver, (By.XPATH, "//*[contains(., 'tr069') or contains(., 'TR-069') or contains(., 'TR069')]"), timeout=3):
            driver.find_element(By.XPATH, "//*[contains(., 'tr069') or contains(., 'TR-069') or contains(., 'TR069')]").click()
    except Exception:
        pass

    # Esperar la tabla PPP Interface
    try:
        status_el = wait_visible(driver, (By.XPATH, "//td[contains(., 'connection status')]/following-sibling::td"), timeout=6)
        status_text = status_el.text.strip().lower()
        return status_text
    except Exception:
        return None
