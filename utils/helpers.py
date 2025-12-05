from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from typing import Optional
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