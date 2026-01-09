from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from utils.helpers import wait_visible, wait_clickable
from utils.logger import get_logger
import time
from data import URL
from utils.locators import USERNAME_INPUT_LOCATOR, PASSWORD_INPUT_LOCATOR, SUBMIT_BUTTON_LOCATOR_1, SUBMIT_BUTTON_LOCATOR_2, SUBMIT_BUTTON_LOCATOR_3, SUBMIT_BUTTON_LOCATOR_4, NAV_BAR_LOCATOR

logger = get_logger(__name__)

def login_smartolt(driver, user, password, timeout=15):
    driver.get(URL)
    try:
        user_input = wait_visible(driver, USERNAME_INPUT_LOCATOR, timeout=timeout)
    except TimeoutException:
        logger.error("No apareció el campo de usuario en el login.")
        raise

    pass_input = driver.find_element(*PASSWORD_INPUT_LOCATOR)
    print('LLEGOOO')
    user_input.clear()
    user_input.send_keys(user)
    pass_input.clear()
    pass_input.send_keys(password)
    

    # Buscar botón submit de forma robusta:
    # intentamos varios selectores en orden
    btn_selectors = [
        SUBMIT_BUTTON_LOCATOR_1,
        SUBMIT_BUTTON_LOCATOR_2,
        SUBMIT_BUTTON_LOCATOR_3,
        SUBMIT_BUTTON_LOCATOR_4,
    ]

    clicked = False
    for sel in btn_selectors:
        try:
            if wait_clickable(driver, sel, timeout=3):
                driver.find_element(*sel).click()
                clicked = True
                break
        except Exception:
            continue

    if not clicked:
        logger.warning("No se encontró un botón de login típico, intentando enviar ENTER en password")
        pass_input.send_keys("\n")
    

    # Esperar a que el dashboard cargue: buscar un elemento del navbar que identifique login correcto
    try:
        wait_visible(driver, NAV_BAR_LOCATOR, timeout=10)
        logger.info("Login exitoso (detectada navbar).")
    except Exception:
        logger.warning("No se detectó navbar tras login; revisar si login fue correcto.")