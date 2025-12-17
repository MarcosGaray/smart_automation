from utils.helpers import wait_visible
from selenium.webdriver.common.by import By
from exceptions import ElementException
from utils.helpers import safe_click,assert_real_function_result
import time
from utils.logger import get_logger
from data import PPP_GATEWAY
from utils import words_and_messages as msg

logger = get_logger(__name__)

def get_ppp_gateway(driver, open_tr069_and_ppp_interface_section=False):
    # open_tr069_and_check_ppp
        try:
            ppp_gateway_value = assert_real_function_result(get_ppp_gateway_value, driver=driver, expected_result=PPP_GATEWAY, attempt_msg=msg.PPP_GATEWAY_ATTEMP_MSG)
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