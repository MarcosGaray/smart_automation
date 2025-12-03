from selenium.webdriver.common.by import By
from utils.helpers import wait_until, wait_visible, wait_clickable, find_in,wait_presence, wait_clickable, safe_click
from utils.logger import get_logger
from sheets.sheets_writer import log_migration_success, log_fail, save_unprocessed
import pdb
from data import VLAN_MIGRATION_DICT
from exceptions import ElementException, Disconnected_ONU_Exception, SVLANException
import time

logger = get_logger(__name__)

def reveal_pppoe_username(driver, timeout=8):
    # Buscar el botón que muestra el username
    possible_buttons = [
        (By.XPATH, "//a[contains(@class,'show_pppoe_username')]")
    ]

    clicked = False
    for sel in possible_buttons:
        try:
            if wait_clickable(driver, sel, timeout=2):
                driver.find_element(*sel).click()
                clicked = True
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


##ACCIONES/INTERACCIONES
# Obtiene el status de la ONU (online, disconnected, etc.)
def get_onu_status(driver, timeout=8):
    time.sleep(3)
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
    
def get_select_target_option(selenium_select, target_text):
    select_target_option = None
    
    for option in selenium_select.options:
        option_text = option.get_attribute("innerText").strip()
        if option_text == target_text:
            select_target_option = option
            break

    if select_target_option is None:
        raise ElementException(f"Target VLAN '{target_text}' no encontrada entre las opciones de VLAN de la ONU")

    return select_target_option

def wait_modal_closed(driver, modal, timeout=60):
    from selenium.common.exceptions import StaleElementReferenceException
    def is_closed(_):
        try:
            # si ya no se muestra → cerrada
            if not modal.is_displayed():
                return True

            style = modal.get_attribute("style") or ""
            if "display: none" in style.lower():
                return True

            # sigue visible → no cerrada
            return False

        except StaleElementReferenceException:
            # Si está stale, significa que fue removida → cerrada
            return True

    wait_until(driver, is_closed, timeout=timeout)
    
def check_svlan_id(driver, svlan_wrapper_locator, timeout=8):
    """
    Devuelve True si la ONU está usando SVLAN-ID.
    Devuelve False si el div está en display:none (SVLAN no usado).
    """

    try:
        wrapper = wait_presence(driver, svlan_wrapper_locator, timeout=timeout)
    except Exception:
        raise ElementException("No se encontró el contenedor svlan_controls_wrapper")

    style = wrapper.get_attribute("style") or ""

    # Si contiene display:none → no usa svlan
    if "display: none" in style.replace(" ", "").lower():
        return False

    # Visible → usa svlan
    return True


def migrate_vlan(driver, onu, timeout=8):
    # 1) Revisar el estado de la ONU
    expected_status = 'Online'
    is_online = True
    try:
        #pdb.set_trace()
        onu_status = get_onu_status(driver, timeout=timeout)    
    except Exception as ex:
        raise ElementException(f"Error al obtener el estado de la ONU")

    if not onu_status.__contains__(expected_status):
        is_online = False

    # 2) Abrir modal Configure
    # 3) Esperar a que la modal esté presente y visible (manejar animación)
    try:
        open_configure_modal(driver)
        modal = get_configuration_modal(driver)
    except ElementException as ex:
        raise


    # 4️⃣ Buscar el SELECT de VLAN
    # 5 Convertir a objeto Select de Selenium
    # 6) Leer la opción actualmente seleccionada por su texto (innerText)
    try:
        select_element = get_select_vlan_element(driver, timeout=6)
        selenium_select = get_selenium_select_element(select_element)
        vlan_select_current_text = get_selenium_select_innerText(selenium_select)
    except ElementException:
        raise
    

    logger.info(f"ONU {onu} - VLAN actual (texto): '{vlan_select_current_text}'")

    # 7) Verificar si la VLAN actual está en el diccionario
    if not is_vlan_in_migration_dictionary(vlan_select_current_text, VLAN_MIGRATION_DICT):
        raise ElementException(f"VLAN actual '{vlan_select_current_text}' no está en el diccionario de migración")

    # 8) Checkear si tiene SVLAN-ID
    try:
        svlan_wrapper_locator = (By.XPATH, "//div[@id='svlan_controls_wrapper']")
        use_svlan = check_svlan_id(driver, svlan_wrapper_locator, timeout=timeout)
    except ElementException:
        raise
    except Exception:
        raise ElementException("Error detectando si la ONU usa SVLAN-ID")

    target_text = VLAN_MIGRATION_DICT[vlan_select_current_text]
    # 9) Si actual == target → ya migrada
    if vlan_select_current_text == target_text:
        logger.info(f"ONU {onu} ya estaba en target VLAN '{target_text}'")
        return True,is_online, use_svlan

    # 10) Buscar la opción cuyo texto coincida con target_text y seleccionar
    try:
        target_option = get_select_target_option(selenium_select, target_text)
        try:
            # seleccionar por visible text si coincide exactamente:
            selenium_select.select_by_visible_text(target_text)
        except Exception:
            # fallback: seleccionar por value del option encontrado
            value = target_option.get_attribute("value")
            selenium_select.select_by_value(value)
    except ElementException as ex:
        raise
    except Exception as ex:
        raise ElementException(f"No se pudo seleccionar la VLAN target '{target_text}': {ex}")


    logger.info(f"ONU {onu} - VLAN target seleccionada '{target_text}'")


    # 11) Click en Save y esperar confirmación (si corresponde)
    save_locator = (By.XPATH, "//a[@id='submitUpdateSpeedProfiles' or contains(@class,'submitUpdateSpeedProfiles') or normalize-space(.)='Save']")
    try:
        safe_click(driver, save_locator, timeout=6)
    except Exception:
        raise ElementException(f"No se pudo hacer click en Save")
    
    # 12) Esperar a que la modal se cierre
    try:
        wait_modal_closed(driver, modal)
    except Exception:
        raise ElementException("No se pudo cerrar la ventana modal de configuración")
    
    

    if is_online == False:
        logger.info(f"ONU {onu} no se encuentra Online. Reboot innecesario. Migración Exitosa!")
        #En vez de excepcion implementear devolucion de otra variable.. return True, online, svlan_id
        #raise Disconnected_ONU_Exception("La ONU no se encuentra Online. Reboot innecesario. Migración Exitosa!")
    
    # 14) Hacer resync
    """  try:
        resync_onu_config(driver, timeout=60)
    except Exception as ex:
        raise
    
    logger.info(f"ONU {onu} Resync exitoso") """
    
    # 15) Hacer Reboot
    try:
        reboot_onu(driver, timeout=8)
    except Exception as ex:
        raise

    logger.info(f"ONU {onu} Reboot iniciado")
    logger.info(f"ONU {onu} VLAN migrada correctamente: {vlan_select_current_text} -> {target_text}")

    return True, is_online ,use_svlan

#resync_onu_config(driver)
def resync_onu_config(driver,timeout=60):
    resync_locator = (By.XPATH, "//a[@id='rebuildModal' or normalize-space(.)='Resync config']")
    try:
        safe_click(driver, resync_locator, timeout=6)

        # Esperar que abra la modal
        resync_modal = get_resync_modal(driver)

        # Click en resync
        confirm_resync_locator = (By.XPATH, "//div[@id='rebuildModal']//a[contains(normalize-space(),'Resync config') and contains(@class,'btn-yellow')]")
        try:
            safe_click(driver, confirm_resync_locator, timeout=10)
        except Exception:
            raise ElementException(f"No se pudo hacer click en confirmar resync")

        # Esperar a que cierre la modal de resync
        try:
            wait_modal_closed(driver, resync_modal, timeout=120)   
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
def reboot_onu(driver,timeout=10):
    reboot_locator = (By.XPATH, "//a[@id='rebootModal' or normalize-space(.)='Reboot']")
    try:
        safe_click(driver, reboot_locator, timeout=6)

        # Esperar queabra la modal
        reboot_modal = get_reboot_modal(driver)

        # Click en reboot
        confirm_reboot_locator = (By.XPATH, "//div[@id='rebootModal']//a[contains(normalize-space(),'Reboot') and contains(@class,'btn-warning')]")
        try:
            safe_click(driver, confirm_reboot_locator, timeout=10)
        except Exception:
            raise ElementException(f"No se pudo hacer click en confirmar reboot")

        # Esperar a que cierre la modal de reboot
        try:
            wait_modal_closed(driver, reboot_modal, timeout=30)   
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
