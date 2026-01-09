from utils.helpers import wait_visible
from selenium.webdriver.common.by import By
from exceptions import ElementException
from utils.helpers import assert_real_function_result
import time
from utils.locators import ATTACHED_VLANS_BUTTON_LOCATOR, CONFIRM_REBOOT_BUTTON_LOCATOR, CONFIRM_RESYNC_BUTTON_LOCATOR, GENERAL_MODAL_LOCATOR_1, ONU_REBOOT_BUTTON_LOCATOR, ONU_RESYNC_BUTTON_LOCATOR, ONU_UPDATE_MODE_BUTTON_LOCATOR, ONU_UPDATE_MODE_MODAL_LOCATOR, PPP_GATEWAY_LOCATOR, REBOOT_MODAL_LOCATOR, RESYNC_MODAL_LOCATOR, SPEED_PROFILE_CONFIGURE_BUTTON_LOCATOR, SPEED_PROFILE_CONFIGURE_MODAL_LOCATOR, SUBMIT_UPDATE_MODE_BUTTON_LOCATOR, SUBMIT_UPDATE_SPEED_PROFILES_BUTTON_LOCATOR, SVLAN_CHECK_BOX_LOCATOR, SVLAN_CONTROLS_WRAPPER_LOCATOR, VLAN_SELECT_LOCATOR, REVEAL_PPPOE_USERNAME_BUTTON_LOCATOR,PPPOE_USERNAME_SPAN_LOCATOR,ONU_STATUS_LOCATOR
from utils.logger import get_logger
from utils import words_and_messages as msg
from data import PPP_VALID_GATEWAY_LIST, SPEEDS_PROFILE_DICT, VLAN_MIGRATION_DICT
from utils.helpers import wait_until, wait_visible, wait_clickable, wait_presence, wait_clickable, safe_click, assert_real_function_result


logger = get_logger(__name__)

def reveal_pppoe_username(driver, timeout=8):
    possible_buttons = [REVEAL_PPPOE_USERNAME_BUTTON_LOCATOR]

    for sel in possible_buttons:
        try:
            if wait_clickable(driver, sel, timeout=2):
                driver.find_element(*sel).click()
                break
        except Exception:
            continue

    # Buscar el span que contiene el username
    possible_spans = [PPPOE_USERNAME_SPAN_LOCATOR]
    #pdb.set_trace()
    for span in possible_spans:
        try:
            username_field = wait_presence(driver, span, timeout=4)
            text = username_field.get_attribute("innerText").strip()
            if text:
                return text
        except Exception:
            continue

    logger.warning("No se pudo obtener PPPoE username con los selectores configurados.")
    return None

def get_onu_status(driver, timeout=8):
    element_status = wait_visible(driver,ONU_STATUS_LOCATOR , timeout=timeout)
    return element_status.get_attribute("innerText").strip()

def open_configure_modal(driver, timeout=8):
    configure_locator = SPEED_PROFILE_CONFIGURE_BUTTON_LOCATOR
    if not safe_click(driver, configure_locator):
        raise ElementException("No se pudo abrir la ventana Configure. Error al clicar en el botón Configure")
    return True

def open_onu_mode_modal(driver, timeout=8):
    onu_mode_locator = ONU_UPDATE_MODE_BUTTON_LOCATOR
    if not safe_click(driver, onu_mode_locator):
        raise ElementException("No se pudo abrir la ventana ONU mode. Error al clicar en el botón ONU mode")
    return True

def get_configuration_modal(driver, timeout=8):
    modal_locators = [SPEED_PROFILE_CONFIGURE_MODAL_LOCATOR,GENERAL_MODAL_LOCATOR_1]

    modal = None
    for loc in modal_locators:
        try:
            modal = wait_visible(driver, loc, timeout=6)
            break
        except Exception:
            continue

    if modal is None:
        raise ElementException("No apareció la ventana modal de configuración (posible animación/carga).")
    return modal

def get_onu_mode_modal(driver, timeout=8):
    modal_locators = [ONU_UPDATE_MODE_MODAL_LOCATOR,GENERAL_MODAL_LOCATOR_1,]

    modal = None
    for loc in modal_locators:
        try:
            modal = wait_visible(driver, loc, timeout=6)
            break
        except Exception:
            continue

    if modal is None:
        raise ElementException("No apareció la ventana modal de onu mode (posible animación/carga).")
    return modal

def get_select_element(driver,select_locator = VLAN_SELECT_LOCATOR, timeout=8):
    select_locator = select_locator
    try:
        select_element = wait_visible(driver, select_locator, timeout=6)
    except Exception:
        raise ElementException("No se encontró el selector especificado.")
    return select_element

def get_selenium_select_element(select_element):
    try:
        from selenium.webdriver.support.ui import Select
        selenium_select = Select(select_element)
    except:
        raise ElementException("No se pudo crear el objeto Select de selenium.")
    return selenium_select

def get_selenium_select_innerText(selenium_select):
    try:
        current_option = selenium_select.first_selected_option
        current_text = current_option.get_attribute("innerText").strip()
    except Exception:
        raise ElementException("No se pudo leer la opción seleccionada del vlan select.")
    return current_text

def is_vlan_in_migration_dictionary(vlan):
    return vlan in VLAN_MIGRATION_DICT.keys()

def is_speed_in_speed_profile_dictionary(speed):
    return speed in SPEEDS_PROFILE_DICT.keys()
    
def get_select_target_option(selenium_select, target_text):
    selenium_select_target_option = None
    
    for option in selenium_select.options:
        option_text = option.get_attribute("innerText").strip()
        if option_text == target_text:
            selenium_select_target_option = option
            break

    if selenium_select_target_option is None:
        raise ElementException(f"Target select text '{target_text}' no encontrada entre las opciones del select.")

    return selenium_select_target_option

def wait_modal_closed(driver, modal, timeout=60):
    from selenium.common.exceptions import StaleElementReferenceException
    def is_closed(_):
        try:
            if not modal.is_displayed():
                return True

            style = modal.get_attribute("style") or ""
            if "display: none" in style.lower():
                return True

            return False

        except StaleElementReferenceException:
            # Si está stale, significa que fue removida → cerrada
            return True

    wait_until(driver, is_closed, timeout=timeout)
    
def check_svlan_id(driver, timeout=2):
    svlan_wrapper_locator = SVLAN_CONTROLS_WRAPPER_LOCATOR
    try:
        wrapper = wait_presence(driver, svlan_wrapper_locator, timeout=timeout)
    except Exception:
        return False

    style = (wrapper.get_attribute("style") or "").strip().lower()

    style = style.replace(" ", "")

    if "display:none" in style:
        return False

    try:
        if not wrapper.is_displayed():
            return False
    except Exception:
        pass

    return True

def alternate_svlan_checkbox(driver, timeout=5):
    svlan_checkbox_locator = SVLAN_CHECK_BOX_LOCATOR
    try:
        safe_click(driver, svlan_checkbox_locator,timeout)
    except Exception:
        raise ElementException("No se pudo alternar el checkbox de SVLAN. Debe quedar unchecked.")

def get_attached_vlans(driver, timeout=8):
    attached_vlans_locator = ATTACHED_VLANS_BUTTON_LOCATOR
    try:
        element = wait_visible(driver, attached_vlans_locator, timeout=timeout)
        element_text = element.get_attribute("innerText").strip().replace(" ", "")

        if not element_text:
            raise ElementException("No posee attached VLANs")

        # Filtrar posibles strings vacíos
        vlans = [vlan for vlan in element_text.split(",") if vlan]

        return vlans
    except ElementException:
        raise
    except Exception:
        raise ElementException("Error detectando si la ONU tiene attached VLANs")

def save_and_close_modal(driver,modal,save_locator=None):
    if save_locator is None:
        raise ElementException("Debe indicar un localizador para el botón 'save' o 'update'")
    try:
        safe_click(driver, save_locator, timeout=6)
    except Exception:
        raise ElementException(f"No se pudo hacer click en 'save' o 'update'")
    
    # Esperar a que la modal se cierre
    try:
        wait_modal_closed(driver, modal)
    except Exception:
        raise ElementException("No se pudo cerrar la ventana modal")
    

def save_and_close_configuration_modal(driver,modal):
    save_locator = SUBMIT_UPDATE_SPEED_PROFILES_BUTTON_LOCATOR
    try:
        save_and_close_modal(driver,modal,save_locator)
        logger.info("Ventana modal de configuración: saved and closed")
    except ElementException as ex:
        message = ex.args[0]
        raise ElementException(f"Error en ventana modal de configuración: {message}")
        
def update_and_close_onu_mode_modal(driver,modal):
    update_locator = SUBMIT_UPDATE_MODE_BUTTON_LOCATOR
    try:
        save_and_close_modal(driver,modal,update_locator)
        logger.info("Ventana modal de onu mode: updated and closed")
    except ElementException as ex:
        message = ex.args[0]
        raise ElementException(f"Error en ventana modal de onu mode: {message}")

#resync_onu_config(driver)
def resync_onu_config(driver,timeout=120):
    resync_locator = ONU_RESYNC_BUTTON_LOCATOR
    try:
        try:
            safe_click(driver, resync_locator, timeout=6)
        except Exception:
            raise ElementException(f"No se pudo hacer click en Resync config")

        # Esperar que abra la modal
        resync_modal = get_resync_modal(driver)

        # Click en resync
        confirm_resync_locator = CONFIRM_RESYNC_BUTTON_LOCATOR
        try:
            safe_click(driver, confirm_resync_locator, timeout=10)
        except Exception:
            raise ElementException(f"No se pudo hacer click en confirmar resync config")

        # Esperar a que cierre la modal de resync
        try:
            wait_modal_closed(driver, resync_modal, timeout=timeout)   
        except Exception:
            raise ElementException(f"No se pudo cerrar la ventana modal de resync")
    except ElementException:
        raise
    except Exception:
        raise ElementException(f"No se pudo hacer click en Resync config")
    
def get_resync_modal(driver, timeout=10):
    modal_locators = [RESYNC_MODAL_LOCATOR,GENERAL_MODAL_LOCATOR_1]

    modal = None
    for loc in modal_locators:
        try:
            modal = wait_visible(driver, loc, timeout=timeout)
            break
        except Exception:
            continue

    if modal is None:
        raise ElementException("No apareció la ventana modal de resync (posible animación/carga).")
    return modal

#reboot_onu(driver)
def reboot_onu(driver,timeout=30):
    reboot_locator = ONU_REBOOT_BUTTON_LOCATOR
    try:
        try:
            safe_click(driver, reboot_locator, timeout=6)
        except Exception:
            raise ElementException(f"No se pudo hacer click en Reboot")

        # Esperar que abra la modal
        reboot_modal = get_reboot_modal(driver)

        # Click en reboot
        confirm_reboot_locator = CONFIRM_REBOOT_BUTTON_LOCATOR
        try:
            safe_click(driver, confirm_reboot_locator, timeout=10)
        except Exception:
            raise ElementException(f"No se pudo hacer click en confirmar reboot")

        # Esperar a que cierre la modal de reboot
        try:
            wait_modal_closed(driver, reboot_modal, timeout=timeout)   
        except Exception:
            raise ElementException("No se pudo cerrar la ventana modal de reboot")
    except ElementException:
        raise
    except Exception:
        raise ElementException(f"No se pudo hacer click en Reboot")
    
def get_reboot_modal(driver, timeout=10):
    modal_locators = [REBOOT_MODAL_LOCATOR,GENERAL_MODAL_LOCATOR_1]

    modal = None
    for loc in modal_locators:
        try:
            modal = wait_visible(driver, loc, timeout=timeout)
            break
        except Exception:
            continue

    if modal is None:
        raise ElementException("No apareció la ventana modal de reboot (posible animación/carga).")
    return modal


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
    ppp_gateway_locator = PPP_GATEWAY_LOCATOR
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