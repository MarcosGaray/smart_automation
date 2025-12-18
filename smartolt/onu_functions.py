from utils.helpers import wait_visible
from selenium.webdriver.common.by import By
from exceptions import ElementException
from utils.helpers import assert_real_function_result
import time
from utils.logger import get_logger
from utils import words_and_messages as msg
from data import PPP_VALID_GATEWAY_LIST

logger = get_logger(__name__)

def get_ppp_gateway(driver):
        try:
            ppp_gateway_value = assert_real_function_result(get_ppp_gateway_value, driver=driver, expected_result="990.990.990.990", attempt_msg=msg.PPP_GATEWAY_ATTEMP_MSG)
            #print("log, llego a get_ppp_gateway_value")
            return ppp_gateway_value
        except ElementException as e:
            logger.error("Error al obtener el PPP Gateway: {e}. Se continua el flujo normal")
        except Exception:
            logger.error("Error inesperado Obteniendo el PPP Gateway. Se continua el flujo normal")
        return None
    
def get_ppp_gateway_value(driver):
    ppp_gateway_locator = (By.XPATH, "//td[normalize-space()='PPP Gateway']/following-sibling::td")
    try:
        ppp_gateway = wait_visible(driver, ppp_gateway_locator,6)
        ppp_gateway_value = ppp_gateway.text.strip().lower()
    except Exception:
        raise ElementException("No se pudo obtener el PPP Gateway")
    return ppp_gateway_value

def is_valid_ppp_gateway(ppp_gateway_value):
    if ppp_gateway_value is None:
        return False
    for ppp_gateway in PPP_VALID_GATEWAY_LIST:
        if ppp_gateway in ppp_gateway_value:
            return True
    return False