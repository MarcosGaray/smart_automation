from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from typing import Optional
import time
from exceptions import ElementException
from utils.logger import get_logger
from utils import words_and_messages as msg

logger = get_logger(__name__)

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

def assert_real_function_result(function, driver, expected_result=None, attempt_msg = {msg.DEFAULT_ATTEMP_MSG}, retries=4, delay=3, comparator=None ):
    last_result = None
    logger.info("")
    for attempt in range(retries):
        attempt_text = f"{msg.ATTEMPT} {attempt + 1}"
        try:
            real_result = function(driver)
            logger.info(f"{attempt_text} - {attempt_msg}: {real_result}")
            last_result = real_result
        except Exception as e:
            short_msg = getattr(e, "msg", str(e)).split("\n")[0].strip()
            logger.warning(f"{attempt_text} {short_msg}")
            time.sleep(delay)
            continue

        # === Comparaciones posibles ===
        if comparator:
            if comparator(real_result, expected_result):
                return real_result

        elif expected_result is not None:
            if isinstance(real_result, str) and isinstance(expected_result, str):
                if expected_result == "connected":
                    if real_result.strip().lower() == expected_result.strip().lower():
                        return real_result
                else:
                    if expected_result.lower() in real_result.lower():
                        return real_result


            # Comparación exacta
            if real_result == expected_result:
                return real_result

        # Esperar antes del próximo intento
        time.sleep(delay)
    # Si nunca coincidió, devolver último resultado
    return last_result
