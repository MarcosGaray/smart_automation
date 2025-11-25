from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from utils.helpers import wait_visible, wait_clickable
from utils.logger import get_logger
import time

logger = get_logger(__name__)

from data import URL

def login_smartolt(driver, user, password, timeout=15):

    driver.get(URL)

    try:
        user_input = wait_visible(driver, (By.XPATH, "//*[@id='identity']"), timeout=timeout)
    except TimeoutException:
        logger.error("No apareció el campo de usuario en el login.")
        raise

    pass_input = driver.find_element(By.XPATH, "//*[@id='password']")
    user_input.clear()
    user_input.send_keys(user)
    pass_input.clear()
    pass_input.send_keys(password)

    # Buscar botón submit de forma robusta:
    # intentamos varios selectores en orden
    btn_selectors = [
        (By.XPATH, "//form//button[@type='submit']"),
        (By.XPATH, "//form//input[@type='submit']"),
        (By.XPATH, "//button[contains(., 'Login')]"),
        (By.XPATH, "//button[contains(., 'Sign in')]"),
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
        wait_visible(driver, (By.XPATH, "//*[contains(@class, 'navbar')]"), timeout=10)
        logger.info("Login exitoso (detectada navbar).")
    except Exception:
        logger.warning("No se detectó navbar tras login; revisar si login fue correcto.")


""" 

# smartolt/login.py
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from utils.helpers import wait_visible, wait_clickable
from utils.logger import get_logger
import time

logger = get_logger(__name__)

def login_smartolt(driver, user, password, timeout=15):

    from data import URL  # import local para flexibilidad
    driver.get(URL)

    # Esperar inputs
    try:
        user_input = wait_visible(driver, (By.XPATH, "//*[@id='identity']"), timeout=timeout)
    except TimeoutException:
        logger.error("No apareció el campo de usuario en el login.")
        raise

    pass_input = driver.find_element(By.XPATH, "//*[@id='password']")
    user_input.clear()
    user_input.send_keys(user)
    pass_input.clear()
    pass_input.send_keys(password)

    # Buscar botón submit de forma robusta:
    # intentamos varios selectores en orden
    btn_selectors = [
        (By.XPATH, "//form//button[@type='submit']"),
        (By.XPATH, "//form//input[@type='submit']"),
        (By.XPATH, "//button[contains(., 'Login')]"),
        (By.XPATH, "//button[contains(., 'Sign in')]"),
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
        # ejemplo: esperar la barra de navegación principal
        wait_visible(driver, (By.XPATH, "//*[@id='navbar-main']"), timeout=10)
        logger.info("Login exitoso (detectada navbar-main).")
    except Exception:
        logger.warning("No se detectó navbar-main tras login; revisar si login fue correcto.")
        # no raise, permitimos que el flujo decida
"""