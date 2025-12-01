from utils.helpers import wait_visible
from selenium.webdriver.common.by import By
from utils.logger import get_logger
from sheets.sheets_reader import load_check_connection_list
from sheets.sheets_writer import log_connection_success, log_connection_fail
from exceptions import ElementException, Disconnected_ONU_Exception, ConnectionValidationException

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


def start_connection_validation(driver):
    logger.info("Iniciando validación de conexión...")
    try:
        onu_list= load_check_connection_list()
        import pdb
        """ pdb.set_trace() """
        for onu_data in onu_list:
            onu_username = onu_data[0]
            onu_url = onu_data[1]
            print(onu_username)
            print(onu_url)

            driver.get(onu_url)
            log_connection_success(onu_username)
            log_connection_fail(onu_username)

    except Exception:  
        raise ConnectionValidationException(f"No se pudo leer archivo de entrada")
    
    input('llegamos aqui')

    """ for onu in onu_list:
        status = open_tr069_and_check_ppp(driver)
        if status == 'disconnected':
            raise Disconnected_ONU_Exception(f"ONU {onu} desconectada") """