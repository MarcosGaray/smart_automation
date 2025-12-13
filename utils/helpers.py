from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from typing import Optional
import time
from exceptions import ElementException

def wait_presence(driver, locator, timeout=15):
    return WebDriverWait(driver, timeout).until(EC.presence_of_element_located(locator))

def wait_visible(driver, locator, timeout=15):
    return WebDriverWait(driver, timeout).until(EC.visibility_of_element_located(locator))

def wait_clickable(driver, locator, timeout=15):
    return WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(locator))

def safe_click(driver, locator, timeout=15):
    try:
        el = wait_clickable(driver, locator, timeout=timeout)
        el.click()
        return True
    except TimeoutException:
        return False
    except Exception:
        raise ElementException("No se pudo hacer safe click en el elemento")

def find_all_in(parent, locator):
    try:
        return parent.find_elements(*locator)
    except Exception:
        return []

def find_in(parent, locator) -> Optional[object]:
    try:
        return parent.find_element(*locator)
    except NoSuchElementException:
        return None

def wait_until(driver,until_expression, timeout=15):
    return WebDriverWait(driver, timeout).until(until_expression)

def assert_real_function_result(function, driver, expected_result=None, retries=3, delay=3, comparator=None ):
    """
    Ejecuta function(driver) varias veces hasta obtener un resultado estable.
    
    Params:
        function: función que recibe driver
        expected_result: string/valor esperado (igualdad exacta)
        retries: número de reintentos
        delay: segundos entre intentos
        comparator: función custom comparator(result, expected) -> bool

    Retorna:
        último resultado real_result
    """

    last_result = None

    for attempt in range(retries):
        try:
            real_result = function(driver)
            print(f"Real result: {real_result}")
            last_result = real_result
        except Exception:
            time.sleep(delay)
            continue

        # === Comparaciones posibles ===
        if comparator:
            if comparator(real_result, expected_result):
                return real_result

        elif expected_result is not None:
            # Si expected_result es string, permitir "Online" dentro de "Online (1m)"
            if isinstance(real_result, str) and isinstance(expected_result, str):
                if expected_result.lower() in real_result.lower():
                    return real_result

            # Comparación exacta
            if real_result == expected_result:
                return real_result

        # Esperar antes del próximo intento
        time.sleep(delay)

    # Si nunca coincidió, devolver último resultado
    return last_result
