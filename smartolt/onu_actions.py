from selenium.webdriver.common.by import By
from utils.helpers import wait_until, wait_visible, wait_clickable, wait_presence, wait_clickable, safe_click
from utils.logger import get_logger
from data import VLAN_MIGRATION_DICT
from exceptions import ElementException
import time

logger = get_logger(__name__)

##ACCIONES/INTERACCIONES
def reveal_pppoe_username(driver, timeout=8):
    possible_buttons = [
        (By.XPATH, "//a[contains(@class,'show_pppoe_username')]")
    ]

    for sel in possible_buttons:
        try:
            if wait_clickable(driver, sel, timeout=2):
                driver.find_element(*sel).click()
                break
        except Exception:
            continue

    # Buscar el span que contiene el username
    possible_spans = [
        (By.XPATH, "//span[contains(@class, 'pppoe_username') and not(contains(@class, 'hidden'))]")
    ]
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
    element_status = wait_visible(driver, (By.XPATH, "//dd[@id='onu_status_wrapper']"), timeout=timeout)
    return element_status.get_attribute("innerText").strip()

def open_configure_modal(driver, timeout=8):
    configure_locator = (By.XPATH, "//a[@href='#updateSpeedProfiles']")
    if not safe_click(driver, configure_locator):
        raise ElementException("No se pudo abrir la ventana Configure. Error al clicar en el botón Configure")
    return True

def get_configuration_modal(driver, timeout=8):
    modal_locators = [
        (By.XPATH, "//div[contains(@class,'modal') and @id='updateSpeedProfiles']"),
        (By.XPATH, "//div[contains(@class,'modal') and not(contains(@style,'display: none'))]"),
    ]

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

def get_select_vlan_element(driver, timeout=8):
    select_locator = (By.XPATH, "//select[@id='extra_vlan_id']")
    try:
        select_element = wait_visible(driver, select_locator, timeout=6)
    except Exception:
        raise ElementException("No se encontró el selector de VLAN.")
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

def is_vlan_in_migration_dictionary(vlan, vlan_migration_dict):
    return vlan in vlan_migration_dict.keys()
    
def get_select_target_option(selenium_select, target_vlan_text):
    selenium_select_target_option = None
    
    for option in selenium_select.options:
        option_text = option.get_attribute("innerText").strip()
        if option_text == target_vlan_text:
            selenium_select_target_option = option
            break

    if selenium_select_target_option is None:
        raise ElementException(f"Target VLAN '{target_vlan_text}' no encontrada entre las opciones de VLAN de la ONU")

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
    svlan_wrapper_locator = (By.XPATH, "//div[@id='svlan_controls_wrapper']")
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


def migrate_vlan(driver, onu, timeout=70):
    # Supuesto: ESTAMOS EN LA PAGINA DE CONFIGURACIÓN DE LA ONU
    # 1) Abrir modal de configuración
    try:
        open_configure_modal(driver)
        modal = get_configuration_modal(driver)
    except ElementException as ex:
        raise


    # 2) Buscar el SELECT de VLAN
    # 3) Convertir a objeto Select de Selenium
    # 4) Leer la opción actualmente seleccionada por su texto (innerText)
    try:
        select_element = get_select_vlan_element(driver, timeout=6)
        selenium_select = get_selenium_select_element(select_element)
        current_selected_vlan_text = get_selenium_select_innerText(selenium_select)
    except ElementException:
        raise
    

    # 5) Checkear si tiene SVLAN-ID
    try:
        use_svlan = check_svlan_id(driver) # True si tiene SVLAN-ID
    except ElementException:
        raise
    except Exception:
        raise ElementException("Error detectando si la ONU usa SVLAN-ID")
    
    logger.info(f"ONU {onu} - VLAN actual (texto): '{current_selected_vlan_text}'")

    # 6) Verificar si la VLAN actual está en el diccionario
    if not is_vlan_in_migration_dictionary(current_selected_vlan_text, VLAN_MIGRATION_DICT):
        raise ElementException(f"VLAN actual '{current_selected_vlan_text}' no está en el diccionario de migración")

    target_vlan_text = VLAN_MIGRATION_DICT[current_selected_vlan_text]

    # 7) Revisar el estado de la ONU
    expected_onu_status = 'Online'
    is_online = True
    try:
        onu_status = get_onu_status(driver, timeout=timeout)    
    except Exception as ex:
        raise ElementException(f"Error al obtener el estado de la ONU")

    if not onu_status.__contains__(expected_onu_status):
        is_online = False


    # 8) Si vlan_actual == vlan_target → ya está migrada
    if current_selected_vlan_text == target_vlan_text:
        logger.info(f"ONU {onu} ya estaba en target VLAN '{target_vlan_text}'")
        return True,is_online, use_svlan

    # 9) Buscar la opción cuyo texto coincida con target_text y seleccionar
    try:
        vlan_target_option = get_select_target_option(selenium_select, target_vlan_text)
        try:
            # seleccionar por visible text si coincide exactamente:
            selenium_select.select_by_visible_text(target_vlan_text)
        except Exception:
            # fallback: seleccionar por value del option encontrado
            value = vlan_target_option.get_attribute("value")
            selenium_select.select_by_value(value)
    except ElementException as ex:
        raise
    except Exception as ex:
        raise ElementException(f"No se pudo seleccionar la VLAN target '{target_vlan_text}': {ex}")


    logger.info(f"ONU {onu} - VLAN target seleccionada '{target_vlan_text}'")


    # 10) Click en Save y esperar confirmación (si corresponde)
    save_locator = (By.XPATH, "//a[@id='submitUpdateSpeedProfiles' or contains(@class,'submitUpdateSpeedProfiles') or normalize-space(.)='Save']")
    try:
        safe_click(driver, save_locator, timeout=6)
    except Exception:
        raise ElementException(f"No se pudo hacer click en Save")
    
    # 11) Esperar a que la modal se cierre
    try:
        wait_modal_closed(driver, modal)
    except Exception:
        raise ElementException("No se pudo cerrar la ventana modal de configuración")
    
    # 12) Determinar si hacer resync o no
    if is_online:
        # Hacer resync
        try:
            resync_onu_config(driver)
            logger.info(f"ONU {onu} Resync exitoso")
        except Exception as ex:
            raise
        
        # Hacer Reboot
        try:
            reboot_onu(driver, timeout=8)
            logger.info(f"ONU {onu} Reboot Exitoso")
        except Exception as ex:
            raise

    logger.info("---------------------------------------------")
    logger.info(f"ONU {onu} VLAN migrada correctamente: {current_selected_vlan_text} -> {target_vlan_text}")
    logger.info("---------------------------------------------")

    return True, is_online ,use_svlan

#resync_onu_config(driver)
def resync_onu_config(driver,timeout=120):
    resync_locator = (By.XPATH, "//a[@id='rebuildModal' or normalize-space(.)='Resync config']")
    try:
        try:
            safe_click(driver, resync_locator, timeout=6)
        except Exception:
            raise ElementException(f"No se pudo hacer click en Resync config")

        # Esperar que abra la modal
        resync_modal = get_resync_modal(driver)

        # Click en resync
        confirm_resync_locator = (By.XPATH, "//div[@id='rebuildModal']//a[contains(normalize-space(),'Resync config') and contains(@class,'btn-yellow')]")
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
    modal_locators = [
        (By.XPATH, "//div[@id='rebuildModal' and contains(@class,'in')]"),
        (By.XPATH, "//div[contains(@class,'modal') and not(contains(@style,'display: none'))]"),
    ]

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
    reboot_locator = (By.XPATH, "//a[@id='rebootModal' or normalize-space(.)='Reboot']")
    try:
        try:
            safe_click(driver, reboot_locator, timeout=6)
        except Exception:
            raise ElementException(f"No se pudo hacer click en Reboot")

        # Esperar que abra la modal
        reboot_modal = get_reboot_modal(driver)

        # Click en reboot
        confirm_reboot_locator = (By.XPATH, "//div[@id='rebootModal']//a[contains(normalize-space(),'Reboot') and contains(@class,'btn-warning')]")
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
    modal_locators = [
        (By.XPATH, "//div[@id='rebootModal' and contains(@class,'in')]"),
        (By.XPATH, "//div[contains(@class,'modal') and not(contains(@style,'display: none'))]"),
    ]

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
